#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API États Financiers SYCEBNL
============================

Ce module gère la génération des états financiers conformes au référentiel SYCEBNL :
- Bilan comptable
- Compte de résultat (compte d'emploi et de ressources)
- Tableau de flux de trésorerie
- États spécifiques EBNL

Auteur: ComptaEBNL-IA
Date: 2025
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from models import db, PlanComptable, EcritureComptable, LigneEcriture, ExerciceComptable

# Création du blueprint
etats_financiers_bp = Blueprint('etats_financiers', __name__)

# === STRUCTURE BILAN SYCEBNL ===

STRUCTURE_BILAN_SYCEBNL = {
    "ACTIF": {
        "ACTIF_IMMOBILISE": {
            "classes": [2],
            "comptes": {
                "20": "Immobilisations destinées à la vente",
                "21": "Immobilisations incorporelles", 
                "22": "Terrains",
                "23": "Bâtiments, installations techniques et agencements",
                "24": "Matériels",
                "25": "Avances et acomptes versés sur immobilisations",
                "26": "Participations et créances rattachées",
                "27": "Autres immobilisations financières",
                "28": "Amortissements des immobilisations"
            }
        },
        "ACTIF_CIRCULANT": {
            "classes": [3, 4, 5],
            "comptes": {
                "31": "Matières premières et fournitures",
                "32": "Autres approvisionnements", 
                "33": "En-cours de production de biens",
                "34": "En-cours de production de services",
                "35": "Stocks de produits",
                "37": "Stocks de marchandises",
                "39": "Dépréciations des stocks",
                "40": "Fournisseurs et comptes rattachés",
                "41": "Clients et comptes rattachés", 
                "42": "Personnel",
                "43": "Organismes sociaux",
                "44": "État et collectivités publiques",
                "45": "Organismes internationaux",
                "46": "Associés et groupe",
                "47": "Autres tiers",
                "48": "Charges et produits constatés d'avance",
                "49": "Dépréciations des comptes de tiers",
                "50": "Valeurs mobilières de placement",
                "51": "Valeurs à encaisser",
                "52": "Banques, établissements financiers et assimilés",
                "53": "Établissements financiers et assimilés",
                "57": "Caisse",
                "58": "Virements internes",
                "59": "Dépréciations des comptes financiers"
            }
        }
    },
    "PASSIF": {
        "RESSOURCES_DURABLES": {
            "classes": [1],
            "comptes": {
                "10": "Dotation",
                "11": "Réserves",
                "12": "Report à nouveau", 
                "13": "Résultat net de l'exercice",
                "14": "Subventions d'investissement",
                "15": "Provisions réglementées et fonds assimilés",
                "16": "Fonds affectés",
                "17": "Fonds reportés",
                "18": "Emprunts et dettes assimilées",
                "19": "Provisions pour risques et charges"
            }
        },
        "PASSIF_CIRCULANT": {
            "classes": [4],
            "comptes_passif": {
                "40": "Fournisseurs et comptes rattachés",
                "42": "Personnel",
                "43": "Organismes sociaux", 
                "44": "État et collectivités publiques",
                "45": "Organismes internationaux",
                "46": "Associés et groupe",
                "47": "Autres tiers",
                "48": "Charges et produits constatés d'avance"
            }
        }
    }
}

# === STRUCTURE COMPTE DE RÉSULTAT SYCEBNL ===

STRUCTURE_COMPTE_RESULTAT_SYCEBNL = {
    "EMPLOIS": {
        "CHARGES_ACTIVITES_ORDINAIRES": {
            "classe": 6,
            "comptes": {
                "60": "Achats et variations de stocks",
                "61": "Transports",
                "62": "Services extérieurs A", 
                "63": "Services extérieurs B",
                "64": "Impôts et taxes",
                "65": "Autres charges",
                "66": "Charges de personnel",
                "67": "Frais financiers et charges assimilées",
                "68": "Dotations aux amortissements",
                "69": "Dotations aux provisions"
            }
        },
        "AUTRES_CHARGES": {
            "classe": 8,
            "comptes": {
                "81": "Valeurs comptables des cessions d'immobilisations",
                "82": "Charges exceptionnelles sur opérations de gestion",
                "83": "Charges exceptionnelles sur opérations en capital",
                "84": "Participation des salariés aux fruits de l'expansion",
                "85": "Impôts sur les bénéfices",
                "86": "Emplois des contributions volontaires en nature",
                "87": "Charges exceptionnelles"
            }
        }
    },
    "RESSOURCES": {
        "PRODUITS_ACTIVITES_ORDINAIRES": {
            "classe": 7,
            "comptes": {
                "70": "Ventes de produits fabriqués, prestations de services",
                "71": "Production stockée",
                "72": "Production immobilisée", 
                "73": "Produits accessoires",
                "74": "Subventions d'exploitation",
                "75": "Autres produits",
                "76": "Produits financiers",
                "77": "Revenus des immobilisations",
                "78": "Reprises de provisions",
                "79": "Transferts de charges"
            }
        },
        "AUTRES_PRODUITS": {
            "classe": 8,
            "comptes": {
                "80": "Produits des cessions d'immobilisations",
                "82": "Produits exceptionnels sur opérations de gestion",
                "83": "Produits exceptionnels sur opérations en capital", 
                "86": "Contributions volontaires en nature",
                "87": "Produits exceptionnels"
            }
        }
    }
}

def calculer_solde_compte(numero_compte, date_debut=None, date_fin=None, exercice_id=None):
    """Calcule le solde d'un compte pour une période donnée"""
    try:
        query = db.session.query(
            func.sum(LigneEcriture.debit).label('total_debit'),
            func.sum(LigneEcriture.credit).label('total_credit')
        ).join(EcritureComptable).join(PlanComptable)
        
        # Filtrer par numéro de compte (avec wildcard pour les comptes parents)
        if len(numero_compte) <= 2:
            # Compte de classe ou principal
            query = query.filter(PlanComptable.numero_compte.like(f"{numero_compte}%"))
        else:
            # Compte spécifique
            query = query.filter(PlanComptable.numero_compte == numero_compte)
        
        # Filtres temporels
        if exercice_id:
            query = query.filter(EcritureComptable.exercice_id == exercice_id)
        else:
            if date_debut:
                query = query.filter(EcritureComptable.date_ecriture >= date_debut)
            if date_fin:
                query = query.filter(EcritureComptable.date_ecriture <= date_fin)
        
        # Seulement les écritures validées
        query = query.filter(EcritureComptable.statut == 'valide')
        
        result = query.first()
        
        debit = result.total_debit or Decimal('0')
        credit = result.total_credit or Decimal('0')
        solde = debit - credit
        
        return {
            'debit': float(debit),
            'credit': float(credit), 
            'solde': float(solde)
        }
        
    except Exception as e:
        return {'debit': 0, 'credit': 0, 'solde': 0, 'erreur': str(e)}

@etats_financiers_bp.route('/bilan', methods=['GET'])
def generer_bilan():
    """Génère le bilan comptable SYCEBNL"""
    try:
        # Paramètres
        date_fin = request.args.get('date_fin', datetime.now().strftime('%Y-%m-%d'))
        exercice_id = request.args.get('exercice_id', type=int)
        format_output = request.args.get('format', 'json')  # json, html, pdf
        
        print(f"🏦 Génération du bilan au {date_fin}")
        
        bilan = {
            "meta": {
                "titre": "BILAN COMPTABLE SYCEBNL",
                "date_fin": date_fin,
                "exercice_id": exercice_id,
                "date_generation": datetime.now().isoformat(),
                "referentiel": "SYCEBNL"
            },
            "actif": {},
            "passif": {},
            "equilibre": {}
        }
        
        total_actif = Decimal('0')
        total_passif = Decimal('0')
        
        # === CALCUL ACTIF ===
        for section_nom, section_data in STRUCTURE_BILAN_SYCEBNL["ACTIF"].items():
            section_total = Decimal('0')
            comptes_section = {}
            
            for compte_num, compte_libelle in section_data["comptes"].items():
                solde_data = calculer_solde_compte(compte_num, date_fin=date_fin, exercice_id=exercice_id)
                solde = Decimal(str(solde_data['solde']))
                
                # Pour l'actif, on prend les soldes débiteurs
                if solde > 0:
                    comptes_section[compte_num] = {
                        'libelle': compte_libelle,
                        'solde': float(solde),
                        'debit': solde_data['debit'],
                        'credit': solde_data['credit']
                    }
                    section_total += solde
            
            if comptes_section:
                bilan["actif"][section_nom] = {
                    'comptes': comptes_section,
                    'total': float(section_total)
                }
                total_actif += section_total
        
        # === CALCUL PASSIF ===
        for section_nom, section_data in STRUCTURE_BILAN_SYCEBNL["PASSIF"].items():
            section_total = Decimal('0')
            comptes_section = {}
            
            comptes_key = "comptes_passif" if "comptes_passif" in section_data else "comptes"
            
            for compte_num, compte_libelle in section_data[comptes_key].items():
                solde_data = calculer_solde_compte(compte_num, date_fin=date_fin, exercice_id=exercice_id)
                solde = Decimal(str(solde_data['solde']))
                
                # Pour le passif, on prend les soldes créditeurs (donc négatifs)
                if solde < 0:
                    comptes_section[compte_num] = {
                        'libelle': compte_libelle,
                        'solde': float(abs(solde)),  # Valeur absolue pour affichage
                        'debit': solde_data['debit'],
                        'credit': solde_data['credit']
                    }
                    section_total += abs(solde)
            
            if comptes_section:
                bilan["passif"][section_nom] = {
                    'comptes': comptes_section,
                    'total': float(section_total)
                }
                total_passif += section_total
        
        # === ÉQUILIBRE ===
        bilan["equilibre"] = {
            'total_actif': float(total_actif),
            'total_passif': float(total_passif),
            'difference': float(total_actif - total_passif),
            'equilibre': abs(float(total_actif - total_passif)) < 0.01
        }
        
        print(f"✅ Bilan généré - Actif: {total_actif}€, Passif: {total_passif}€")
        
        return jsonify({
            'success': True,
            'data': bilan,
            'message': f'Bilan généré avec succès au {date_fin}'
        })
        
    except Exception as e:
        print(f"❌ Erreur génération bilan: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération du bilan'
        }), 500

@etats_financiers_bp.route('/compte-resultat', methods=['GET'])
def generer_compte_resultat():
    """Génère le compte de résultat (compte d'emploi et de ressources) SYCEBNL"""
    try:
        # Paramètres
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin', datetime.now().strftime('%Y-%m-%d'))
        exercice_id = request.args.get('exercice_id', type=int)
        
        # Si pas de date de début, prendre le 1er janvier de l'année de la date de fin
        if not date_debut:
            annee = datetime.strptime(date_fin, '%Y-%m-%d').year
            date_debut = f"{annee}-01-01"
        
        print(f"📊 Génération compte de résultat du {date_debut} au {date_fin}")
        
        compte_resultat = {
            "meta": {
                "titre": "COMPTE D'EMPLOI ET DE RESSOURCES SYCEBNL",
                "periode": f"Du {date_debut} au {date_fin}",
                "exercice_id": exercice_id,
                "date_generation": datetime.now().isoformat(),
                "referentiel": "SYCEBNL"
            },
            "emplois": {},
            "ressources": {},
            "resultat": {}
        }
        
        total_emplois = Decimal('0')
        total_ressources = Decimal('0')
        
        # === CALCUL EMPLOIS (CHARGES) ===
        for section_nom, section_data in STRUCTURE_COMPTE_RESULTAT_SYCEBNL["EMPLOIS"].items():
            section_total = Decimal('0')
            comptes_section = {}
            
            for compte_num, compte_libelle in section_data["comptes"].items():
                solde_data = calculer_solde_compte(
                    compte_num, 
                    date_debut=date_debut, 
                    date_fin=date_fin, 
                    exercice_id=exercice_id
                )
                solde = Decimal(str(solde_data['solde']))
                
                # Pour les charges, on prend les soldes débiteurs
                if solde > 0:
                    comptes_section[compte_num] = {
                        'libelle': compte_libelle,
                        'montant': float(solde),
                        'debit': solde_data['debit'],
                        'credit': solde_data['credit']
                    }
                    section_total += solde
            
            if comptes_section:
                compte_resultat["emplois"][section_nom] = {
                    'comptes': comptes_section,
                    'total': float(section_total)
                }
                total_emplois += section_total
        
        # === CALCUL RESSOURCES (PRODUITS) ===
        for section_nom, section_data in STRUCTURE_COMPTE_RESULTAT_SYCEBNL["RESSOURCES"].items():
            section_total = Decimal('0')
            comptes_section = {}
            
            for compte_num, compte_libelle in section_data["comptes"].items():
                solde_data = calculer_solde_compte(
                    compte_num, 
                    date_debut=date_debut, 
                    date_fin=date_fin, 
                    exercice_id=exercice_id
                )
                solde = Decimal(str(solde_data['solde']))
                
                # Pour les produits, on prend les soldes créditeurs (donc négatifs)
                if solde < 0:
                    comptes_section[compte_num] = {
                        'libelle': compte_libelle,
                        'montant': float(abs(solde)),  # Valeur absolue pour affichage
                        'debit': solde_data['debit'],
                        'credit': solde_data['credit']
                    }
                    section_total += abs(solde)
            
            if comptes_section:
                compte_resultat["ressources"][section_nom] = {
                    'comptes': comptes_section,
                    'total': float(section_total)
                }
                total_ressources += section_total
        
        # === RÉSULTAT ===
        resultat_net = total_ressources - total_emplois
        
        compte_resultat["resultat"] = {
            'total_emplois': float(total_emplois),
            'total_ressources': float(total_ressources),
            'resultat_net': float(resultat_net),
            'type': 'excedent' if resultat_net > 0 else 'deficit' if resultat_net < 0 else 'equilibre'
        }
        
        print(f"✅ Compte de résultat généré - Résultat: {resultat_net}€")
        
        return jsonify({
            'success': True,
            'data': compte_resultat,
            'message': f'Compte de résultat généré pour la période {date_debut} - {date_fin}'
        })
        
    except Exception as e:
        print(f"❌ Erreur génération compte de résultat: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération du compte de résultat'
        }), 500

@etats_financiers_bp.route('/flux-tresorerie', methods=['GET'])
def generer_flux_tresorerie():
    """Génère le tableau de flux de trésorerie SYCEBNL"""
    try:
        # Paramètres
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin', datetime.now().strftime('%Y-%m-%d'))
        exercice_id = request.args.get('exercice_id', type=int)
        
        if not date_debut:
            annee = datetime.strptime(date_fin, '%Y-%m-%d').year
            date_debut = f"{annee}-01-01"
        
        print(f"💰 Génération flux de trésorerie du {date_debut} au {date_fin}")
        
        # Comptes de trésorerie SYCEBNL
        comptes_tresorerie = ['51', '52', '53', '57', '58']  # Classes 5
        
        flux_tresorerie = {
            "meta": {
                "titre": "TABLEAU DE FLUX DE TRÉSORERIE SYCEBNL",
                "periode": f"Du {date_debut} au {date_fin}",
                "exercice_id": exercice_id,
                "date_generation": datetime.now().isoformat()
            },
            "tresorerie_debut": {},
            "flux_activites": {},
            "tresorerie_fin": {},
            "variation": {}
        }
        
        # Calcul de la trésorerie de début (date_debut - 1 jour)
        date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
        date_avant_debut = (date_debut_obj - timedelta(days=1)).strftime('%Y-%m-%d')
        
        tresorerie_debut = Decimal('0')
        tresorerie_fin = Decimal('0')
        
        for compte in comptes_tresorerie:
            # Trésorerie de début
            solde_debut = calculer_solde_compte(compte, date_fin=date_avant_debut, exercice_id=exercice_id)
            tresorerie_debut += Decimal(str(solde_debut['solde']))
            
            # Trésorerie de fin
            solde_fin = calculer_solde_compte(compte, date_fin=date_fin, exercice_id=exercice_id)
            tresorerie_fin += Decimal(str(solde_fin['solde']))
            
            flux_tresorerie["tresorerie_debut"][compte] = {
                'solde': float(solde_debut['solde']),
                'debit': solde_debut['debit'],
                'credit': solde_debut['credit']
            }
            
            flux_tresorerie["tresorerie_fin"][compte] = {
                'solde': float(solde_fin['solde']),
                'debit': solde_fin['debit'],
                'credit': solde_fin['credit']
            }
        
        # Variation de trésorerie
        variation = tresorerie_fin - tresorerie_debut
        
        flux_tresorerie["variation"] = {
            'tresorerie_debut': float(tresorerie_debut),
            'tresorerie_fin': float(tresorerie_fin),
            'variation_nette': float(variation),
            'type': 'augmentation' if variation > 0 else 'diminution' if variation < 0 else 'stable'
        }
        
        print(f"✅ Flux de trésorerie généré - Variation: {variation}€")
        
        return jsonify({
            'success': True,
            'data': flux_tresorerie,
            'message': f'Flux de trésorerie généré pour la période {date_debut} - {date_fin}'
        })
        
    except Exception as e:
        print(f"❌ Erreur génération flux de trésorerie: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération du flux de trésorerie'
        }), 500

@etats_financiers_bp.route('/etats-ebnl', methods=['GET'])
def generer_etats_ebnl():
    """Génère les états spécifiques aux EBNL"""
    try:
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin', datetime.now().strftime('%Y-%m-%d'))
        exercice_id = request.args.get('exercice_id', type=int)
        
        if not date_debut:
            annee = datetime.strptime(date_fin, '%Y-%m-%d').year
            date_debut = f"{annee}-01-01"
        
        print(f"🏛️ Génération états EBNL du {date_debut} au {date_fin}")
        
        etats_ebnl = {
            "meta": {
                "titre": "ÉTATS SPÉCIFIQUES EBNL",
                "periode": f"Du {date_debut} au {date_fin}",
                "exercice_id": exercice_id,
                "date_generation": datetime.now().isoformat()
            },
            "fonds_affectes": {},
            "contributions_volontaires": {},
            "subventions": {},
            "adherents": {}
        }
        
        # === FONDS AFFECTÉS (Classe 16) ===
        comptes_fonds = ['16', '160', '161', '162', '163', '164', '165', '166', '167', '168']
        fonds_total = Decimal('0')
        
        for compte in comptes_fonds:
            solde_data = calculer_solde_compte(compte, date_debut=date_debut, date_fin=date_fin, exercice_id=exercice_id)
            solde = Decimal(str(solde_data['solde']))
            
            if abs(solde) > 0:
                etats_ebnl["fonds_affectes"][compte] = {
                    'montant': float(abs(solde)),
                    'debit': solde_data['debit'],
                    'credit': solde_data['credit']
                }
                fonds_total += abs(solde)
        
        etats_ebnl["fonds_affectes"]["total"] = float(fonds_total)
        
        # === CONTRIBUTIONS VOLONTAIRES (Classe 86) ===
        comptes_contrib = ['86', '860', '861', '862', '863']
        contrib_total = Decimal('0')
        
        for compte in comptes_contrib:
            solde_data = calculer_solde_compte(compte, date_debut=date_debut, date_fin=date_fin, exercice_id=exercice_id)
            solde = Decimal(str(solde_data['solde']))
            
            if abs(solde) > 0:
                etats_ebnl["contributions_volontaires"][compte] = {
                    'montant': float(abs(solde)),
                    'debit': solde_data['debit'],
                    'credit': solde_data['credit']
                }
                contrib_total += abs(solde)
        
        etats_ebnl["contributions_volontaires"]["total"] = float(contrib_total)
        
        # === SUBVENTIONS (Comptes 74, 14) ===
        comptes_subv = ['74', '740', '741', '742', '743', '744', '14', '140', '141', '142']
        subv_total = Decimal('0')
        
        for compte in comptes_subv:
            solde_data = calculer_solde_compte(compte, date_debut=date_debut, date_fin=date_fin, exercice_id=exercice_id)
            solde = Decimal(str(solde_data['solde']))
            
            if abs(solde) > 0:
                etats_ebnl["subventions"][compte] = {
                    'montant': float(abs(solde)),
                    'debit': solde_data['debit'],
                    'credit': solde_data['credit']
                }
                subv_total += abs(solde)
        
        etats_ebnl["subventions"]["total"] = float(subv_total)
        
        print(f"✅ États EBNL générés")
        
        return jsonify({
            'success': True,
            'data': etats_ebnl,
            'message': f'États EBNL générés pour la période {date_debut} - {date_fin}'
        })
        
    except Exception as e:
        print(f"❌ Erreur génération états EBNL: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération des états EBNL'
        }), 500

@etats_financiers_bp.route('/synthese', methods=['GET'])
def synthese_etats_financiers():
    """Génère une synthèse de tous les états financiers"""
    try:
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin', datetime.now().strftime('%Y-%m-%d'))
        exercice_id = request.args.get('exercice_id', type=int)
        
        if not date_debut:
            annee = datetime.strptime(date_fin, '%Y-%m-%d').year
            date_debut = f"{annee}-01-01"
        
        print(f"📋 Génération synthèse états financiers du {date_debut} au {date_fin}")
        
        synthese = {
            "meta": {
                "titre": "SYNTHÈSE DES ÉTATS FINANCIERS SYCEBNL",
                "periode": f"Du {date_debut} au {date_fin}",
                "exercice_id": exercice_id,
                "date_generation": datetime.now().isoformat()
            },
            "indicateurs_cles": {},
            "ratios": {},
            "evolution": {}
        }
        
        # Calculs des indicateurs clés
        total_actif = Decimal('0')
        total_passif = Decimal('0')
        total_charges = Decimal('0')
        total_produits = Decimal('0')
        tresorerie = Decimal('0')
        
        # Actif total (classe 2, 3, 4, 5)
        for classe in [2, 3, 4, 5]:
            solde_data = calculer_solde_compte(str(classe), date_fin=date_fin, exercice_id=exercice_id)
            if solde_data['solde'] > 0:
                total_actif += Decimal(str(solde_data['solde']))
        
        # Charges (classe 6)
        solde_charges = calculer_solde_compte('6', date_debut=date_debut, date_fin=date_fin, exercice_id=exercice_id)
        if solde_charges['solde'] > 0:
            total_charges = Decimal(str(solde_charges['solde']))
        
        # Produits (classe 7)
        solde_produits = calculer_solde_compte('7', date_debut=date_debut, date_fin=date_fin, exercice_id=exercice_id)
        if solde_produits['solde'] < 0:
            total_produits = abs(Decimal(str(solde_produits['solde'])))
        
        # Trésorerie (comptes 5)
        solde_tresorerie = calculer_solde_compte('5', date_fin=date_fin, exercice_id=exercice_id)
        tresorerie = Decimal(str(solde_tresorerie['solde']))
        
        resultat_net = total_produits - total_charges
        
        synthese["indicateurs_cles"] = {
            'total_actif': float(total_actif),
            'total_charges': float(total_charges),
            'total_produits': float(total_produits),
            'resultat_net': float(resultat_net),
            'tresorerie': float(tresorerie)
        }
        
        # Ratios financiers
        synthese["ratios"] = {
            'taux_resultat': float((resultat_net / total_produits * 100) if total_produits > 0 else 0),
            'ratio_tresorerie': float((tresorerie / total_actif * 100) if total_actif > 0 else 0),
            'autonomie_financiere': float((abs(solde_produits['solde']) / total_charges * 100) if total_charges > 0 else 0)
        }
        
        print(f"✅ Synthèse générée - Résultat: {resultat_net}€")
        
        return jsonify({
            'success': True,
            'data': synthese,
            'message': f'Synthèse des états financiers générée pour la période {date_debut} - {date_fin}'
        })
        
    except Exception as e:
        print(f"❌ Erreur génération synthèse: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération de la synthèse'
        }), 500