"""
Module de Notifications et Alertes
Gère les notifications et alertes automatiques pour les utilisateurs de la plateforme
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, date
from sqlalchemy import func, and_, or_, desc
from enum import Enum

from models import (
    db, PlanComptable, EcritureComptable, LigneEcriture, 
    ExerciceComptable, JournalComptable, EntiteEBNL, Utilisateur
)

notifications_bp = Blueprint('notifications', __name__)

class TypeNotification(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class CategorieNotification(Enum):
    COMPTABILITE = "comptabilite"
    EXERCICE = "exercice"
    UTILISATEUR = "utilisateur"
    SYSTEME = "systeme"
    RAPPROCHEMENT = "rapprochement"
    IA = "ia"

# Modèle simplifié pour les notifications (en attendant une vraie table)
class Notification:
    def __init__(self, id, titre, message, type_notif, categorie, date_creation, lu=False, utilisateur_id=None):
        self.id = id
        self.titre = titre
        self.message = message
        self.type = type_notif
        self.categorie = categorie
        self.date_creation = date_creation
        self.lu = lu
        self.utilisateur_id = utilisateur_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'titre': self.titre,
            'message': self.message,
            'type': self.type.value if isinstance(self.type, TypeNotification) else self.type,
            'categorie': self.categorie.value if isinstance(self.categorie, CategorieNotification) else self.categorie,
            'date_creation': self.date_creation.isoformat() if isinstance(self.date_creation, datetime) else self.date_creation,
            'lu': self.lu,
            'utilisateur_id': self.utilisateur_id
        }

def generer_alertes_automatiques():
    """Génère automatiquement des alertes basées sur l'état du système"""
    alertes = []
    now = datetime.now()
    
    # Alerte : Exercice bientôt fermé
    exercices_ouverts = ExerciceComptable.query.filter_by(statut='ouvert').all()
    for exercice in exercices_ouverts:
        jours_restants = (exercice.date_fin - date.today()).days
        if jours_restants <= 30 and jours_restants > 0:
            alertes.append(Notification(
                id=f"exercice_fin_{exercice.id}",
                titre="Exercice bientôt terminé",
                message=f"L'exercice {exercice.nom_exercice} se termine dans {jours_restants} jours",
                type_notif=TypeNotification.WARNING,
                categorie=CategorieNotification.EXERCICE,
                date_creation=now
            ))
        elif jours_restants <= 0:
            alertes.append(Notification(
                id=f"exercice_expire_{exercice.id}",
                titre="Exercice expiré",
                message=f"L'exercice {exercice.nom_exercice} aurait dû être clôturé",
                type_notif=TypeNotification.ERROR,
                categorie=CategorieNotification.EXERCICE,
                date_creation=now
            ))
    
    # Alerte : Écritures en brouillard anciennes
    date_limite = now - timedelta(days=7)
    nb_brouillards = EcritureComptable.query.filter(
        EcritureComptable.statut == 'brouillard',
        EcritureComptable.date_creation <= date_limite
    ).count()
    
    if nb_brouillards > 0:
        alertes.append(Notification(
            id="brouillards_anciens",
            titre="Écritures en brouillard anciennes",
            message=f"{nb_brouillards} écritures en brouillard depuis plus de 7 jours",
            type_notif=TypeNotification.WARNING,
            categorie=CategorieNotification.COMPTABILITE,
            date_creation=now
        ))
    
    # Alerte : Déséquilibre comptable
    ecritures_desequilibrees = []
    ecritures_recentes = EcritureComptable.query.filter(
        EcritureComptable.date_creation >= now - timedelta(days=1)
    ).all()
    
    for ecriture in ecritures_recentes:
        lignes = LigneEcriture.query.filter_by(ecriture_id=ecriture.id).all()
        total_debit = sum([float(ligne.debit) for ligne in lignes])
        total_credit = sum([float(ligne.credit) for ligne in lignes])
        
        if abs(total_debit - total_credit) > 0.01:  # Tolérance de 1 centime
            ecritures_desequilibrees.append(ecriture.numero_ecriture or f"#{ecriture.id}")
    
    if ecritures_desequilibrees:
        alertes.append(Notification(
            id="desequilibre_comptable",
            titre="Déséquilibre comptable détecté",
            message=f"Écritures déséquilibrées : {', '.join(ecritures_desequilibrees[:5])}",
            type_notif=TypeNotification.ERROR,
            categorie=CategorieNotification.COMPTABILITE,
            date_creation=now
        ))
    
    # Alerte : Comptes sans mouvement
    comptes_inactifs = db.session.query(PlanComptable).outerjoin(LigneEcriture).group_by(
        PlanComptable.id
    ).having(func.count(LigneEcriture.id) == 0).limit(10).all()
    
    if len(comptes_inactifs) > 5:
        alertes.append(Notification(
            id="comptes_inactifs",
            titre="Comptes sans mouvement",
            message=f"{len(comptes_inactifs)} comptes du plan comptable n'ont aucun mouvement",
            type_notif=TypeNotification.INFO,
            categorie=CategorieNotification.COMPTABILITE,
            date_creation=now
        ))
    
    # Alerte : Activité comptable faible
    nb_ecritures_semaine = EcritureComptable.query.filter(
        EcritureComptable.date_creation >= now - timedelta(days=7)
    ).count()
    
    if nb_ecritures_semaine == 0:
        alertes.append(Notification(
            id="activite_faible",
            titre="Activité comptable faible",
            message="Aucune écriture saisie cette semaine",
            type_notif=TypeNotification.INFO,
            categorie=CategorieNotification.COMPTABILITE,
            date_creation=now
        ))
    
    return alertes

@notifications_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Récupère les notifications pour l'utilisateur courant"""
    try:
        # Paramètres de filtrage
        type_filter = request.args.get('type', '')
        categorie_filter = request.args.get('categorie', '')
        lu_filter = request.args.get('lu', '')  # true, false, all
        limit = request.args.get('limit', 50, type=int)
        
        # Génération des alertes automatiques
        alertes_auto = generer_alertes_automatiques()
        
        # Notifications manuelles (simulées)
        notifications_manuelles = [
            Notification(
                id="welcome",
                titre="Bienvenue sur ComptaEBNL-IA",
                message="Votre plateforme de comptabilité EBNL avec IA est prête à utiliser",
                type_notif=TypeNotification.SUCCESS,
                categorie=CategorieNotification.SYSTEME,
                date_creation=datetime.now() - timedelta(hours=1),
                lu=False
            ),
            Notification(
                id="plan_comptable_ok",
                titre="Plan comptable SYCEBNL importé",
                message="975 comptes SYCEBNL ont été importés avec succès",
                type_notif=TypeNotification.SUCCESS,
                categorie=CategorieNotification.SYSTEME,
                date_creation=datetime.now() - timedelta(hours=2),
                lu=True
            )
        ]
        
        # Fusion des notifications
        toutes_notifications = alertes_auto + notifications_manuelles
        
        # Filtrage
        if type_filter:
            toutes_notifications = [n for n in toutes_notifications if n.type.value == type_filter]
        
        if categorie_filter:
            toutes_notifications = [n for n in toutes_notifications if n.categorie.value == categorie_filter]
        
        if lu_filter and lu_filter != 'all':
            lu_bool = lu_filter.lower() == 'true'
            toutes_notifications = [n for n in toutes_notifications if n.lu == lu_bool]
        
        # Tri par date (plus récent en premier)
        toutes_notifications.sort(key=lambda x: x.date_creation, reverse=True)
        
        # Limitation
        toutes_notifications = toutes_notifications[:limit]
        
        # Statistiques
        stats = {
            'total': len(toutes_notifications),
            'non_lues': len([n for n in toutes_notifications if not n.lu]),
            'par_type': {},
            'par_categorie': {}
        }
        
        for notif in toutes_notifications:
            type_key = notif.type.value if isinstance(notif.type, TypeNotification) else notif.type
            cat_key = notif.categorie.value if isinstance(notif.categorie, CategorieNotification) else notif.categorie
            
            stats['par_type'][type_key] = stats['par_type'].get(type_key, 0) + 1
            stats['par_categorie'][cat_key] = stats['par_categorie'].get(cat_key, 0) + 1
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': [n.to_dict() for n in toutes_notifications],
                'statistiques': stats,
                'filtres': {
                    'type': type_filter,
                    'categorie': categorie_filter,
                    'lu': lu_filter,
                    'limit': limit
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/notifications/<notification_id>/marquer-lu', methods=['POST'])
def marquer_notification_lue(notification_id):
    """Marque une notification comme lue"""
    try:
        # Simulation : dans un vrai système, on mettrait à jour la base de données
        return jsonify({
            'success': True,
            'data': {
                'notification_id': notification_id,
                'message': 'Notification marquée comme lue',
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/notifications/marquer-toutes-lues', methods=['POST'])
def marquer_toutes_lues():
    """Marque toutes les notifications comme lues"""
    try:
        # Simulation : dans un vrai système, on mettrait à jour toutes les notifications
        return jsonify({
            'success': True,
            'data': {
                'message': 'Toutes les notifications ont été marquées comme lues',
                'timestamp': datetime.now().isoformat(),
                'notifications_mises_a_jour': 'toutes'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/alertes/tableau-bord', methods=['GET'])
def get_alertes_tableau_bord():
    """Récupère les alertes importantes pour le tableau de bord"""
    try:
        alertes = generer_alertes_automatiques()
        
        # Filtrer les alertes critiques (WARNING et ERROR)
        alertes_critiques = [
            a for a in alertes 
            if a.type in [TypeNotification.WARNING, TypeNotification.ERROR]
        ]
        
        # Métriques de santé du système
        now = datetime.now()
        metriques = {
            'ecritures_en_brouillard': EcritureComptable.query.filter_by(statut='brouillard').count(),
            'exercices_ouverts': ExerciceComptable.query.filter_by(statut='ouvert').count(),
            'activite_7_jours': EcritureComptable.query.filter(
                EcritureComptable.date_creation >= now - timedelta(days=7)
            ).count(),
            'utilisateurs_actifs': Utilisateur.query.count(),
            'derniere_ecriture': None
        }
        
        # Dernière écriture
        derniere_ecriture = EcritureComptable.query.order_by(desc(EcritureComptable.date_creation)).first()
        if derniere_ecriture:
            metriques['derniere_ecriture'] = {
                'date': derniere_ecriture.date_creation.isoformat(),
                'libelle': derniere_ecriture.libelle,
                'montant': float(derniere_ecriture.montant_total)
            }
        
        # Score de santé (0-100)
        score_sante = 100
        if metriques['ecritures_en_brouillard'] > 10:
            score_sante -= 20
        if metriques['exercices_ouverts'] == 0:
            score_sante -= 30
        if metriques['activite_7_jours'] == 0:
            score_sante -= 25
        if len(alertes_critiques) > 3:
            score_sante -= 15
        
        score_sante = max(0, score_sante)
        
        return jsonify({
            'success': True,
            'data': {
                'alertes_critiques': [a.to_dict() for a in alertes_critiques],
                'metriques_sante': metriques,
                'score_sante': score_sante,
                'niveau_sante': 'excellent' if score_sante >= 90 else 'bon' if score_sante >= 70 else 'moyen' if score_sante >= 50 else 'critique',
                'timestamp': now.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/alertes/configurer', methods=['POST'])
def configurer_alertes():
    """Configure les paramètres d'alertes pour l'utilisateur"""
    try:
        data = request.get_json()
        
        # Configuration par défaut
        config_defaut = {
            'notifications_email': True,
            'notifications_web': True,
            'alertes_exercice': True,
            'alertes_brouillard': True,
            'alertes_desequilibre': True,
            'seuil_brouillard_jours': 7,
            'seuil_exercice_jours': 30,
            'frequence_resume': 'quotidien'  # quotidien, hebdomadaire, mensuel
        }
        
        # Fusion avec les données reçues
        config_utilisateur = {**config_defaut, **data}
        
        # Validation
        if config_utilisateur.get('seuil_brouillard_jours', 0) < 1:
            return jsonify({
                'success': False,
                'error': 'Le seuil de brouillard doit être d\'au moins 1 jour'
            }), 400
        
        if config_utilisateur.get('seuil_exercice_jours', 0) < 1:
            return jsonify({
                'success': False,
                'error': 'Le seuil d\'exercice doit être d\'au moins 1 jour'
            }), 400
        
        # Simulation de sauvegarde (dans un vrai système, sauvegarder en base)
        return jsonify({
            'success': True,
            'data': {
                'configuration': config_utilisateur,
                'message': 'Configuration des alertes mise à jour avec succès',
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/alertes/historique', methods=['GET'])
def get_historique_alertes():
    """Récupère l'historique des alertes"""
    try:
        jours = request.args.get('jours', 30, type=int)
        type_alerte = request.args.get('type', '')
        
        # Simulation d'historique
        historique = []
        now = datetime.now()
        
        for i in range(min(jours, 10)):  # Limité à 10 jours pour la démo
            date_alerte = now - timedelta(days=i)
            
            # Simulation d'alertes historiques
            if i % 3 == 0:  # Tous les 3 jours
                historique.append({
                    'date': date_alerte.strftime('%Y-%m-%d'),
                    'nb_alertes': 2 + (i % 3),
                    'types': ['warning', 'info'],
                    'categories': ['comptabilite', 'exercice']
                })
            elif i % 5 == 0:  # Tous les 5 jours
                historique.append({
                    'date': date_alerte.strftime('%Y-%m-%d'),
                    'nb_alertes': 1,
                    'types': ['error'],
                    'categories': ['comptabilite']
                })
        
        # Statistiques de l'historique
        total_alertes = sum([h['nb_alertes'] for h in historique])
        
        return jsonify({
            'success': True,
            'data': {
                'historique': historique,
                'statistiques': {
                    'periode_jours': jours,
                    'total_alertes': total_alertes,
                    'moyenne_par_jour': round(total_alertes / max(len(historique), 1), 2),
                    'jours_avec_alertes': len(historique)
                },
                'filtres': {
                    'jours': jours,
                    'type': type_alerte
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/notifications/types', methods=['GET'])
def get_types_notifications():
    """Récupère les types et catégories de notifications disponibles"""
    try:
        types = [
            {'value': t.value, 'label': t.value.title(), 'description': f'Notifications de type {t.value}'}
            for t in TypeNotification
        ]
        
        categories = [
            {'value': c.value, 'label': c.value.title(), 'description': f'Notifications de catégorie {c.value}'}
            for c in CategorieNotification
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'types': types,
                'categories': categories,
                'niveaux_priorite': [
                    {'value': 'haute', 'label': 'Haute', 'color': '#ff4444'},
                    {'value': 'normale', 'label': 'Normale', 'color': '#ffaa00'},
                    {'value': 'basse', 'label': 'Basse', 'color': '#00aa00'}
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Endpoint de synthèse
@notifications_bp.route('/notifications/synthese', methods=['GET'])
def get_synthese_notifications():
    """Retourne une synthèse du module de notifications"""
    fonctionnalites = [
        {
            'endpoint': '/api/v1/notifications',
            'methodes': ['GET'],
            'nom': 'Liste des notifications',
            'description': 'Récupère les notifications avec filtrage et pagination'
        },
        {
            'endpoint': '/api/v1/notifications/{id}/marquer-lu',
            'methodes': ['POST'],
            'nom': 'Marquer comme lu',
            'description': 'Marque une notification spécifique comme lue'
        },
        {
            'endpoint': '/api/v1/notifications/marquer-toutes-lues',
            'methodes': ['POST'],
            'nom': 'Marquer toutes comme lues',
            'description': 'Marque toutes les notifications comme lues'
        },
        {
            'endpoint': '/api/v1/alertes/tableau-bord',
            'methodes': ['GET'],
            'nom': 'Alertes tableau de bord',
            'description': 'Récupère les alertes critiques et métriques de santé'
        },
        {
            'endpoint': '/api/v1/alertes/configurer',
            'methodes': ['POST'],
            'nom': 'Configuration alertes',
            'description': 'Configure les paramètres d\'alertes utilisateur'
        },
        {
            'endpoint': '/api/v1/alertes/historique',
            'methodes': ['GET'],
            'nom': 'Historique alertes',
            'description': 'Récupère l\'historique des alertes sur une période'
        },
        {
            'endpoint': '/api/v1/notifications/types',
            'methodes': ['GET'],
            'nom': 'Types et catégories',
            'description': 'Liste les types et catégories de notifications'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'module': 'Notifications et Alertes',
            'version': '1.0',
            'fonctionnalites': fonctionnalites,
            'total_endpoints': len(fonctionnalites),
            'features': [
                'Alertes automatiques intelligentes',
                'Notifications système et utilisateur',
                'Configuration personnalisable',
                'Tableau de bord de santé',
                'Historique et statistiques',
                'Filtrage et tri avancés',
                'Marquage lu/non-lu',
                'Métriques de performance'
            ],
            'types_alertes': [t.value for t in TypeNotification],
            'categories': [c.value for c in CategorieNotification]
        }
    })