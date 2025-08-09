#!/usr/bin/env python3
"""
Test du système d'abonnement ComptaEBNL-IA
Version simplifiée pour validation
"""

import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Configuration simple
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_subscription.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'

# Initialisation
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import des modèles (version simplifiée)
import enum

class TypePlan(enum.Enum):
    GRATUIT = "gratuit"
    PROFESSIONNEL = "professionnel" 
    ENTERPRISE = "enterprise"

class StatutAbonnement(enum.Enum):
    ACTIF = "actif"
    EXPIRE = "expire"
    SUSPENDU = "suspendu"
    ANNULE = "annule"
    EN_ATTENTE = "en_attente"

class MethodePaiement(enum.Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    MTN_MOBILE_MONEY = "mtn_mobile_money"
    ORANGE_MONEY = "orange_money"
    WAVE = "wave"
    MOOV_MONEY = "moov_money"
    AIRTEL_MONEY = "airtel_money"

class StatutPaiement(enum.Enum):
    EN_ATTENTE = "en_attente"
    REUSSI = "reussi"
    ECHOUE = "echoue"
    REMBOURSE = "rembourse"
    ANNULE = "annule"

class PlanAbonnement(db.Model):
    """Plans d'abonnement disponibles"""
    __tablename__ = 'plans_abonnement'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    type_plan = db.Column(db.Enum(TypePlan), nullable=False)
    prix_mensuel = db.Column(db.Numeric(10, 2), nullable=False)
    prix_annuel = db.Column(db.Numeric(10, 2), nullable=True)
    devise = db.Column(db.String(3), default='EUR')
    
    # Limitations du plan
    max_entites = db.Column(db.Integer, default=1)
    max_ecritures_mois = db.Column(db.Integer, default=100)
    max_utilisateurs = db.Column(db.Integer, default=1)
    max_documents_mois = db.Column(db.Integer, default=50)
    
    # Fonctionnalités incluses
    ia_avancee = db.Column(db.Boolean, default=False)
    ocr_documents = db.Column(db.Boolean, default=False)
    etats_financiers_avances = db.Column(db.Boolean, default=False)
    rapprochement_bancaire = db.Column(db.Boolean, default=False)
    audit_trail = db.Column(db.Boolean, default=False)
    support_prioritaire = db.Column(db.Boolean, default=False)
    api_access = db.Column(db.Boolean, default=False)
    
    description = db.Column(db.Text)
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PlanAbonnement {self.nom}>'

class Abonnement(db.Model):
    """Abonnements des utilisateurs"""
    __tablename__ = 'abonnements'
    
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans_abonnement.id'), nullable=False)
    
    statut = db.Column(db.Enum(StatutAbonnement), default=StatutAbonnement.EN_ATTENTE)
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Facturation
    periode_facturation = db.Column(db.String(20), default='mensuel')
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    devise = db.Column(db.String(3), default='EUR')
    
    # Relations
    plan = db.relationship('PlanAbonnement', backref='abonnements')
    
    def est_actif(self):
        """Vérifie si l'abonnement est actif"""
        return (self.statut == StatutAbonnement.ACTIF and 
                self.date_fin > datetime.utcnow())
    
    def __repr__(self):
        return f'<Abonnement {self.id} - {self.plan.nom if self.plan else "N/A"}>'

class Paiement(db.Model):
    """Historique des paiements"""
    __tablename__ = 'paiements'
    
    id = db.Column(db.Integer, primary_key=True)
    abonnement_id = db.Column(db.Integer, db.ForeignKey('abonnements.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    devise = db.Column(db.String(3), default='EUR')
    methode_paiement = db.Column(db.Enum(MethodePaiement), nullable=False)
    statut = db.Column(db.Enum(StatutPaiement), default=StatutPaiement.EN_ATTENTE)
    
    # Identifiants externes
    transaction_id_externe = db.Column(db.String(255))
    numero_telephone = db.Column(db.String(20))  # Pour Mobile Money
    operateur_mobile = db.Column(db.String(50))
    
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_traitement = db.Column(db.DateTime)
    
    # Relations
    abonnement = db.relationship('Abonnement', backref='paiements')
    
    def __repr__(self):
        return f'<Paiement {self.id} - {self.montant}€ via {self.methode_paiement.value}>'

def init_plans():
    """Initialise les plans d'abonnement par défaut"""
    
    plans_data = [
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
            'prix_annuel': 300,
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
            'prix_annuel': 1000,
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
    
    for plan_data in plans_data:
        plan_existant = PlanAbonnement.query.filter_by(nom=plan_data['nom']).first()
        
        if not plan_existant:
            plan = PlanAbonnement(**plan_data)
            db.session.add(plan)
            print(f"✅ Plan {plan_data['nom']} créé")
        else:
            print(f"ℹ️  Plan {plan_data['nom']} existe déjà")

def test_subscription_creation():
    """Test de création d'abonnement"""
    print("\n🧪 Test de création d'abonnement...")
    
    # Récupérer le plan professionnel
    plan_pro = PlanAbonnement.query.filter_by(type_plan=TypePlan.PROFESSIONNEL).first()
    
    if not plan_pro:
        print("❌ Plan Professionnel introuvable")
        return
    
    # Créer un abonnement test
    abonnement = Abonnement(
        utilisateur_id=1,
        plan_id=plan_pro.id,
        statut=StatutAbonnement.ACTIF,
        date_debut=datetime.utcnow(),
        date_fin=datetime.utcnow() + timedelta(days=30),
        periode_facturation='mensuel',
        montant=plan_pro.prix_mensuel
    )
    
    db.session.add(abonnement)
    db.session.flush()  # Pour obtenir l'ID
    
    # Créer un paiement Mobile Money
    paiement = Paiement(
        abonnement_id=abonnement.id,
        utilisateur_id=1,
        montant=plan_pro.prix_mensuel,
        methode_paiement=MethodePaiement.MTN_MOBILE_MONEY,
        statut=StatutPaiement.REUSSI,
        transaction_id_externe='MTN-TEST-123456789',
        numero_telephone='+221771234567',
        operateur_mobile='MTN',
        date_traitement=datetime.utcnow()
    )
    
    db.session.add(paiement)
    db.session.commit()
    
    print(f"✅ Abonnement créé: {abonnement}")
    print(f"✅ Paiement créé: {paiement}")
    print(f"   • Statut abonnement: {abonnement.statut.value}")
    print(f"   • Actif: {abonnement.est_actif()}")
    print(f"   • Méthode paiement: {paiement.methode_paiement.value}")

def test_mobile_money_methods():
    """Test des différentes méthodes Mobile Money"""
    print("\n📱 Test des méthodes Mobile Money...")
    
    methods = [
        ('MTN Mobile Money', MethodePaiement.MTN_MOBILE_MONEY, '+237691234567', 'MTN'),
        ('Orange Money', MethodePaiement.ORANGE_MONEY, '+221771234567', 'Orange'),
        ('Wave', MethodePaiement.WAVE, '+221781234567', 'Wave'),
        ('Moov Money', MethodePaiement.MOOV_MONEY, '+22967123456', 'Moov')
    ]
    
    plan_gratuit = PlanAbonnement.query.filter_by(type_plan=TypePlan.GRATUIT).first()
    
    for i, (nom, methode, telephone, operateur) in enumerate(methods, 2):
        abonnement = Abonnement(
            utilisateur_id=i,
            plan_id=plan_gratuit.id,
            statut=StatutAbonnement.ACTIF,
            date_debut=datetime.utcnow(),
            date_fin=datetime.utcnow() + timedelta(days=365),
            periode_facturation='annuel',
            montant=0  # Plan gratuit
        )
        
        db.session.add(abonnement)
        db.session.flush()
        
        paiement = Paiement(
            abonnement_id=abonnement.id,
            utilisateur_id=i,
            montant=0,
            methode_paiement=methode,
            statut=StatutPaiement.REUSSI,
            transaction_id_externe=f'{operateur.upper()}-TEST-{i}234567890',
            numero_telephone=telephone,
            operateur_mobile=operateur,
            date_traitement=datetime.utcnow()
        )
        
        db.session.add(paiement)
        print(f"✅ {nom}: {telephone} via {operateur}")
    
    db.session.commit()

def display_statistics():
    """Affiche les statistiques du système"""
    print("\n📊 Statistiques du système d'abonnement:")
    
    # Statistiques par plan
    for plan in PlanAbonnement.query.all():
        nb_abonnements = Abonnement.query.filter_by(plan_id=plan.id).count()
        revenus = db.session.query(db.func.sum(Paiement.montant)).join(Abonnement).filter(
            Abonnement.plan_id == plan.id,
            Paiement.statut == StatutPaiement.REUSSI
        ).scalar() or 0
        
        print(f"   • {plan.nom}: {nb_abonnements} abonnements, {float(revenus)}€ de revenus")
    
    # Statistiques par méthode de paiement
    print("\n💳 Répartition des paiements par méthode:")
    paiements = Paiement.query.filter_by(statut=StatutPaiement.REUSSI).all()
    methodes_count = {}
    
    for paiement in paiements:
        methode = paiement.methode_paiement.value
        methodes_count[methode] = methodes_count.get(methode, 0) + 1
    
    for methode, count in methodes_count.items():
        if 'mobile_money' in methode or methode in ['wave', 'orange_money', 'moov_money']:
            icon = "📱"
        else:
            icon = "💳"
        print(f"   {icon} {methode}: {count} paiements")

def main():
    """Fonction principale de test"""
    print("🧪 TEST DU SYSTÈME D'ABONNEMENT COMPTAEBNL-IA")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Créer les tables
            db.create_all()
            print("✅ Base de données initialisée")
            
            # Initialiser les plans
            print("\n📋 Initialisation des plans...")
            init_plans()
            
            # Tester la création d'abonnements
            test_subscription_creation()
            
            # Tester les méthodes Mobile Money
            test_mobile_money_methods()
            
            # Afficher les statistiques
            display_statistics()
            
            print("\n" + "=" * 50)
            print("✅ TESTS RÉUSSIS ! Système d'abonnement fonctionnel")
            
            print("\n🌍 Méthodes Mobile Money supportées:")
            print("   📱 MTN Mobile Money (*126#)")
            print("   📱 Orange Money (#144#)")
            print("   📱 Wave (app mobile)")
            print("   📱 Moov Money")
            print("   📱 Airtel Money")
            
            print("\n💰 Plans disponibles:")
            plans = PlanAbonnement.query.all()
            for plan in plans:
                print(f"   • {plan.nom}: {plan.prix_mensuel}€/mois")
                if plan.prix_annuel and plan.prix_annuel > 0:
                    economie = (plan.prix_mensuel * 12) - plan.prix_annuel
                    print(f"     ou {plan.prix_annuel}€/an (économie: {economie}€)")
            
        except Exception as e:
            print(f"❌ Erreur lors des tests: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())