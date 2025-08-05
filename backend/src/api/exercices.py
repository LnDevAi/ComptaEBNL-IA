#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Gestion des Exercices Comptables
====================================

Ce module gère les exercices comptables :
- Création et gestion des exercices
- Ouverture et clôture d'exercices
- Gestion des périodes comptables
- Validation et contrôles de cohérence
- Archivage des exercices

Auteur: ComptaEBNL-IA
Date: 2025
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from models import db, ExerciceComptable, EcritureComptable, LigneEcriture, PlanComptable

# Création du blueprint
exercices_bp = Blueprint('exercices', __name__)

@exercices_bp.route('/exercices', methods=['GET'])
def get_exercices():
    """Liste tous les exercices comptables"""
    try:
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filtres
        statut = request.args.get('statut')  # ouvert, ferme, archive
        annee = request.args.get('annee', type=int)
        
        print(f"📅 Récupération des exercices (page {page})")
        
        # Construction de la requête
        query = ExerciceComptable.query
        
        if statut:
            query = query.filter(ExerciceComptable.statut == statut)
        
        if annee:
            query = query.filter(func.extract('year', ExerciceComptable.date_debut) == annee)
        
                # Pagination
        exercices_paginated = query.order_by(ExerciceComptable.date_debut.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        exercices_data = []
        for exercice in exercices_paginated.items:
            # Calculer quelques statistiques (simplifiées pour l'instant)
            nb_ecritures = 0  # EcritureComptable.query.filter_by(exercice_id=exercice.id).count()
            
            # Calculer le total des mouvements (simplifié pour l'instant)
            total_mouvements = 0
            
            exercice_dict = exercice.to_dict()
            exercice_dict.update({
                'nb_ecritures': nb_ecritures,
                'total_mouvements': float(total_mouvements),
                'duree_jours': (exercice.date_fin - exercice.date_debut).days + 1 if exercice.date_fin else None
            })
            
            exercices_data.append(exercice_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'exercices': exercices_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': exercices_paginated.total,
                    'pages': exercices_paginated.pages,
                    'has_next': exercices_paginated.has_next,
                    'has_prev': exercices_paginated.has_prev
                }
            },
            'message': f'{len(exercices_data)} exercices récupérés'
        })
        
    except Exception as e:
        print(f"❌ Erreur récupération exercices: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des exercices'
        }), 500

@exercices_bp.route('/exercices', methods=['POST'])
def create_exercice():
    """Crée un nouvel exercice comptable"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['nom_exercice', 'date_debut', 'date_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Champ requis manquant: {field}'
                }), 400
        
        # Conversion des dates
        try:
            date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
            date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Format de date invalide: {e}'
            }), 400
        
        # Validations métier
        if date_debut >= date_fin:
            return jsonify({
                'success': False,
                'error': 'La date de début doit être antérieure à la date de fin'
            }), 400
        
        # Vérifier qu'il n'y a pas de chevauchement avec d'autres exercices
        exercice_existant = ExerciceComptable.query.filter(
            or_(
                and_(ExerciceComptable.date_debut <= date_debut, ExerciceComptable.date_fin >= date_debut),
                and_(ExerciceComptable.date_debut <= date_fin, ExerciceComptable.date_fin >= date_fin),
                and_(ExerciceComptable.date_debut >= date_debut, ExerciceComptable.date_fin <= date_fin)
            )
        ).first()
        
        if exercice_existant:
            return jsonify({
                'success': False,
                'error': f'Chevauchement avec l\'exercice existant: {exercice_existant.nom_exercice}'
            }), 400
        
        print(f"📅 Création exercice: {data['nom_exercice']} ({date_debut} - {date_fin})")
        
        # Créer l'exercice
        exercice = ExerciceComptable(
            nom_exercice=data['nom_exercice'],
            date_debut=date_debut,
            date_fin=date_fin,
            statut='ouvert'
        )
        
        db.session.add(exercice)
        db.session.commit()
        
        print(f"✅ Exercice créé avec l'ID: {exercice.id}")
        
        return jsonify({
            'success': True,
            'data': exercice.to_dict(),
            'message': f'Exercice "{exercice.nom_exercice}" créé avec succès'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur création exercice: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la création de l\'exercice'
        }), 500

@exercices_bp.route('/exercices/<int:exercice_id>', methods=['GET'])
def get_exercice_detail(exercice_id):
    """Récupère les détails d'un exercice comptable"""
    try:
        exercice = ExerciceComptable.query.get_or_404(exercice_id)
        
        print(f"📋 Détails exercice: {exercice.libelle}")
        
        # Statistiques détaillées
        stats = {}
        
        # Nombre d'écritures par statut
        stats['ecritures'] = {
            'total': EcritureComptable.query.filter_by(exercice_id=exercice_id).count(),
            'brouillard': EcritureComptable.query.filter_by(exercice_id=exercice_id, statut='brouillard').count(),
            'valide': EcritureComptable.query.filter_by(exercice_id=exercice_id, statut='valide').count(),
            'annule': EcritureComptable.query.filter_by(exercice_id=exercice_id, statut='annule').count()
        }
        
        # Totaux par journal
        journaux_stats = db.session.query(
            EcritureComptable.journal,
            func.count(EcritureComptable.id).label('nb_ecritures'),
            func.sum(LigneEcriture.debit).label('total_debit'),
            func.sum(LigneEcriture.credit).label('total_credit')
        ).join(LigneEcriture).filter(
            EcritureComptable.exercice_id == exercice_id,
            EcritureComptable.statut == 'valide'
        ).group_by(EcritureComptable.journal).all()
        
        stats['journaux'] = {}
        for journal_stat in journaux_stats:
            stats['journaux'][journal_stat.journal] = {
                'nb_ecritures': journal_stat.nb_ecritures,
                'total_debit': float(journal_stat.total_debit or 0),
                'total_credit': float(journal_stat.total_credit or 0)
            }
        
        # Soldes par classe comptable
        classes_stats = db.session.query(
            PlanComptable.classe,
            func.sum(LigneEcriture.debit).label('total_debit'),
            func.sum(LigneEcriture.credit).label('total_credit')
        ).join(LigneEcriture).join(EcritureComptable).filter(
            EcritureComptable.exercice_id == exercice_id,
            EcritureComptable.statut == 'valide'
        ).group_by(PlanComptable.classe).all()
        
        stats['classes'] = {}
        for classe_stat in classes_stats:
            debit = float(classe_stat.total_debit or 0)
            credit = float(classe_stat.total_credit or 0)
            stats['classes'][classe_stat.classe] = {
                'debit': debit,
                'credit': credit,
                'solde': debit - credit
            }
        
        # Équilibre général
        total_debit = sum(classe['debit'] for classe in stats['classes'].values())
        total_credit = sum(classe['credit'] for classe in stats['classes'].values())
        
        stats['equilibre'] = {
            'total_debit': total_debit,
            'total_credit': total_credit,
            'difference': total_debit - total_credit,
            'equilibre': abs(total_debit - total_credit) < 0.01
        }
        
        # Progression temporelle (par mois)
        progression = db.session.query(
            func.extract('year', EcritureComptable.date_ecriture).label('annee'),
            func.extract('month', EcritureComptable.date_ecriture).label('mois'),
            func.count(EcritureComptable.id).label('nb_ecritures'),
            func.sum(LigneEcriture.debit).label('total_debit'),
            func.sum(LigneEcriture.credit).label('total_credit')
        ).join(LigneEcriture).filter(
            EcritureComptable.exercice_id == exercice_id,
            EcritureComptable.statut == 'valide'
        ).group_by('annee', 'mois').order_by('annee', 'mois').all()
        
        stats['progression'] = []
        for prog in progression:
            stats['progression'].append({
                'periode': f"{int(prog.annee)}-{int(prog.mois):02d}",
                'nb_ecritures': prog.nb_ecritures,
                'total_debit': float(prog.total_debit or 0),
                'total_credit': float(prog.total_credit or 0)
            })
        
        exercice_dict = exercice.to_dict()
        exercice_dict['statistiques'] = stats
        
        return jsonify({
            'success': True,
            'data': exercice_dict,
            'message': f'Détails de l\'exercice "{exercice.libelle}" récupérés'
        })
        
    except Exception as e:
        print(f"❌ Erreur récupération détails exercice: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des détails de l\'exercice'
        }), 500

@exercices_bp.route('/exercices/<int:exercice_id>/cloturer', methods=['POST'])
def cloturer_exercice(exercice_id):
    """Clôture un exercice comptable"""
    try:
        exercice = ExerciceComptable.query.get_or_404(exercice_id)
        
        if exercice.statut != 'ouvert':
            return jsonify({
                'success': False,
                'error': f'L\'exercice est déjà {exercice.statut}'
            }), 400
        
        data = request.get_json() or {}
        cloture_definitive = data.get('definitif', False)
        
        print(f"🔒 Clôture exercice: {exercice.libelle} (définitive: {cloture_definitive})")
        
        # Vérifications avant clôture
        verifications = []
        
        # 1. Vérifier l'équilibre général
        total_debit = db.session.query(func.sum(LigneEcriture.debit)).join(EcritureComptable).filter(
            EcritureComptable.exercice_id == exercice_id,
            EcritureComptable.statut == 'valide'
        ).scalar() or 0
        
        total_credit = db.session.query(func.sum(LigneEcriture.credit)).join(EcritureComptable).filter(
            EcritureComptable.exercice_id == exercice_id,
            EcritureComptable.statut == 'valide'
        ).scalar() or 0
        
        if abs(float(total_debit - total_credit)) > 0.01:
            verifications.append({
                'type': 'erreur',
                'message': f'Déséquilibre comptable: {float(total_debit - total_credit):.2f}€'
            })
        
        # 2. Vérifier les écritures non validées
        nb_brouillard = EcritureComptable.query.filter_by(
            exercice_id=exercice_id, 
            statut='brouillard'
        ).count()
        
        if nb_brouillard > 0:
            verifications.append({
                'type': 'avertissement',
                'message': f'{nb_brouillard} écriture(s) encore en brouillard'
            })
        
        # 3. Vérifier que la date de fin est passée
        if exercice.date_fin > date.today():
            verifications.append({
                'type': 'avertissement',
                'message': 'La date de fin d\'exercice n\'est pas encore atteinte'
            })
        
        # Si erreurs bloquantes, arrêter
        erreurs = [v for v in verifications if v['type'] == 'erreur']
        if erreurs and not data.get('forcer', False):
            return jsonify({
                'success': False,
                'error': 'Erreurs bloquantes détectées',
                'verifications': verifications,
                'message': 'Utilisez "forcer": true pour passer outre les erreurs'
            }), 400
        
        # Effectuer la clôture
        exercice.statut = 'ferme'
        exercice.date_cloture = datetime.now()
        exercice.cloture_definitif = cloture_definitive
        
        if cloture_definitive:
            # Générer les écritures de clôture (à nouveau et résultat)
            resultat_net = float(total_credit - total_debit)  # Crédit - Débit pour le résultat
            
            if abs(resultat_net) > 0.01:
                # Créer l'écriture de clôture du résultat
                from api.comptabilite import creer_ecriture_cloture
                creer_ecriture_cloture(exercice_id, resultat_net)
        
        db.session.commit()
        
        print(f"✅ Exercice clôturé: {exercice.libelle}")
        
        return jsonify({
            'success': True,
            'data': {
                'exercice': exercice.to_dict(),
                'verifications': verifications,
                'resultat_net': float(total_credit - total_debit) if cloture_definitive else None
            },
            'message': f'Exercice "{exercice.libelle}" clôturé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur clôture exercice: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la clôture de l\'exercice'
        }), 500

@exercices_bp.route('/exercices/<int:exercice_id>/rouvrir', methods=['POST'])
def rouvrir_exercice(exercice_id):
    """Rouvre un exercice comptable clôturé"""
    try:
        exercice = ExerciceComptable.query.get_or_404(exercice_id)
        
        if exercice.statut != 'ferme':
            return jsonify({
                'success': False,
                'error': f'L\'exercice n\'est pas fermé (statut: {exercice.statut})'
            }), 400
        
        if exercice.cloture_definitif:
            return jsonify({
                'success': False,
                'error': 'Impossible de rouvrir un exercice clôturé définitivement'
            }), 400
        
        print(f"🔓 Réouverture exercice: {exercice.libelle}")
        
        # Réouvrir l'exercice
        exercice.statut = 'ouvert'
        exercice.date_cloture = None
        
        db.session.commit()
        
        print(f"✅ Exercice rouvert: {exercice.libelle}")
        
        return jsonify({
            'success': True,
            'data': exercice.to_dict(),
            'message': f'Exercice "{exercice.libelle}" rouvert avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur réouverture exercice: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la réouverture de l\'exercice'
        }), 500

@exercices_bp.route('/exercices/<int:exercice_id>/archiver', methods=['POST'])
def archiver_exercice(exercice_id):
    """Archive un exercice comptable"""
    try:
        exercice = ExerciceComptable.query.get_or_404(exercice_id)
        
        if exercice.statut != 'ferme':
            return jsonify({
                'success': False,
                'error': 'Seuls les exercices fermés peuvent être archivés'
            }), 400
        
        if not exercice.cloture_definitif:
            return jsonify({
                'success': False,
                'error': 'L\'exercice doit être clôturé définitivement avant archivage'
            }), 400
        
        print(f"📦 Archivage exercice: {exercice.libelle}")
        
        # Archiver l'exercice
        exercice.statut = 'archive'
        exercice.date_archivage = datetime.now()
        
        db.session.commit()
        
        print(f"✅ Exercice archivé: {exercice.libelle}")
        
        return jsonify({
            'success': True,
            'data': exercice.to_dict(),
            'message': f'Exercice "{exercice.libelle}" archivé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur archivage exercice: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'archivage de l\'exercice'
        }), 500

@exercices_bp.route('/exercices/courant', methods=['GET'])
def get_exercice_courant():
    """Récupère l'exercice comptable courant"""
    try:
        # Chercher l'exercice ouvert qui contient la date d'aujourd'hui
        aujourd_hui = date.today()
        
        exercice_courant = ExerciceComptable.query.filter(
            ExerciceComptable.statut == 'ouvert',
            ExerciceComptable.date_debut <= aujourd_hui,
            ExerciceComptable.date_fin >= aujourd_hui
        ).first()
        
        if not exercice_courant:
            # Si aucun exercice courant, prendre le plus récent ouvert
            exercice_courant = ExerciceComptable.query.filter_by(
                statut='ouvert'
            ).order_by(ExerciceComptable.date_debut.desc()).first()
        
        if not exercice_courant:
            return jsonify({
                'success': False,
                'error': 'Aucun exercice ouvert trouvé',
                'message': 'Créez un nouvel exercice comptable'
            }), 404
        
        print(f"📅 Exercice courant: {exercice_courant.nom_exercice}")
        
        return jsonify({
            'success': True,
            'data': exercice_courant.to_dict(),
            'message': f'Exercice courant: {exercice_courant.nom_exercice}'
        })
        
    except Exception as e:
        print(f"❌ Erreur récupération exercice courant: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération de l\'exercice courant'
        }), 500

@exercices_bp.route('/exercices/stats', methods=['GET'])
def get_stats_exercices():
    """Récupère les statistiques globales des exercices"""
    try:
        print("📊 Calcul statistiques exercices")
        
        stats = {}
        
        # Nombre d'exercices par statut
        stats['par_statut'] = {}
        statuts = db.session.query(
            ExerciceComptable.statut,
            func.count(ExerciceComptable.id).label('count')
        ).group_by(ExerciceComptable.statut).all()
        
        for statut in statuts:
            stats['par_statut'][statut.statut] = statut.count
        
        # Exercice le plus ancien et le plus récent
        plus_ancien = ExerciceComptable.query.order_by(ExerciceComptable.date_debut.asc()).first()
        plus_recent = ExerciceComptable.query.order_by(ExerciceComptable.date_debut.desc()).first()
        
        stats['periodes'] = {
            'plus_ancien': plus_ancien.to_dict() if plus_ancien else None,
            'plus_recent': plus_recent.to_dict() if plus_recent else None
        }
        
        # Total des mouvements par exercice
        mouvements = db.session.query(
            ExerciceComptable.id,
            ExerciceComptable.libelle,
            func.sum(LigneEcriture.debit + LigneEcriture.credit).label('total_mouvements')
        ).join(EcritureComptable).join(LigneEcriture).filter(
            EcritureComptable.statut == 'valide'
        ).group_by(ExerciceComptable.id, ExerciceComptable.libelle).all()
        
        stats['mouvements'] = []
        for mouvement in mouvements:
            stats['mouvements'].append({
                'exercice_id': mouvement.id,
                'libelle': mouvement.libelle,
                'total_mouvements': float(mouvement.total_mouvements or 0)
            })
        
        return jsonify({
            'success': True,
            'data': stats,
            'message': 'Statistiques des exercices calculées'
        })
        
    except Exception as e:
        print(f"❌ Erreur calcul statistiques exercices: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors du calcul des statistiques'
        }), 500