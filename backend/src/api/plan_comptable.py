#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Plan Comptable SYCEBNL
ComptaEBNL-IA - Gestion comptable pour entités à but non lucratif
"""

from flask import Blueprint, jsonify, request
from models import PlanComptable
from data.sycebnl_plan_comptable import CLASSES_SYCEBNL

plan_comptable_bp = Blueprint('plan_comptable', __name__)

@plan_comptable_bp.route('/plan-comptable', methods=['GET'])
def get_plan_comptable():
    """
    Récupère tous les comptes du plan comptable SYCEBNL
    
    Query Parameters:
    - classe: Filtrer par classe (1-9)
    - niveau: Filtrer par niveau (0-3) 
    - search: Recherche par numéro ou libellé
    - limit: Nombre max de résultats (défaut: 100)
    """
    try:
        # Paramètres de requête
        classe = request.args.get('classe', type=int)
        niveau = request.args.get('niveau', type=int)
        search = request.args.get('search', '')
        limit = request.args.get('limit', 100, type=int)
        
        # Construction de la requête
        query = PlanComptable.query
        
        if classe:
            query = query.filter_by(classe=classe)
            
        if niveau is not None:
            query = query.filter_by(niveau=niveau)
            
        if search:
            if search.isdigit():
                # Recherche par numéro
                query = query.filter(PlanComptable.numero_compte.like(f"{search}%"))
            else:
                # Recherche par libellé
                query = query.filter(PlanComptable.libelle_compte.ilike(f"%{search}%"))
        
        # Exécution avec limitation
        comptes = query.order_by(PlanComptable.numero_compte).limit(limit).all()
        
        # Formatage de la réponse
        result = {
            'success': True,
            'data': [compte.to_dict() for compte in comptes],
            'total': len(comptes),
            'filters': {
                'classe': classe,
                'niveau': niveau,
                'search': search,
                'limit': limit
            }
        }
        
        # Ajouter info de classe si filtrée
        if classe and classe in CLASSES_SYCEBNL:
            result['classe_info'] = {
                'numero': classe,
                'libelle': CLASSES_SYCEBNL[classe]
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération du plan comptable'
        }), 500

@plan_comptable_bp.route('/plan-comptable/classes', methods=['GET'])
def get_classes():
    """Récupère la liste des classes SYCEBNL avec compteurs"""
    try:
        classes_info = []
        
        for classe_num in range(1, 10):
            count = PlanComptable.query.filter_by(classe=classe_num).count()
            
            classes_info.append({
                'numero': classe_num,
                'libelle': CLASSES_SYCEBNL.get(classe_num, f'Classe {classe_num}'),
                'nombre_comptes': count,
                'actif': count > 0
            })
        
        return jsonify({
            'success': True,
            'data': classes_info,
            'total_classes': len([c for c in classes_info if c['actif']])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des classes'
        }), 500

@plan_comptable_bp.route('/plan-comptable/classe/<int:classe>', methods=['GET'])
def get_comptes_by_classe(classe):
    """Récupère tous les comptes d'une classe donnée"""
    try:
        if classe not in range(1, 10):
            return jsonify({
                'success': False,
                'error': 'Classe invalide',
                'message': 'La classe doit être entre 1 et 9'
            }), 400
        
        comptes = PlanComptable.query.filter_by(classe=classe)\
                                    .order_by(PlanComptable.numero_compte).all()
        
        return jsonify({
            'success': True,
            'data': [compte.to_dict() for compte in comptes],
            'classe_info': {
                'numero': classe,
                'libelle': CLASSES_SYCEBNL.get(classe, f'Classe {classe}'),
                'nombre_comptes': len(comptes)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Erreur lors de la récupération des comptes de la classe {classe}'
        }), 500

@plan_comptable_bp.route('/plan-comptable/compte/<numero>', methods=['GET'])
def get_compte_by_numero(numero):
    """Récupère un compte spécifique par son numéro"""
    try:
        compte = PlanComptable.query.filter_by(numero_compte=numero).first()
        
        if not compte:
            return jsonify({
                'success': False,
                'error': 'Compte non trouvé',
                'message': f'Le compte {numero} n\'existe pas dans le plan SYCEBNL'
            }), 404
        
        # Récupérer les comptes enfants
        enfants = PlanComptable.query.filter_by(parent_id=compte.id).all()
        
        # Récupérer le compte parent
        parent = None
        if compte.parent_id:
            parent = PlanComptable.query.get(compte.parent_id)
        
        result = compte.to_dict()
        result.update({
            'enfants': [enfant.to_dict() for enfant in enfants],
            'parent': parent.to_dict() if parent else None,
            'classe_info': {
                'numero': compte.classe,
                'libelle': CLASSES_SYCEBNL.get(compte.classe, f'Classe {compte.classe}')
            }
        })
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Erreur lors de la récupération du compte {numero}'
        }), 500

@plan_comptable_bp.route('/plan-comptable/search', methods=['GET'])
def search_comptes():
    """Recherche avancée dans le plan comptable"""
    try:
        query_param = request.args.get('q', '')
        classe = request.args.get('classe', type=int)
        exact = request.args.get('exact', 'false').lower() == 'true'
        limit = request.args.get('limit', 20, type=int)
        
        if not query_param:
            return jsonify({
                'success': False,
                'error': 'Paramètre de recherche manquant',
                'message': 'Le paramètre "q" est requis'
            }), 400
        
        # Construction de la requête
        query = PlanComptable.query
        
        if classe:
            query = query.filter_by(classe=classe)
        
        if query_param.isdigit():
            # Recherche par numéro
            if exact:
                query = query.filter(PlanComptable.numero_compte == query_param)
            else:
                query = query.filter(PlanComptable.numero_compte.like(f"{query_param}%"))
        else:
            # Recherche par libellé
            if exact:
                query = query.filter(PlanComptable.libelle_compte.ilike(query_param))
            else:
                query = query.filter(PlanComptable.libelle_compte.ilike(f"%{query_param}%"))
        
        comptes = query.order_by(PlanComptable.numero_compte).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [compte.to_dict() for compte in comptes],
            'query': query_param,
            'total_found': len(comptes),
            'search_params': {
                'exact': exact,
                'classe': classe,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la recherche'
        }), 500

@plan_comptable_bp.route('/plan-comptable/stats', methods=['GET'])
def get_stats_plan_comptable():
    """Statistiques du plan comptable SYCEBNL"""
    try:
        total_comptes = PlanComptable.query.count()
        
        # Stats par classe
        stats_classes = []
        for classe_num in range(1, 10):
            count = PlanComptable.query.filter_by(classe=classe_num).count()
            if count > 0:
                stats_classes.append({
                    'classe': classe_num,
                    'libelle': CLASSES_SYCEBNL.get(classe_num, f'Classe {classe_num}'),
                    'nombre_comptes': count,
                    'pourcentage': round((count / total_comptes) * 100, 2) if total_comptes > 0 else 0
                })
        
        # Stats par niveau
        stats_niveaux = []
        for niveau in range(0, 4):
            count = PlanComptable.query.filter_by(niveau=niveau).count()
            if count > 0:
                niveau_desc = {
                    0: "Classes principales",
                    1: "Comptes principaux",
                    2: "Comptes divisionnaires", 
                    3: "Sous-comptes"
                }
                stats_niveaux.append({
                    'niveau': niveau,
                    'description': niveau_desc.get(niveau, f'Niveau {niveau}'),
                    'nombre_comptes': count,
                    'pourcentage': round((count / total_comptes) * 100, 2) if total_comptes > 0 else 0
                })
        
        # Comptes spécifiques EBNL
        comptes_ebnl = [
            ("758", "Contributions volontaires en nature"),
            ("7581", "Bénévolat"),
            ("412", "Adhérents et usagers"),
            ("1311", "Fonds dédiés avec obligation contractuelle"),
            ("756", "Dons et legs")
        ]
        
        ebnl_status = []
        for numero, description in comptes_ebnl:
            existe = PlanComptable.query.filter_by(numero_compte=numero).first() is not None
            ebnl_status.append({
                'numero': numero,
                'description': description,
                'presente': existe
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_comptes': total_comptes,
                'stats_par_classe': stats_classes,
                'stats_par_niveau': stats_niveaux,
                'comptes_specifiques_ebnl': ebnl_status,
                'referentiel': 'SYCEBNL - Système Comptable des Entités à But Non Lucratif'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors du calcul des statistiques'
        }), 500

# Validation du plan comptable
@plan_comptable_bp.route('/plan-comptable/validate', methods=['GET'])
def validate_plan_comptable():
    """Valide la cohérence du plan comptable SYCEBNL"""
    try:
        issues = []
        
        # Vérifier les comptes orphelins (parent_id pointant vers un compte inexistant)
        comptes_avec_parent = PlanComptable.query.filter(PlanComptable.parent_id.isnot(None)).all()
        for compte in comptes_avec_parent:
            parent = PlanComptable.query.get(compte.parent_id)
            if not parent:
                issues.append({
                    'type': 'parent_manquant',
                    'compte': compte.numero_compte,
                    'message': f'Compte {compte.numero_compte} référence un parent inexistant (ID: {compte.parent_id})'
                })
        
        # Vérifier la cohérence classe/numéro
        comptes = PlanComptable.query.all()
        for compte in comptes:
            premier_chiffre = int(compte.numero_compte[0]) if compte.numero_compte and compte.numero_compte[0].isdigit() else None
            if premier_chiffre and premier_chiffre != compte.classe:
                issues.append({
                    'type': 'incoherence_classe',
                    'compte': compte.numero_compte,
                    'message': f'Compte {compte.numero_compte} en classe {compte.classe} mais commence par {premier_chiffre}'
                })
        
        return jsonify({
            'success': True,
            'data': {
                'valide': len(issues) == 0,
                'nombre_problemes': len(issues),
                'problemes': issues
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la validation'
        }), 500