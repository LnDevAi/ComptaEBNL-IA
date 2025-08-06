"""
Middleware de Gestion des Quotas d'Abonnement
Contrôle l'accès aux fonctionnalités selon le plan d'abonnement
"""

from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
from typing import Optional, Callable, Any

from models import (
    db, Abonnement, UtilisationQuota, PlanAbonnement,
    StatutAbonnement, TypePlan
)

class SubscriptionError(Exception):
    """Exception pour les erreurs d'abonnement"""
    def __init__(self, message: str, code: str = 'SUBSCRIPTION_ERROR', status_code: int = 402):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class QuotaManager:
    """Gestionnaire des quotas d'utilisation"""
    
    @staticmethod
    def get_current_usage(abonnement_id: int, annee: int = None, mois: int = None) -> UtilisationQuota:
        """Récupère ou crée l'utilisation du mois courant"""
        if not annee or not mois:
            now = datetime.now()
            annee = now.year
            mois = now.month
        
        utilisation = UtilisationQuota.query.filter_by(
            abonnement_id=abonnement_id,
            annee=annee,
            mois=mois
        ).first()
        
        if not utilisation:
            utilisation = UtilisationQuota(
                abonnement_id=abonnement_id,
                annee=annee,
                mois=mois
            )
            db.session.add(utilisation)
            db.session.commit()
        
        return utilisation
    
    @staticmethod
    def check_quota(abonnement: Abonnement, resource_type: str, quantity: int = 1) -> bool:
        """Vérifie si le quota permet l'utilisation"""
        plan = abonnement.plan
        
        # Plans illimités
        if plan.type_plan in [TypePlan.PROFESSIONNEL, TypePlan.ENTERPRISE]:
            if resource_type == 'ecritures' and plan.max_ecritures_mois == -1:
                return True
            if resource_type == 'documents' and plan.max_documents_mois == -1:
                return True
            if resource_type == 'utilisateurs' and plan.max_utilisateurs == -1:
                return True
        
        # Vérifier les quotas spécifiques
        utilisation = QuotaManager.get_current_usage(abonnement.id)
        
        if resource_type == 'ecritures':
            limite = plan.max_ecritures_mois
            if limite == -1:
                return True
            return (utilisation.ecritures_utilisees + quantity) <= limite
        
        elif resource_type == 'documents':
            limite = plan.max_documents_mois
            if limite == -1:
                return True
            return (utilisation.documents_traites + quantity) <= limite
        
        elif resource_type == 'utilisateurs':
            limite = plan.max_utilisateurs
            if limite == -1:
                return True
            # Compter les utilisateurs actuels (à implémenter selon votre modèle utilisateur)
            return True  # Placeholder
        
        elif resource_type == 'entites':
            limite = plan.max_entites
            if limite == -1:
                return True
            # Compter les entités actuelles
            return True  # Placeholder
        
        return False
    
    @staticmethod
    def increment_usage(abonnement_id: int, resource_type: str, quantity: int = 1):
        """Incrémente l'utilisation d'une ressource"""
        utilisation = QuotaManager.get_current_usage(abonnement_id)
        
        if resource_type == 'ecritures':
            utilisation.ecritures_utilisees += quantity
        elif resource_type == 'documents':
            utilisation.documents_traites += quantity
        elif resource_type == 'api_calls':
            utilisation.appels_api += quantity
        elif resource_type == 'stockage':
            utilisation.stockage_utilise_mb += quantity
        
        utilisation.date_maj = datetime.utcnow()
        db.session.commit()

def subscription_required(f: Callable) -> Callable:
    """Décorateur pour vérifier qu'un abonnement actif existe"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Récupérer l'utilisateur actuel (à adapter selon votre système d'auth)
        user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Authentification requise',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        # Vérifier l'abonnement actif
        abonnement = Abonnement.query.filter_by(
            utilisateur_id=user_id,
            statut=StatutAbonnement.ACTIF
        ).order_by(Abonnement.date_creation.desc()).first()
        
        if not abonnement or not abonnement.est_actif():
            return jsonify({
                'success': False,
                'error': 'Abonnement actif requis pour accéder à cette fonctionnalité',
                'code': 'SUBSCRIPTION_REQUIRED',
                'upgrade_url': '/pricing'
            }), 402
        
        # Ajouter l'abonnement au contexte
        g.current_subscription = abonnement
        
        return f(*args, **kwargs)
    
    return decorated_function

def feature_required(feature_name: str):
    """Décorateur pour vérifier qu'une fonctionnalité est disponible dans le plan"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            abonnement = getattr(g, 'current_subscription', None)
            
            if not abonnement:
                return jsonify({
                    'success': False,
                    'error': 'Abonnement requis',
                    'code': 'SUBSCRIPTION_REQUIRED'
                }), 402
            
            plan = abonnement.plan
            
            # Vérifier les fonctionnalités selon le plan
            feature_map = {
                'ia_avancee': plan.ia_avancee,
                'ocr_documents': plan.ocr_documents,
                'etats_financiers_avances': plan.etats_financiers_avances,
                'rapprochement_bancaire': plan.rapprochement_bancaire,
                'audit_trail': plan.audit_trail,
                'support_prioritaire': plan.support_prioritaire,
                'api_access': plan.api_access
            }
            
            if feature_name not in feature_map or not feature_map[feature_name]:
                return jsonify({
                    'success': False,
                    'error': f'Fonctionnalité "{feature_name}" non disponible dans votre plan {plan.nom}',
                    'code': 'FEATURE_NOT_AVAILABLE',
                    'plan_actuel': plan.nom,
                    'upgrade_url': '/pricing'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def quota_required(resource_type: str, quantity: int = 1):
    """Décorateur pour vérifier et consommer les quotas"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            abonnement = getattr(g, 'current_subscription', None)
            
            if not abonnement:
                return jsonify({
                    'success': False,
                    'error': 'Abonnement requis',
                    'code': 'SUBSCRIPTION_REQUIRED'
                }), 402
            
            # Vérifier le quota
            if not QuotaManager.check_quota(abonnement, resource_type, quantity):
                plan = abonnement.plan
                utilisation = QuotaManager.get_current_usage(abonnement.id)
                
                # Messages d'erreur spécifiques
                if resource_type == 'ecritures':
                    current = utilisation.ecritures_utilisees
                    limit = plan.max_ecritures_mois
                elif resource_type == 'documents':
                    current = utilisation.documents_traites
                    limit = plan.max_documents_mois
                else:
                    current = 0
                    limit = 0
                
                return jsonify({
                    'success': False,
                    'error': f'Quota {resource_type} dépassé pour le plan {plan.nom}',
                    'code': 'QUOTA_EXCEEDED',
                    'quota_details': {
                        'resource_type': resource_type,
                        'current_usage': current,
                        'limit': limit if limit != -1 else 'illimité',
                        'plan': plan.nom
                    },
                    'upgrade_url': '/pricing'
                }), 429
            
            # Exécuter la fonction
            result = f(*args, **kwargs)
            
            # Incrémenter l'utilisation si la fonction a réussi
            if hasattr(result, 'status_code'):
                if 200 <= result.status_code < 300:
                    QuotaManager.increment_usage(abonnement.id, resource_type, quantity)
            else:
                # Pour les fonctions qui ne retournent pas de Response Flask
                QuotaManager.increment_usage(abonnement.id, resource_type, quantity)
            
            return result
        
        return decorated_function
    return decorator

def plan_required(min_plan_type: TypePlan):
    """Décorateur pour exiger un niveau de plan minimum"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            abonnement = getattr(g, 'current_subscription', None)
            
            if not abonnement:
                return jsonify({
                    'success': False,
                    'error': 'Abonnement requis',
                    'code': 'SUBSCRIPTION_REQUIRED'
                }), 402
            
            # Hiérarchie des plans
            plan_hierarchy = {
                TypePlan.GRATUIT: 0,
                TypePlan.PROFESSIONNEL: 1,
                TypePlan.ENTERPRISE: 2
            }
            
            current_level = plan_hierarchy.get(abonnement.plan.type_plan, 0)
            required_level = plan_hierarchy.get(min_plan_type, 0)
            
            if current_level < required_level:
                return jsonify({
                    'success': False,
                    'error': f'Plan {min_plan_type.value} ou supérieur requis',
                    'code': 'PLAN_UPGRADE_REQUIRED',
                    'plan_actuel': abonnement.plan.nom,
                    'plan_requis': min_plan_type.value,
                    'upgrade_url': '/pricing'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def check_subscription_status():
    """Middleware pour vérifier le statut des abonnements expirés"""
    now = datetime.utcnow()
    
    # Marquer les abonnements expirés
    expired_subscriptions = Abonnement.query.filter(
        Abonnement.statut == StatutAbonnement.ACTIF,
        Abonnement.date_fin <= now
    ).all()
    
    for subscription in expired_subscriptions:
        subscription.statut = StatutAbonnement.EXPIRE
    
    if expired_subscriptions:
        db.session.commit()

# Middleware Flask pour les vérifications automatiques
def init_subscription_middleware(app):
    """Initialise le middleware d'abonnement"""
    
    @app.before_request
    def before_request():
        # Vérifier les abonnements expirés périodiquement
        check_subscription_status()
        
        # Ajouter les informations d'abonnement au contexte si l'utilisateur est connecté
        user_id = request.headers.get('X-User-ID')
        if user_id:
            abonnement = Abonnement.query.filter_by(
                utilisateur_id=user_id,
                statut=StatutAbonnement.ACTIF
            ).order_by(Abonnement.date_creation.desc()).first()
            
            g.current_subscription = abonnement
    
    @app.errorhandler(SubscriptionError)
    def handle_subscription_error(error):
        return jsonify({
            'success': False,
            'error': error.message,
            'code': error.code
        }), error.status_code

# Utilitaires pour les vérifications manuelles
class SubscriptionChecker:
    """Classe utilitaire pour les vérifications d'abonnement"""
    
    @staticmethod
    def can_access_feature(user_id: int, feature_name: str) -> bool:
        """Vérifie si un utilisateur peut accéder à une fonctionnalité"""
        abonnement = Abonnement.query.filter_by(
            utilisateur_id=user_id,
            statut=StatutAbonnement.ACTIF
        ).first()
        
        if not abonnement or not abonnement.est_actif():
            return False
        
        plan = abonnement.plan
        feature_map = {
            'ia_avancee': plan.ia_avancee,
            'ocr_documents': plan.ocr_documents,
            'etats_financiers_avances': plan.etats_financiers_avances,
            'rapprochement_bancaire': plan.rapprochement_bancaire,
            'audit_trail': plan.audit_trail,
            'support_prioritaire': plan.support_prioritaire,
            'api_access': plan.api_access
        }
        
        return feature_map.get(feature_name, False)
    
    @staticmethod
    def get_quota_status(user_id: int) -> dict:
        """Récupère le statut des quotas d'un utilisateur"""
        abonnement = Abonnement.query.filter_by(
            utilisateur_id=user_id,
            statut=StatutAbonnement.ACTIF
        ).first()
        
        if not abonnement:
            return {'error': 'Aucun abonnement actif'}
        
        plan = abonnement.plan
        utilisation = QuotaManager.get_current_usage(abonnement.id)
        
        return {
            'plan': plan.nom,
            'quotas': {
                'ecritures': {
                    'utilise': utilisation.ecritures_utilisees,
                    'limite': plan.max_ecritures_mois if plan.max_ecritures_mois != -1 else 'illimité',
                    'pourcentage': (utilisation.ecritures_utilisees / plan.max_ecritures_mois * 100) 
                                   if plan.max_ecritures_mois != -1 else 0
                },
                'documents': {
                    'utilise': utilisation.documents_traites,
                    'limite': plan.max_documents_mois if plan.max_documents_mois != -1 else 'illimité',
                    'pourcentage': (utilisation.documents_traites / plan.max_documents_mois * 100) 
                                   if plan.max_documents_mois != -1 else 0
                },
                'stockage': {
                    'utilise_mb': utilisation.stockage_utilise_mb,
                    'limite': 'illimité'  # À définir selon vos besoins
                }
            },
            'fonctionnalites': {
                'ia_avancee': plan.ia_avancee,
                'ocr_documents': plan.ocr_documents,
                'etats_financiers_avances': plan.etats_financiers_avances,
                'rapprochement_bancaire': plan.rapprochement_bancaire,
                'audit_trail': plan.audit_trail,
                'support_prioritaire': plan.support_prioritaire,
                'api_access': plan.api_access
            }
        }

# Exemple d'utilisation des décorateurs
def example_usage():
    """Exemples d'utilisation des décorateurs de middleware"""
    
    from flask import Blueprint
    
    example_bp = Blueprint('example', __name__)
    
    @example_bp.route('/ecritures', methods=['POST'])
    @subscription_required
    @quota_required('ecritures', 1)
    def create_ecriture():
        """Créer une écriture avec vérification de quota"""
        # Logique de création d'écriture
        return jsonify({'success': True, 'message': 'Écriture créée'})
    
    @example_bp.route('/ia/analyze', methods=['POST'])
    @subscription_required
    @feature_required('ia_avancee')
    @quota_required('documents', 1)
    def ai_analyze():
        """Analyse IA avec vérification de fonctionnalité"""
        # Logique d'analyse IA
        return jsonify({'success': True, 'message': 'Analyse IA effectuée'})
    
    @example_bp.route('/admin/stats', methods=['GET'])
    @subscription_required
    @plan_required(TypePlan.ENTERPRISE)
    def admin_stats():
        """Statistiques admin pour plan Enterprise"""
        # Logique de statistiques admin
        return jsonify({'success': True, 'data': {}})
    
    return example_bp

if __name__ == '__main__':
    print("Middleware d'abonnement configuré !")
    print("Décorateurs disponibles:")
    print("  - @subscription_required")
    print("  - @feature_required('nom_fonctionnalite')")
    print("  - @quota_required('resource_type', quantity)")
    print("  - @plan_required(TypePlan.MINIMUM)")