"""
Module de Rapprochement Bancaire Automatique
Permet la réconciliation entre les écritures comptables et les relevés bancaires
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc
from decimal import Decimal
import csv
import re

from models import (
    db, PlanComptable, EcritureComptable, LigneEcriture, 
    ExerciceComptable, JournalComptable
)

reconciliation_bp = Blueprint('reconciliation', __name__)

# Modèle simplifié pour les mouvements bancaires
class MouvementBancaire:
    def __init__(self, date, libelle, montant, reference=None):
        self.date = date
        self.libelle = libelle.strip()
        self.montant = float(montant)
        self.reference = reference
        self.id = f"{date}_{montant}_{hash(libelle) % 10000}"

def nettoyer_libelle(libelle):
    """Nettoie et normalise un libellé pour la comparaison"""
    libelle_clean = re.sub(r'[^\w\s]', '', libelle.lower())
    libelle_clean = re.sub(r'\s+', ' ', libelle_clean).strip()
    return libelle_clean

def calculer_score_similarite(libelle1, libelle2):
    """Calcule un score de similarité entre deux libellés (0-100)"""
    lib1_clean = nettoyer_libelle(libelle1)
    lib2_clean = nettoyer_libelle(libelle2)
    
    mots1 = set(lib1_clean.split())
    mots2 = set(lib2_clean.split())
    
    if not mots1 or not mots2:
        return 0
    
    mots_communs = mots1.intersection(mots2)
    score = (len(mots_communs) * 2) / (len(mots1) + len(mots2)) * 100
    
    return min(100, score)

@reconciliation_bp.route('/rapprochement/ecritures-non-rapprochees', methods=['GET'])
def get_ecritures_non_rapprochees():
    """Récupère les écritures comptables non rapprochées"""
    try:
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        compte_bancaire = request.args.get('compte', '512')
        
        if date_debut:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        else:
            date_debut = datetime.now().date() - timedelta(days=30)
            
        if date_fin:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        else:
            date_fin = datetime.now().date()
        
        # Requête pour les écritures bancaires sur la période
        ecritures_query = db.session.query(EcritureComptable, LigneEcriture).join(
            LigneEcriture
        ).filter(
            EcritureComptable.date_ecriture >= date_debut,
            EcritureComptable.date_ecriture <= date_fin,
            LigneEcriture.numero_compte.like(f'{compte_bancaire}%')
        ).order_by(desc(EcritureComptable.date_ecriture))
        
        ecritures_non_rapprochees = []
        for ecriture, ligne in ecritures_query.all():
            montant = float(ligne.debit - ligne.credit)
            
            ecritures_non_rapprochees.append({
                'ecriture_id': ecriture.id,
                'date': ecriture.date_ecriture.strftime('%Y-%m-%d'),
                'libelle': ecriture.libelle,
                'montant': montant,
                'piece_justificative': ecriture.piece_justificative,
                'journal': ecriture.journal,
                'numero_compte': ligne.numero_compte
            })
        
        return jsonify({
            'success': True,
            'data': {
                'ecritures_non_rapprochees': ecritures_non_rapprochees,
                'periode': {
                    'debut': date_debut.strftime('%Y-%m-%d'),
                    'fin': date_fin.strftime('%Y-%m-%d')
                },
                'total': len(ecritures_non_rapprochees)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reconciliation_bp.route('/rapprochement/statistiques', methods=['GET'])
def get_statistiques_rapprochement():
    """Génère des statistiques sur le rapprochement bancaire"""
    try:
        mois = request.args.get('mois', 3, type=int)
        
        date_fin = datetime.now().date()
        date_debut = date_fin - timedelta(days=mois * 30)
        
        # Écritures totales sur la période
        total_ecritures = db.session.query(EcritureComptable, LigneEcriture).join(
            LigneEcriture
        ).filter(
            EcritureComptable.date_ecriture >= date_debut,
            EcritureComptable.date_ecriture <= date_fin,
            LigneEcriture.numero_compte.like('512%')
        ).count()
        
        # Pour l'instant, aucune écriture n'est rapprochée (fonctionnalité future)
        ecritures_rapprochees = 0
        
        # Calcul des ratios
        taux_rapprochement = (ecritures_rapprochees / total_ecritures * 100) if total_ecritures > 0 else 0
        
        # Mouvements par mois
        mouvements_mensuels = []
        for i in range(mois):
            debut_mois = date_fin - timedelta(days=(i+1) * 30)
            fin_mois = date_fin - timedelta(days=i * 30)
            
            nb_mouvements = db.session.query(EcritureComptable, LigneEcriture).join(
                LigneEcriture
            ).filter(
                EcritureComptable.date_ecriture >= debut_mois,
                EcritureComptable.date_ecriture <= fin_mois,
                LigneEcriture.numero_compte.like('512%')
            ).count()
            
            mouvements_mensuels.append({
                'mois': fin_mois.strftime('%Y-%m'),
                'nb_mouvements': nb_mouvements
            })
        
        return jsonify({
            'success': True,
            'data': {
                'periode': {
                    'debut': date_debut.strftime('%Y-%m-%d'),
                    'fin': date_fin.strftime('%Y-%m-%d'),
                    'nb_mois': mois
                },
                'statistiques_globales': {
                    'total_ecritures_bancaires': total_ecritures,
                    'ecritures_rapprochees': ecritures_rapprochees,
                    'ecritures_non_rapprochees': total_ecritures - ecritures_rapprochees,
                    'taux_rapprochement': round(taux_rapprochement, 2)
                },
                'evolution_mensuelle': list(reversed(mouvements_mensuels))
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reconciliation_bp.route('/rapprochement/modele-csv', methods=['GET'])
def get_modele_csv():
    """Fournit un modèle de fichier CSV pour l'import des relevés bancaires"""
    try:
        lignes_exemple = [
            ['Date', 'Libelle', 'Montant', 'Reference'],
            ['2024-01-15', 'Don de Jean Dupont', '100.00', 'DON001'],
            ['2024-01-16', 'Paiement facture électricité', '-45.80', 'FACT123'],
            ['2024-01-17', 'Subvention municipale', '500.00', 'SUB2024-001'],
            ['2024-01-18', 'Achat fournitures bureau', '-25.30', 'ACH789']
        ]
        
        contenu_csv = '\n'.join([';'.join(ligne) for ligne in lignes_exemple])
        
        return jsonify({
            'success': True,
            'data': {
                'nom_fichier': 'modele_releve_bancaire.csv',
                'contenu': contenu_csv,
                'instructions': [
                    'Utilisez le point-virgule (;) comme séparateur',
                    'Format de date: AAAA-MM-JJ',
                    'Montants: positifs pour les entrées, négatifs pour les sorties',
                    'Colonnes obligatoires: Date, Libelle, Montant',
                    'Colonne optionnelle: Reference'
                ],
                'apercu': lignes_exemple
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reconciliation_bp.route('/rapprochement/correspondances', methods=['POST'])
def rechercher_correspondances():
    """Recherche les correspondances entre mouvements bancaires et écritures"""
    try:
        data = request.get_json()
        
        date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        tolerance_montant = data.get('tolerance_montant', 0.01)
        seuil_similarite = data.get('seuil_similarite', 70)
        
        # Reconstruction des mouvements bancaires
        mouvements_bancaires = []
        for mvt_data in data['mouvements_bancaires']:
            mouvements_bancaires.append(MouvementBancaire(
                date=datetime.strptime(mvt_data['date'], '%Y-%m-%d').date(),
                libelle=mvt_data['libelle'],
                montant=mvt_data['montant'],
                reference=mvt_data.get('reference', '')
            ))
        
        # Récupération des écritures comptables
        ecritures_comptables = db.session.query(EcritureComptable, LigneEcriture).join(
            LigneEcriture
        ).filter(
            EcritureComptable.date_ecriture >= date_debut,
            EcritureComptable.date_ecriture <= date_fin,
            or_(
                LigneEcriture.numero_compte.like('512%'),
                LigneEcriture.numero_compte.like('53%')
            )
        ).all()
        
        correspondances = []
        for mouvement in mouvements_bancaires:
            meilleures_correspondances = []
            
            for ecriture, ligne in ecritures_comptables:
                montant_ecriture = float(ligne.debit - ligne.credit)
                
                # Vérification montant
                if abs(abs(mouvement.montant) - abs(montant_ecriture)) <= tolerance_montant:
                    score_libelle = calculer_score_similarite(mouvement.libelle, ecriture.libelle)
                    delta_jours = abs((mouvement.date - ecriture.date_ecriture).days)
                    score_date = max(0, 100 - (delta_jours * 10))
                    score_global = (score_libelle * 0.7) + (score_date * 0.3)
                    
                    if score_global >= seuil_similarite:
                        meilleures_correspondances.append({
                            'ecriture_id': ecriture.id,
                            'ligne_id': ligne.id,
                            'ecriture': {
                                'id': ecriture.id,
                                'date': ecriture.date_ecriture.strftime('%Y-%m-%d'),
                                'libelle': ecriture.libelle,
                                'montant': montant_ecriture,
                                'piece_justificative': ecriture.piece_justificative
                            },
                            'scores': {
                                'libelle': round(score_libelle, 2),
                                'date': round(score_date, 2),
                                'global': round(score_global, 2)
                            }
                        })
            
            meilleures_correspondances.sort(key=lambda x: x['scores']['global'], reverse=True)
            
            correspondances.append({
                'mouvement_bancaire': {
                    'id': mouvement.id,
                    'date': mouvement.date.strftime('%Y-%m-%d'),
                    'libelle': mouvement.libelle,
                    'montant': mouvement.montant,
                    'reference': mouvement.reference
                },
                'correspondances_trouvees': meilleures_correspondances[:3],
                'statut': 'automatique' if meilleures_correspondances and meilleures_correspondances[0]['scores']['global'] >= 90 else 'manuel'
            })
        
        # Statistiques
        nb_automatiques = sum(1 for c in correspondances if c['statut'] == 'automatique')
        nb_manuels = len(correspondances) - nb_automatiques
        
        return jsonify({
            'success': True,
            'data': {
                'correspondances': correspondances,
                'statistiques': {
                    'total_mouvements': len(correspondances),
                    'correspondances_automatiques': nb_automatiques,
                    'correspondances_manuelles': nb_manuels,
                    'taux_automatisation': round((nb_automatiques / len(correspondances)) * 100, 2) if correspondances else 0
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reconciliation_bp.route('/rapprochement/synthese', methods=['GET'])
def get_synthese_rapprochement():
    """Retourne une synthèse du module de rapprochement bancaire"""
    fonctionnalites = [
        {
            'endpoint': '/api/v1/rapprochement/import-releve',
            'methode': 'POST',
            'nom': 'Import relevé bancaire',
            'description': 'Importe un fichier CSV de relevé bancaire',
            'parametres': ['fichier (CSV)', 'date_debut', 'date_fin']
        },
        {
            'endpoint': '/api/v1/rapprochement/correspondances',
            'methode': 'POST',
            'nom': 'Recherche correspondances',
            'description': 'Trouve automatiquement les correspondances entre relevé et écritures',
            'parametres': ['mouvements_bancaires', 'date_debut', 'date_fin', 'tolerance_montant', 'seuil_similarite']
        },
        {
            'endpoint': '/api/v1/rapprochement/ecritures-non-rapprochees',
            'methode': 'GET',
            'nom': 'Écritures non rapprochées',
            'description': 'Liste les écritures comptables non encore rapprochées',
            'parametres': ['date_debut', 'date_fin', 'compte']
        },
        {
            'endpoint': '/api/v1/rapprochement/statistiques',
            'methode': 'GET',
            'nom': 'Statistiques rapprochement',
            'description': 'Fournit des statistiques sur le taux de rapprochement',
            'parametres': ['mois']
        },
        {
            'endpoint': '/api/v1/rapprochement/modele-csv',
            'methode': 'GET',
            'nom': 'Modèle CSV',
            'description': 'Fournit un modèle de fichier CSV pour l\'import',
            'parametres': []
        }
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'module': 'Rapprochement Bancaire Automatique',
            'version': '1.0',
            'fonctionnalites': fonctionnalites,
            'total_endpoints': len(fonctionnalites),
            'formats_supportes': ['CSV'],
            'algorithmes': [
                'Matching par montant avec tolérance',
                'Similarité textuelle des libellés',
                'Pondération temporelle (proximité des dates)',
                'Score global de correspondance'
            ]
        }
    })