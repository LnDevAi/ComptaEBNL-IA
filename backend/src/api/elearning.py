"""
API E-Learning ComptaEBNL-IA
Gestion des formations, inscriptions, quiz et certificats pour les EBNL de l'espace OHADA
"""

from flask import Blueprint, request, jsonify, current_app, g, send_file
from datetime import datetime, timedelta
import json
import uuid
import os
import io
from functools import wraps

# Import des services
try:
    from services.certificate_generator import CertificateGenerator
except ImportError:
    CertificateGenerator = None

try:
    from services.subscription_service import (
        check_formation_access, check_certificate_generation, 
        check_pdf_download_access, get_user_limitations
    )
except ImportError:
    # Fonctions de fallback si le service subscription n'est pas disponible
    def check_formation_access(user_id, formation):
        return True, ""
    def check_certificate_generation(user_id):
        return True, ""
    def check_pdf_download_access(user_id):
        return True
    def get_user_limitations(user_id):
        return {}

# Import des modèles (à adapter selon la structure)
try:
    from models_elearning import (
        db, CategorieFormation, Formation, ModuleFormation, Lecon, Quiz, 
        QuestionQuiz, TentativeQuiz, InscriptionFormation, ProgressionLecon,
        EvaluationFormation, Certificat, StatutProgression, StatutCertificat,
        NiveauDifficulte, TypeContenu, TypeQuiz
    )
except ImportError:
    # Fallback si les modèles ne sont pas encore intégrés
    from models import db

# Import du middleware d'abonnement
try:
    from middleware.subscription_middleware import subscription_required, plan_required
except ImportError:
    # Decorators de fallback si middleware pas encore intégré
    def subscription_required(f):
        return f
    def plan_required(plan):
        def decorator(f):
            return f
        return decorator

elearning_bp = Blueprint('elearning', __name__)

# ============================
# UTILITAIRES
# ============================

def get_current_user_id():
    """Récupère l'ID de l'utilisateur actuel (à adapter selon le système d'auth)"""
    # TODO: Intégrer avec le système d'authentification existant
    return getattr(g, 'current_user_id', 1)  # Valeur par défaut pour les tests

def check_formation_access(formation, user_plan="gratuit"):
    """Vérifie si l'utilisateur a accès à une formation selon son plan"""
    plan_hierarchy = {
        "gratuit": 0,
        "professionnel": 1, 
        "enterprise": 2
    }
    
    required_level = plan_hierarchy.get(formation.plan_requis, 0)
    user_level = plan_hierarchy.get(user_plan, 0)
    
    return user_level >= required_level

def calculate_progression(inscription):
    """Calcule la progression d'une inscription"""
    if not inscription.formation.modules:
        return 0.0
    
    total_lecons = 0
    lecons_terminees = 0
    
    for module in inscription.formation.modules:
        total_lecons += len(module.lecons)
        for lecon in module.lecons:
            progression = ProgressionLecon.query.filter_by(
                inscription_id=inscription.id,
                lecon_id=lecon.id
            ).first()
            if progression and progression.termine:
                lecons_terminees += 1
    
    if total_lecons == 0:
        return 0.0
    
    return (lecons_terminees / total_lecons) * 100

# ============================
# ENDPOINTS FORMATIONS
# ============================

@elearning_bp.route('/categories', methods=['GET'])
def get_categories():
    """Récupère toutes les catégories de formation"""
    try:
        categories = CategorieFormation.query.filter_by(actif=True).order_by(CategorieFormation.ordre).all()
        return jsonify({
            'success': True,
            'categories': [cat.to_dict() for cat in categories]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des catégories: {str(e)}'
        }), 500

@elearning_bp.route('/formations', methods=['GET'])
def get_formations():
    """Récupère toutes les formations disponibles"""
    try:
        # Paramètres de filtrage
        categorie_id = request.args.get('categorie_id', type=int)
        niveau = request.args.get('niveau')
        plan_requis = request.args.get('plan_requis')
        search = request.args.get('search', '').strip()
        
        # Construction de la requête
        query = Formation.query.filter_by(publie=True)
        
        if categorie_id:
            query = query.filter_by(categorie_id=categorie_id)
        
        if niveau:
            query = query.filter_by(niveau=niveau)
        
        if plan_requis:
            query = query.filter_by(plan_requis=plan_requis)
        
        if search:
            query = query.filter(Formation.titre.contains(search))
        
        formations = query.order_by(Formation.date_publication.desc()).all()
        
        # Vérifier l'accès selon le plan utilisateur (si connecté)
        user_plan = getattr(g, 'current_subscription', {}).get('plan', {}).get('type_plan', 'gratuit')
        
        formations_data = []
        for formation in formations:
            formation_dict = formation.to_dict()
            formation_dict['accessible'] = check_formation_access(formation, user_plan)
            formations_data.append(formation_dict)
        
        return jsonify({
            'success': True,
            'formations': formations_data,
            'total': len(formations_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des formations: {str(e)}'
        }), 500

@elearning_bp.route('/formations/<int:formation_id>', methods=['GET'])
def get_formation_detail(formation_id):
    """Récupère le détail d'une formation avec ses modules"""
    try:
        formation = Formation.query.filter_by(id=formation_id, publie=True).first()
        
        if not formation:
            return jsonify({
                'success': False,
                'message': 'Formation non trouvée'
            }), 404
        
        # Vérifier l'accès
        user_plan = getattr(g, 'current_subscription', {}).get('plan', {}).get('type_plan', 'gratuit')
        if not check_formation_access(formation, user_plan):
            return jsonify({
                'success': False,
                'message': f'Cette formation nécessite un abonnement {formation.plan_requis}',
                'plan_requis': formation.plan_requis
            }), 403
        
        # Récupérer l'inscription de l'utilisateur si elle existe
        user_id = get_current_user_id()
        inscription = InscriptionFormation.query.filter_by(
            formation_id=formation_id,
            utilisateur_id=user_id
        ).first()
        
        formation_data = formation.to_dict(include_modules=True)
        
        if inscription:
            formation_data['inscription'] = {
                'id': inscription.id,
                'statut': inscription.statut.value,
                'date_inscription': inscription.date_inscription.isoformat(),
                'pourcentage_completion': calculate_progression(inscription),
                'temps_passe': inscription.temps_passe
            }
        else:
            formation_data['inscription'] = None
        
        return jsonify({
            'success': True,
            'formation': formation_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération de la formation: {str(e)}'
        }), 500

@elearning_bp.route('/formations/<int:formation_id>/inscrire', methods=['POST'])
@subscription_required
def inscrire_formation(formation_id):
    """Inscrit l'utilisateur à une formation"""
    try:
        formation = Formation.query.filter_by(id=formation_id, publie=True).first()
        
        if not formation:
            return jsonify({
                'success': False,
                'message': 'Formation non trouvée'
            }), 404
        
        user_id = get_current_user_id()
        
        # Vérifier si déjà inscrit
        inscription_existante = InscriptionFormation.query.filter_by(
            formation_id=formation_id,
            utilisateur_id=user_id
        ).first()
        
        if inscription_existante:
            return jsonify({
                'success': False,
                'message': 'Vous êtes déjà inscrit à cette formation'
            }), 400
        
        # Vérifier l'accès selon le plan d'abonnement
        access_allowed, access_message = check_formation_access(user_id, formation)
        if not access_allowed:
            return jsonify({
                'success': False,
                'message': access_message,
                'upgrade_required': True,
                'plan_requis': formation.plan_requis
            }), 403
        
        # Créer l'inscription
        inscription = InscriptionFormation(
            formation_id=formation_id,
            utilisateur_id=user_id,
            statut=StatutProgression.NON_COMMENCE,
            date_inscription=datetime.utcnow()
        )
        
        db.session.add(inscription)
        
        # Mettre à jour le compteur d'inscrits
        formation.nb_inscrits += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Inscription réussie',
            'inscription': inscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'inscription: {str(e)}'
        }), 500

# ============================
# ENDPOINTS LEÇONS
# ============================

@elearning_bp.route('/lecons/<int:lecon_id>', methods=['GET'])
@subscription_required
def get_lecon_detail(lecon_id):
    """Récupère le détail d'une leçon"""
    try:
        lecon = Lecon.query.get(lecon_id)
        
        if not lecon:
            return jsonify({
                'success': False,
                'message': 'Leçon non trouvée'
            }), 404
        
        # Vérifier l'accès à la formation
        formation = lecon.module.formation
        user_plan = getattr(g, 'current_subscription', {}).get('plan', {}).get('type_plan', 'gratuit')
        
        if not lecon.gratuit and not check_formation_access(formation, user_plan):
            return jsonify({
                'success': False,
                'message': f'Cette leçon nécessite un abonnement {formation.plan_requis}',
                'plan_requis': formation.plan_requis
            }), 403
        
        # Vérifier l'inscription
        user_id = get_current_user_id()
        inscription = InscriptionFormation.query.filter_by(
            formation_id=formation.id,
            utilisateur_id=user_id
        ).first()
        
        if not inscription and not lecon.gratuit:
            return jsonify({
                'success': False,
                'message': 'Vous devez vous inscrire à la formation pour accéder à cette leçon'
            }), 403
        
        lecon_data = lecon.to_dict()
        
        # Ajouter la progression si inscription existe
        if inscription:
            progression = ProgressionLecon.query.filter_by(
                inscription_id=inscription.id,
                lecon_id=lecon_id
            ).first()
            
            if progression:
                lecon_data['progression'] = progression.to_dict()
            else:
                lecon_data['progression'] = None
        
        return jsonify({
            'success': True,
            'lecon': lecon_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération de la leçon: {str(e)}'
        }), 500

@elearning_bp.route('/lecons/<int:lecon_id>/commencer', methods=['POST'])
@subscription_required
def commencer_lecon(lecon_id):
    """Marque le début d'une leçon"""
    try:
        lecon = Lecon.query.get(lecon_id)
        if not lecon:
            return jsonify({
                'success': False,
                'message': 'Leçon non trouvée'
            }), 404
        
        user_id = get_current_user_id()
        formation = lecon.module.formation
        
        inscription = InscriptionFormation.query.filter_by(
            formation_id=formation.id,
            utilisateur_id=user_id
        ).first()
        
        if not inscription:
            return jsonify({
                'success': False,
                'message': 'Vous devez vous inscrire à la formation'
            }), 403
        
        # Créer ou mettre à jour la progression
        progression = ProgressionLecon.query.filter_by(
            inscription_id=inscription.id,
            lecon_id=lecon_id
        ).first()
        
        if not progression:
            progression = ProgressionLecon(
                inscription_id=inscription.id,
                lecon_id=lecon_id,
                utilisateur_id=user_id,
                commence=True,
                date_debut=datetime.utcnow()
            )
            db.session.add(progression)
        elif not progression.commence:
            progression.commence = True
            progression.date_debut = datetime.utcnow()
        
        # Mettre à jour le statut de l'inscription
        if inscription.statut == StatutProgression.NON_COMMENCE:
            inscription.statut = StatutProgression.EN_COURS
            inscription.date_debut = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leçon commencée',
            'progression': progression.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors du démarrage de la leçon: {str(e)}'
        }), 500

@elearning_bp.route('/lecons/<int:lecon_id>/terminer', methods=['POST'])
@subscription_required
def terminer_lecon(lecon_id):
    """Marque la fin d'une leçon"""
    try:
        data = request.get_json() or {}
        temps_passe = data.get('temps_passe', 0)  # en secondes
        
        lecon = Lecon.query.get(lecon_id)
        if not lecon:
            return jsonify({
                'success': False,
                'message': 'Leçon non trouvée'
            }), 404
        
        user_id = get_current_user_id()
        formation = lecon.module.formation
        
        inscription = InscriptionFormation.query.filter_by(
            formation_id=formation.id,
            utilisateur_id=user_id
        ).first()
        
        if not inscription:
            return jsonify({
                'success': False,
                'message': 'Inscription non trouvée'
            }), 403
        
        # Mettre à jour la progression
        progression = ProgressionLecon.query.filter_by(
            inscription_id=inscription.id,
            lecon_id=lecon_id
        ).first()
        
        if not progression:
            return jsonify({
                'success': False,
                'message': 'Progression non trouvée'
            }), 404
        
        progression.termine = True
        progression.date_fin = datetime.utcnow()
        progression.temps_passe = temps_passe
        
        # Mettre à jour le temps total de l'inscription
        inscription.temps_passe += temps_passe // 60  # conversion en minutes
        
        # Recalculer la progression globale
        inscription.pourcentage_completion = calculate_progression(inscription)
        
        # Vérifier si la formation est terminée
        if inscription.pourcentage_completion >= 100:
            inscription.statut = StatutProgression.TERMINE
            inscription.date_fin = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leçon terminée',
            'progression': progression.to_dict(),
            'inscription': {
                'pourcentage_completion': inscription.pourcentage_completion,
                'statut': inscription.statut.value
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la finalisation de la leçon: {str(e)}'
        }), 500

# ============================
# ENDPOINTS QUIZ
# ============================

@elearning_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
@subscription_required
def get_quiz_detail(quiz_id):
    """Récupère le détail d'un quiz avec ses questions"""
    try:
        quiz = Quiz.query.get(quiz_id)
        
        if not quiz:
            return jsonify({
                'success': False,
                'message': 'Quiz non trouvé'
            }), 404
        
        # Vérifier l'accès
        formation = quiz.lecon.module.formation
        user_plan = getattr(g, 'current_subscription', {}).get('plan', {}).get('type_plan', 'gratuit')
        
        if not check_formation_access(formation, user_plan):
            return jsonify({
                'success': False,
                'message': f'Ce quiz nécessite un abonnement {formation.plan_requis}'
            }), 403
        
        user_id = get_current_user_id()
        
        # Vérifier le nombre de tentatives
        nb_tentatives = TentativeQuiz.query.filter_by(
            quiz_id=quiz_id,
            utilisateur_id=user_id
        ).count()
        
        if nb_tentatives >= quiz.tentatives_max:
            return jsonify({
                'success': False,
                'message': f'Nombre maximum de tentatives atteint ({quiz.tentatives_max})'
            }), 403
        
        quiz_data = quiz.to_dict()
        quiz_data['questions'] = [q.to_dict(include_answers=False) for q in quiz.questions]
        quiz_data['tentatives_restantes'] = quiz.tentatives_max - nb_tentatives
        
        return jsonify({
            'success': True,
            'quiz': quiz_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération du quiz: {str(e)}'
        }), 500

@elearning_bp.route('/quiz/<int:quiz_id>/commencer', methods=['POST'])
@subscription_required
def commencer_quiz(quiz_id):
    """Démarre une nouvelle tentative de quiz"""
    try:
        quiz = Quiz.query.get(quiz_id)
        
        if not quiz:
            return jsonify({
                'success': False,
                'message': 'Quiz non trouvé'
            }), 404
        
        user_id = get_current_user_id()
        
        # Vérifier les tentatives
        nb_tentatives = TentativeQuiz.query.filter_by(
            quiz_id=quiz_id,
            utilisateur_id=user_id
        ).count()
        
        if nb_tentatives >= quiz.tentatives_max:
            return jsonify({
                'success': False,
                'message': 'Nombre maximum de tentatives atteint'
            }), 403
        
        # Créer une nouvelle tentative
        tentative = TentativeQuiz(
            quiz_id=quiz_id,
            utilisateur_id=user_id,
            date_debut=datetime.utcnow()
        )
        
        db.session.add(tentative)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quiz commencé',
            'tentative_id': tentative.id,
            'temps_limite': quiz.temps_limite
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors du démarrage du quiz: {str(e)}'
        }), 500

@elearning_bp.route('/quiz/<int:quiz_id>/soumettre', methods=['POST'])
@subscription_required
def soumettre_quiz(quiz_id):
    """Soumet les réponses d'un quiz"""
    try:
        data = request.get_json()
        tentative_id = data.get('tentative_id')
        reponses = data.get('reponses', {})  # {question_id: reponse}
        
        if not tentative_id:
            return jsonify({
                'success': False,
                'message': 'ID de tentative manquant'
            }), 400
        
        tentative = TentativeQuiz.query.get(tentative_id)
        
        if not tentative or tentative.quiz_id != quiz_id:
            return jsonify({
                'success': False,
                'message': 'Tentative non trouvée'
            }), 404
        
        if tentative.date_fin:
            return jsonify({
                'success': False,
                'message': 'Quiz déjà soumis'
            }), 400
        
        quiz = tentative.quiz
        
        # Calculer le score
        points_obtenus = 0
        points_total = 0
        resultats_questions = []
        
        for question in quiz.questions:
            points_total += question.points
            reponse_utilisateur = reponses.get(str(question.id), "")
            
            correct = False
            if question.type_question == TypeQuiz.QCM:
                # Pour QCM, vérifier si la réponse correspond à un choix correct
                choix = question.get_choix()
                for choix_item in choix:
                    if choix_item['texte'] == reponse_utilisateur and choix_item['correct']:
                        correct = True
                        break
            elif question.type_question == TypeQuiz.VRAI_FAUX:
                correct = reponse_utilisateur.lower() == question.reponse_correcte.lower()
            elif question.type_question == TypeQuiz.REPONSE_LIBRE:
                correct = reponse_utilisateur.strip().lower() == question.reponse_correcte.strip().lower()
            
            if correct:
                points_obtenus += question.points
            
            resultats_questions.append({
                'question_id': question.id,
                'correct': correct,
                'reponse_utilisateur': reponse_utilisateur,
                'reponse_correcte': question.reponse_correcte,
                'explication': question.explication,
                'points': question.points if correct else 0
            })
        
        # Calculer les notes
        note = points_obtenus / points_total if points_total > 0 else 0
        note_sur_20 = note * 20
        reussi = note >= quiz.note_minimum
        
        # Mettre à jour la tentative
        tentative.note = note
        tentative.note_sur_20 = note_sur_20
        tentative.reussi = reussi
        tentative.date_fin = datetime.utcnow()
        tentative.duree_secondes = int((tentative.date_fin - tentative.date_debut).total_seconds())
        tentative.reponses_json = json.dumps(reponses)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quiz soumis avec succès',
            'resultat': {
                'note': note,
                'note_sur_20': note_sur_20,
                'reussi': reussi,
                'points_obtenus': points_obtenus,
                'points_total': points_total,
                'duree_secondes': tentative.duree_secondes,
                'questions': resultats_questions
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la soumission du quiz: {str(e)}'
        }), 500

# ============================
# ENDPOINTS PROGRESSION
# ============================

@elearning_bp.route('/mes-formations', methods=['GET'])
@subscription_required
def get_mes_formations():
    """Récupère les formations de l'utilisateur connecté"""
    try:
        user_id = get_current_user_id()
        
        inscriptions = InscriptionFormation.query.filter_by(
            utilisateur_id=user_id
        ).order_by(InscriptionFormation.date_inscription.desc()).all()
        
        formations_data = []
        for inscription in inscriptions:
            formation_dict = inscription.formation.to_dict()
            formation_dict['inscription'] = {
                'id': inscription.id,
                'statut': inscription.statut.value,
                'date_inscription': inscription.date_inscription.isoformat(),
                'pourcentage_completion': calculate_progression(inscription),
                'temps_passe': inscription.temps_passe
            }
            formations_data.append(formation_dict)
        
        return jsonify({
            'success': True,
            'formations': formations_data,
            'total': len(formations_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des formations: {str(e)}'
        }), 500

@elearning_bp.route('/mes-certificats', methods=['GET'])
@subscription_required
def get_mes_certificats():
    """Récupère les certificats de l'utilisateur"""
    try:
        user_id = get_current_user_id()
        
        certificats = Certificat.query.filter_by(
            utilisateur_id=user_id
        ).order_by(Certificat.date_obtention.desc()).all()
        
        return jsonify({
            'success': True,
            'certificats': [cert.to_dict() for cert in certificats],
            'total': len(certificats)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des certificats: {str(e)}'
        }), 500

# ============================
# ENDPOINTS ÉVALUATIONS
# ============================

@elearning_bp.route('/formations/<int:formation_id>/evaluer', methods=['POST'])
@subscription_required
def evaluer_formation(formation_id):
    """Permet d'évaluer une formation"""
    try:
        data = request.get_json()
        note = data.get('note')  # 1-5
        commentaire = data.get('commentaire', '')
        note_contenu = data.get('note_contenu')
        note_pedagogie = data.get('note_pedagogie')
        note_pratique = data.get('note_pratique')
        
        if not note or note < 1 or note > 5:
            return jsonify({
                'success': False,
                'message': 'Note invalide (doit être entre 1 et 5)'
            }), 400
        
        formation = Formation.query.get(formation_id)
        if not formation:
            return jsonify({
                'success': False,
                'message': 'Formation non trouvée'
            }), 404
        
        user_id = get_current_user_id()
        
        # Vérifier que l'utilisateur a terminé la formation
        inscription = InscriptionFormation.query.filter_by(
            formation_id=formation_id,
            utilisateur_id=user_id
        ).first()
        
        if not inscription or inscription.statut != StatutProgression.TERMINE:
            return jsonify({
                'success': False,
                'message': 'Vous devez terminer la formation pour l\'évaluer'
            }), 403
        
        # Vérifier si déjà évalué
        evaluation_existante = EvaluationFormation.query.filter_by(
            formation_id=formation_id,
            utilisateur_id=user_id
        ).first()
        
        if evaluation_existante:
            # Mettre à jour l'évaluation existante
            evaluation_existante.note = note
            evaluation_existante.commentaire = commentaire
            evaluation_existante.note_contenu = note_contenu
            evaluation_existante.note_pedagogie = note_pedagogie
            evaluation_existante.note_pratique = note_pratique
            evaluation_existante.date_evaluation = datetime.utcnow()
            
            evaluation = evaluation_existante
        else:
            # Créer nouvelle évaluation
            evaluation = EvaluationFormation(
                formation_id=formation_id,
                utilisateur_id=user_id,
                note=note,
                commentaire=commentaire,
                note_contenu=note_contenu,
                note_pedagogie=note_pedagogie,
                note_pratique=note_pratique
            )
            db.session.add(evaluation)
            formation.nb_evaluations += 1
        
        # Recalculer la note moyenne de la formation
        evaluations = EvaluationFormation.query.filter_by(formation_id=formation_id).all()
        if evaluations:
            formation.note_moyenne = sum(eval.note for eval in evaluations) / len(evaluations)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Évaluation enregistrée',
            'evaluation': evaluation.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'évaluation: {str(e)}'
        }), 500

# ============================
# ENDPOINTS CERTIFICATS
# ============================

@elearning_bp.route('/formations/<int:formation_id>/certificat', methods=['POST'])
@subscription_required
def generer_certificat(formation_id):
    """Génère un certificat pour une formation terminée"""
    try:
        data = request.get_json() or {}
        nom_beneficiaire = data.get('nom_beneficiaire', '').strip()
        
        if not nom_beneficiaire:
            return jsonify({
                'success': False,
                'message': 'Nom du bénéficiaire requis'
            }), 400
        
        formation = Formation.query.get(formation_id)
        if not formation:
            return jsonify({
                'success': False,
                'message': 'Formation non trouvée'
            }), 404
        
        user_id = get_current_user_id()
        
        # Vérifier la limite de certificats selon le plan
        cert_allowed, cert_message = check_certificate_generation(user_id)
        if not cert_allowed:
            return jsonify({
                'success': False,
                'message': cert_message,
                'upgrade_required': True
            }), 403
        
        # Vérifier que la formation est terminée
        inscription = InscriptionFormation.query.filter_by(
            formation_id=formation_id,
            utilisateur_id=user_id,
            statut=StatutProgression.TERMINE
        ).first()
        
        if not inscription:
            return jsonify({
                'success': False,
                'message': 'Vous devez terminer la formation pour obtenir le certificat'
            }), 403
        
        # Vérifier si certificat existe déjà
        certificat_existant = Certificat.query.filter_by(
            formation_id=formation_id,
            utilisateur_id=user_id
        ).first()
        
        if certificat_existant:
            return jsonify({
                'success': True,
                'message': 'Certificat déjà généré',
                'certificat': certificat_existant.to_dict()
            })
        
        # Calculer la note finale (moyenne des quiz réussis)
        note_finale = 0.75  # Note par défaut si pas de quiz
        
        # TODO: Calculer la vraie note finale basée sur les quiz
        tentatives_reussies = TentativeQuiz.query.join(Quiz).join(Lecon).join(ModuleFormation).filter(
            ModuleFormation.formation_id == formation_id,
            TentativeQuiz.utilisateur_id == user_id,
            TentativeQuiz.reussi == True
        ).all()
        
        if tentatives_reussies:
            note_finale = sum(t.note for t in tentatives_reussies) / len(tentatives_reussies)
        
        # Créer le certificat
        certificat = Certificat(
            formation_id=formation_id,
            utilisateur_id=user_id,
            nom_beneficiaire=nom_beneficiaire,
            statut=StatutCertificat.VALIDE,
            note_finale=note_finale
        )
        
        # Générer le numéro et la mention
        certificat.numero_certificat = certificat.generer_numero()
        certificat.mention = certificat.calculer_mention(note_finale)
        
        # Générer le PDF du certificat
        if CertificateGenerator:
            try:
                # Préparer les données pour le générateur
                certificat_data = {
                    'numero_certificat': certificat.numero_certificat,
                    'nom_beneficiaire': nom_beneficiaire,
                    'formation_titre': formation.titre,
                    'categorie_nom': formation.categorie.nom,
                    'duree_formation': formation.duree_estimee // 60,  # Conversion en heures
                    'date_obtention': datetime.utcnow().isoformat(),
                    'note_finale': note_finale,
                    'mention': certificat.mention
                }
                
                # Générer le PDF
                generator = CertificateGenerator()
                pdf_content = generator.generate_certificate(certificat_data)
                
                # Sauvegarder le fichier PDF
                certificates_dir = os.path.join(current_app.instance_path, 'certificates')
                os.makedirs(certificates_dir, exist_ok=True)
                
                pdf_filename = f"certificat_{certificat.numero_certificat}.pdf"
                pdf_path = os.path.join(certificates_dir, pdf_filename)
                
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Stocker le chemin relatif dans la base
                certificat.fichier_pdf = f"certificates/{pdf_filename}"
                
            except Exception as e:
                current_app.logger.error(f"Erreur génération PDF: {str(e)}")
                # Continue sans le PDF en cas d'erreur
        
        db.session.add(certificat)
        
        # Mettre à jour le statut de l'inscription
        inscription.statut = StatutProgression.CERTIFIE
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Certificat généré avec succès',
            'certificat': certificat.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la génération du certificat: {str(e)}'
        }), 500

@elearning_bp.route('/certificats/<string:numero_certificat>/telecharger', methods=['GET'])
@subscription_required
def telecharger_certificat(numero_certificat):
    """Télécharge le PDF d'un certificat"""
    try:
        user_id = get_current_user_id()
        
        # Vérifier l'accès au téléchargement PDF selon le plan
        if not check_pdf_download_access(user_id):
            return jsonify({
                'success': False,
                'message': 'Le téléchargement PDF nécessite un abonnement Professionnel ou Enterprise',
                'upgrade_required': True
            }), 403
        
        # Vérifier que le certificat appartient à l'utilisateur
        certificat = Certificat.query.filter_by(
            numero_certificat=numero_certificat,
            utilisateur_id=user_id
        ).first()
        
        if not certificat:
            return jsonify({
                'success': False,
                'message': 'Certificat non trouvé ou non autorisé'
            }), 404
        
        if not certificat.fichier_pdf:
            return jsonify({
                'success': False,
                'message': 'PDF du certificat non disponible'
            }), 404
        
        # Chemin complet du fichier PDF
        pdf_path = os.path.join(current_app.instance_path, certificat.fichier_pdf)
        
        if not os.path.exists(pdf_path):
            # Régénérer le PDF si le fichier n'existe pas
            if CertificateGenerator:
                try:
                    certificat_data = {
                        'numero_certificat': certificat.numero_certificat,
                        'nom_beneficiaire': certificat.nom_beneficiaire,
                        'formation_titre': certificat.formation.titre,
                        'categorie_nom': certificat.formation.categorie.nom,
                        'duree_formation': certificat.formation.duree_estimee // 60,
                        'date_obtention': certificat.date_obtention.isoformat(),
                        'note_finale': certificat.note_finale,
                        'mention': certificat.mention
                    }
                    
                    generator = CertificateGenerator()
                    pdf_content = generator.generate_certificate(certificat_data)
                    
                    # Créer le dossier si nécessaire
                    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                    
                    # Sauvegarder le fichier
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_content)
                        
                except Exception as e:
                    current_app.logger.error(f"Erreur régénération PDF: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': 'Erreur lors de la génération du PDF'
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'message': 'Service de génération PDF non disponible'
                }), 500
        
        # Envoyer le fichier PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"certificat_{certificat.numero_certificat}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du téléchargement: {str(e)}'
        }), 500

@elearning_bp.route('/certificats/<string:numero_certificat>/verifier', methods=['GET'])
def verifier_certificat(numero_certificat):
    """Vérifie l'authenticité d'un certificat"""
    try:
        certificat = Certificat.query.filter_by(numero_certificat=numero_certificat).first()
        
        if not certificat:
            return jsonify({
                'success': False,
                'message': 'Certificat non trouvé'
            }), 404
        
        est_valide = (
            certificat.statut == StatutCertificat.VALIDE and
            (not certificat.date_expiration or certificat.date_expiration > datetime.utcnow())
        )
        
        return jsonify({
            'success': True,
            'certificat': {
                'numero_certificat': certificat.numero_certificat,
                'nom_beneficiaire': certificat.nom_beneficiaire,
                'formation': certificat.formation.titre,
                'date_obtention': certificat.date_obtention.isoformat(),
                'note_finale': certificat.note_finale,
                'mention': certificat.mention,
                'est_valide': est_valide,
                'statut': certificat.statut.value
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la vérification: {str(e)}'
        }), 500

# ============================
# ENDPOINTS PLAN ET LIMITATIONS
# ============================

@elearning_bp.route('/mon-plan', methods=['GET'])
@subscription_required
def get_user_plan_info():
    """Récupère les informations du plan et limitations de l'utilisateur"""
    try:
        user_id = get_current_user_id()
        limitations = get_user_limitations(user_id)
        
        return jsonify({
            'success': True,
            'plan_info': limitations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des informations: {str(e)}'
        }), 500

# ============================
# ENDPOINTS STATISTIQUES
# ============================

@elearning_bp.route('/admin/statistiques', methods=['GET'])
@plan_required('enterprise')  # Seuls les admins Enterprise peuvent voir les stats
def get_statistiques_elearning():
    """Récupère les statistiques du système e-learning"""
    try:
        stats = {
            'formations': {
                'total': Formation.query.count(),
                'publiees': Formation.query.filter_by(publie=True).count(),
                'par_niveau': {}
            },
            'inscriptions': {
                'total': InscriptionFormation.query.count(),
                'actives': InscriptionFormation.query.filter_by(statut=StatutProgression.EN_COURS).count(),
                'terminees': InscriptionFormation.query.filter_by(statut=StatutProgression.TERMINE).count(),
                'certifiees': InscriptionFormation.query.filter_by(statut=StatutProgression.CERTIFIE).count()
            },
            'quiz': {
                'total': Quiz.query.count(),
                'tentatives_total': TentativeQuiz.query.count(),
                'tentatives_reussies': TentativeQuiz.query.filter_by(reussi=True).count(),
                'taux_reussite': 0
            },
            'certificats': {
                'total': Certificat.query.count(),
                'valides': Certificat.query.filter_by(statut=StatutCertificat.VALIDE).count()
            }
        }
        
        # Calcul du taux de réussite des quiz
        if stats['quiz']['tentatives_total'] > 0:
            stats['quiz']['taux_reussite'] = (
                stats['quiz']['tentatives_reussies'] / stats['quiz']['tentatives_total']
            ) * 100
        
        # Répartition par niveau
        for niveau in NiveauDifficulte:
            count = Formation.query.filter_by(niveau=niveau, publie=True).count()
            stats['formations']['par_niveau'][niveau.value] = count
        
        return jsonify({
            'success': True,
            'statistiques': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des statistiques: {str(e)}'
        }), 500

# ============================
# GESTION D'ERREURS
# ============================

@elearning_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'message': 'Ressource non trouvée'
    }), 404

@elearning_bp.errorhandler(403)
def forbidden_error(error):
    return jsonify({
        'success': False,
        'message': 'Accès interdit'
    }), 403

@elearning_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'message': 'Erreur interne du serveur'
    }), 500

if __name__ == '__main__':
    print("📚 API E-Learning ComptaEBNL-IA - EBNL de l'espace OHADA")
    print("Endpoints disponibles:")
    print("  • GET  /categories - Liste des catégories")
    print("  • GET  /formations - Liste des formations") 
    print("  • GET  /formations/<id> - Détail formation")
    print("  • POST /formations/<id>/inscrire - Inscription")
    print("  • GET  /lecons/<id> - Détail leçon")
    print("  • POST /lecons/<id>/commencer - Commencer leçon")
    print("  • POST /lecons/<id>/terminer - Terminer leçon")
    print("  • GET  /quiz/<id> - Détail quiz")
    print("  • POST /quiz/<id>/commencer - Commencer quiz")
    print("  • POST /quiz/<id>/soumettre - Soumettre quiz")
    print("  • GET  /mes-formations - Mes formations")
    print("  • GET  /mes-certificats - Mes certificats")
    print("  • POST /formations/<id>/evaluer - Évaluer formation")
    print("  • POST /formations/<id>/certificat - Générer certificat")
    print("  • GET  /certificats/<numero>/verifier - Vérifier certificat")
    print("  • GET  /admin/statistiques - Statistiques (admin)")