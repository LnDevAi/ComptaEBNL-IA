#!/usr/bin/env python3
"""
Script d'initialisation des données d'abonnement
Crée les plans par défaut et quelques coupons de test
"""

import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_app
from src.models import (
    db, PlanAbonnement, CouponReduction, TypePlan
)

def init_plans():
    """Initialise les plans d'abonnement par défaut"""
    
    plans_data = [
        {
            'nom': 'Gratuit',
            'type_plan': TypePlan.GRATUIT,
            'prix_mensuel': 0,
            'prix_annuel': 0,
            'devise': 'EUR',
            'max_entites': 1,
            'max_ecritures_mois': 100,
            'max_utilisateurs': 1,
            'max_documents_mois': 10,
            'ia_avancee': False,
            'ocr_documents': False,
            'etats_financiers_avances': False,
            'rapprochement_bancaire': False,
            'audit_trail': False,
            'support_prioritaire': False,
            'api_access': False,
            'description': 'Plan gratuit pour découvrir ComptaEBNL-IA. Idéal pour les petites EBNL qui débutent.',
            'actif': True
        },
        {
            'nom': 'Professionnel',
            'type_plan': TypePlan.PROFESSIONNEL,
            'prix_mensuel': 30,
            'prix_annuel': 300,  # 2 mois gratuits
            'devise': 'EUR',
            'max_entites': 3,
            'max_ecritures_mois': -1,  # Illimité
            'max_utilisateurs': 5,
            'max_documents_mois': 500,
            'ia_avancee': True,
            'ocr_documents': True,
            'etats_financiers_avances': True,
            'rapprochement_bancaire': True,
            'audit_trail': False,
            'support_prioritaire': False,
            'api_access': False,
            'description': 'Plan professionnel avec IA avancée et OCR. Parfait pour les EBNL en croissance.',
            'actif': True
        },
        {
            'nom': 'Enterprise',
            'type_plan': TypePlan.ENTERPRISE,
            'prix_mensuel': 100,
            'prix_annuel': 1000,  # 2 mois gratuits
            'devise': 'EUR',
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
            'description': 'Plan enterprise avec toutes les fonctionnalités. Pour les grandes EBNL et fédérations.',
            'actif': True
        }
    ]
    
    for plan_data in plans_data:
        plan_existant = PlanAbonnement.query.filter_by(
            nom=plan_data['nom']
        ).first()
        
        if not plan_existant:
            plan = PlanAbonnement(**plan_data)
            db.session.add(plan)
            print(f"✅ Plan {plan_data['nom']} créé")
        else:
            print(f"ℹ️  Plan {plan_data['nom']} existe déjà")

def init_coupons():
    """Initialise quelques coupons de test"""
    
    coupons_data = [
        {
            'code': 'LAUNCH2024',
            'description': 'Réduction de lancement 50%',
            'type_reduction': 'pourcentage',
            'valeur_reduction': 50,
            'montant_minimum': 10,
            'utilisations_max': 100,
            'date_debut': datetime.utcnow(),
            'date_fin': datetime.utcnow() + timedelta(days=90),
            'actif': True
        },
        {
            'code': 'FIRST10',
            'description': '10€ de réduction pour les nouveaux clients',
            'type_reduction': 'montant_fixe',
            'valeur_reduction': 10,
            'montant_minimum': 20,
            'utilisations_max': 50,
            'date_debut': datetime.utcnow(),
            'date_fin': datetime.utcnow() + timedelta(days=60),
            'actif': True
        },
        {
            'code': 'EBNL2024',
            'description': 'Réduction spéciale EBNL 30%',
            'type_reduction': 'pourcentage',
            'valeur_reduction': 30,
            'montant_minimum': 25,
            'utilisations_max': None,  # Illimité
            'date_debut': datetime.utcnow(),
            'date_fin': datetime.utcnow() + timedelta(days=365),
            'actif': True
        }
    ]
    
    for coupon_data in coupons_data:
        coupon_existant = CouponReduction.query.filter_by(
            code=coupon_data['code']
        ).first()
        
        if not coupon_existant:
            coupon = CouponReduction(**coupon_data)
            db.session.add(coupon)
            print(f"🎟️  Coupon {coupon_data['code']} créé")
        else:
            print(f"ℹ️  Coupon {coupon_data['code']} existe déjà")

def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initialisation des données d'abonnement ComptaEBNL-IA")
    print("=" * 60)
    
    # Créer l'application Flask
    app = create_app()
    
    with app.app_context():
        try:
            # Créer les tables si elles n'existent pas
            db.create_all()
            
            # Initialiser les plans
            print("\n📋 Initialisation des plans d'abonnement...")
            init_plans()
            
            # Initialiser les coupons
            print("\n🎟️  Initialisation des coupons...")
            init_coupons()
            
            # Valider les changements
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ Initialisation terminée avec succès !")
            print("\n📊 Résumé:")
            
            # Afficher les statistiques
            nb_plans = PlanAbonnement.query.count()
            nb_coupons = CouponReduction.query.count()
            
            print(f"   • Plans d'abonnement: {nb_plans}")
            print(f"   • Coupons de réduction: {nb_coupons}")
            
            print("\n🌐 Plans disponibles:")
            plans = PlanAbonnement.query.all()
            for plan in plans:
                if plan.prix_annuel and plan.prix_annuel > 0:
                    economie = (plan.prix_mensuel * 12) - plan.prix_annuel
                    print(f"   • {plan.nom}: {plan.prix_mensuel}€/mois ou {plan.prix_annuel}€/an (économie: {economie}€)")
                else:
                    print(f"   • {plan.nom}: {plan.prix_mensuel}€/mois")
            
            print("\n🎟️  Coupons disponibles:")
            coupons = CouponReduction.query.filter_by(actif=True).all()
            for coupon in coupons:
                if coupon.type_reduction == 'pourcentage':
                    print(f"   • {coupon.code}: {coupon.valeur_reduction}% de réduction")
                else:
                    print(f"   • {coupon.code}: {coupon.valeur_reduction}€ de réduction")
            
            print("\n🚀 Vous pouvez maintenant:")
            print("   1. Démarrer l'application: python src/app.py")
            print("   2. Accéder aux plans: http://localhost:5000/api/v1/plans")
            print("   3. Tester les abonnements dans l'interface frontend")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")
            db.session.rollback()
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())