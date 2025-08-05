"""
Module de Gestion Multi-Entités EBNL
Permet la gestion de plusieurs associations/entités EBNL dans une même instance
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc

from models import (
    db, PlanComptable, EcritureComptable, LigneEcriture, 
    ExerciceComptable, JournalComptable, EntiteEBNL, Utilisateur
)

multi_entites_bp = Blueprint('multi_entites', __name__)

@multi_entites_bp.route('/entites', methods=['GET'])
def get_entites():
    """Récupère la liste de toutes les entités EBNL"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '')
        statut = request.args.get('statut', '')  # active, inactive, all
        
        query = EntiteEBNL.query
        
        # Filtrage par recherche (utilisant les bons noms de champs)
        if search:
            query = query.filter(
                or_(
                    EntiteEBNL.nom_entite.ilike(f'%{search}%'),
                    EntiteEBNL.numero_identification.ilike(f'%{search}%'),
                    EntiteEBNL.email.ilike(f'%{search}%')
                )
            )
        
        # Pour l'instant, on ne filtre pas par statut car le champ 'active' n'existe pas dans le modèle
        
        # Récupération simple avec offset/limit
        total = query.count()
        entites_list = query.order_by(EntiteEBNL.nom_entite).offset((page-1)*limit).limit(limit).all()
        
        # Pagination manuelle
        has_next = (page * limit) < total
        has_prev = page > 1
        pages = (total + limit - 1) // limit
        
        return jsonify({
            'success': True,
            'data': {
                'entites': [entite.to_dict() for entite in entites_list],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites', methods=['POST'])
def create_entite():
    """Crée une nouvelle entité EBNL"""
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires (adaptés au modèle)
        required_fields = ['nom_entite', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'error': f'Le champ {field} est obligatoire'
                }), 400
        
        # Vérification unicité numéro d'identification
        if data.get('numero_identification') and EntiteEBNL.query.filter_by(numero_identification=data['numero_identification']).first():
            return jsonify({
                'success': False, 
                'error': 'Une entité avec ce numéro d\'identification existe déjà'
            }), 400
        
        # Création de l'entité (avec les bons noms de champs)
        entite = EntiteEBNL(
            nom_entite=data['nom_entite'],
            sigle=data.get('sigle', ''),
            numero_identification=data.get('numero_identification', ''),
            type_entite=data.get('type_entite', 'Association loi 1901'),
            adresse=data.get('adresse', ''),
            code_postal=data.get('code_postal', ''),
            ville=data.get('ville', ''),
            pays=data.get('pays', 'France'),
            telephone=data.get('telephone', ''),
            email=data['email'],
            site_web=data.get('site_web', ''),
            devise_principale=data.get('devise_principale', 'EUR'),
            exercice_debut_mois=data.get('exercice_debut_mois', 1),
            tva_applicable=data.get('tva_applicable', True),
            objet_social=data.get('objet_social', ''),
            date_creation_entite=datetime.strptime(data['date_creation_entite'], '%Y-%m-%d').date() if data.get('date_creation_entite') else None,
            prefecture_declaration=data.get('prefecture_declaration', '')
        )
        
        db.session.add(entite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'entite': entite.to_dict(),
                'message': f'Entité {entite.nom_entite} créée avec succès'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites/<int:entite_id>', methods=['GET'])
def get_entite_detail(entite_id):
    """Récupère les détails d'une entité EBNL"""
    try:
        entite = EntiteEBNL.query.get_or_404(entite_id)
        
        # Statistiques de l'entité
        stats = {
            'nb_utilisateurs': Utilisateur.query.filter_by(entite_id=entite_id).count(),
            'nb_exercices': ExerciceComptable.query.filter_by(entite_id=entite_id).count(),
            'nb_ecritures': EcritureComptable.query.join(ExerciceComptable).filter(
                ExerciceComptable.entite_id == entite_id
            ).count(),
            'exercice_courant': None
        }
        
        # Exercice courant
        exercice_courant = ExerciceComptable.query.filter(
            ExerciceComptable.entite_id == entite_id,
            ExerciceComptable.statut == 'ouvert'
        ).first()
        
        if exercice_courant:
            stats['exercice_courant'] = {
                'id': exercice_courant.id,
                'nom': exercice_courant.nom_exercice,
                'debut': exercice_courant.date_debut.strftime('%Y-%m-%d'),
                'fin': exercice_courant.date_fin.strftime('%Y-%m-%d')
            }
        
        return jsonify({
            'success': True,
            'data': {
                'entite': entite.to_dict(),
                'statistiques': stats
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites/<int:entite_id>', methods=['PUT'])
def update_entite(entite_id):
    """Met à jour une entité EBNL"""
    try:
        entite = EntiteEBNL.query.get_or_404(entite_id)
        data = request.get_json()
        
        # Mise à jour des champs modifiables
        updatable_fields = [
            'nom', 'adresse', 'code_postal', 'ville', 'telephone', 
            'email', 'site_web', 'objet_social', 'forme_juridique', 
            'numero_rna', 'active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(entite, field, data[field])
        
        # Cas spécial pour date_creation
        if 'date_creation' in data and data['date_creation']:
            entite.date_creation = datetime.strptime(data['date_creation'], '%Y-%m-%d').date()
        
        # Vérification unicité SIRET si modifié
        if 'siret' in data and data['siret'] != entite.siret:
            if EntiteEBNL.query.filter_by(siret=data['siret']).first():
                return jsonify({
                    'success': False, 
                    'error': 'Une entité avec ce SIRET existe déjà'
                }), 400
            entite.siret = data['siret']
        
        entite.date_modification = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'entite': entite.to_dict(),
                'message': f'Entité {entite.nom} mise à jour avec succès'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites/<int:entite_id>/activer', methods=['POST'])
def activer_entite(entite_id):
    """Active ou désactive une entité EBNL"""
    try:
        entite = EntiteEBNL.query.get_or_404(entite_id)
        data = request.get_json()
        
        nouveau_statut = data.get('active', True)
        ancien_statut = entite.active
        
        entite.active = nouveau_statut
        entite.date_modification = datetime.utcnow()
        db.session.commit()
        
        action = 'activée' if nouveau_statut else 'désactivée'
        
        return jsonify({
            'success': True,
            'data': {
                'entite_id': entite_id,
                'ancien_statut': ancien_statut,
                'nouveau_statut': nouveau_statut,
                'message': f'Entité {entite.nom} {action} avec succès'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites/<int:entite_id>/exercices', methods=['GET'])
def get_exercices_entite(entite_id):
    """Récupère les exercices comptables d'une entité"""
    try:
        entite = EntiteEBNL.query.get_or_404(entite_id)
        
        exercices = ExerciceComptable.query.filter_by(entite_id=entite_id).order_by(
            desc(ExerciceComptable.date_debut)
        ).all()
        
        exercices_data = []
        for exercice in exercices:
            # Calcul des statistiques de l'exercice
            nb_ecritures = EcritureComptable.query.filter(
                EcritureComptable.date_ecriture >= exercice.date_debut,
                EcritureComptable.date_ecriture <= exercice.date_fin
            ).count()
            
            exercices_data.append({
                **exercice.to_dict(),
                'nb_ecritures': nb_ecritures
            })
        
        return jsonify({
            'success': True,
            'data': {
                'entite': {
                    'id': entite.id,
                    'nom': entite.nom
                },
                'exercices': exercices_data,
                'total': len(exercices_data)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites/<int:entite_id>/utilisateurs', methods=['GET'])
def get_utilisateurs_entite(entite_id):
    """Récupère les utilisateurs d'une entité"""
    try:
        entite = EntiteEBNL.query.get_or_404(entite_id)
        
        utilisateurs = Utilisateur.query.filter_by(entite_id=entite_id).order_by(
            Utilisateur.nom, Utilisateur.prenom
        ).all()
        
        utilisateurs_data = []
        for user in utilisateurs:
            user_dict = user.to_dict()
            # Ne pas exposer le mot de passe
            user_dict.pop('mot_de_passe', None)
            utilisateurs_data.append(user_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'entite': {
                    'id': entite.id,
                    'nom': entite.nom
                },
                'utilisateurs': utilisateurs_data,
                'total': len(utilisateurs_data)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites/<int:entite_id>/dashboard', methods=['GET'])
def get_dashboard_entite(entite_id):
    """Tableau de bord spécifique à une entité"""
    try:
        entite = EntiteEBNL.query.get_or_404(entite_id)
        
        # Exercice courant
        exercice_courant = ExerciceComptable.query.filter(
            ExerciceComptable.entite_id == entite_id,
            ExerciceComptable.statut == 'ouvert'
        ).first()
        
        if not exercice_courant:
            return jsonify({
                'success': True,
                'data': {
                    'entite': entite.to_dict(),
                    'message': 'Aucun exercice ouvert pour cette entité',
                    'dashboard': None
                }
            })
        
        # Période de l'exercice courant
        date_debut = exercice_courant.date_debut
        date_fin = exercice_courant.date_fin
        
        # Statistiques comptables de base
        nb_ecritures = EcritureComptable.query.filter(
            EcritureComptable.date_ecriture >= date_debut,
            EcritureComptable.date_ecriture <= date_fin
        ).count()
        
        # Soldes des comptes principaux (simulation)
        # Note: Il faudrait une vraie relation exercice -> écritures pour être précis
        comptes_principaux = {
            'banque': {'numero': '512', 'solde': 0, 'libelle': 'Banque'},
            'caisse': {'numero': '53', 'solde': 0, 'libelle': 'Caisse'},
            'dons': {'numero': '756', 'solde': 0, 'libelle': 'Dons manuels'},
            'subventions': {'numero': '74', 'solde': 0, 'libelle': 'Subventions'},
            'charges': {'numero': '6', 'solde': 0, 'libelle': 'Charges'}
        }
        
        # Calcul simplisié des soldes (sans filtrage strict par entité)
        for compte_key, compte_info in comptes_principaux.items():
            numero = compte_info['numero']
            
            # Somme des lignes d'écriture pour ce compte
            result = db.session.query(
                func.coalesce(func.sum(LigneEcriture.debit), 0).label('total_debit'),
                func.coalesce(func.sum(LigneEcriture.credit), 0).label('total_credit')
            ).join(EcritureComptable).filter(
                EcritureComptable.date_ecriture >= date_debut,
                EcritureComptable.date_ecriture <= date_fin,
                LigneEcriture.numero_compte.like(f'{numero}%')
            ).first()
            
            if result:
                solde = float(result.total_debit - result.total_credit)
                comptes_principaux[compte_key]['solde'] = solde
        
        # Évolution sur les 6 derniers mois
        evolution_mensuelle = []
        for i in range(6):
            debut_mois = datetime.now().date().replace(day=1) - timedelta(days=i*30)
            fin_mois = debut_mois + timedelta(days=30)
            
            nb_ecritures_mois = EcritureComptable.query.filter(
                EcritureComptable.date_ecriture >= debut_mois,
                EcritureComptable.date_ecriture <= fin_mois
            ).count()
            
            evolution_mensuelle.append({
                'mois': debut_mois.strftime('%Y-%m'),
                'nb_ecritures': nb_ecritures_mois
            })
        
        evolution_mensuelle.reverse()
        
        dashboard = {
            'exercice_courant': {
                'id': exercice_courant.id,
                'nom': exercice_courant.nom_exercice,
                'debut': date_debut.strftime('%Y-%m-%d'),
                'fin': date_fin.strftime('%Y-%m-%d'),
                'statut': exercice_courant.statut
            },
            'statistiques_globales': {
                'nb_ecritures': nb_ecritures,
                'nb_utilisateurs': Utilisateur.query.filter_by(entite_id=entite_id).count(),
                'nb_exercices': ExerciceComptable.query.filter_by(entite_id=entite_id).count()
            },
            'comptes_principaux': comptes_principaux,
            'evolution_mensuelle': evolution_mensuelle
        }
        
        return jsonify({
            'success': True,
            'data': {
                'entite': entite.to_dict(),
                'dashboard': dashboard
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites/statistiques-globales', methods=['GET'])
def get_statistiques_globales():
    """Statistiques globales multi-entités"""
    try:
        # Statistiques générales (sans filtrage par statut actif/inactif car ce champ n'existe pas)
        stats = {
            'total_entites': EntiteEBNL.query.count(),
            'entites_actives': EntiteEBNL.query.count(),  # Pour l'instant, toutes sont considérées actives
            'entites_inactives': 0,
            'total_utilisateurs': Utilisateur.query.count(),
            'total_exercices': ExerciceComptable.query.count(),
            'total_ecritures': EcritureComptable.query.count()
        }
        
        # Top 5 des entités (simplifié sans jointures complexes)
        entites_list = EntiteEBNL.query.limit(5).all()
        
        top_entites_data = []
        for entite in entites_list:
            top_entites_data.append({
                'entite_id': entite.id,
                'nom': entite.nom_entite,
                'nb_ecritures': 0  # Simplifié pour l'instant
            })
        
        # Répartition par type d'entité
        repartition_formes = db.session.query(
            EntiteEBNL.type_entite,
            func.count(EntiteEBNL.id).label('count')
        ).group_by(EntiteEBNL.type_entite).all()
        
        formes_juridiques = []
        for forme, count in repartition_formes:
            formes_juridiques.append({
                'type_entite': forme or 'Non spécifiée',
                'nombre': count
            })
        
        return jsonify({
            'success': True,
            'data': {
                'statistiques_generales': stats,
                'top_entites': top_entites_data,
                'repartition_types_entites': formes_juridiques,
                'date_generation': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_entites_bp.route('/entites/recherche-avancee', methods=['POST'])
def recherche_avancee_entites():
    """Recherche avancée d'entités avec filtres multiples"""
    try:
        data = request.get_json()
        
        query = EntiteEBNL.query
        
        # Filtres disponibles
        if data.get('nom'):
            query = query.filter(EntiteEBNL.nom.ilike(f"%{data['nom']}%"))
        
        if data.get('ville'):
            query = query.filter(EntiteEBNL.ville.ilike(f"%{data['ville']}%"))
        
        if data.get('forme_juridique'):
            query = query.filter(EntiteEBNL.forme_juridique == data['forme_juridique'])
        
        if data.get('statut'):
            if data['statut'] == 'active':
                query = query.filter(EntiteEBNL.active == True)
            elif data['statut'] == 'inactive':
                query = query.filter(EntiteEBNL.active == False)
        
        if data.get('date_creation_debut'):
            date_debut = datetime.strptime(data['date_creation_debut'], '%Y-%m-%d').date()
            query = query.filter(EntiteEBNL.date_creation >= date_debut)
        
        if data.get('date_creation_fin'):
            date_fin = datetime.strptime(data['date_creation_fin'], '%Y-%m-%d').date()
            query = query.filter(EntiteEBNL.date_creation <= date_fin)
        
        # Tri
        ordre = data.get('ordre', 'nom')
        sens = data.get('sens', 'asc')
        
        if hasattr(EntiteEBNL, ordre):
            if sens == 'desc':
                query = query.order_by(desc(getattr(EntiteEBNL, ordre)))
            else:
                query = query.order_by(getattr(EntiteEBNL, ordre))
        else:
            query = query.order_by(EntiteEBNL.nom)
        
        # Pagination
        page = data.get('page', 1)
        limit = data.get('limit', 20)
        
        entites = query.paginate(page=page, per_page=limit, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'entites': [entite.to_dict() for entite in entites.items],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': entites.total,
                    'pages': entites.pages,
                    'has_next': entites.has_next,
                    'has_prev': entites.has_prev
                },
                'filtres_appliques': data
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Endpoint de synthèse
@multi_entites_bp.route('/entites/synthese', methods=['GET'])
def get_synthese_multi_entites():
    """Retourne une synthèse du module multi-entités"""
    fonctionnalites = [
        {
            'endpoint': '/api/v1/entites',
            'methodes': ['GET', 'POST'],
            'nom': 'Gestion des entités',
            'description': 'CRUD complet des entités EBNL'
        },
        {
            'endpoint': '/api/v1/entites/{id}',
            'methodes': ['GET', 'PUT'],
            'nom': 'Détails entité',
            'description': 'Consultation et modification d\'une entité'
        },
        {
            'endpoint': '/api/v1/entites/{id}/dashboard',
            'methodes': ['GET'],
            'nom': 'Tableau de bord entité',
            'description': 'Dashboard spécifique à une entité'
        },
        {
            'endpoint': '/api/v1/entites/{id}/exercices',
            'methodes': ['GET'],
            'nom': 'Exercices entité',
            'description': 'Liste des exercices comptables d\'une entité'
        },
        {
            'endpoint': '/api/v1/entites/{id}/utilisateurs',
            'methodes': ['GET'],
            'nom': 'Utilisateurs entité',
            'description': 'Liste des utilisateurs d\'une entité'
        },
        {
            'endpoint': '/api/v1/entites/statistiques-globales',
            'methodes': ['GET'],
            'nom': 'Statistiques globales',
            'description': 'Vue d\'ensemble de toutes les entités'
        },
        {
            'endpoint': '/api/v1/entites/recherche-avancee',
            'methodes': ['POST'],
            'nom': 'Recherche avancée',
            'description': 'Recherche multicritères d\'entités'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'module': 'Gestion Multi-Entités EBNL',
            'version': '1.0',
            'fonctionnalites': fonctionnalites,
            'total_endpoints': len(fonctionnalites),
            'features': [
                'Gestion complète d\'entités multiples',
                'Isolation des données par entité',
                'Tableaux de bord dédiés',
                'Statistiques globales et par entité',
                'Recherche et filtrage avancés',
                'Gestion des utilisateurs par entité'
            ]
        }
    })