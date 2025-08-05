#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Comptabilité - Écritures et Journaux
ComptaEBNL-IA - Gestion comptable pour entités à but non lucratif
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, date
from decimal import Decimal
from models import (
    db, 
    EcritureComptable, 
    LigneEcriture, 
    PlanComptable,
    JournalComptable
)

comptabilite_bp = Blueprint('comptabilite', __name__)

@comptabilite_bp.route('/ecritures', methods=['GET'])
def get_ecritures():
    """
    Récupère les écritures comptables
    
    Query Parameters:
    - date_debut: Date de début (YYYY-MM-DD)
    - date_fin: Date de fin (YYYY-MM-DD)
    - journal: Code du journal
    - compte: Numéro de compte
    - limit: Nombre max de résultats (défaut: 50)
    - page: Page (défaut: 1)
    """
    try:
        # Paramètres de requête
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        journal = request.args.get('journal')
        compte = request.args.get('compte')
        limit = request.args.get('limit', 50, type=int)
        page = request.args.get('page', 1, type=int)
        
        # Construction de la requête
        query = EcritureComptable.query
        
        # Filtres par date
        if date_debut:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            query = query.filter(EcritureComptable.date_ecriture >= date_debut_obj)
            
        if date_fin:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            query = query.filter(EcritureComptable.date_ecriture <= date_fin_obj)
            
        # Filtre par journal
        if journal:
            query = query.filter(EcritureComptable.journal == journal)
            
        # Filtre par compte (via les lignes d'écriture)
        if compte:
            query = query.join(LigneEcriture).filter(LigneEcriture.numero_compte == compte)
        
        # Pagination
        offset = (page - 1) * limit
        ecritures = query.order_by(EcritureComptable.date_ecriture.desc())\
                        .offset(offset)\
                        .limit(limit)\
                        .all()
        
        total = query.count()
        
        # Formatage de la réponse
        result = {
            'success': True,
            'data': [ecriture.to_dict() for ecriture in ecritures],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            },
            'filters': {
                'date_debut': date_debut,
                'date_fin': date_fin,
                'journal': journal,
                'compte': compte
            }
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Format de date invalide',
            'message': 'Utilisez le format YYYY-MM-DD pour les dates'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des écritures'
        }), 500

@comptabilite_bp.route('/ecritures', methods=['POST'])
def create_ecriture():
    """
    Crée une nouvelle écriture comptable
    
    Body JSON:
    {
        "date_ecriture": "2024-01-15",
        "libelle": "Achat fournitures bureau",
        "journal": "ACH",
        "piece_justificative": "FAC-2024-001",
        "lignes": [
            {
                "numero_compte": "6064",
                "libelle": "Fournitures de bureau",
                "debit": 120.50,
                "credit": 0
            },
            {
                "numero_compte": "401",
                "libelle": "Fournisseur ABC",
                "debit": 0,
                "credit": 120.50
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Données JSON manquantes',
                'message': 'Le body de la requête doit contenir du JSON'
            }), 400
        
        # Validation des champs obligatoires
        required_fields = ['date_ecriture', 'libelle', 'lignes']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Champ obligatoire manquant: {field}',
                    'message': f'Le champ "{field}" est requis'
                }), 400
        
        # Validation des lignes
        lignes = data.get('lignes', [])
        if len(lignes) < 2:
            return jsonify({
                'success': False,
                'error': 'Nombre de lignes insuffisant',
                'message': 'Une écriture doit avoir au moins 2 lignes'
            }), 400
        
        # Validation de l'équilibre débit/crédit
        total_debit = sum(Decimal(str(ligne.get('debit', 0))) for ligne in lignes)
        total_credit = sum(Decimal(str(ligne.get('credit', 0))) for ligne in lignes)
        
        if total_debit != total_credit:
            return jsonify({
                'success': False,
                'error': 'Écriture non équilibrée',
                'message': f'Total débit ({total_debit}) ≠ Total crédit ({total_credit})'
            }), 400
        
        # Validation des comptes
        for i, ligne in enumerate(lignes):
            numero_compte = ligne.get('numero_compte')
            if not numero_compte:
                return jsonify({
                    'success': False,
                    'error': f'Numéro de compte manquant ligne {i+1}',
                    'message': 'Chaque ligne doit avoir un numéro de compte'
                }), 400
                
            compte = PlanComptable.query.filter_by(numero_compte=numero_compte).first()
            if not compte:
                return jsonify({
                    'success': False,
                    'error': f'Compte inexistant: {numero_compte}',
                    'message': f'Le compte {numero_compte} n\'existe pas dans le plan SYCEBNL'
                }), 400
        
        # Créer l'écriture
        ecriture = EcritureComptable(
            date_ecriture=datetime.strptime(data['date_ecriture'], '%Y-%m-%d').date(),
            libelle=data['libelle'],
            journal=data.get('journal', 'OD'),  # Journal "Opérations Diverses" par défaut
            piece_justificative=data.get('piece_justificative'),
            montant_total=total_debit,
            statut='brouillard'  # Par défaut en brouillard
        )
        
        db.session.add(ecriture)
        db.session.flush()  # Pour obtenir l'ID de l'écriture
        
        # Créer les lignes d'écriture
        for ligne_data in lignes:
            ligne = LigneEcriture(
                ecriture_id=ecriture.id,
                numero_compte=ligne_data['numero_compte'],
                libelle=ligne_data.get('libelle', ''),
                debit=Decimal(str(ligne_data.get('debit', 0))),
                credit=Decimal(str(ligne_data.get('credit', 0)))
            )
            db.session.add(ligne)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': ecriture.to_dict(),
            'message': f'Écriture créée avec succès (ID: {ecriture.id})'
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Format de date invalide',
            'message': 'Utilisez le format YYYY-MM-DD pour la date'
        }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la création de l\'écriture'
        }), 500

@comptabilite_bp.route('/ecritures/<int:ecriture_id>', methods=['GET'])
def get_ecriture_detail(ecriture_id):
    """Récupère le détail d'une écriture comptable"""
    try:
        ecriture = EcritureComptable.query.get(ecriture_id)
        
        if not ecriture:
            return jsonify({
                'success': False,
                'error': 'Écriture non trouvée',
                'message': f'L\'écriture {ecriture_id} n\'existe pas'
            }), 404
        
        return jsonify({
            'success': True,
            'data': ecriture.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Erreur lors de la récupération de l\'écriture {ecriture_id}'
        }), 500

@comptabilite_bp.route('/ecritures/<int:ecriture_id>/valider', methods=['POST'])
def valider_ecriture(ecriture_id):
    """Valide une écriture (passage de brouillard à validé)"""
    try:
        ecriture = EcritureComptable.query.get(ecriture_id)
        
        if not ecriture:
            return jsonify({
                'success': False,
                'error': 'Écriture non trouvée',
                'message': f'L\'écriture {ecriture_id} n\'existe pas'
            }), 404
        
        if ecriture.statut == 'valide':
            return jsonify({
                'success': False,
                'error': 'Écriture déjà validée',
                'message': 'Cette écriture est déjà validée'
            }), 400
        
        # Vérifier l'équilibre
        total_debit = sum(ligne.debit for ligne in ecriture.lignes)
        total_credit = sum(ligne.credit for ligne in ecriture.lignes)
        
        if total_debit != total_credit:
            return jsonify({
                'success': False,
                'error': 'Écriture non équilibrée',
                'message': 'Impossible de valider une écriture non équilibrée'
            }), 400
        
        # Valider
        ecriture.statut = 'valide'
        ecriture.date_validation = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': ecriture.to_dict(),
            'message': 'Écriture validée avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la validation'
        }), 500

@comptabilite_bp.route('/balance', methods=['GET'])
def get_balance():
    """
    Génère la balance comptable
    
    Query Parameters:
    - date_debut: Date de début (YYYY-MM-DD)
    - date_fin: Date de fin (YYYY-MM-DD)
    - classe: Filtrer par classe (1-9)
    - niveau: Niveau de détail (1-3)
    """
    try:
        # Paramètres
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin') 
        classe = request.args.get('classe', type=int)
        niveau = request.args.get('niveau', 3, type=int)  # Niveau 3 par défaut (le plus détaillé)
        
        # Construction de la requête pour les lignes d'écriture validées
        query = db.session.query(
            LigneEcriture.numero_compte,
            PlanComptable.libelle_compte,
            PlanComptable.classe,
            PlanComptable.niveau,
            db.func.sum(LigneEcriture.debit).label('total_debit'),
            db.func.sum(LigneEcriture.credit).label('total_credit')
        ).join(
            EcritureComptable, LigneEcriture.ecriture_id == EcritureComptable.id
        ).join(
            PlanComptable, LigneEcriture.numero_compte == PlanComptable.numero_compte
        ).filter(
            EcritureComptable.statut == 'valide'
        )
        
        # Filtres par date
        if date_debut:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            query = query.filter(EcritureComptable.date_ecriture >= date_debut_obj)
            
        if date_fin:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            query = query.filter(EcritureComptable.date_ecriture <= date_fin_obj)
        
        # Filtre par classe
        if classe:
            query = query.filter(PlanComptable.classe == classe)
            
        # Filtre par niveau
        if niveau:
            query = query.filter(PlanComptable.niveau <= niveau)
        
        # Grouper par compte
        query = query.group_by(
            LigneEcriture.numero_compte,
            PlanComptable.libelle_compte,
            PlanComptable.classe,
            PlanComptable.niveau
        ).order_by(LigneEcriture.numero_compte)
        
        lignes_balance = query.all()
        
        # Formatage de la balance
        balance = []
        total_debit_general = Decimal('0')
        total_credit_general = Decimal('0')
        
        for ligne in lignes_balance:
            debit = ligne.total_debit or Decimal('0')
            credit = ligne.total_credit or Decimal('0')
            solde = debit - credit
            
            balance.append({
                'numero_compte': ligne.numero_compte,
                'libelle_compte': ligne.libelle_compte,
                'classe': ligne.classe,
                'niveau': ligne.niveau,
                'debit': float(debit),
                'credit': float(credit),
                'solde': float(solde),
                'sens_solde': 'débiteur' if solde > 0 else 'créditeur' if solde < 0 else 'nul'
            })
            
            total_debit_general += debit
            total_credit_general += credit
        
        return jsonify({
            'success': True,
            'data': {
                'lignes': balance,
                'totaux': {
                    'total_debit': float(total_debit_general),
                    'total_credit': float(total_credit_general),
                    'equilibre': total_debit_general == total_credit_general
                },
                'parametres': {
                    'date_debut': date_debut,
                    'date_fin': date_fin,
                    'classe': classe,
                    'niveau': niveau,
                    'nombre_comptes': len(balance)
                }
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Format de date invalide',
            'message': 'Utilisez le format YYYY-MM-DD pour les dates'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération de la balance'
        }), 500

@comptabilite_bp.route('/grand-livre/<numero_compte>', methods=['GET'])
def get_grand_livre_compte(numero_compte):
    """
    Génère le grand livre d'un compte
    
    Query Parameters:
    - date_debut: Date de début (YYYY-MM-DD)
    - date_fin: Date de fin (YYYY-MM-DD)
    """
    try:
        # Vérifier l'existence du compte
        compte = PlanComptable.query.filter_by(numero_compte=numero_compte).first()
        if not compte:
            return jsonify({
                'success': False,
                'error': 'Compte inexistant',
                'message': f'Le compte {numero_compte} n\'existe pas'
            }), 404
        
        # Paramètres
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        # Requête pour les lignes du compte
        query = db.session.query(
            EcritureComptable.date_ecriture,
            EcritureComptable.libelle,
            EcritureComptable.journal,
            EcritureComptable.piece_justificative,
            LigneEcriture.libelle.label('libelle_ligne'),
            LigneEcriture.debit,
            LigneEcriture.credit
        ).join(
            LigneEcriture, EcritureComptable.id == LigneEcriture.ecriture_id
        ).filter(
            LigneEcriture.numero_compte == numero_compte,
            EcritureComptable.statut == 'valide'
        )
        
        # Filtres par date
        if date_debut:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            query = query.filter(EcritureComptable.date_ecriture >= date_debut_obj)
            
        if date_fin:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            query = query.filter(EcritureComptable.date_ecriture <= date_fin_obj)
        
        # Ordonner par date
        mouvements = query.order_by(EcritureComptable.date_ecriture).all()
        
        # Calculer les soldes progressifs
        solde_cumule = Decimal('0')
        lignes_grand_livre = []
        
        for mouvement in mouvements:
            debit = mouvement.debit or Decimal('0')
            credit = mouvement.credit or Decimal('0')
            solde_cumule += debit - credit
            
            lignes_grand_livre.append({
                'date': mouvement.date_ecriture.isoformat(),
                'libelle_ecriture': mouvement.libelle,
                'libelle_ligne': mouvement.libelle_ligne,
                'journal': mouvement.journal,
                'piece_justificative': mouvement.piece_justificative,
                'debit': float(debit),
                'credit': float(credit),
                'solde_cumule': float(solde_cumule)
            })
        
        # Totaux
        total_debit = sum(Decimal(str(ligne['debit'])) for ligne in lignes_grand_livre)
        total_credit = sum(Decimal(str(ligne['credit'])) for ligne in lignes_grand_livre)
        
        return jsonify({
            'success': True,
            'data': {
                'compte': {
                    'numero': compte.numero_compte,
                    'libelle': compte.libelle_compte,
                    'classe': compte.classe
                },
                'mouvements': lignes_grand_livre,
                'totaux': {
                    'total_debit': float(total_debit),
                    'total_credit': float(total_credit),
                    'solde_final': float(solde_cumule),
                    'nombre_mouvements': len(lignes_grand_livre)
                },
                'parametres': {
                    'date_debut': date_debut,
                    'date_fin': date_fin
                }
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Format de date invalide',
            'message': 'Utilisez le format YYYY-MM-DD pour les dates'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération du grand livre'
        }), 500

@comptabilite_bp.route('/journaux', methods=['GET'])
def get_journaux():
    """Récupère la liste des journaux comptables"""
    try:
        journaux = JournalComptable.query.order_by(JournalComptable.code).all()
        
        return jsonify({
            'success': True,
            'data': [journal.to_dict() for journal in journaux]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des journaux'
        }), 500

@comptabilite_bp.route('/tableau-bord', methods=['GET'])
def get_tableau_bord():
    """Génère un tableau de bord comptable avec indicateurs clés"""
    try:
        # Période par défaut : année en cours
        annee_courante = datetime.now().year
        date_debut = date(annee_courante, 1, 1)
        date_fin = date(annee_courante, 12, 31)
        
        # Paramètres optionnels
        date_debut_param = request.args.get('date_debut')
        date_fin_param = request.args.get('date_fin')
        
        if date_debut_param:
            date_debut = datetime.strptime(date_debut_param, '%Y-%m-%d').date()
        if date_fin_param:
            date_fin = datetime.strptime(date_fin_param, '%Y-%m-%d').date()
        
        # Statistiques générales
        total_ecritures = EcritureComptable.query.filter(
            EcritureComptable.date_ecriture.between(date_debut, date_fin)
        ).count()
        
        ecritures_brouillard = EcritureComptable.query.filter(
            EcritureComptable.date_ecriture.between(date_debut, date_fin),
            EcritureComptable.statut == 'brouillard'
        ).count()
        
        # Totaux par classe (pour les classes 6 et 7 notamment)
        totaux_classes = {}
        for classe in [6, 7]:  # Charges et Produits
            total = db.session.query(
                db.func.sum(LigneEcriture.debit - LigneEcriture.credit)
            ).join(
                EcritureComptable, LigneEcriture.ecriture_id == EcritureComptable.id
            ).join(
                PlanComptable, LigneEcriture.numero_compte == PlanComptable.numero_compte
            ).filter(
                PlanComptable.classe == classe,
                EcritureComptable.statut == 'valide',
                EcritureComptable.date_ecriture.between(date_debut, date_fin)
            ).scalar() or Decimal('0')
            
            totaux_classes[classe] = float(total)
        
        # Calcul du résultat simplifié (Produits - Charges)
        resultat = totaux_classes.get(7, 0) - abs(totaux_classes.get(6, 0))
        
        return jsonify({
            'success': True,
            'data': {
                'periode': {
                    'date_debut': date_debut.isoformat(),
                    'date_fin': date_fin.isoformat()
                },
                'statistiques': {
                    'total_ecritures': total_ecritures,
                    'ecritures_brouillard': ecritures_brouillard,
                    'ecritures_validees': total_ecritures - ecritures_brouillard
                },
                'totaux_classes': {
                    'charges': totaux_classes.get(6, 0),
                    'produits': totaux_classes.get(7, 0),
                    'resultat_simplifie': resultat
                },
                'indicateurs': {
                    'taux_validation': round((1 - ecritures_brouillard/total_ecritures) * 100, 2) if total_ecritures > 0 else 100,
                    'signe_resultat': 'bénéfice' if resultat > 0 else 'perte' if resultat < 0 else 'équilibre'
                }
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Format de date invalide',
            'message': 'Utilisez le format YYYY-MM-DD pour les dates'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération du tableau de bord'
        }), 500