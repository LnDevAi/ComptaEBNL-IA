"""
Module de Rapports et Analyses Avancées
Fournit des analyses comptables et financières pour les EBNL
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract, case, desc
from decimal import Decimal
import calendar

from models import (
    db, PlanComptable, EcritureComptable, LigneEcriture, 
    ExerciceComptable, JournalComptable, EntiteEBNL
)

rapports_analytics_bp = Blueprint('rapports_analytics', __name__)

def calculer_solde_compte_periode(numero_compte, date_debut, date_fin):
    """Calcule le solde d'un compte sur une période donnée"""
    try:
        query = db.session.query(
            func.coalesce(func.sum(LigneEcriture.debit), 0).label('total_debit'),
            func.coalesce(func.sum(LigneEcriture.credit), 0).label('total_credit')
        ).join(EcritureComptable).filter(
            LigneEcriture.numero_compte == numero_compte,
            EcritureComptable.date_ecriture >= date_debut,
            EcritureComptable.date_ecriture <= date_fin
        ).first()
        
        if query:
            return float(query.total_debit - query.total_credit)
        return 0.0
    except Exception:
        return 0.0

def get_evolution_compte(numero_compte, mois=12):
    """Récupère l'évolution d'un compte sur X mois"""
    evolution = []
    today = datetime.now()
    
    for i in range(mois):
        date_fin = today - timedelta(days=i*30)
        date_debut = date_fin - timedelta(days=30)
        
        solde = calculer_solde_compte_periode(numero_compte, date_debut, date_fin)
        
        evolution.append({
            'mois': date_fin.strftime('%Y-%m'),
            'solde': solde
        })
    
    return list(reversed(evolution))

@rapports_analytics_bp.route('/dashboard/kpi', methods=['GET'])
def get_kpi_dashboard():
    """Tableau de bord avec indicateurs clés pour EBNL"""
    try:
        exercice_id = request.args.get('exercice_id', type=int)
        
        # Période par défaut : exercice courant ou année en cours
        if exercice_id:
            exercice = ExerciceComptable.query.get(exercice_id)
            if exercice:
                date_debut = exercice.date_debut
                date_fin = exercice.date_fin
            else:
                date_debut = datetime(datetime.now().year, 1, 1)
                date_fin = datetime(datetime.now().year, 12, 31)
        else:
            date_debut = datetime(datetime.now().year, 1, 1)
            date_fin = datetime(datetime.now().year, 12, 31)

        # KPI spécifiques aux EBNL
        kpis = {
            # Ressources et emplois
            'total_dons': calculer_solde_compte_periode('756', date_debut, date_fin),
            'total_subventions': calculer_solde_compte_periode('74', date_debut, date_fin),
            'total_cotisations': calculer_solde_compte_periode('7561', date_debut, date_fin),
            'total_charges': calculer_solde_compte_periode('6', date_debut, date_fin),
            
            # Trésorerie
            'tresorerie_banque': calculer_solde_compte_periode('512', date_debut, date_fin),
            'tresorerie_caisse': calculer_solde_compte_periode('53', date_debut, date_fin),
            
            # Patrimoine
            'total_actif': calculer_solde_compte_periode('2', date_debut, date_fin),
            'fonds_associatifs': calculer_solde_compte_periode('10', date_debut, date_fin),
            
            # Activité
            'nb_ecritures': EcritureComptable.query.filter(
                EcritureComptable.date_ecriture >= date_debut,
                EcritureComptable.date_ecriture <= date_fin
            ).count(),
            
            # Ratios spécifiques EBNL
            'ratio_autonomie': 0,  # Calculé ci-dessous
            'ratio_liquidite': 0   # Calculé ci-dessous
        }
        
        # Calcul des ratios
        total_ressources = kpis['total_dons'] + kpis['total_subventions'] + kpis['total_cotisations']
        if total_ressources > 0:
            kpis['ratio_autonomie'] = round((kpis['total_dons'] / total_ressources) * 100, 2)
        
        if kpis['total_charges'] > 0:
            kpis['ratio_liquidite'] = round((kpis['tresorerie_banque'] + kpis['tresorerie_caisse']) / abs(kpis['total_charges']) * 100, 2)

        return jsonify({
            'success': True,
            'data': {
                'kpis': kpis,
                'periode': {
                    'debut': date_debut.strftime('%Y-%m-%d'),
                    'fin': date_fin.strftime('%Y-%m-%d')
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rapports_analytics_bp.route('/analyses/evolution-tresorerie', methods=['GET'])
def analyser_evolution_tresorerie():
    """Analyse de l'évolution de la trésorerie"""
    try:
        mois = request.args.get('mois', 12, type=int)
        
        # Évolution des comptes de trésorerie
        comptes_tresorerie = ['512', '53', '531']  # Banque, Caisse, CCP
        evolution = {}
        
        for compte in comptes_tresorerie:
            plan_compte = PlanComptable.query.filter_by(numero_compte=compte).first()
            if plan_compte:
                evolution[compte] = {
                    'libelle': plan_compte.libelle_compte,
                    'evolution': get_evolution_compte(compte, mois)
                }
        
        # Calcul de tendance
        total_actuel = sum([calculer_solde_compte_periode(c, datetime.now() - timedelta(days=30), datetime.now()) for c in comptes_tresorerie])
        total_precedent = sum([calculer_solde_compte_periode(c, datetime.now() - timedelta(days=60), datetime.now() - timedelta(days=30)) for c in comptes_tresorerie])
        
        tendance = 'stable'
        variation = 0
        if total_precedent != 0:
            variation = ((total_actuel - total_precedent) / abs(total_precedent)) * 100
            if variation > 5:
                tendance = 'hausse'
            elif variation < -5:
                tendance = 'baisse'

        return jsonify({
            'success': True,
            'data': {
                'evolution_comptes': evolution,
                'synthese': {
                    'total_actuel': round(total_actuel, 2),
                    'total_precedent': round(total_precedent, 2),
                    'variation_pct': round(variation, 2),
                    'tendance': tendance
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rapports_analytics_bp.route('/analyses/ressources-ebnl', methods=['GET'])
def analyser_ressources_ebnl():
    """Analyse des ressources spécifiques aux EBNL"""
    try:
        exercice_id = request.args.get('exercice_id', type=int)
        
        if exercice_id:
            exercice = ExerciceComptable.query.get(exercice_id)
            if exercice:
                date_debut = exercice.date_debut
                date_fin = exercice.date_fin
            else:
                date_debut = datetime(datetime.now().year, 1, 1)
                date_fin = datetime(datetime.now().year, 12, 31)
        else:
            date_debut = datetime(datetime.now().year, 1, 1)
            date_fin = datetime(datetime.now().year, 12, 31)

        # Analyse des différents types de ressources
        ressources = {
            'dons_manuels': {
                'compte': '7561',
                'montant': calculer_solde_compte_periode('7561', date_debut, date_fin),
                'libelle': 'Dons manuels'
            },
            'dons_nature': {
                'compte': '7562',
                'montant': calculer_solde_compte_periode('7562', date_debut, date_fin),
                'libelle': 'Dons en nature'
            },
            'subventions_exploitation': {
                'compte': '740',
                'montant': calculer_solde_compte_periode('740', date_debut, date_fin),
                'libelle': 'Subventions d\'exploitation'
            },
            'subventions_equipement': {
                'compte': '1311',
                'montant': calculer_solde_compte_periode('1311', date_debut, date_fin),
                'libelle': 'Subventions d\'équipement'
            },
            'cotisations': {
                'compte': '756',
                'montant': calculer_solde_compte_periode('756', date_debut, date_fin),
                'libelle': 'Cotisations'
            },
            'ventes_marchandises': {
                'compte': '707',
                'montant': calculer_solde_compte_periode('707', date_debut, date_fin),
                'libelle': 'Ventes de marchandises'
            }
        }
        
        # Calcul du total et des pourcentages
        total_ressources = sum([r['montant'] for r in ressources.values()])
        
        for ressource in ressources.values():
            if total_ressources > 0:
                ressource['pourcentage'] = round((ressource['montant'] / total_ressources) * 100, 2)
            else:
                ressource['pourcentage'] = 0

        # Analyse de diversification
        nb_sources_actives = sum([1 for r in ressources.values() if r['montant'] > 0])
        niveau_diversification = 'faible' if nb_sources_actives <= 2 else 'moyen' if nb_sources_actives <= 4 else 'élevé'

        return jsonify({
            'success': True,
            'data': {
                'ressources': ressources,
                'synthese': {
                    'total_ressources': round(total_ressources, 2),
                    'nb_sources_actives': nb_sources_actives,
                    'niveau_diversification': niveau_diversification,
                    'periode': {
                        'debut': date_debut.strftime('%Y-%m-%d'),
                        'fin': date_fin.strftime('%Y-%m-%d')
                    }
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rapports_analytics_bp.route('/analyses/repartition-charges', methods=['GET'])
def analyser_repartition_charges():
    """Analyse de la répartition des charges"""
    try:
        exercice_id = request.args.get('exercice_id', type=int)
        
        if exercice_id:
            exercice = ExerciceComptable.query.get(exercice_id)
            if exercice:
                date_debut = exercice.date_debut
                date_fin = exercice.date_fin
            else:
                date_debut = datetime(datetime.now().year, 1, 1)
                date_fin = datetime(datetime.now().year, 12, 31)
        else:
            date_debut = datetime(datetime.now().year, 1, 1)
            date_fin = datetime(datetime.now().year, 12, 31)

        # Analyse par classes de charges
        charges = {
            'charges_personnel': {
                'compte': '64',
                'montant': abs(calculer_solde_compte_periode('64', date_debut, date_fin)),
                'libelle': 'Charges de personnel'
            },
            'charges_fonctionnement': {
                'compte': '61',
                'montant': abs(calculer_solde_compte_periode('61', date_debut, date_fin)),
                'libelle': 'Services extérieurs'
            },
            'charges_autres_services': {
                'compte': '62',
                'montant': abs(calculer_solde_compte_periode('62', date_debut, date_fin)),
                'libelle': 'Autres services extérieurs'
            },
            'impots_taxes': {
                'compte': '63',
                'montant': abs(calculer_solde_compte_periode('63', date_debut, date_fin)),
                'libelle': 'Impôts et taxes'
            },
            'dotations_amortissements': {
                'compte': '681',
                'montant': abs(calculer_solde_compte_periode('681', date_debut, date_fin)),
                'libelle': 'Dotations aux amortissements'
            },
            'charges_financieres': {
                'compte': '66',
                'montant': abs(calculer_solde_compte_periode('66', date_debut, date_fin)),
                'libelle': 'Charges financières'
            }
        }
        
        # Calcul du total et des pourcentages
        total_charges = sum([c['montant'] for c in charges.values()])
        
        for charge in charges.values():
            if total_charges > 0:
                charge['pourcentage'] = round((charge['montant'] / total_charges) * 100, 2)
            else:
                charge['pourcentage'] = 0

        # Ratios d'efficacité pour EBNL
        total_ressources = calculer_solde_compte_periode('7', date_debut, date_fin)
        ratio_efficacite = 0
        if total_ressources > 0:
            ratio_efficacite = round((total_charges / total_ressources) * 100, 2)

        return jsonify({
            'success': True,
            'data': {
                'charges': charges,
                'synthese': {
                    'total_charges': round(total_charges, 2),
                    'ratio_efficacite': ratio_efficacite,
                    'periode': {
                        'debut': date_debut.strftime('%Y-%m-%d'),
                        'fin': date_fin.strftime('%Y-%m-%d')
                    }
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rapports_analytics_bp.route('/analyses/activite-mensuelle', methods=['GET'])
def analyser_activite_mensuelle():
    """Analyse de l'activité comptable mensuelle"""
    try:
        annee = request.args.get('annee', datetime.now().year, type=int)
        
        activite_mensuelle = []
        
        for mois in range(1, 13):
            date_debut = datetime(annee, mois, 1)
            # Dernier jour du mois
            dernier_jour = calendar.monthrange(annee, mois)[1]
            date_fin = datetime(annee, mois, dernier_jour)
            
            # Statistiques du mois
            nb_ecritures = EcritureComptable.query.filter(
                EcritureComptable.date_ecriture >= date_debut,
                EcritureComptable.date_ecriture <= date_fin
            ).count()
            
            # Montant total des mouvements
            total_mouvements = db.session.query(
                func.coalesce(func.sum(LigneEcriture.debit + LigneEcriture.credit), 0)
            ).join(EcritureComptable).filter(
                EcritureComptable.date_ecriture >= date_debut,
                EcritureComptable.date_ecriture <= date_fin
            ).scalar() or 0

            activite_mensuelle.append({
                'mois': f"{annee}-{mois:02d}",
                'nom_mois': calendar.month_name[mois],
                'nb_ecritures': nb_ecritures,
                'total_mouvements': float(total_mouvements)
            })
        
        # Calcul de statistiques annuelles
        total_ecritures_annee = sum([m['nb_ecritures'] for m in activite_mensuelle])
        total_mouvements_annee = sum([m['total_mouvements'] for m in activite_mensuelle])
        mois_le_plus_actif = max(activite_mensuelle, key=lambda x: x['nb_ecritures'])['nom_mois']

        return jsonify({
            'success': True,
            'data': {
                'activite_mensuelle': activite_mensuelle,
                'synthese_annuelle': {
                    'annee': annee,
                    'total_ecritures': total_ecritures_annee,
                    'total_mouvements': round(total_mouvements_annee, 2),
                    'moyenne_ecritures_mois': round(total_ecritures_annee / 12, 1),
                    'mois_plus_actif': mois_le_plus_actif
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rapports_analytics_bp.route('/analyses/comptes-top', methods=['GET'])
def analyser_comptes_top():
    """Analyse des comptes les plus mouvementés"""
    try:
        limite = request.args.get('limite', 10, type=int)
        exercice_id = request.args.get('exercice_id', type=int)
        
        if exercice_id:
            exercice = ExerciceComptable.query.get(exercice_id)
            if exercice:
                date_debut = exercice.date_debut
                date_fin = exercice.date_fin
            else:
                date_debut = datetime(datetime.now().year, 1, 1)
                date_fin = datetime(datetime.now().year, 12, 31)
        else:
            date_debut = datetime(datetime.now().year, 1, 1)
            date_fin = datetime(datetime.now().year, 12, 31)

        # Requête pour les comptes les plus mouvementés
        comptes_actifs = db.session.query(
            LigneEcriture.numero_compte,
            func.count(LigneEcriture.id).label('nb_mouvements'),
            func.sum(LigneEcriture.debit + LigneEcriture.credit).label('total_mouvement'),
            func.sum(LigneEcriture.debit).label('total_debit'),
            func.sum(LigneEcriture.credit).label('total_credit')
        ).join(EcritureComptable).filter(
            EcritureComptable.date_ecriture >= date_debut,
            EcritureComptable.date_ecriture <= date_fin
        ).group_by(
            LigneEcriture.numero_compte
        ).order_by(
            desc(func.count(LigneEcriture.id))
        ).limit(limite).all()

        # Enrichissement avec les libellés des comptes
        top_comptes = []
        for compte_stat in comptes_actifs:
            plan_compte = PlanComptable.query.filter_by(numero_compte=compte_stat.numero_compte).first()
            
            top_comptes.append({
                'numero_compte': compte_stat.numero_compte,
                'libelle_compte': plan_compte.libelle_compte if plan_compte else 'Compte inconnu',
                'nb_mouvements': compte_stat.nb_mouvements,
                'total_mouvement': float(compte_stat.total_mouvement or 0),
                'total_debit': float(compte_stat.total_debit or 0),
                'total_credit': float(compte_stat.total_credit or 0),
                'solde': float((compte_stat.total_debit or 0) - (compte_stat.total_credit or 0))
            })

        return jsonify({
            'success': True,
            'data': {
                'top_comptes': top_comptes,
                'periode': {
                    'debut': date_debut.strftime('%Y-%m-%d'),
                    'fin': date_fin.strftime('%Y-%m-%d')
                },
                'limite': limite
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rapports_analytics_bp.route('/previsions/budget', methods=['GET'])
def generer_previsions_budget():
    """Génère des prévisions budgétaires basées sur l'historique"""
    try:
        # Analyse sur les 12 derniers mois pour prédire
        annee_precedente = datetime.now().year - 1
        date_debut_historique = datetime(annee_precedente, 1, 1)
        date_fin_historique = datetime(annee_precedente, 12, 31)
        
        # Collecte des données historiques par classe
        classes_analyse = ['6', '7']  # Charges et produits
        previsions = {}
        
        for classe in classes_analyse:
            comptes_classe = PlanComptable.query.filter(
                PlanComptable.numero_compte.like(f'{classe}%')
            ).all()
            
            total_historique = 0
            for compte in comptes_classe:
                solde = calculer_solde_compte_periode(
                    compte.numero_compte, 
                    date_debut_historique, 
                    date_fin_historique
                )
                total_historique += abs(solde)
            
            # Prévision simple : augmentation de 3% par rapport à l'année précédente
            prevision = total_historique * 1.03
            
            previsions[classe] = {
                'classe': classe,
                'libelle': 'Charges' if classe == '6' else 'Produits',
                'historique_n1': round(total_historique, 2),
                'prevision_n': round(prevision, 2),
                'variation_pct': 3.0
            }
        
        # Calcul du résultat prévisionnel
        resultat_previsionnel = previsions.get('7', {}).get('prevision_n', 0) - previsions.get('6', {}).get('prevision_n', 0)
        
        return jsonify({
            'success': True,
            'data': {
                'previsions_par_classe': previsions,
                'synthese': {
                    'resultat_previsionnel': round(resultat_previsionnel, 2),
                    'annee_prevision': datetime.now().year,
                    'annee_reference': annee_precedente,
                    'methode': 'Trend historique +3%'
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rapports_analytics_bp.route('/export/rapport-complet', methods=['GET'])
def exporter_rapport_complet():
    """Exporte un rapport d'analyse complet"""
    try:
        format_export = request.args.get('format', 'json').lower()
        exercice_id = request.args.get('exercice_id', type=int)
        
        # Collecte de toutes les analyses
        rapport_complet = {
            'meta': {
                'date_generation': datetime.now().isoformat(),
                'exercice_id': exercice_id,
                'format': format_export
            },
            'kpi': {},
            'evolution_tresorerie': {},
            'ressources_ebnl': {},
            'repartition_charges': {},
            'activite_mensuelle': {},
            'comptes_top': {},
            'previsions': {}
        }
        
        # Note: Pour une implémentation complète, il faudrait appeler chaque fonction d'analyse
        # et compiler les résultats. Ici, on retourne la structure pour démonstration.
        
        if format_export == 'csv':
            # Conversion en CSV (simplifié)
            return jsonify({
                'success': True,
                'message': 'Export CSV pas encore implémenté',
                'data': rapport_complet
            })
        
        return jsonify({
            'success': True,
            'data': rapport_complet
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Endpoint de synthèse
@rapports_analytics_bp.route('/synthese', methods=['GET'])
def get_synthese_rapports():
    """Retourne une synthèse de tous les rapports disponibles"""
    rapports_disponibles = [
        {
            'endpoint': '/api/v1/dashboard/kpi',
            'nom': 'Tableau de bord KPI EBNL',
            'description': 'Indicateurs clés pour associations (dons, subventions, trésorerie)',
            'parametres': ['exercice_id']
        },
        {
            'endpoint': '/api/v1/analyses/evolution-tresorerie',
            'nom': 'Évolution de la trésorerie',
            'description': 'Analyse des mouvements de trésorerie sur plusieurs mois',
            'parametres': ['mois']
        },
        {
            'endpoint': '/api/v1/analyses/ressources-ebnl',
            'nom': 'Analyse des ressources EBNL',
            'description': 'Répartition et diversification des ressources associatives',
            'parametres': ['exercice_id']
        },
        {
            'endpoint': '/api/v1/analyses/repartition-charges',
            'nom': 'Répartition des charges',
            'description': 'Analyse détaillée des postes de charges',
            'parametres': ['exercice_id']
        },
        {
            'endpoint': '/api/v1/analyses/activite-mensuelle',
            'nom': 'Activité comptable mensuelle',
            'description': 'Suivi de l\'activité comptable mois par mois',
            'parametres': ['annee']
        },
        {
            'endpoint': '/api/v1/analyses/comptes-top',
            'nom': 'Comptes les plus actifs',
            'description': 'Classement des comptes par nombre de mouvements',
            'parametres': ['limite', 'exercice_id']
        },
        {
            'endpoint': '/api/v1/previsions/budget',
            'nom': 'Prévisions budgétaires',
            'description': 'Prévisions basées sur l\'historique comptable',
            'parametres': []
        }
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'rapports_disponibles': rapports_disponibles,
            'total_rapports': len(rapports_disponibles)
        }
    })