"""
Service d'intégration Subscription-E-learning pour ComptaEBNL-IA
Gère les règles d'accès et les limitations selon les plans d'abonnement
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Configuration des plans et limitations
PLAN_CONFIGURATIONS = {
    'gratuit': {
        'max_formations': 2,
        'max_certificats': 1,
        'acces_formations_premium': False,
        'acces_quiz_avances': False,
        'duree_limite_heures': 10,
        'support_prioritaire': False,
        'telechargement_pdf': False,
        'acces_statistiques': False
    },
    'professionnel': {
        'max_formations': 10,
        'max_certificats': 5,
        'acces_formations_premium': True,
        'acces_quiz_avances': True,
        'duree_limite_heures': 50,
        'support_prioritaire': True,
        'telechargement_pdf': True,
        'acces_statistiques': True
    },
    'enterprise': {
        'max_formations': -1,  # Illimité
        'max_certificats': -1,  # Illimité
        'acces_formations_premium': True,
        'acces_quiz_avances': True,
        'duree_limite_heures': -1,  # Illimité
        'support_prioritaire': True,
        'telechargement_pdf': True,
        'acces_statistiques': True,
        'acces_admin': True,
        'api_access': True
    }
}

class SubscriptionElearningService:
    """Service d'intégration subscription-elearning"""
    
    def __init__(self):
        self.plans_config = PLAN_CONFIGURATIONS
    
    def get_user_plan(self, user_id: int) -> str:
        """
        Récupère le plan d'abonnement de l'utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            str: Nom du plan ('gratuit', 'professionnel', 'enterprise')
        """
        try:
            # Import ici pour éviter les imports circulaires
            from models_subscription import Abonnement
            
            abonnement = Abonnement.query.filter_by(
                utilisateur_id=user_id,
                actif=True
            ).first()
            
            if abonnement and abonnement.date_fin > datetime.utcnow():
                return abonnement.plan.nom.lower()
            else:
                return 'gratuit'
                
        except Exception:
            # En cas d'erreur, retourner le plan gratuit par défaut
            return 'gratuit'
    
    def check_formation_access(self, user_id: int, formation) -> Tuple[bool, str]:
        """
        Vérifie si l'utilisateur peut accéder à une formation
        
        Args:
            user_id: ID de l'utilisateur
            formation: Objet Formation
            
        Returns:
            Tuple[bool, str]: (accès_autorisé, message_erreur)
        """
        user_plan = self.get_user_plan(user_id)
        plan_config = self.plans_config.get(user_plan, self.plans_config['gratuit'])
        
        # Vérifier si la formation est premium
        if formation.plan_requis != 'gratuit' and not plan_config['acces_formations_premium']:
            return False, f"Cette formation nécessite un abonnement {formation.plan_requis}"
        
        # Vérifier le nombre maximum de formations
        if plan_config['max_formations'] != -1:
            current_count = self._count_user_formations(user_id)
            if current_count >= plan_config['max_formations']:
                return False, f"Limite de {plan_config['max_formations']} formations atteinte pour le plan {user_plan}"
        
        return True, ""
    
    def check_certificate_generation(self, user_id: int) -> Tuple[bool, str]:
        """
        Vérifie si l'utilisateur peut générer un nouveau certificat
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Tuple[bool, str]: (génération_autorisée, message_erreur)
        """
        user_plan = self.get_user_plan(user_id)
        plan_config = self.plans_config.get(user_plan, self.plans_config['gratuit'])
        
        if plan_config['max_certificats'] != -1:
            current_count = self._count_user_certificates(user_id)
            if current_count >= plan_config['max_certificats']:
                return False, f"Limite de {plan_config['max_certificats']} certificats atteinte pour le plan {user_plan}"
        
        return True, ""
    
    def check_pdf_download_access(self, user_id: int) -> bool:
        """
        Vérifie si l'utilisateur peut télécharger les PDFs
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: Accès autorisé au téléchargement PDF
        """
        user_plan = self.get_user_plan(user_id)
        plan_config = self.plans_config.get(user_plan, self.plans_config['gratuit'])
        return plan_config.get('telechargement_pdf', False)
    
    def check_quiz_access(self, user_id: int, quiz) -> Tuple[bool, str]:
        """
        Vérifie si l'utilisateur peut accéder à un quiz
        
        Args:
            user_id: ID de l'utilisateur
            quiz: Objet Quiz
            
        Returns:
            Tuple[bool, str]: (accès_autorisé, message_erreur)
        """
        user_plan = self.get_user_plan(user_id)
        plan_config = self.plans_config.get(user_plan, self.plans_config['gratuit'])
        
        # Vérifier les quiz avancés
        if hasattr(quiz, 'type_quiz') and quiz.type_quiz == 'avance':
            if not plan_config['acces_quiz_avances']:
                return False, "Les quiz avancés nécessitent un abonnement professionnel ou enterprise"
        
        return True, ""
    
    def check_admin_access(self, user_id: int) -> bool:
        """
        Vérifie si l'utilisateur a accès aux fonctions admin
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: Accès admin autorisé
        """
        user_plan = self.get_user_plan(user_id)
        plan_config = self.plans_config.get(user_plan, self.plans_config['gratuit'])
        return plan_config.get('acces_admin', False)
    
    def get_user_limitations(self, user_id: int) -> Dict:
        """
        Récupère les limitations actuelles de l'utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict: Limitations et usage actuel
        """
        user_plan = self.get_user_plan(user_id)
        plan_config = self.plans_config.get(user_plan, self.plans_config['gratuit'])
        
        current_formations = self._count_user_formations(user_id)
        current_certificates = self._count_user_certificates(user_id)
        current_hours = self._count_user_hours(user_id)
        
        return {
            'plan': user_plan,
            'formations': {
                'current': current_formations,
                'limit': plan_config['max_formations'],
                'unlimited': plan_config['max_formations'] == -1
            },
            'certificats': {
                'current': current_certificates,
                'limit': plan_config['max_certificats'],
                'unlimited': plan_config['max_certificats'] == -1
            },
            'heures': {
                'current': current_hours,
                'limit': plan_config['duree_limite_heures'],
                'unlimited': plan_config['duree_limite_heures'] == -1
            },
            'features': {
                'formations_premium': plan_config['acces_formations_premium'],
                'quiz_avances': plan_config['acces_quiz_avances'],
                'support_prioritaire': plan_config['support_prioritaire'],
                'telechargement_pdf': plan_config['telechargement_pdf'],
                'statistiques': plan_config['acces_statistiques'],
                'admin': plan_config.get('acces_admin', False)
            }
        }
    
    def get_upgrade_recommendations(self, user_id: int) -> List[Dict]:
        """
        Génère des recommandations de mise à niveau
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            List[Dict]: Liste des recommandations
        """
        user_plan = self.get_user_plan(user_id)
        limitations = self.get_user_limitations(user_id)
        recommendations = []
        
        if user_plan == 'gratuit':
            # Vérifier si proche des limites
            if limitations['formations']['current'] >= limitations['formations']['limit'] * 0.8:
                recommendations.append({
                    'type': 'formations_limit',
                    'message': 'Vous approchez de la limite de formations. Passez au plan Professionnel pour plus de formations.',
                    'suggested_plan': 'professionnel'
                })
            
            if limitations['certificats']['current'] >= limitations['certificats']['limit']:
                recommendations.append({
                    'type': 'certificates_limit',
                    'message': 'Limite de certificats atteinte. Upgrader pour obtenir plus de certificats.',
                    'suggested_plan': 'professionnel'
                })
        
        elif user_plan == 'professionnel':
            if limitations['formations']['current'] >= limitations['formations']['limit'] * 0.9:
                recommendations.append({
                    'type': 'formations_limit',
                    'message': 'Passez au plan Enterprise pour un accès illimité.',
                    'suggested_plan': 'enterprise'
                })
        
        return recommendations
    
    def _count_user_formations(self, user_id: int) -> int:
        """Compte les formations inscrites de l'utilisateur"""
        try:
            from models_elearning import InscriptionFormation
            return InscriptionFormation.query.filter_by(utilisateur_id=user_id).count()
        except Exception:
            return 0
    
    def _count_user_certificates(self, user_id: int) -> int:
        """Compte les certificats de l'utilisateur"""
        try:
            from models_elearning import Certificat
            return Certificat.query.filter_by(utilisateur_id=user_id).count()
        except Exception:
            return 0
    
    def _count_user_hours(self, user_id: int) -> float:
        """Compte les heures d'apprentissage de l'utilisateur"""
        try:
            from models_elearning import InscriptionFormation
            inscriptions = InscriptionFormation.query.filter_by(utilisateur_id=user_id).all()
            total_minutes = sum(inscription.temps_passe or 0 for inscription in inscriptions)
            return total_minutes / 60.0  # Conversion en heures
        except Exception:
            return 0.0

# Instance globale du service
subscription_service = SubscriptionElearningService()

# Fonctions utilitaires pour l'API
def check_formation_access(user_id: int, formation) -> Tuple[bool, str]:
    """Fonction utilitaire pour vérifier l'accès à une formation"""
    return subscription_service.check_formation_access(user_id, formation)

def check_certificate_generation(user_id: int) -> Tuple[bool, str]:
    """Fonction utilitaire pour vérifier la génération de certificat"""
    return subscription_service.check_certificate_generation(user_id)

def check_pdf_download_access(user_id: int) -> bool:
    """Fonction utilitaire pour vérifier l'accès au téléchargement PDF"""
    return subscription_service.check_pdf_download_access(user_id)

def get_user_limitations(user_id: int) -> Dict:
    """Fonction utilitaire pour récupérer les limitations utilisateur"""
    return subscription_service.get_user_limitations(user_id)