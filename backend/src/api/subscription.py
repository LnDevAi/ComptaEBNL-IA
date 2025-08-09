"""
Module de Gestion des Abonnements SaaS
Gère les plans, abonnements, paiements (Stripe, PayPal, Mobile Money)
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from decimal import Decimal
import json
import hashlib
import hmac
import uuid
import requests
from functools import wraps

from models import (
    db, PlanAbonnement, Abonnement, Paiement, UtilisationQuota,
    CouponReduction, Utilisateur, TypePlan, StatutAbonnement,
    MethodePaiement, StatutPaiement
)

subscription_bp = Blueprint('subscription', __name__)

# ============================
# DECORATORS ET UTILS
# ============================

def subscription_required(f):
    """Décorator pour vérifier l'abonnement actif"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            return jsonify({'success': False, 'error': 'Authentification requise'}), 401
        
        # Vérifier l'abonnement actif
        abonnement = Abonnement.query.filter_by(
            utilisateur_id=current_user.id,
            statut=StatutAbonnement.ACTIF
        ).first()
        
        if not abonnement or not abonnement.est_actif():
            return jsonify({
                'success': False, 
                'error': 'Abonnement actif requis',
                'code': 'SUBSCRIPTION_REQUIRED'
            }), 402
        
        kwargs['current_subscription'] = abonnement
        return f(*args, **kwargs)
    return decorated_function

def check_quota(resource_type):
    """Décorator pour vérifier les quotas d'utilisation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            abonnement = kwargs.get('current_subscription')
            if not abonnement:
                return f(*args, **kwargs)
            
            # Vérifier le quota selon le type de ressource
            if resource_type == 'ecritures':
                if abonnement.ecritures_utilisees_mois >= abonnement.plan.max_ecritures_mois:
                    return jsonify({
                        'success': False,
                        'error': 'Quota d\'écritures dépassé',
                        'quota_actuel': abonnement.ecritures_utilisees_mois,
                        'quota_max': abonnement.plan.max_ecritures_mois
                    }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================
# GESTION DES PLANS
# ============================

@subscription_bp.route('/plans', methods=['GET'])
def get_plans():
    """Récupère tous les plans d'abonnement disponibles"""
    try:
        plans = PlanAbonnement.query.filter_by(actif=True).all()
        
        plans_data = []
        for plan in plans:
            plan_dict = plan.to_dict()
            
            # Ajouter des informations calculées
            if plan.prix_annuel:
                economie_annuelle = (plan.prix_mensuel * 12) - plan.prix_annuel
                plan_dict['economie_annuelle'] = float(economie_annuelle)
                plan_dict['pourcentage_economie'] = round((economie_annuelle / (plan.prix_mensuel * 12)) * 100, 1)
            
            plans_data.append(plan_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'plans': plans_data,
                'devises_supportees': ['EUR', 'XOF', 'XAF', 'USD'],
                'methodes_paiement': [
                    'stripe', 'paypal', 'mtn_mobile_money', 
                    'orange_money', 'wave', 'moov_money', 'airtel_money'
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_plan_detail(plan_id):
    """Détails d'un plan spécifique"""
    try:
        plan = PlanAbonnement.query.get(plan_id)
        if not plan:
            return jsonify({'success': False, 'error': 'Plan introuvable'}), 404
        
        return jsonify({
            'success': True,
            'data': plan.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================
# GESTION DES ABONNEMENTS
# ============================

@subscription_bp.route('/mon-abonnement', methods=['GET'])
def get_my_subscription():
    """Récupère l'abonnement actuel de l'utilisateur"""
    try:
        # Pour la démo, on simule un utilisateur connecté
        user_id = request.headers.get('X-User-ID', 1)
        
        abonnement = Abonnement.query.filter_by(
            utilisateur_id=user_id
        ).order_by(Abonnement.date_creation.desc()).first()
        
        if not abonnement:
            return jsonify({
                'success': True,
                'data': {
                    'abonnement': None,
                    'a_abonnement': False
                }
            })
        
        # Récupérer les statistiques d'utilisation
        now = datetime.now()
        utilisation = UtilisationQuota.query.filter_by(
            abonnement_id=abonnement.id,
            annee=now.year,
            mois=now.month
        ).first()
        
        abonnement_data = abonnement.to_dict()
        if utilisation:
            abonnement_data['utilisation_detaillee'] = {
                'ecritures': utilisation.ecritures_utilisees,
                'documents': utilisation.documents_traites,
                'api_calls': utilisation.appels_api,
                'stockage_mb': utilisation.stockage_utilise_mb
            }
        
        return jsonify({
            'success': True,
            'data': {
                'abonnement': abonnement_data,
                'a_abonnement': True
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route('/souscrire', methods=['POST'])
def create_subscription():
    """Créer un nouvel abonnement"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['plan_id', 'periode', 'methode_paiement']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ requis: {field}'}), 400
        
        # Vérifier le plan
        plan = PlanAbonnement.query.get(data['plan_id'])
        if not plan:
            return jsonify({'success': False, 'error': 'Plan introuvable'}), 404
        
        # Calculer le montant selon la période
        if data['periode'] == 'mensuel':
            montant = plan.prix_mensuel
            date_fin = datetime.utcnow() + timedelta(days=30)
        elif data['periode'] == 'annuel' and plan.prix_annuel:
            montant = plan.prix_annuel
            date_fin = datetime.utcnow() + timedelta(days=365)
        else:
            return jsonify({'success': False, 'error': 'Période invalide'}), 400
        
        # Appliquer un coupon si fourni
        if 'code_coupon' in data:
            coupon = CouponReduction.query.filter_by(code=data['code_coupon']).first()
            if coupon and coupon.est_valide(float(montant)):
                reduction = coupon.calculer_reduction(float(montant))
                montant = max(0, montant - Decimal(str(reduction)))
                coupon.utilisations_actuelles += 1
        
        # Créer l'abonnement
        user_id = request.headers.get('X-User-ID', 1)  # Simulation
        
        abonnement = Abonnement(
            utilisateur_id=user_id,
            plan_id=plan.id,
            statut=StatutAbonnement.EN_ATTENTE,
            date_debut=datetime.utcnow(),
            date_fin=date_fin,
            periode_facturation=data['periode'],
            montant=montant,
            devise=data.get('devise', 'EUR')
        )
        
        db.session.add(abonnement)
        db.session.flush()  # Pour obtenir l'ID
        
        # Créer le paiement
        paiement = Paiement(
            abonnement_id=abonnement.id,
            utilisateur_id=user_id,
            montant=montant,
            devise=abonnement.devise,
            methode_paiement=MethodePaiement(data['methode_paiement']),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Traitement selon la méthode de paiement
        payment_result = process_payment(paiement, data)
        
        if payment_result['success']:
            abonnement.statut = StatutAbonnement.ACTIF
            paiement.statut = StatutPaiement.REUSSI
            paiement.date_traitement = datetime.utcnow()
        else:
            paiement.statut = StatutPaiement.ECHOUE
            paiement.message_erreur = payment_result.get('error', 'Erreur de paiement')
        
        db.session.add(paiement)
        db.session.commit()
        
        return jsonify({
            'success': payment_result['success'],
            'data': {
                'abonnement_id': abonnement.id,
                'paiement_id': paiement.id,
                'montant': float(montant),
                'statut': abonnement.statut.value,
                'payment_url': payment_result.get('payment_url'),
                'transaction_id': payment_result.get('transaction_id')
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================
# TRAITEMENT DES PAIEMENTS
# ============================

def process_payment(paiement, data):
    """Traite un paiement selon la méthode choisie"""
    
    if paiement.methode_paiement == MethodePaiement.STRIPE:
        return process_stripe_payment(paiement, data)
    
    elif paiement.methode_paiement == MethodePaiement.PAYPAL:
        return process_paypal_payment(paiement, data)
    
    elif paiement.methode_paiement in [
        MethodePaiement.MTN_MOBILE_MONEY,
        MethodePaiement.ORANGE_MONEY,
        MethodePaiement.WAVE,
        MethodePaiement.MOOV_MONEY,
        MethodePaiement.AIRTEL_MONEY
    ]:
        return process_mobile_money_payment(paiement, data)
    
    else:
        return {'success': False, 'error': 'Méthode de paiement non supportée'}

def process_stripe_payment(paiement, data):
    """Traitement Stripe"""
    try:
        # Configuration Stripe (à adapter avec vos clés)
        stripe_api_key = current_app.config.get('STRIPE_SECRET_KEY', 'sk_test_...')
        
        # Simulation d'un paiement Stripe réussi
        transaction_id = f"pi_{uuid.uuid4().hex[:24]}"
        
        paiement.stripe_payment_intent_id = transaction_id
        paiement.transaction_id_externe = transaction_id
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'payment_url': f"https://checkout.stripe.com/pay/{transaction_id}"
        }
    
    except Exception as e:
        return {'success': False, 'error': f'Erreur Stripe: {str(e)}'}

def process_paypal_payment(paiement, data):
    """Traitement PayPal"""
    try:
        # Simulation d'un paiement PayPal
        order_id = f"PAYPAL-{uuid.uuid4().hex[:16].upper()}"
        
        paiement.paypal_order_id = order_id
        paiement.transaction_id_externe = order_id
        
        return {
            'success': True,
            'transaction_id': order_id,
            'payment_url': f"https://www.paypal.com/checkoutnow?token={order_id}"
        }
    
    except Exception as e:
        return {'success': False, 'error': f'Erreur PayPal: {str(e)}'}

def process_mobile_money_payment(paiement, data):
    """Traitement Mobile Money (MTN, Orange, Wave, etc.)"""
    try:
        # Validation des données Mobile Money
        if 'numero_telephone' not in data:
            return {'success': False, 'error': 'Numéro de téléphone requis'}
        
        numero = data['numero_telephone']
        operateur = paiement.methode_paiement.value
        
        # Sauvegarder les détails Mobile Money
        paiement.numero_telephone = numero
        paiement.operateur_mobile = operateur
        
        # Simulation selon l'opérateur
        if paiement.methode_paiement == MethodePaiement.MTN_MOBILE_MONEY:
            return process_mtn_mobile_money(paiement, data)
        
        elif paiement.methode_paiement == MethodePaiement.ORANGE_MONEY:
            return process_orange_money(paiement, data)
        
        elif paiement.methode_paiement == MethodePaiement.WAVE:
            return process_wave_payment(paiement, data)
        
        else:
            # Simulation générique pour autres opérateurs
            transaction_id = f"MM-{operateur.upper()}-{uuid.uuid4().hex[:12]}"
            paiement.mobile_money_transaction_id = transaction_id
            paiement.transaction_id_externe = transaction_id
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'message': f'Paiement initié via {operateur}. Composez *XXX# pour confirmer.'
            }
    
    except Exception as e:
        return {'success': False, 'error': f'Erreur Mobile Money: {str(e)}'}

def process_mtn_mobile_money(paiement, data):
    """Traitement MTN Mobile Money"""
    try:
        # Simulation de l'API MTN MoMo
        transaction_id = f"MTN-{uuid.uuid4().hex[:16]}"
        
        # En production, intégrer l'API MTN MoMo
        # https://momodeveloper.mtn.com/
        
        paiement.mobile_money_transaction_id = transaction_id
        paiement.transaction_id_externe = transaction_id
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'message': 'Composez *126# pour confirmer votre paiement MTN Mobile Money',
            'instructions': [
                '1. Composez *126#',
                '2. Sélectionnez "Payer"',
                '3. Entrez le code marchand: 123456',
                '4. Confirmez le montant et votre PIN'
            ]
        }
    
    except Exception as e:
        return {'success': False, 'error': f'Erreur MTN MoMo: {str(e)}'}

def process_orange_money(paiement, data):
    """Traitement Orange Money"""
    try:
        transaction_id = f"OM-{uuid.uuid4().hex[:16]}"
        
        # En production, intégrer l'API Orange Money
        # https://developer.orange.com/apis/orange-money-api/
        
        paiement.mobile_money_transaction_id = transaction_id
        paiement.transaction_id_externe = transaction_id
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'message': 'Composez #144# pour confirmer votre paiement Orange Money',
            'instructions': [
                '1. Composez #144#',
                '2. Sélectionnez "Paiement marchand"',
                '3. Entrez le code: 789123',
                '4. Confirmez avec votre code secret'
            ]
        }
    
    except Exception as e:
        return {'success': False, 'error': f'Erreur Orange Money: {str(e)}'}

def process_wave_payment(paiement, data):
    """Traitement Wave"""
    try:
        transaction_id = f"WAVE-{uuid.uuid4().hex[:16]}"
        
        # En production, intégrer l'API Wave
        # https://developer.wave.com/
        
        paiement.mobile_money_transaction_id = transaction_id
        paiement.transaction_id_externe = transaction_id
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'message': 'Ouvrez votre app Wave pour confirmer le paiement',
            'payment_url': f"wave://pay?merchant=comptaebnl&amount={paiement.montant}&ref={transaction_id}"
        }
    
    except Exception as e:
        return {'success': False, 'error': f'Erreur Wave: {str(e)}'}

# ============================
# WEBHOOKS DE PAIEMENT
# ============================

@subscription_bp.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Webhook Stripe pour confirmer les paiements"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # Vérification de la signature (à implémenter avec votre endpoint secret)
        # stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        event = request.get_json()
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent_id = event['data']['object']['id']
            
            # Trouver le paiement correspondant
            paiement = Paiement.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if paiement:
                paiement.statut = StatutPaiement.REUSSI
                paiement.date_traitement = datetime.utcnow()
                
                # Activer l'abonnement
                paiement.abonnement.statut = StatutAbonnement.ACTIF
                
                db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@subscription_bp.route('/webhooks/mobile-money', methods=['POST'])
def mobile_money_webhook():
    """Webhook générique pour Mobile Money"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        status = data.get('status', 'failed')
        
        # Trouver le paiement
        paiement = Paiement.query.filter_by(
            mobile_money_transaction_id=transaction_id
        ).first()
        
        if paiement:
            if status == 'successful':
                paiement.statut = StatutPaiement.REUSSI
                paiement.abonnement.statut = StatutAbonnement.ACTIF
            else:
                paiement.statut = StatutPaiement.ECHOUE
                paiement.message_erreur = data.get('error_message', 'Paiement échoué')
            
            paiement.date_traitement = datetime.utcnow()
            db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================
# GESTION DES COUPONS
# ============================

@subscription_bp.route('/coupons/verifier', methods=['POST'])
def verify_coupon():
    """Vérifier la validité d'un code coupon"""
    try:
        data = request.get_json()
        code = data.get('code', '').upper()
        montant = Decimal(str(data.get('montant', 0)))
        
        coupon = CouponReduction.query.filter_by(code=code).first()
        
        if not coupon:
            return jsonify({'success': False, 'error': 'Code coupon invalide'}), 404
        
        if not coupon.est_valide(float(montant)):
            return jsonify({'success': False, 'error': 'Code coupon expiré ou inutilisable'}), 400
        
        reduction = coupon.calculer_reduction(float(montant))
        nouveau_montant = max(0, float(montant) - reduction)
        
        return jsonify({
            'success': True,
            'data': {
                'coupon': {
                    'code': coupon.code,
                    'description': coupon.description,
                    'type_reduction': coupon.type_reduction,
                    'valeur_reduction': float(coupon.valeur_reduction)
                },
                'montant_original': float(montant),
                'montant_reduction': reduction,
                'nouveau_montant': nouveau_montant,
                'pourcentage_economie': round((reduction / float(montant)) * 100, 1) if montant > 0 else 0
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================
# STATISTIQUES ABONNEMENTS
# ============================

@subscription_bp.route('/admin/statistiques', methods=['GET'])
def get_subscription_stats():
    """Statistiques administrateur des abonnements"""
    try:
        # Répartition par plan
        stats_plans = db.session.query(
            PlanAbonnement.nom,
            PlanAbonnement.type_plan,
            db.func.count(Abonnement.id).label('nb_abonnements'),
            db.func.sum(Abonnement.montant).label('revenus_total')
        ).join(Abonnement).group_by(PlanAbonnement.id).all()
        
        # Statistiques globales
        total_abonnements = Abonnement.query.count()
        abonnements_actifs = Abonnement.query.filter_by(statut=StatutAbonnement.ACTIF).count()
        revenus_mois = db.session.query(db.func.sum(Paiement.montant)).filter(
            Paiement.statut == StatutPaiement.REUSSI,
            Paiement.date_creation >= datetime.now().replace(day=1)
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'statistiques_globales': {
                    'total_abonnements': total_abonnements,
                    'abonnements_actifs': abonnements_actifs,
                    'taux_activation': round((abonnements_actifs / max(total_abonnements, 1)) * 100, 1),
                    'revenus_mois_courant': float(revenus_mois)
                },
                'repartition_plans': [
                    {
                        'plan': stat.nom,
                        'type': stat.type_plan.value,
                        'abonnements': stat.nb_abonnements,
                        'revenus': float(stat.revenus_total or 0)
                    }
                    for stat in stats_plans
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================
# INITIALISATION DES PLANS
# ============================

def init_default_plans():
    """Initialise les plans par défaut"""
    plans_defaut = [
        {
            'nom': 'Gratuit',
            'type_plan': TypePlan.GRATUIT,
            'prix_mensuel': 0,
            'prix_annuel': 0,
            'max_entites': 1,
            'max_ecritures_mois': 100,
            'max_utilisateurs': 1,
            'max_documents_mois': 10,
            'description': 'Plan gratuit pour découvrir ComptaEBNL-IA'
        },
        {
            'nom': 'Professionnel',
            'type_plan': TypePlan.PROFESSIONNEL,
            'prix_mensuel': 30,
            'prix_annuel': 300,  # 2 mois gratuits
            'max_entites': 3,
            'max_ecritures_mois': -1,  # Illimité
            'max_utilisateurs': 5,
            'max_documents_mois': 500,
            'ia_avancee': True,
            'ocr_documents': True,
            'etats_financiers_avances': True,
            'rapprochement_bancaire': True,
            'description': 'Plan professionnel avec IA avancée'
        },
        {
            'nom': 'Enterprise',
            'type_plan': TypePlan.ENTERPRISE,
            'prix_mensuel': 100,
            'prix_annuel': 1000,  # 2 mois gratuits
            'max_entites': -1,  # Illimité
            'max_ecritures_mois': -1,  # Illimité
            'max_utilisateurs': -1,  # Illimité
            'max_documents_mois': -1,  # Illimité
            'ia_avancee': True,
            'ocr_documents': True,
            'etats_financiers_avances': True,
            'rapprochement_bancaire': True,
            'audit_trail': True,
            'support_prioritaire': True,
            'api_access': True,
            'description': 'Plan enterprise avec toutes les fonctionnalités'
        }
    ]
    
    for plan_data in plans_defaut:
        plan_existant = PlanAbonnement.query.filter_by(
            nom=plan_data['nom']
        ).first()
        
        if not plan_existant:
            plan = PlanAbonnement(**plan_data)
            db.session.add(plan)
    
    try:
        db.session.commit()
        print("✅ Plans d'abonnement initialisés")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur lors de l'initialisation des plans: {e}")

if __name__ == '__main__':
    init_default_plans()