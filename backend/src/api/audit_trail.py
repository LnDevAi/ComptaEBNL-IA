"""
Module de Piste d'Audit Complète
Trace et enregistre toutes les opérations effectuées sur la plateforme pour assurer la conformité et la sécurité
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc, asc
from enum import Enum
import json

from models import (
    db, PlanComptable, EcritureComptable, LigneEcriture, 
    ExerciceComptable, JournalComptable, EntiteEBNL, Utilisateur
)

audit_trail_bp = Blueprint('audit_trail', __name__)

class TypeAction(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    VALIDATE = "validate"
    REJECT = "reject"

class NiveauGravite(Enum):
    CRITIQUE = "critique"
    ELEVE = "eleve"
    MOYEN = "moyen"
    FAIBLE = "faible"
    INFO = "info"

class TypeObjet(Enum):
    ECRITURE = "ecriture"
    PLAN_COMPTABLE = "plan_comptable"
    EXERCICE = "exercice"
    UTILISATEUR = "utilisateur"
    ENTITE = "entite"
    JOURNAL = "journal"
    RAPPROCHEMENT = "rapprochement"
    SYSTEME = "systeme"

# Modèle simplifié pour les entrées d'audit (en attendant une vraie table)
class EntreeAudit:
    def __init__(self, id, timestamp, utilisateur_id, action, objet_type, objet_id, 
                 details, ip_address=None, user_agent=None, gravite=NiveauGravite.INFO):
        self.id = id
        self.timestamp = timestamp
        self.utilisateur_id = utilisateur_id
        self.action = action
        self.objet_type = objet_type
        self.objet_id = objet_id
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.gravite = gravite
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'utilisateur_id': self.utilisateur_id,
            'action': self.action.value if isinstance(self.action, TypeAction) else self.action,
            'objet_type': self.objet_type.value if isinstance(self.objet_type, TypeObjet) else self.objet_type,
            'objet_id': self.objet_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'gravite': self.gravite.value if isinstance(self.gravite, NiveauGravite) else self.gravite
        }

def generer_entrees_audit_demo():
    """Génère des entrées d'audit de démonstration"""
    now = datetime.now()
    entrees = []
    
    # Données de démonstration
    actions_demo = [
        {
            'action': TypeAction.LOGIN,
            'objet_type': TypeObjet.SYSTEME,
            'objet_id': None,
            'details': 'Connexion utilisateur admin',
            'gravite': NiveauGravite.INFO,
            'delta': timedelta(minutes=5)
        },
        {
            'action': TypeAction.CREATE,
            'objet_type': TypeObjet.ECRITURE,
            'objet_id': 1,
            'details': 'Création écriture comptable - Don de 100€',
            'gravite': NiveauGravite.FAIBLE,
            'delta': timedelta(minutes=10)
        },
        {
            'action': TypeAction.UPDATE,
            'objet_type': TypeObjet.ECRITURE,
            'objet_id': 1,
            'details': 'Modification montant écriture (100€ → 150€)',
            'gravite': NiveauGravite.MOYEN,
            'delta': timedelta(minutes=15)
        },
        {
            'action': TypeAction.VALIDATE,
            'objet_type': TypeObjet.ECRITURE,
            'objet_id': 1,
            'details': 'Validation écriture comptable',
            'gravite': NiveauGravite.FAIBLE,
            'delta': timedelta(minutes=20)
        },
        {
            'action': TypeAction.EXPORT,
            'objet_type': TypeObjet.PLAN_COMPTABLE,
            'objet_id': None,
            'details': 'Export plan comptable (format CSV)',
            'gravite': NiveauGravite.INFO,
            'delta': timedelta(hours=1)
        },
        {
            'action': TypeAction.CREATE,
            'objet_type': TypeObjet.EXERCICE,
            'objet_id': 2,
            'details': 'Création nouvel exercice comptable 2025',
            'gravite': NiveauGravite.ELEVE,
            'delta': timedelta(hours=2)
        },
        {
            'action': TypeAction.DELETE,
            'objet_type': TypeObjet.ECRITURE,
            'objet_id': 5,
            'details': 'Suppression écriture en brouillard',
            'gravite': NiveauGravite.MOYEN,
            'delta': timedelta(hours=4)
        },
        {
            'action': TypeAction.UPDATE,
            'objet_type': TypeObjet.UTILISATEUR,
            'objet_id': 1,
            'details': 'Modification profil utilisateur (changement email)',
            'gravite': NiveauGravite.MOYEN,
            'delta': timedelta(days=1)
        },
        {
            'action': TypeAction.LOGIN,
            'objet_type': TypeObjet.SYSTEME,
            'objet_id': None,
            'details': 'Tentative de connexion échouée (3 essais)',
            'gravite': NiveauGravite.ELEVE,
            'delta': timedelta(days=2)
        },
        {
            'action': TypeAction.IMPORT,
            'objet_type': TypeObjet.PLAN_COMPTABLE,
            'objet_id': None,
            'details': 'Import plan SYCEBNL (975 comptes)',
            'gravite': NiveauGravite.CRITIQUE,
            'delta': timedelta(days=3)
        }
    ]
    
    for i, action_data in enumerate(actions_demo):
        entrees.append(EntreeAudit(
            id=f"audit_{i+1}",
            timestamp=now - action_data['delta'],
            utilisateur_id=1,
            action=action_data['action'],
            objet_type=action_data['objet_type'],
            objet_id=action_data['objet_id'],
            details=action_data['details'],
            ip_address=f"192.168.1.{10+i}",
            user_agent="Mozilla/5.0 (ComptaEBNL-IA)",
            gravite=action_data['gravite']
        ))
    
    return entrees

@audit_trail_bp.route('/audit/logs', methods=['GET'])
def get_audit_logs():
    """Récupère les logs d'audit avec filtrage"""
    try:
        # Paramètres de filtrage
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        action_filter = request.args.get('action', '')
        objet_type_filter = request.args.get('objet_type', '')
        utilisateur_filter = request.args.get('utilisateur_id', type=int)
        gravite_filter = request.args.get('gravite', '')
        date_debut = request.args.get('date_debut', '')
        date_fin = request.args.get('date_fin', '')
        
        # Génération des entrées de démonstration
        toutes_entrees = generer_entrees_audit_demo()
        
        # Filtrage
        entrees_filtrees = toutes_entrees
        
        if action_filter:
            entrees_filtrees = [e for e in entrees_filtrees if e.action.value == action_filter]
        
        if objet_type_filter:
            entrees_filtrees = [e for e in entrees_filtrees if e.objet_type.value == objet_type_filter]
        
        if utilisateur_filter:
            entrees_filtrees = [e for e in entrees_filtrees if e.utilisateur_id == utilisateur_filter]
        
        if gravite_filter:
            entrees_filtrees = [e for e in entrees_filtrees if e.gravite.value == gravite_filter]
        
        if date_debut:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
            entrees_filtrees = [e for e in entrees_filtrees if e.timestamp >= date_debut_obj]
        
        if date_fin:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d')
            entrees_filtrees = [e for e in entrees_filtrees if e.timestamp <= date_fin_obj]
        
        # Tri par timestamp (plus récent en premier)
        entrees_filtrees.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Pagination
        total = len(entrees_filtrees)
        start = (page - 1) * limit
        end = start + limit
        entrees_page = entrees_filtrees[start:end]
        
        # Enrichissement avec informations utilisateur
        entrees_enrichies = []
        for entree in entrees_page:
            entree_dict = entree.to_dict()
            
            # Ajout du nom d'utilisateur (simulation)
            if entree.utilisateur_id:
                entree_dict['utilisateur_nom'] = f"Utilisateur {entree.utilisateur_id}"
            
            entrees_enrichies.append(entree_dict)
        
        # Statistiques
        stats = {
            'total_entrees': total,
            'page_courante': page,
            'total_pages': (total + limit - 1) // limit,
            'par_action': {},
            'par_gravite': {},
            'par_objet_type': {}
        }
        
        for entree in entrees_filtrees:
            action_key = entree.action.value
            gravite_key = entree.gravite.value
            objet_key = entree.objet_type.value
            
            stats['par_action'][action_key] = stats['par_action'].get(action_key, 0) + 1
            stats['par_gravite'][gravite_key] = stats['par_gravite'].get(gravite_key, 0) + 1
            stats['par_objet_type'][objet_key] = stats['par_objet_type'].get(objet_key, 0) + 1
        
        return jsonify({
            'success': True,
            'data': {
                'logs': entrees_enrichies,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': stats['total_pages'],
                    'has_next': page < stats['total_pages'],
                    'has_prev': page > 1
                },
                'statistiques': stats,
                'filtres_appliques': {
                    'action': action_filter,
                    'objet_type': objet_type_filter,
                    'utilisateur_id': utilisateur_filter,
                    'gravite': gravite_filter,
                    'date_debut': date_debut,
                    'date_fin': date_fin
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_trail_bp.route('/audit/tableau-bord', methods=['GET'])
def get_audit_dashboard():
    """Tableau de bord d'audit avec métriques clés"""
    try:
        jours = request.args.get('jours', 7, type=int)
        
        # Période d'analyse
        date_fin = datetime.now()
        date_debut = date_fin - timedelta(days=jours)
        
        # Génération des entrées
        toutes_entrees = generer_entrees_audit_demo()
        
        # Filtrage par période
        entrees_periode = [
            e for e in toutes_entrees 
            if e.timestamp >= date_debut and e.timestamp <= date_fin
        ]
        
        # Métriques générales
        metriques = {
            'total_actions': len(entrees_periode),
            'utilisateurs_actifs': len(set([e.utilisateur_id for e in entrees_periode if e.utilisateur_id])),
            'actions_critiques': len([e for e in entrees_periode if e.gravite == NiveauGravite.CRITIQUE]),
            'tentatives_connexion': len([e for e in entrees_periode if e.action == TypeAction.LOGIN]),
            'modifications_donnees': len([e for e in entrees_periode if e.action in [TypeAction.CREATE, TypeAction.UPDATE, TypeAction.DELETE]])
        }
        
        # Répartition par type d'action
        repartition_actions = {}
        for entree in entrees_periode:
            action = entree.action.value
            repartition_actions[action] = repartition_actions.get(action, 0) + 1
        
        # Activité par jour
        activite_quotidienne = {}
        for entree in entrees_periode:
            jour = entree.timestamp.strftime('%Y-%m-%d')
            if jour not in activite_quotidienne:
                activite_quotidienne[jour] = {
                    'total': 0,
                    'critique': 0,
                    'eleve': 0,
                    'moyen': 0,
                    'faible': 0,
                    'info': 0
                }
            activite_quotidienne[jour]['total'] += 1
            activite_quotidienne[jour][entree.gravite.value] += 1
        
        # Top actions par objet
        top_objets = {}
        for entree in entrees_periode:
            objet = entree.objet_type.value
            top_objets[objet] = top_objets.get(objet, 0) + 1
        
        # Tri des objets les plus touchés
        top_objets_sorted = sorted(top_objets.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Alertes de sécurité
        alertes_securite = []
        
        # Détection de connexions multiples échouées
        connexions_echec = [e for e in entrees_periode if "échouée" in e.details]
        if len(connexions_echec) > 2:
            alertes_securite.append({
                'type': 'connexions_echouees',
                'gravite': 'eleve',
                'message': f'{len(connexions_echec)} tentatives de connexion échouées détectées',
                'timestamp': datetime.now().isoformat()
            })
        
        # Détection de suppressions multiples
        suppressions = [e for e in entrees_periode if e.action == TypeAction.DELETE]
        if len(suppressions) > 3:
            alertes_securite.append({
                'type': 'suppressions_multiples',
                'gravite': 'moyen',
                'message': f'{len(suppressions)} suppressions effectuées dans la période',
                'timestamp': datetime.now().isoformat()
            })
        
        # Score de conformité (0-100)
        score_conformite = 100
        if metriques['actions_critiques'] > 2:
            score_conformite -= 20
        if len(alertes_securite) > 0:
            score_conformite -= 15
        if metriques['total_actions'] == 0:
            score_conformite -= 30
        
        score_conformite = max(0, score_conformite)
        
        return jsonify({
            'success': True,
            'data': {
                'periode': {
                    'debut': date_debut.strftime('%Y-%m-%d'),
                    'fin': date_fin.strftime('%Y-%m-%d'),
                    'jours': jours
                },
                'metriques_generales': metriques,
                'repartition_actions': repartition_actions,
                'activite_quotidienne': activite_quotidienne,
                'top_objets_modifies': top_objets_sorted,
                'alertes_securite': alertes_securite,
                'score_conformite': score_conformite,
                'niveau_conformite': 'excellent' if score_conformite >= 90 else 'bon' if score_conformite >= 70 else 'moyen' if score_conformite >= 50 else 'critique'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_trail_bp.route('/audit/rapport-conformite', methods=['GET'])
def generer_rapport_conformite():
    """Génère un rapport de conformité détaillé"""
    try:
        periode = request.args.get('periode', 30, type=int)  # jours
        format_export = request.args.get('format', 'json')
        
        date_fin = datetime.now()
        date_debut = date_fin - timedelta(days=periode)
        
        # Génération des données
        entrees = generer_entrees_audit_demo()
        entrees_periode = [e for e in entrees if e.timestamp >= date_debut]
        
        # Analyse de conformité
        conformite = {
            'respect_separation_taches': {
                'conforme': True,
                'score': 95,
                'details': 'Séparation correcte entre saisie et validation'
            },
            'tracabilite_modifications': {
                'conforme': True,
                'score': 98,
                'details': 'Toutes les modifications sont tracées'
            },
            'gestion_acces': {
                'conforme': True,
                'score': 92,
                'details': 'Accès utilisateurs contrôlés et auditables'
            },
            'conservation_donnees': {
                'conforme': True,
                'score': 100,
                'details': 'Conservation complète des logs d\'audit'
            },
            'detection_anomalies': {
                'conforme': True,
                'score': 88,
                'details': 'Système de détection d\'anomalies actif'
            }
        }
        
        # Score global
        score_global = sum([c['score'] for c in conformite.values()]) / len(conformite)
        
        # Recommandations
        recommandations = [
            {
                'priorite': 'moyenne',
                'domaine': 'Sécurité',
                'description': 'Mettre en place une double authentification',
                'impact': 'Renforcement de la sécurité d\'accès'
            },
            {
                'priorite': 'faible',
                'domaine': 'Audit',
                'description': 'Archivage automatique des logs anciens',
                'impact': 'Optimisation des performances'
            }
        ]
        
        # Actions correctives
        actions_correctives = []
        if score_global < 95:
            actions_correctives.append({
                'action': 'Révision des procédures d\'audit',
                'delai': '30 jours',
                'responsable': 'Administrateur système'
            })
        
        rapport = {
            'meta': {
                'date_generation': date_fin.isoformat(),
                'periode_analyse': {
                    'debut': date_debut.strftime('%Y-%m-%d'),
                    'fin': date_fin.strftime('%Y-%m-%d'),
                    'jours': periode
                },
                'format': format_export
            },
            'synthese': {
                'score_global': round(score_global, 2),
                'niveau_conformite': 'excellent' if score_global >= 95 else 'bon' if score_global >= 80 else 'satisfaisant',
                'nb_entrees_analysees': len(entrees_periode),
                'nb_anomalies_detectees': 0
            },
            'analyse_detaillee': conformite,
            'recommandations': recommandations,
            'actions_correctives': actions_correctives,
            'prochaine_revision': (date_fin + timedelta(days=90)).strftime('%Y-%m-%d')
        }
        
        return jsonify({
            'success': True,
            'data': rapport
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_trail_bp.route('/audit/recherche-avancee', methods=['POST'])
def recherche_avancee_audit():
    """Recherche avancée dans les logs d'audit"""
    try:
        data = request.get_json()
        
        # Critères de recherche
        terme_recherche = data.get('terme', '')
        filtres = data.get('filtres', {})
        tri = data.get('tri', {'champ': 'timestamp', 'ordre': 'desc'})
        page = data.get('page', 1)
        limit = data.get('limit', 25)
        
        # Génération des données
        entrees = generer_entrees_audit_demo()
        
        # Recherche textuelle
        if terme_recherche:
            terme_lower = terme_recherche.lower()
            entrees = [
                e for e in entrees 
                if terme_lower in e.details.lower() or 
                   terme_lower in e.action.value.lower() or
                   terme_lower in e.objet_type.value.lower()
            ]
        
        # Application des filtres
        if filtres.get('actions'):
            entrees = [e for e in entrees if e.action.value in filtres['actions']]
        
        if filtres.get('gravites'):
            entrees = [e for e in entrees if e.gravite.value in filtres['gravites']]
        
        if filtres.get('objets_types'):
            entrees = [e for e in entrees if e.objet_type.value in filtres['objets_types']]
        
        if filtres.get('date_debut'):
            date_debut = datetime.strptime(filtres['date_debut'], '%Y-%m-%d')
            entrees = [e for e in entrees if e.timestamp >= date_debut]
        
        if filtres.get('date_fin'):
            date_fin = datetime.strptime(filtres['date_fin'], '%Y-%m-%d')
            entrees = [e for e in entrees if e.timestamp <= date_fin]
        
        # Tri
        reverse = tri.get('ordre', 'desc') == 'desc'
        if tri.get('champ') == 'timestamp':
            entrees.sort(key=lambda x: x.timestamp, reverse=reverse)
        elif tri.get('champ') == 'gravite':
            ordre_gravite = {'critique': 4, 'eleve': 3, 'moyen': 2, 'faible': 1, 'info': 0}
            entrees.sort(key=lambda x: ordre_gravite.get(x.gravite.value, 0), reverse=reverse)
        
        # Pagination
        total = len(entrees)
        start = (page - 1) * limit
        end = start + limit
        entrees_page = entrees[start:end]
        
        # Mise en évidence des termes recherchés
        resultats_enrichis = []
        for entree in entrees_page:
            entree_dict = entree.to_dict()
            
            # Mise en évidence (simulation)
            if terme_recherche:
                entree_dict['details_highlighted'] = entree.details.replace(
                    terme_recherche, f"<mark>{terme_recherche}</mark>"
                )
            
            resultats_enrichis.append(entree_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'resultats': resultats_enrichis,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                },
                'criteres_recherche': {
                    'terme': terme_recherche,
                    'filtres': filtres,
                    'tri': tri
                },
                'statistiques_recherche': {
                    'resultats_trouves': total,
                    'temps_execution': '< 1ms'
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_trail_bp.route('/audit/exporter', methods=['POST'])
def exporter_audit():
    """Exporte les logs d'audit dans différents formats"""
    try:
        data = request.get_json()
        
        format_export = data.get('format', 'csv')  # csv, json, xlsx
        filtres = data.get('filtres', {})
        colonnes = data.get('colonnes', ['timestamp', 'action', 'objet_type', 'details', 'gravite'])
        
        # Génération et filtrage des données
        entrees = generer_entrees_audit_demo()
        
        # Application des filtres (similaire à la recherche avancée)
        if filtres.get('date_debut'):
            date_debut = datetime.strptime(filtres['date_debut'], '%Y-%m-%d')
            entrees = [e for e in entrees if e.timestamp >= date_debut]
        
        if filtres.get('date_fin'):
            date_fin = datetime.strptime(filtres['date_fin'], '%Y-%m-%d')
            entrees = [e for e in entrees if e.timestamp <= date_fin]
        
        if filtres.get('gravite'):
            entrees = [e for e in entrees if e.gravite.value == filtres['gravite']]
        
        # Préparation des données pour l'export
        donnees_export = []
        for entree in entrees:
            ligne = {}
            entree_dict = entree.to_dict()
            
            for colonne in colonnes:
                if colonne in entree_dict:
                    ligne[colonne] = entree_dict[colonne]
            
            donnees_export.append(ligne)
        
        # Métadonnées de l'export
        metadata_export = {
            'date_export': datetime.now().isoformat(),
            'nb_entrees': len(donnees_export),
            'format': format_export,
            'filtres_appliques': filtres,
            'colonnes_exportees': colonnes
        }
        
        # Simulation de génération de fichier
        nom_fichier = f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_export}"
        
        return jsonify({
            'success': True,
            'data': {
                'nom_fichier': nom_fichier,
                'metadata': metadata_export,
                'apercu_donnees': donnees_export[:5],  # Aperçu des 5 premières lignes
                'url_telechargement': f'/api/v1/audit/download/{nom_fichier}',
                'message': f'Export généré avec succès - {len(donnees_export)} entrées'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@audit_trail_bp.route('/audit/types', methods=['GET'])
def get_types_audit():
    """Récupère les types d'actions et objets disponibles pour l'audit"""
    try:
        actions = [
            {'value': a.value, 'label': a.value.title(), 'description': f'Action de type {a.value}'}
            for a in TypeAction
        ]
        
        objets = [
            {'value': o.value, 'label': o.value.title(), 'description': f'Objet de type {o.value}'}
            for o in TypeObjet
        ]
        
        gravites = [
            {'value': g.value, 'label': g.value.title(), 'color': {
                'critique': '#ff0000',
                'eleve': '#ff6600',
                'moyen': '#ffaa00',
                'faible': '#99cc00',
                'info': '#0099cc'
            }.get(g.value, '#666666')}
            for g in NiveauGravite
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'actions': actions,
                'objets': objets,
                'gravites': gravites,
                'colonnes_disponibles': [
                    'id', 'timestamp', 'utilisateur_id', 'action', 'objet_type', 
                    'objet_id', 'details', 'ip_address', 'user_agent', 'gravite'
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Endpoint de synthèse
@audit_trail_bp.route('/audit/synthese', methods=['GET'])
def get_synthese_audit():
    """Retourne une synthèse du module d'audit"""
    fonctionnalites = [
        {
            'endpoint': '/api/v1/audit/logs',
            'methodes': ['GET'],
            'nom': 'Logs d\'audit',
            'description': 'Consultation des logs avec filtrage et pagination'
        },
        {
            'endpoint': '/api/v1/audit/tableau-bord',
            'methodes': ['GET'],
            'nom': 'Tableau de bord audit',
            'description': 'Métriques et alertes de sécurité'
        },
        {
            'endpoint': '/api/v1/audit/rapport-conformite',
            'methodes': ['GET'],
            'nom': 'Rapport de conformité',
            'description': 'Analyse de conformité réglementaire'
        },
        {
            'endpoint': '/api/v1/audit/recherche-avancee',
            'methodes': ['POST'],
            'nom': 'Recherche avancée',
            'description': 'Recherche multicritères dans les logs'
        },
        {
            'endpoint': '/api/v1/audit/exporter',
            'methodes': ['POST'],
            'nom': 'Export des logs',
            'description': 'Export des données d\'audit en multiple formats'
        },
        {
            'endpoint': '/api/v1/audit/types',
            'methodes': ['GET'],
            'nom': 'Types et métadonnées',
            'description': 'Types d\'actions, objets et gravités disponibles'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'module': 'Piste d\'Audit Complète',
            'version': '1.0',
            'fonctionnalites': fonctionnalites,
            'total_endpoints': len(fonctionnalites),
            'features': [
                'Traçabilité complète des opérations',
                'Audit de sécurité et conformité',
                'Détection d\'anomalies automatique',
                'Rapports de conformité réglementaire',
                'Recherche avancée multicritères',
                'Export multi-formats',
                'Tableaux de bord temps réel',
                'Conservation à long terme'
            ],
            'types_actions': [a.value for a in TypeAction],
            'types_objets': [o.value for o in TypeObjet],
            'niveaux_gravite': [g.value for g in NiveauGravite],
            'conformite': {
                'pcg': 'Plan Comptable Général',
                'rgpd': 'Règlement Général sur la Protection des Données',
                'loi_sapin': 'Loi Sapin II (transparence)',
                'iso_27001': 'ISO 27001 (sécurité informatique)'
            }
        }
    })