#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Intelligence Artificielle - OCR et Génération d'Écritures
ComptaEBNL-IA - Agent IA comptable pour entités à but non lucratif
"""

from flask import Blueprint, jsonify, request, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json
from decimal import Decimal

# Import optionnel d'OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

ia_bp = Blueprint('ia', __name__)

# Configuration pour l'upload de fichiers
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Vérifie si le fichier est autorisé"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ia_bp.route('/upload-document', methods=['POST'])
def upload_document():
    """
    Upload et traitement d'un document comptable
    
    Form-data:
    - file: Fichier à traiter (PDF, image)
    - type_document: Type de document (facture, recu, releve_bancaire, etc.)
    """
    try:
        # Vérifier la présence du fichier
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier trouvé',
                'message': 'Le champ "file" est requis'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nom de fichier vide',
                'message': 'Veuillez sélectionner un fichier'
            }), 400
        
        # Vérifier l'extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Type de fichier non autorisé',
                'message': f'Extensions autorisées: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Vérifier la taille (werkzeug limite automatiquement, mais on double-check)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Retour au début
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': 'Fichier trop volumineux',
                'message': f'Taille maximum autorisée: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Sauvegarder le fichier
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Créer le dossier uploads s'il n'existe pas
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Paramètres supplémentaires
        type_document = request.form.get('type_document', 'inconnu')
        
        # Ici on simule le traitement OCR (en attendant l'implémentation réelle)
        document_info = {
            'id': timestamp,
            'filename': filename,
            'filepath': filepath,
            'size': file_size,
            'type_document': type_document,
            'status': 'uploaded',
            'ocr_status': 'pending'
        }
        
        return jsonify({
            'success': True,
            'data': document_info,
            'message': 'Document uploadé avec succès'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'upload du document'
        }), 500

@ia_bp.route('/ocr-document/<document_id>', methods=['POST'])
def process_ocr(document_id):
    """
    Lance le traitement OCR sur un document
    
    En attendant l'implémentation complète de l'OCR, 
    cette fonction simule l'extraction de données
    """
    try:
        # Simulation des données extraites par OCR
        # Dans la vraie implémentation, on utiliserait Tesseract ou une API OCR
        extracted_data = {
            'document_id': document_id,
            'ocr_confidence': 0.95,
            'detected_fields': {
                'date': '2024-01-15',
                'fournisseur': 'SARL BUREAU PLUS',
                'montant_total': '120.50',
                'montant_ht': '100.42',
                'tva': '20.08',
                'numero_facture': 'FAC-2024-001',
                'description': 'Fournitures de bureau - Papier A4, stylos'
            },
            'suggested_accounts': {
                'charge': {
                    'numero': '6064',
                    'libelle': 'Fournitures de bureau',
                    'confidence': 0.9
                },
                'fournisseur': {
                    'numero': '401',
                    'libelle': 'Fournisseurs',
                    'confidence': 0.85
                }
            },
            'status': 'completed'
        }
        
        return jsonify({
            'success': True,
            'data': extracted_data,
            'message': 'OCR traité avec succès'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors du traitement OCR'
        }), 500

@ia_bp.route('/generer-ecriture', methods=['POST'])
def generer_ecriture_ia():
    """
    Génère automatiquement une écriture comptable basée sur les données extraites
    
    Body JSON:
    {
        "type_operation": "achat",
        "fournisseur": "SARL BUREAU PLUS",
        "date": "2024-01-15",
        "montant_ht": 100.42,
        "tva": 20.08,
        "description": "Fournitures de bureau",
        "numero_piece": "FAC-2024-001"
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
        
        # Analyse du type d'opération et génération de l'écriture
        type_operation = data.get('type_operation', '').lower()
        
        if type_operation == 'achat':
            ecriture_generee = generer_ecriture_achat(data)
        elif type_operation == 'vente':
            ecriture_generee = generer_ecriture_vente(data)
        elif type_operation == 'banque':
            ecriture_generee = generer_ecriture_banque(data)
        elif type_operation == 'don':
            ecriture_generee = generer_ecriture_don(data)
        elif type_operation == 'subvention':
            ecriture_generee = generer_ecriture_subvention(data)
        else:
            # Écriture générique
            ecriture_generee = generer_ecriture_generique(data)
        
        return jsonify({
            'success': True,
            'data': ecriture_generee,
            'message': 'Écriture générée automatiquement par l\'IA'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération de l\'écriture'
        }), 500

def generer_ecriture_achat(data):
    """Génère une écriture d'achat (fournisseur)"""
    montant_ht = Decimal(str(data.get('montant_ht', 0)))
    tva = Decimal(str(data.get('tva', 0)))
    montant_ttc = montant_ht + tva
    
    # Sélection intelligente du compte de charge
    description = data.get('description', '').lower()
    compte_charge = '6064'  # Fournitures de bureau par défaut
    
    if 'carburant' in description or 'essence' in description:
        compte_charge = '6025'  # Carburants
    elif 'telephone' in description or 'communication' in description:
        compte_charge = '6261'  # Télécommunications
    elif 'fourniture' in description:
        compte_charge = '6064'  # Fournitures de bureau
    elif 'entretien' in description or 'maintenance' in description:
        compte_charge = '6156'  # Maintenance
    
    lignes = [
        {
            'numero_compte': compte_charge,
            'libelle': data.get('description', 'Achat'),
            'debit': float(montant_ht),
            'credit': 0
        }
    ]
    
    # Ajouter la TVA si présente
    if tva > 0:
        lignes.append({
            'numero_compte': '4456',  # TVA déductible
            'libelle': 'TVA déductible',
            'debit': float(tva),
            'credit': 0
        })
    
    # Compte fournisseur
    lignes.append({
        'numero_compte': '401',
        'libelle': data.get('fournisseur', 'Fournisseur'),
        'debit': 0,
        'credit': float(montant_ttc)
    })
    
    return {
        'date_ecriture': data.get('date'),
        'libelle': f"Achat - {data.get('fournisseur', 'Fournisseur')}",
        'journal': 'ACH',  # Journal des achats
        'piece_justificative': data.get('numero_piece'),
        'lignes': lignes,
        'ia_confidence': 0.9,
        'suggestions': {
            'validation_recommandee': True,
            'comptes_alternatifs': []
        }
    }

def generer_ecriture_vente(data):
    """Génère une écriture de vente"""
    montant_ht = Decimal(str(data.get('montant_ht', 0)))
    tva = Decimal(str(data.get('tva', 0)))
    montant_ttc = montant_ht + tva
    
    lignes = [
        {
            'numero_compte': '411',  # Clients
            'libelle': data.get('client', 'Client'),
            'debit': float(montant_ttc),
            'credit': 0
        },
        {
            'numero_compte': '7011',  # Ventes dans la région
            'libelle': data.get('description', 'Vente'),
            'debit': 0,
            'credit': float(montant_ht)
        }
    ]
    
    # Ajouter la TVA si présente
    if tva > 0:
        lignes.append({
            'numero_compte': '4455',  # TVA collectée
            'libelle': 'TVA collectée',
            'debit': 0,
            'credit': float(tva)
        })
    
    return {
        'date_ecriture': data.get('date'),
        'libelle': f"Vente - {data.get('client', 'Client')}",
        'journal': 'VTE',  # Journal des ventes
        'piece_justificative': data.get('numero_piece'),
        'lignes': lignes,
        'ia_confidence': 0.88
    }

def generer_ecriture_don(data):
    """Génère une écriture de don (spécifique EBNL)"""
    montant = Decimal(str(data.get('montant', 0)))
    type_don = data.get('type_don', 'manuel')
    
    compte_produit = '7561'  # Dons manuels par défaut
    if type_don == 'nature':
        compte_produit = '7562'  # Dons en nature
    elif type_don == 'legs':
        compte_produit = '7563'  # Legs
    
    lignes = [
        {
            'numero_compte': '571',  # Caisse ou banque
            'libelle': 'Encaissement don',
            'debit': float(montant),
            'credit': 0
        },
        {
            'numero_compte': compte_produit,
            'libelle': f"Don - {data.get('donateur', 'Anonyme')}",
            'debit': 0,
            'credit': float(montant)
        }
    ]
    
    return {
        'date_ecriture': data.get('date'),
        'libelle': f"Don - {data.get('donateur', 'Anonyme')}",
        'journal': 'DON',  # Journal spécial dons
        'piece_justificative': data.get('numero_piece'),
        'lignes': lignes,
        'ia_confidence': 0.95,
        'suggestions': {
            'recu_fiscal': True,
            'type_ebnl': 'don'
        }
    }

def generer_ecriture_subvention(data):
    """Génère une écriture de subvention (spécifique EBNL)"""
    montant = Decimal(str(data.get('montant', 0)))
    organisme = data.get('organisme', '').lower()
    
    # Déterminer le compte selon l'organisme
    compte_produit = '7183'  # Subventions versées par des tiers (par défaut)
    if 'etat' in organisme or 'gouvernement' in organisme:
        compte_produit = '7181'  # Subventions versées par l'État
    elif 'international' in organisme or 'unesco' in organisme or 'ue' in organisme:
        compte_produit = '7182'  # Subventions versées par les organismes internationaux
    
    lignes = [
        {
            'numero_compte': '4551',  # Subventions à recevoir
            'libelle': f"Subvention à recevoir - {data.get('organisme')}",
            'debit': float(montant),
            'credit': 0
        },
        {
            'numero_compte': compte_produit,
            'libelle': f"Subvention - {data.get('organisme')}",
            'debit': 0,
            'credit': float(montant)
        }
    ]
    
    return {
        'date_ecriture': data.get('date'),
        'libelle': f"Subvention - {data.get('organisme')}",
        'journal': 'SUB',  # Journal des subventions
        'piece_justificative': data.get('numero_piece'),
        'lignes': lignes,
        'ia_confidence': 0.92,
        'suggestions': {
            'fonds_affectes': True,
            'suivi_projet': data.get('projet')
        }
    }

def generer_ecriture_banque(data):
    """Génère une écriture bancaire générique"""
    montant = Decimal(str(data.get('montant', 0)))
    sens = data.get('sens', 'debit')  # debit ou credit
    
    if sens == 'debit':
        # Encaissement
        lignes = [
            {
                'numero_compte': '521',  # Banque
                'libelle': data.get('description', 'Encaissement'),
                'debit': float(montant),
                'credit': 0
            },
            {
                'numero_compte': '4541',  # Compte d'attente
                'libelle': 'À régulariser',
                'debit': 0,
                'credit': float(montant)
            }
        ]
    else:
        # Décaissement
        lignes = [
            {
                'numero_compte': '4541',  # Compte d'attente
                'libelle': 'À régulariser',
                'debit': float(montant),
                'credit': 0
            },
            {
                'numero_compte': '521',  # Banque
                'libelle': data.get('description', 'Décaissement'),
                'debit': 0,
                'credit': float(montant)
            }
        ]
    
    return {
        'date_ecriture': data.get('date'),
        'libelle': f"Mouvement bancaire - {data.get('description', 'Non précisé')}",
        'journal': 'BQ',  # Journal de banque
        'piece_justificative': data.get('numero_piece'),
        'lignes': lignes,
        'ia_confidence': 0.75,
        'suggestions': {
            'regularisation_necessaire': True
        }
    }

def generer_ecriture_generique(data):
    """Génère une écriture générique quand le type n'est pas reconnu"""
    montant = Decimal(str(data.get('montant', 0)))
    
    lignes = [
        {
            'numero_compte': '4541',  # Compte d'attente débiteur
            'libelle': data.get('description', 'Opération à analyser'),
            'debit': float(montant),
            'credit': 0
        },
        {
            'numero_compte': '4542',  # Compte d'attente créditeur
            'libelle': 'Contrepartie à déterminer',
            'debit': 0,
            'credit': float(montant)
        }
    ]
    
    return {
        'date_ecriture': data.get('date'),
        'libelle': f"Opération à analyser - {data.get('description', 'Non précisé')}",
        'journal': 'OD',  # Opérations diverses
        'piece_justificative': data.get('numero_piece'),
        'lignes': lignes,
        'ia_confidence': 0.6,
        'suggestions': {
            'analyse_manuelle_requise': True,
            'comptes_temporaires': True
        }
    }

@ia_bp.route('/suggestions-compte', methods=['POST'])
def suggestions_compte():
    """
    Suggère des comptes comptables basés sur une description
    
    Body JSON:
    {
        "description": "Achat de carburant pour véhicule de service",
        "montant": 85.50,
        "type_operation": "charge"
    }
    """
    try:
        data = request.get_json()
        description = data.get('description', '').lower()
        type_operation = data.get('type_operation', 'charge').lower()
        
        # Système de suggestions basé sur des mots-clés
        suggestions = []
        
        if type_operation == 'charge':
            suggestions = analyser_charge(description)
        elif type_operation == 'produit':
            suggestions = analyser_produit(description)
        elif type_operation == 'immobilisation':
            suggestions = analyser_immobilisation(description)
        
        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'description_analysee': description,
                'type_operation': type_operation
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération des suggestions'
        }), 500

def analyser_charge(description):
    """Analyse une description pour suggérer des comptes de charge"""
    suggestions = []
    
    # Mapping description -> comptes
    mappings = {
        'carburant|essence|gasoil': ('6025', 'Carburants', 0.95),
        'telephone|communication|internet': ('6261', 'Télécommunications', 0.90),
        'fourniture|papier|stylo|bureau': ('6064', 'Fournitures de bureau', 0.88),
        'entretien|maintenance|reparation': ('6156', 'Maintenance', 0.85),
        'assurance': ('6161', 'Assurances multirisques', 0.92),
        'formation|stage': ('6184', 'Formation', 0.90),
        'transport|taxi|uber': ('6251', 'Voyages et déplacements', 0.87),
        'restaurant|repas': ('6257', 'Réceptions', 0.85),
        'electricite|edf': ('6051', 'Électricité', 0.93),
        'eau|veolia': ('6052', 'Eau', 0.93),
        'salaire|appointement': ('6611', 'Appointements salaires', 0.95),
        'loyer|location': ('6132', 'Locations immobilières', 0.90)
    }
    
    import re
    for pattern, (numero, libelle, confidence) in mappings.items():
        if re.search(pattern, description):
            suggestions.append({
                'numero_compte': numero,
                'libelle_compte': libelle,
                'confidence': confidence,
                'raison': f'Correspondance détectée: "{pattern}"'
            })
    
    # Suggestion par défaut si rien trouvé
    if not suggestions:
        suggestions.append({
            'numero_compte': '6068',
            'libelle_compte': 'Autres matières et fournitures',
            'confidence': 0.5,
            'raison': 'Suggestion par défaut pour charges'
        })
    
    return suggestions

def analyser_produit(description):
    """Analyse une description pour suggérer des comptes de produit"""
    suggestions = []
    
    mappings = {
        'don|donation': ('7561', 'Dons manuels', 0.95),
        'subvention': ('7181', 'Subventions d\'exploitation', 0.92),
        'cotisation|adhesion': ('7561', 'Cotisations des adhérents', 0.90),
        'vente|prestation': ('7011', 'Ventes de marchandises', 0.85),
        'benevola': ('7581', 'Bénévolat', 0.98),
        'legs': ('7563', 'Legs', 0.95)
    }
    
    import re
    for pattern, (numero, libelle, confidence) in mappings.items():
        if re.search(pattern, description):
            suggestions.append({
                'numero_compte': numero,
                'libelle_compte': libelle,
                'confidence': confidence,
                'raison': f'Correspondance détectée: "{pattern}"'
            })
    
    return suggestions

def analyser_immobilisation(description):
    """Analyse une description pour suggérer des comptes d'immobilisation"""
    suggestions = []
    
    mappings = {
        'ordinateur|pc|laptop': ('2131', 'Logiciels', 0.80),
        'vehicule|voiture|camion': ('2182', 'Matériel de transport', 0.95),
        'mobilier|bureau|chaise': ('2184', 'Mobilier', 0.90),
        'batiment|construction': ('213', 'Constructions', 0.92),
        'terrain': ('22', 'Terrains', 0.98)
    }
    
    import re
    for pattern, (numero, libelle, confidence) in mappings.items():
        if re.search(pattern, description):
            suggestions.append({
                'numero_compte': numero,
                'libelle_compte': libelle,
                'confidence': confidence,
                'raison': f'Correspondance détectée: "{pattern}"'
            })
    
    return suggestions

@ia_bp.route('/config-ia', methods=['GET'])
def get_config_ia():
    """Récupère la configuration de l'IA"""
    try:
        config = {
            'ocr_enabled': True,
            'openai_available': OPENAI_AVAILABLE,
            'openai_enabled': OPENAI_AVAILABLE and bool(os.getenv('OPENAI_API_KEY')),
            'max_file_size': MAX_FILE_SIZE,
            'allowed_extensions': list(ALLOWED_EXTENSIONS),
            'confidence_threshold': 0.8,
            'auto_validation_threshold': 0.95,
            'supported_operations': [
                'achat', 'vente', 'don', 'subvention', 'banque'
            ]
        }
        
        return jsonify({
            'success': True,
            'data': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération de la configuration'
        }), 500