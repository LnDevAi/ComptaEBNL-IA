"""
API Gestion Avancée ComptaEBNL-IA
Gestion multi-projets, multi-bailleurs : dirigeants, budget, activités, patrimoine
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from datetime import datetime, date
import os
import pandas as pd
from werkzeug.utils import secure_filename
import json
from decimal import Decimal

# Import des modèles
from models_gestion import (
    db, Dirigeant, Bailleur, Projet, Budget, LigneBudget, Activite, 
    Bien, Balance, LigneBalance, Financement,
    TypeDirigeant, StatutDirigeant, TypeBailleur, StatutProjet,
    TypeActivite, TypeBien, StatutBudget
)

# Middleware d'authentification (à adapter selon votre système)
from middleware.subscription_middleware import subscription_required

gestion_bp = Blueprint('gestion', __name__)

# Configuration upload
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xlsx', 'xls', 'csv', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user_id():
    """Récupère l'ID de l'utilisateur connecté"""
    # À adapter selon votre système d'authentification
    return 1  # Placeholder

def get_user_association_id():
    """Récupère l'ID de l'association de l'utilisateur"""
    # À adapter selon votre logique métier
    return 1  # Placeholder

# ============================
# ENDPOINTS DIRIGEANTS
# ============================

@gestion_bp.route('/dirigeants', methods=['GET'])
@subscription_required
def get_dirigeants():
    """Récupère la liste des dirigeants"""
    try:
        association_id = get_user_association_id()
        dirigeants = Dirigeant.query.filter_by(association_id=association_id).all()
        
        return jsonify({
            'success': True,
            'dirigeants': [d.to_dict() for d in dirigeants]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des dirigeants: {str(e)}'
        }), 500

@gestion_bp.route('/dirigeants', methods=['POST'])
@subscription_required
def create_dirigeant():
    """Crée un nouveau dirigeant"""
    try:
        data = request.get_json()
        association_id = get_user_association_id()
        
        dirigeant = Dirigeant(
            association_id=association_id,
            nom=data['nom'],
            prenoms=data['prenoms'],
            type_dirigeant=TypeDirigeant(data['type_dirigeant']),
            date_nomination=datetime.strptime(data['date_nomination'], '%Y-%m-%d').date(),
            telephone=data.get('telephone'),
            email=data.get('email'),
            adresse=data.get('adresse'),
            profession=data.get('profession'),
            nationalite=data.get('nationalite'),
            pouvoir_signature=data.get('pouvoir_signature', False),
            pouvoir_engagement=data.get('pouvoir_engagement', False),
            seuil_engagement=data.get('seuil_engagement', 0),
            cree_par=get_current_user_id()
        )
        
        if data.get('date_naissance'):
            dirigeant.date_naissance = datetime.strptime(data['date_naissance'], '%Y-%m-%d').date()
        
        if data.get('date_fin_mandat'):
            dirigeant.date_fin_mandat = datetime.strptime(data['date_fin_mandat'], '%Y-%m-%d').date()
        
        db.session.add(dirigeant)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Dirigeant créé avec succès',
            'dirigeant': dirigeant.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création du dirigeant: {str(e)}'
        }), 500

@gestion_bp.route('/dirigeants/<int:dirigeant_id>', methods=['PUT'])
@subscription_required
def update_dirigeant(dirigeant_id):
    """Met à jour un dirigeant"""
    try:
        association_id = get_user_association_id()
        dirigeant = Dirigeant.query.filter_by(id=dirigeant_id, association_id=association_id).first()
        
        if not dirigeant:
            return jsonify({
                'success': False,
                'message': 'Dirigeant non trouvé'
            }), 404
        
        data = request.get_json()
        
        # Mise à jour des champs
        for field in ['nom', 'prenoms', 'telephone', 'email', 'adresse', 'profession', 'nationalite']:
            if field in data:
                setattr(dirigeant, field, data[field])
        
        if 'type_dirigeant' in data:
            dirigeant.type_dirigeant = TypeDirigeant(data['type_dirigeant'])
        
        if 'statut' in data:
            dirigeant.statut = StatutDirigeant(data['statut'])
        
        if 'pouvoir_signature' in data:
            dirigeant.pouvoir_signature = data['pouvoir_signature']
        
        if 'pouvoir_engagement' in data:
            dirigeant.pouvoir_engagement = data['pouvoir_engagement']
        
        if 'seuil_engagement' in data:
            dirigeant.seuil_engagement = data['seuil_engagement']
        
        dirigeant.date_modification = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Dirigeant mis à jour avec succès',
            'dirigeant': dirigeant.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la mise à jour: {str(e)}'
        }), 500

# ============================
# ENDPOINTS BAILLEURS
# ============================

@gestion_bp.route('/bailleurs', methods=['GET'])
@subscription_required
def get_bailleurs():
    """Récupère la liste des bailleurs"""
    try:
        bailleurs = Bailleur.query.filter_by(actif=True).all()
        
        return jsonify({
            'success': True,
            'bailleurs': [b.to_dict() for b in bailleurs]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des bailleurs: {str(e)}'
        }), 500

@gestion_bp.route('/bailleurs', methods=['POST'])
@subscription_required
def create_bailleur():
    """Crée un nouveau bailleur"""
    try:
        data = request.get_json()
        
        bailleur = Bailleur(
            nom=data['nom'],
            sigle=data.get('sigle'),
            type_bailleur=TypeBailleur(data['type_bailleur']),
            pays_origine=data.get('pays_origine'),
            adresse=data.get('adresse'),
            telephone=data.get('telephone'),
            email=data.get('email'),
            site_web=data.get('site_web'),
            contact_nom=data.get('contact_nom'),
            contact_fonction=data.get('contact_fonction'),
            contact_telephone=data.get('contact_telephone'),
            contact_email=data.get('contact_email')
        )
        
        db.session.add(bailleur)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bailleur créé avec succès',
            'bailleur': bailleur.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création du bailleur: {str(e)}'
        }), 500

# ============================
# ENDPOINTS PROJETS
# ============================

@gestion_bp.route('/projets', methods=['GET'])
@subscription_required
def get_projets():
    """Récupère la liste des projets"""
    try:
        association_id = get_user_association_id()
        projets = Projet.query.filter_by(association_id=association_id).all()
        
        return jsonify({
            'success': True,
            'projets': [p.to_dict() for p in projets]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des projets: {str(e)}'
        }), 500

@gestion_bp.route('/projets', methods=['POST'])
@subscription_required
def create_projet():
    """Crée un nouveau projet"""
    try:
        data = request.get_json()
        association_id = get_user_association_id()
        
        projet = Projet(
            association_id=association_id,
            code_projet=data['code_projet'],
            titre=data['titre'],
            description=data.get('description'),
            date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
            date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date(),
            budget_total=Decimal(str(data['budget_total'])),
            bailleur_id=data.get('bailleur_id'),
            contribution_bailleur=Decimal(str(data.get('contribution_bailleur', 0))),
            contribution_association=Decimal(str(data.get('contribution_association', 0))),
            chef_projet=data.get('chef_projet'),
            coordinateur=data.get('coordinateur'),
            pays=data.get('pays'),
            cree_par=get_current_user_id()
        )
        
        # Calculer la durée en mois
        if projet.date_debut and projet.date_fin:
            delta = projet.date_fin - projet.date_debut
            projet.duree_mois = round(delta.days / 30)
        
        db.session.add(projet)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Projet créé avec succès',
            'projet': projet.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création du projet: {str(e)}'
        }), 500

@gestion_bp.route('/projets/<int:projet_id>/statut', methods=['PUT'])
@subscription_required
def update_projet_statut(projet_id):
    """Met à jour le statut d'un projet"""
    try:
        association_id = get_user_association_id()
        projet = Projet.query.filter_by(id=projet_id, association_id=association_id).first()
        
        if not projet:
            return jsonify({
                'success': False,
                'message': 'Projet non trouvé'
            }), 404
        
        data = request.get_json()
        projet.statut = StatutProjet(data['statut'])
        
        if 'taux_execution_physique' in data:
            projet.taux_execution_physique = Decimal(str(data['taux_execution_physique']))
        
        if 'taux_execution_financiere' in data:
            projet.taux_execution_financiere = Decimal(str(data['taux_execution_financiere']))
        
        projet.date_modification = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Statut du projet mis à jour',
            'projet': projet.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la mise à jour: {str(e)}'
        }), 500

# ============================
# ENDPOINTS BUDGET
# ============================

@gestion_bp.route('/budgets', methods=['GET'])
@subscription_required
def get_budgets():
    """Récupère la liste des budgets"""
    try:
        association_id = get_user_association_id()
        budgets = Budget.query.filter_by(association_id=association_id).all()
        
        return jsonify({
            'success': True,
            'budgets': [b.to_dict() for b in budgets]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des budgets: {str(e)}'
        }), 500

@gestion_bp.route('/budgets', methods=['POST'])
@subscription_required
def create_budget():
    """Crée un nouveau budget"""
    try:
        data = request.get_json()
        association_id = get_user_association_id()
        
        budget = Budget(
            association_id=association_id,
            projet_id=data.get('projet_id'),
            libelle=data['libelle'],
            exercice=data['exercice'],
            date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
            date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date(),
            commentaires=data.get('commentaires'),
            cree_par=get_current_user_id()
        )
        
        db.session.add(budget)
        db.session.flush()  # Pour récupérer l'ID
        
        # Ajouter les lignes de budget
        if 'lignes' in data:
            for ligne_data in data['lignes']:
                ligne = LigneBudget(
                    budget_id=budget.id,
                    compte_comptable=ligne_data.get('compte_comptable'),
                    categorie=ligne_data['categorie'],
                    sous_categorie=ligne_data.get('sous_categorie'),
                    libelle=ligne_data['libelle'],
                    description=ligne_data.get('description'),
                    montant_prevu=Decimal(str(ligne_data['montant_prevu'])),
                    ordre_affichage=ligne_data.get('ordre_affichage', 0)
                )
                db.session.add(ligne)
        
        # Calculer les totaux
        budget.total_recettes_prevues = sum(
            ligne.montant_prevu for ligne in budget.lignes_budget 
            if ligne.categorie.lower() == 'recettes'
        )
        budget.total_depenses_prevues = sum(
            ligne.montant_prevu for ligne in budget.lignes_budget 
            if ligne.categorie.lower() == 'depenses'
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Budget créé avec succès',
            'budget': budget.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création du budget: {str(e)}'
        }), 500

@gestion_bp.route('/budgets/<int:budget_id>/lignes', methods=['GET'])
@subscription_required
def get_lignes_budget(budget_id):
    """Récupère les lignes d'un budget"""
    try:
        association_id = get_user_association_id()
        budget = Budget.query.filter_by(id=budget_id, association_id=association_id).first()
        
        if not budget:
            return jsonify({
                'success': False,
                'message': 'Budget non trouvé'
            }), 404
        
        lignes = LigneBudget.query.filter_by(budget_id=budget_id).order_by(LigneBudget.ordre_affichage).all()
        
        return jsonify({
            'success': True,
            'lignes': [l.to_dict() for l in lignes]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des lignes: {str(e)}'
        }), 500

@gestion_bp.route('/budgets/<int:budget_id>/valider', methods=['PUT'])
@subscription_required
def valider_budget(budget_id):
    """Valide un budget"""
    try:
        association_id = get_user_association_id()
        budget = Budget.query.filter_by(id=budget_id, association_id=association_id).first()
        
        if not budget:
            return jsonify({
                'success': False,
                'message': 'Budget non trouvé'
            }), 404
        
        budget.statut = StatutBudget.VALIDE
        budget.date_validation = datetime.utcnow()
        budget.valide_par = get_current_user_id()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Budget validé avec succès',
            'budget': budget.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la validation: {str(e)}'
        }), 500

# ============================
# ENDPOINTS ACTIVITÉS
# ============================

@gestion_bp.route('/activites', methods=['GET'])
@subscription_required
def get_activites():
    """Récupère la liste des activités"""
    try:
        association_id = get_user_association_id()
        projet_id = request.args.get('projet_id')
        
        query = Activite.query.filter_by(association_id=association_id)
        if projet_id:
            query = query.filter_by(projet_id=projet_id)
        
        activites = query.all()
        
        return jsonify({
            'success': True,
            'activites': [a.to_dict() for a in activites]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des activités: {str(e)}'
        }), 500

@gestion_bp.route('/activites', methods=['POST'])
@subscription_required
def create_activite():
    """Crée une nouvelle activité"""
    try:
        data = request.get_json()
        association_id = get_user_association_id()
        
        activite = Activite(
            association_id=association_id,
            projet_id=data.get('projet_id'),
            code_activite=data.get('code_activite'),
            titre=data['titre'],
            description=data.get('description'),
            type_activite=TypeActivite(data['type_activite']),
            lieu=data.get('lieu'),
            region=data.get('region'),
            nombre_participants_prevu=data.get('nombre_participants_prevu', 0),
            budget_alloue=Decimal(str(data.get('budget_alloue', 0))),
            responsable_activite=data.get('responsable_activite'),
            cree_par=get_current_user_id()
        )
        
        if data.get('date_debut_prevue'):
            activite.date_debut_prevue = datetime.strptime(data['date_debut_prevue'], '%Y-%m-%d').date()
        
        if data.get('date_fin_prevue'):
            activite.date_fin_prevue = datetime.strptime(data['date_fin_prevue'], '%Y-%m-%d').date()
        
        db.session.add(activite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Activité créée avec succès',
            'activite': activite.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création de l\'activité: {str(e)}'
        }), 500

# ============================
# ENDPOINTS PATRIMOINE
# ============================

@gestion_bp.route('/biens', methods=['GET'])
@subscription_required
def get_biens():
    """Récupère la liste des biens"""
    try:
        association_id = get_user_association_id()
        biens = Bien.query.filter_by(association_id=association_id).all()
        
        return jsonify({
            'success': True,
            'biens': [b.to_dict() for b in biens]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des biens: {str(e)}'
        }), 500

@gestion_bp.route('/biens', methods=['POST'])
@subscription_required
def create_bien():
    """Crée un nouveau bien"""
    try:
        data = request.get_json()
        association_id = get_user_association_id()
        
        # Générer un numéro d'inventaire unique
        numero_inventaire = data.get('numero_inventaire')
        if not numero_inventaire:
            # Auto-générer : BN-YYYY-XXXX
            year = datetime.now().year
            count = Bien.query.filter_by(association_id=association_id).count() + 1
            numero_inventaire = f"BN-{year}-{count:04d}"
        
        bien = Bien(
            association_id=association_id,
            projet_id=data.get('projet_id'),
            numero_inventaire=numero_inventaire,
            libelle=data['libelle'],
            description=data.get('description'),
            type_bien=TypeBien(data['type_bien']),
            marque=data.get('marque'),
            modele=data.get('modele'),
            numero_serie=data.get('numero_serie'),
            valeur_acquisition=Decimal(str(data.get('valeur_acquisition', 0))),
            valeur_actuelle=Decimal(str(data.get('valeur_actuelle', 0))),
            localisation=data.get('localisation'),
            responsable_bien=data.get('responsable_bien'),
            duree_amortissement_annees=data.get('duree_amortissement_annees'),
            cree_par=get_current_user_id()
        )
        
        if data.get('date_acquisition'):
            bien.date_acquisition = datetime.strptime(data['date_acquisition'], '%Y-%m-%d').date()
        
        if data.get('date_mise_service'):
            bien.date_mise_service = datetime.strptime(data['date_mise_service'], '%Y-%m-%d').date()
        
        db.session.add(bien)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bien créé avec succès',
            'bien': bien.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création du bien: {str(e)}'
        }), 500

# ============================
# ENDPOINTS BALANCE
# ============================

@gestion_bp.route('/balances', methods=['GET'])
@subscription_required
def get_balances():
    """Récupère la liste des balances"""
    try:
        association_id = get_user_association_id()
        balances = Balance.query.filter_by(association_id=association_id).all()
        
        return jsonify({
            'success': True,
            'balances': [b.to_dict() for b in balances]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des balances: {str(e)}'
        }), 500

@gestion_bp.route('/balances/upload', methods=['POST'])
@subscription_required
def upload_balance():
    """Upload et traitement d'une balance Excel/CSV"""
    try:
        if 'fichier' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['fichier']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Nom de fichier vide'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Type de fichier non autorisé'
            }), 400
        
        # Récupérer les paramètres
        exercice = int(request.form.get('exercice'))
        date_cloture = datetime.strptime(request.form.get('date_cloture'), '%Y-%m-%d').date()
        type_balance = request.form.get('type_balance', 'balance_n1')
        
        # Sauvegarder le fichier
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_app.instance_path, 'uploads', 'balances')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Créer l'enregistrement Balance
        association_id = get_user_association_id()
        balance = Balance(
            association_id=association_id,
            exercice=exercice,
            date_cloture=date_cloture,
            type_balance=type_balance,
            fichier_balance=f"uploads/balances/{filename}",
            importe_par=get_current_user_id()
        )
        
        db.session.add(balance)
        db.session.flush()
        
        # Traiter le fichier Excel/CSV
        try:
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:  # CSV
                df = pd.read_csv(file_path)
            
            # Colonnes attendues (à adapter selon le format)
            colonnes_requises = ['numero_compte', 'libelle_compte', 'solde_debiteur', 'solde_crediteur']
            
            # Vérifier les colonnes
            if not all(col in df.columns for col in colonnes_requises):
                return jsonify({
                    'success': False,
                    'message': f'Colonnes requises manquantes: {colonnes_requises}'
                }), 400
            
            # Traiter chaque ligne
            for index, row in df.iterrows():
                ligne = LigneBalance(
                    balance_id=balance.id,
                    numero_compte=str(row['numero_compte']).strip(),
                    libelle_compte=str(row['libelle_compte']).strip(),
                    solde_debiteur=Decimal(str(row.get('solde_debiteur', 0) or 0)),
                    solde_crediteur=Decimal(str(row.get('solde_crediteur', 0) or 0)),
                    mouvement_debit=Decimal(str(row.get('mouvement_debit', 0) or 0)),
                    mouvement_credit=Decimal(str(row.get('mouvement_credit', 0) or 0)),
                    ligne_fichier=index + 2  # +2 car index commence à 0 et ligne d'en-tête
                )
                db.session.add(ligne)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Balance importée avec succès ({len(df)} lignes)',
                'balance': balance.to_dict()
            })
            
        except Exception as e:
            # Supprimer le fichier en cas d'erreur de traitement
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'import: {str(e)}'
        }), 500

@gestion_bp.route('/balances/<int:balance_id>/lignes', methods=['GET'])
@subscription_required
def get_lignes_balance(balance_id):
    """Récupère les lignes d'une balance"""
    try:
        association_id = get_user_association_id()
        balance = Balance.query.filter_by(id=balance_id, association_id=association_id).first()
        
        if not balance:
            return jsonify({
                'success': False,
                'message': 'Balance non trouvée'
            }), 404
        
        lignes = LigneBalance.query.filter_by(balance_id=balance_id).all()
        
        return jsonify({
            'success': True,
            'lignes': [l.to_dict() for l in lignes],
            'balance': balance.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des lignes: {str(e)}'
        }), 500

@gestion_bp.route('/balances/<int:balance_id>/valider', methods=['PUT'])
@subscription_required
def valider_balance(balance_id):
    """Valide une balance pour intégration"""
    try:
        association_id = get_user_association_id()
        balance = Balance.query.filter_by(id=balance_id, association_id=association_id).first()
        
        if not balance:
            return jsonify({
                'success': False,
                'message': 'Balance non trouvée'
            }), 404
        
        balance.statut = 'valide'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Balance validée avec succès',
            'balance': balance.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la validation: {str(e)}'
        }), 500

# ============================
# ENDPOINTS FINANCEMENTS
# ============================

@gestion_bp.route('/financements', methods=['GET'])
@subscription_required
def get_financements():
    """Récupère la liste des financements"""
    try:
        association_id = get_user_association_id()
        financements = Financement.query.filter_by(association_id=association_id).all()
        
        return jsonify({
            'success': True,
            'financements': [f.to_dict() for f in financements]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des financements: {str(e)}'
        }), 500

@gestion_bp.route('/financements', methods=['POST'])
@subscription_required
def create_financement():
    """Crée un nouveau financement"""
    try:
        data = request.get_json()
        association_id = get_user_association_id()
        
        financement = Financement(
            association_id=association_id,
            projet_id=data.get('projet_id'),
            bailleur_id=data['bailleur_id'],
            numero_convention=data.get('numero_convention'),
            libelle=data['libelle'],
            montant_accorde=Decimal(str(data['montant_accorde'])),
            date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
            date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date(),
            conditions_decaissement=data.get('conditions_decaissement'),
            modalites_reporting=data.get('modalites_reporting'),
            cree_par=get_current_user_id()
        )
        
        if data.get('date_signature'):
            financement.date_signature = datetime.strptime(data['date_signature'], '%Y-%m-%d').date()
        
        db.session.add(financement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Financement créé avec succès',
            'financement': financement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création du financement: {str(e)}'
        }), 500

# ============================
# ENDPOINTS STATISTIQUES
# ============================

@gestion_bp.route('/dashboard/statistiques', methods=['GET'])
@subscription_required
def get_dashboard_stats():
    """Récupère les statistiques du tableau de bord"""
    try:
        association_id = get_user_association_id()
        
        # Compter les éléments
        nb_dirigeants = Dirigeant.query.filter_by(association_id=association_id, statut=StatutDirigeant.ACTIF).count()
        nb_projets = Projet.query.filter_by(association_id=association_id).count()
        nb_projets_actifs = Projet.query.filter_by(association_id=association_id, statut=StatutProjet.EN_COURS).count()
        nb_activites = Activite.query.filter_by(association_id=association_id).count()
        nb_biens = Bien.query.filter_by(association_id=association_id).count()
        
        # Budgets
        budgets = Budget.query.filter_by(association_id=association_id).all()
        total_budget_prevu = sum(b.total_recettes_prevues or 0 for b in budgets)
        total_budget_realise = sum(b.total_recettes_realisees or 0 for b in budgets)
        
        # Financements
        financements = Financement.query.filter_by(association_id=association_id).all()
        total_financements = sum(f.montant_accorde or 0 for f in financements)
        total_decaisse = sum(f.montant_decaisse or 0 for f in financements)
        
        # Patrimoine
        biens = Bien.query.filter_by(association_id=association_id).all()
        valeur_patrimoine = sum(b.valeur_actuelle or b.valeur_acquisition or 0 for b in biens)
        
        return jsonify({
            'success': True,
            'statistiques': {
                'dirigeants': {
                    'total': nb_dirigeants,
                    'actifs': nb_dirigeants
                },
                'projets': {
                    'total': nb_projets,
                    'actifs': nb_projets_actifs,
                    'taux_activite': round((nb_projets_actifs / nb_projets * 100) if nb_projets > 0 else 0, 1)
                },
                'activites': {
                    'total': nb_activites
                },
                'budget': {
                    'prevu': float(total_budget_prevu),
                    'realise': float(total_budget_realise),
                    'taux_execution': round((total_budget_realise / total_budget_prevu * 100) if total_budget_prevu > 0 else 0, 1)
                },
                'financements': {
                    'total_accorde': float(total_financements),
                    'total_decaisse': float(total_decaisse),
                    'taux_decaissement': round((total_decaisse / total_financements * 100) if total_financements > 0 else 0, 1)
                },
                'patrimoine': {
                    'valeur_totale': float(valeur_patrimoine),
                    'nombre_biens': nb_biens
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des statistiques: {str(e)}'
        }), 500

# ============================
# GESTION DES ERREURS
# ============================

@gestion_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Ressource non trouvée'
    }), 404

@gestion_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'message': 'Erreur interne du serveur'
    }), 500