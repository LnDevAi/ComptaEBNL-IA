#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Gestion des Utilisateurs et Permissions
===========================================

Ce module gère les utilisateurs et leurs permissions :
- Authentification et autorisation
- Gestion des rôles et permissions
- Profils utilisateurs
- Audit et traçabilité
- Sécurité des accès

Auteur: ComptaEBNL-IA
Date: 2025
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
from sqlalchemy import func

from models import db, Utilisateur

# Création du blueprint
utilisateurs_bp = Blueprint('utilisateurs', __name__)

# Configuration JWT (à déplacer dans config.py en production)
JWT_SECRET = 'votre_cle_secrete_jwt_super_securisee'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def token_required(f):
    """Décorateur pour vérifier l'authentification JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Récupérer le token depuis l'en-tête Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Format d\'autorisation invalide'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token d\'authentification requis'
            }), 401
        
        try:
            # Décoder le token
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = data['user_id']
            current_user = Utilisateur.query.get(current_user_id)
            
            if not current_user or not current_user.actif:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur non trouvé ou inactif'
                }), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token expiré'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'Token invalide'
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def permission_required(permission):
    """Décorateur pour vérifier les permissions spécifiques"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            # Vérifier les permissions selon le rôle
            permissions_par_role = {
                'administrateur': ['*'],  # Toutes les permissions
                'comptable': [
                    'ecriture.create', 'ecriture.read', 'ecriture.update', 'ecriture.validate',
                    'plan_comptable.read', 'balance.read', 'etats_financiers.read',
                    'exercice.read', 'exercice.create'
                ],
                'assistant': [
                    'ecriture.create', 'ecriture.read', 'plan_comptable.read',
                    'balance.read'
                ],
                'consultant': [
                    'ecriture.read', 'plan_comptable.read', 'balance.read',
                    'etats_financiers.read'
                ]
            }
            
            user_permissions = permissions_par_role.get(current_user.role, [])
            
            if '*' not in user_permissions and permission not in user_permissions:
                return jsonify({
                    'success': False,
                    'error': f'Permission insuffisante: {permission} requise'
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated
    return decorator

@utilisateurs_bp.route('/auth/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['nom_utilisateur', 'email', 'mot_de_passe', 'nom_complet']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Champ requis manquant: {field}'
                }), 400
        
        # Vérifier que l'utilisateur n'existe pas déjà
        if Utilisateur.query.filter_by(nom_utilisateur=data['nom_utilisateur']).first():
            return jsonify({
                'success': False,
                'error': 'Nom d\'utilisateur déjà utilisé'
            }), 400
        
        if Utilisateur.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'error': 'Email déjà utilisé'
            }), 400
        
        # Valider le mot de passe
        if len(data['mot_de_passe']) < 8:
            return jsonify({
                'success': False,
                'error': 'Le mot de passe doit contenir au moins 8 caractères'
            }), 400
        
        print(f"👤 Inscription utilisateur: {data['nom_utilisateur']}")
        
        # Créer l'utilisateur
        utilisateur = Utilisateur(
            nom_utilisateur=data['nom_utilisateur'],
            email=data['email'],
            mot_de_passe=generate_password_hash(data['mot_de_passe']),
            nom_complet=data['nom_complet'],
            role=data.get('role', 'assistant'),  # Rôle par défaut
            actif=True
        )
        
        db.session.add(utilisateur)
        db.session.commit()
        
        print(f"✅ Utilisateur créé: {utilisateur.nom_utilisateur}")
        
        return jsonify({
            'success': True,
            'data': {
                'id': utilisateur.id,
                'nom_utilisateur': utilisateur.nom_utilisateur,
                'email': utilisateur.email,
                'nom_complet': utilisateur.nom_complet,
                'role': utilisateur.role
            },
            'message': 'Utilisateur créé avec succès'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur inscription: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'inscription'
        }), 500

@utilisateurs_bp.route('/auth/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        
        if not data.get('nom_utilisateur') or not data.get('mot_de_passe'):
            return jsonify({
                'success': False,
                'error': 'Nom d\'utilisateur et mot de passe requis'
            }), 400
        
        # Chercher l'utilisateur
        utilisateur = Utilisateur.query.filter_by(
            nom_utilisateur=data['nom_utilisateur']
        ).first()
        
        if not utilisateur or not check_password_hash(utilisateur.mot_de_passe, data['mot_de_passe']):
            return jsonify({
                'success': False,
                'error': 'Nom d\'utilisateur ou mot de passe incorrect'
            }), 401
        
        if not utilisateur.actif:
            return jsonify({
                'success': False,
                'error': 'Compte utilisateur désactivé'
            }), 401
        
        # Mettre à jour la dernière connexion
        utilisateur.derniere_connexion = datetime.datetime.utcnow()
        db.session.commit()
        
        # Générer le token JWT
        token_payload = {
            'user_id': utilisateur.id,
            'nom_utilisateur': utilisateur.nom_utilisateur,
            'role': utilisateur.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        print(f"🔐 Connexion réussie: {utilisateur.nom_utilisateur}")
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'utilisateur': utilisateur.to_dict(),
                'expires_in': JWT_EXPIRATION_HOURS * 3600  # en secondes
            },
            'message': 'Connexion réussie'
        })
        
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la connexion'
        }), 500

@utilisateurs_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Récupère les informations de l'utilisateur connecté"""
    try:
        return jsonify({
            'success': True,
            'data': current_user.to_dict(),
            'message': 'Profil utilisateur récupéré'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération du profil'
        }), 500

@utilisateurs_bp.route('/utilisateurs', methods=['GET'])
@token_required
@permission_required('utilisateur.read')
def get_utilisateurs(current_user):
    """Liste tous les utilisateurs (admin seulement)"""
    try:
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filtres
        role_filter = request.args.get('role')
        actif_filter = request.args.get('actif')
        
        print(f"👥 Récupération utilisateurs (page {page})")
        
        # Construction de la requête
        query = Utilisateur.query
        
        if role_filter:
            query = query.filter(Utilisateur.role == role_filter)
        
        if actif_filter is not None:
            actif_bool = actif_filter.lower() == 'true'
            query = query.filter(Utilisateur.actif == actif_bool)
        
        # Pagination
        utilisateurs_paginated = query.order_by(Utilisateur.nom_utilisateur).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        utilisateurs_data = [user.to_dict() for user in utilisateurs_paginated.items]
        
        return jsonify({
            'success': True,
            'data': {
                'utilisateurs': utilisateurs_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': utilisateurs_paginated.total,
                    'pages': utilisateurs_paginated.pages,
                    'has_next': utilisateurs_paginated.has_next,
                    'has_prev': utilisateurs_paginated.has_prev
                }
            },
            'message': f'{len(utilisateurs_data)} utilisateurs récupérés'
        })
        
    except Exception as e:
        print(f"❌ Erreur récupération utilisateurs: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des utilisateurs'
        }), 500

@utilisateurs_bp.route('/utilisateurs/<int:user_id>', methods=['PUT'])
@token_required
@permission_required('utilisateur.update')
def update_utilisateur(current_user, user_id):
    """Met à jour un utilisateur"""
    try:
        utilisateur = Utilisateur.query.get_or_404(user_id)
        data = request.get_json()
        
        # Seuls les admins peuvent modifier les autres utilisateurs
        if current_user.role != 'administrateur' and current_user.id != user_id:
            return jsonify({
                'success': False,
                'error': 'Permission insuffisante'
            }), 403
        
        print(f"✏️  Mise à jour utilisateur: {utilisateur.nom_utilisateur}")
        
        # Mise à jour des champs autorisés
        if 'nom_complet' in data:
            utilisateur.nom_complet = data['nom_complet']
        
        if 'email' in data:
            # Vérifier que l'email n'est pas déjà utilisé
            existing = Utilisateur.query.filter(
                Utilisateur.email == data['email'],
                Utilisateur.id != user_id
            ).first()
            
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Email déjà utilisé'
                }), 400
            
            utilisateur.email = data['email']
        
        # Seuls les admins peuvent changer le rôle et le statut
        if current_user.role == 'administrateur':
            if 'role' in data:
                roles_valides = ['administrateur', 'comptable', 'assistant', 'consultant']
                if data['role'] in roles_valides:
                    utilisateur.role = data['role']
            
            if 'actif' in data:
                utilisateur.actif = data['actif']
            
            if 'peut_valider' in data:
                utilisateur.peut_valider = data['peut_valider']
            
            if 'peut_cloturer' in data:
                utilisateur.peut_cloturer = data['peut_cloturer']
            
            if 'peut_gerer_plan_comptable' in data:
                utilisateur.peut_gerer_plan_comptable = data['peut_gerer_plan_comptable']
        
        # Changer le mot de passe
        if 'nouveau_mot_de_passe' in data:
            if len(data['nouveau_mot_de_passe']) < 8:
                return jsonify({
                    'success': False,
                    'error': 'Le mot de passe doit contenir au moins 8 caractères'
                }), 400
            
            utilisateur.mot_de_passe = generate_password_hash(data['nouveau_mot_de_passe'])
        
        db.session.commit()
        
        print(f"✅ Utilisateur mis à jour: {utilisateur.nom_utilisateur}")
        
        return jsonify({
            'success': True,
            'data': utilisateur.to_dict(),
            'message': 'Utilisateur mis à jour avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur mise à jour utilisateur: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la mise à jour'
        }), 500

@utilisateurs_bp.route('/utilisateurs/<int:user_id>', methods=['DELETE'])
@token_required
@permission_required('utilisateur.delete')
def delete_utilisateur(current_user, user_id):
    """Supprime un utilisateur (admin seulement)"""
    try:
        if current_user.role != 'administrateur':
            return jsonify({
                'success': False,
                'error': 'Seuls les administrateurs peuvent supprimer des utilisateurs'
            }), 403
        
        utilisateur = Utilisateur.query.get_or_404(user_id)
        
        # Empêcher la suppression de son propre compte
        if current_user.id == user_id:
            return jsonify({
                'success': False,
                'error': 'Impossible de supprimer son propre compte'
            }), 400
        
        print(f"🗑️  Suppression utilisateur: {utilisateur.nom_utilisateur}")
        
        nom_utilisateur = utilisateur.nom_utilisateur
        db.session.delete(utilisateur)
        db.session.commit()
        
        print(f"✅ Utilisateur supprimé: {nom_utilisateur}")
        
        return jsonify({
            'success': True,
            'message': f'Utilisateur "{nom_utilisateur}" supprimé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur suppression utilisateur: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la suppression'
        }), 500

@utilisateurs_bp.route('/roles', methods=['GET'])
@token_required
def get_roles(current_user):
    """Récupère la liste des rôles disponibles"""
    try:
        roles = [
            {
                'code': 'administrateur',
                'nom': 'Administrateur',
                'description': 'Accès complet à toutes les fonctionnalités',
                'permissions': ['*']
            },
            {
                'code': 'comptable',
                'nom': 'Comptable',
                'description': 'Gestion comptable complète',
                'permissions': [
                    'ecriture.create', 'ecriture.read', 'ecriture.update', 'ecriture.validate',
                    'plan_comptable.read', 'balance.read', 'etats_financiers.read',
                    'exercice.read', 'exercice.create'
                ]
            },
            {
                'code': 'assistant',
                'nom': 'Assistant comptable',
                'description': 'Saisie d\'écritures et consultation',
                'permissions': [
                    'ecriture.create', 'ecriture.read', 'plan_comptable.read', 'balance.read'
                ]
            },
            {
                'code': 'consultant',
                'nom': 'Consultant',
                'description': 'Consultation uniquement',
                'permissions': [
                    'ecriture.read', 'plan_comptable.read', 'balance.read', 'etats_financiers.read'
                ]
            }
        ]
        
        return jsonify({
            'success': True,
            'data': roles,
            'message': 'Rôles récupérés'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des rôles'
        }), 500

@utilisateurs_bp.route('/stats', methods=['GET'])
@token_required
@permission_required('utilisateur.read')
def get_stats_utilisateurs(current_user):
    """Récupère les statistiques des utilisateurs"""
    try:
        print("📊 Calcul statistiques utilisateurs")
        
        stats = {}
        
        # Nombre d'utilisateurs par rôle
        stats['par_role'] = {}
        roles = db.session.query(
            Utilisateur.role,
            func.count(Utilisateur.id).label('count')
        ).group_by(Utilisateur.role).all()
        
        for role in roles:
            stats['par_role'][role.role] = role.count
        
        # Utilisateurs actifs/inactifs
        stats['par_statut'] = {
            'actifs': Utilisateur.query.filter_by(actif=True).count(),
            'inactifs': Utilisateur.query.filter_by(actif=False).count()
        }
        
        # Total
        stats['total'] = Utilisateur.query.count()
        
        # Dernières connexions
        derniers_connectes = Utilisateur.query.filter(
            Utilisateur.derniere_connexion.isnot(None)
        ).order_by(Utilisateur.derniere_connexion.desc()).limit(5).all()
        
        stats['derniers_connectes'] = []
        for user in derniers_connectes:
            stats['derniers_connectes'].append({
                'nom_utilisateur': user.nom_utilisateur,
                'nom_complet': user.nom_complet,
                'derniere_connexion': user.derniere_connexion.isoformat() if user.derniere_connexion else None
            })
        
        return jsonify({
            'success': True,
            'data': stats,
            'message': 'Statistiques des utilisateurs calculées'
        })
        
    except Exception as e:
        print(f"❌ Erreur calcul statistiques utilisateurs: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors du calcul des statistiques'
        }), 500