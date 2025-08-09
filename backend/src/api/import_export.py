#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Import/Export
=================

Ce module gère l'import et l'export de données comptables :
- Import/Export CSV et Excel
- Export des états financiers (PDF, Excel)
- Import d'écritures comptables en lot
- Export du plan comptable
- Formats FEC (Fichier des Écritures Comptables)

Auteur: ComptaEBNL-IA
Date: 2025
"""

from flask import Blueprint, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
import csv
import json
import io
import os
from datetime import datetime, date
from decimal import Decimal
import tempfile

from models import db, PlanComptable, EcritureComptable, LigneEcriture, ExerciceComptable, JournalComptable

# Création du blueprint
import_export_bp = Blueprint('import_export', __name__)

# Configuration des types de fichiers autorisés
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_csv_headers(headers, required_headers):
    """Valide que les en-têtes CSV requis sont présents"""
    missing_headers = set(required_headers) - set(headers)
    if missing_headers:
        return False, f"En-têtes manquants: {', '.join(missing_headers)}"
    return True, None

@import_export_bp.route('/export/plan-comptable', methods=['GET'])
def export_plan_comptable():
    """Exporte le plan comptable SYCEBNL"""
    try:
        format_export = request.args.get('format', 'csv').lower()  # csv, json, xlsx
        classe_filter = request.args.get('classe', type=int)
        actif_only = request.args.get('actif_only', 'false').lower() == 'true'
        
        print(f"📤 Export plan comptable (format: {format_export})")
        
        # Construction de la requête
        query = PlanComptable.query
        
        if classe_filter:
            query = query.filter(PlanComptable.classe == classe_filter)
        
        if actif_only:
            query = query.filter(PlanComptable.actif == True)
        
        comptes = query.order_by(PlanComptable.numero_compte).all()
        
        if format_export == 'json':
            # Export JSON
            data = {
                'meta': {
                    'export_date': datetime.now().isoformat(),
                    'total_comptes': len(comptes),
                    'format': 'SYCEBNL',
                    'classe_filter': classe_filter,
                    'actif_only': actif_only
                },
                'comptes': [compte.to_dict() for compte in comptes]
            }
            
            response = make_response(jsonify(data))
            response.headers['Content-Disposition'] = f'attachment; filename=plan_comptable_sycebnl_{datetime.now().strftime("%Y%m%d")}.json'
            return response
            
        elif format_export == 'csv':
            # Export CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # En-têtes CSV
            headers = ['numero_compte', 'libelle_compte', 'classe', 'niveau', 'parent_id', 'actif', 'observations']
            writer.writerow(headers)
            
            # Données
            for compte in comptes:
                writer.writerow([
                    compte.numero_compte,
                    compte.libelle_compte,
                    compte.classe,
                    compte.niveau,
                    compte.parent_id or '',
                    'Oui' if compte.actif else 'Non',
                    compte.observations or ''
                ])
            
            # Créer la réponse
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=plan_comptable_sycebnl_{datetime.now().strftime("%Y%m%d")}.csv'
            
            return response
        
        else:
            return jsonify({
                'success': False,
                'error': f'Format non supporté: {format_export}',
                'formats_supportes': ['csv', 'json']
            }), 400
        
    except Exception as e:
        print(f"❌ Erreur export plan comptable: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'export du plan comptable'
        }), 500

@import_export_bp.route('/export/ecritures', methods=['GET'])
def export_ecritures():
    """Exporte les écritures comptables"""
    try:
        format_export = request.args.get('format', 'csv').lower()
        exercice_id = request.args.get('exercice_id', type=int)
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        journal = request.args.get('journal')
        statut = request.args.get('statut', 'valide')
        
        print(f"📤 Export écritures (format: {format_export})")
        
        # Construction de la requête
        query = EcritureComptable.query
        
        if exercice_id:
            query = query.filter(EcritureComptable.exercice_id == exercice_id)
        
        if date_debut:
            query = query.filter(EcritureComptable.date_ecriture >= date_debut)
        
        if date_fin:
            query = query.filter(EcritureComptable.date_ecriture <= date_fin)
        
        if journal:
            query = query.filter(EcritureComptable.journal == journal)
        
        if statut:
            query = query.filter(EcritureComptable.statut == statut)
        
        ecritures = query.order_by(EcritureComptable.date_ecriture, EcritureComptable.numero_ecriture).all()
        
        if format_export == 'csv':
            # Export CSV détaillé (une ligne par ligne d'écriture)
            output = io.StringIO()
            writer = csv.writer(output)
            
            # En-têtes CSV
            headers = [
                'numero_ecriture', 'date_ecriture', 'journal', 'libelle_ecriture',
                'piece_justificative', 'numero_compte', 'libelle_compte', 'libelle_ligne',
                'debit', 'credit', 'statut', 'exercice_id'
            ]
            writer.writerow(headers)
            
            # Données
            for ecriture in ecritures:
                for ligne in ecriture.lignes:
                    writer.writerow([
                        ecriture.numero_ecriture,
                        ecriture.date_ecriture.strftime('%Y-%m-%d'),
                        ecriture.journal,
                        ecriture.libelle,
                        ecriture.piece_justificative or '',
                        ligne.compte.numero_compte,
                        ligne.compte.libelle_compte,
                        ligne.libelle,
                        float(ligne.debit),
                        float(ligne.credit),
                        ecriture.statut,
                        ecriture.exercice_id
                    ])
            
            # Créer la réponse
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=ecritures_{datetime.now().strftime("%Y%m%d")}.csv'
            
            return response
            
        elif format_export == 'fec':
            # Export au format FEC (Fichier des Écritures Comptables)
            output = io.StringIO()
            writer = csv.writer(output, delimiter='|')
            
            # En-têtes FEC
            headers = [
                'JournalCode', 'JournalLib', 'EcritureNum', 'EcritureDate',
                'CompteNum', 'CompteLib', 'CompAuxNum', 'CompAuxLib',
                'PieceRef', 'PieceDate', 'EcritureLib', 'Debit', 'Credit',
                'EcritureLet', 'DateLet', 'ValidDate', 'Montantdevise', 'Idevise'
            ]
            writer.writerow(headers)
            
            # Données au format FEC
            for ecriture in ecritures:
                for ligne in ecriture.lignes:
                    writer.writerow([
                        ecriture.journal,
                        '', # JournalLib - à remplir depuis JournalComptable
                        ecriture.numero_ecriture,
                        ecriture.date_ecriture.strftime('%Y%m%d'),
                        ligne.compte.numero_compte,
                        ligne.compte.libelle_compte,
                        '', # CompAuxNum
                        '', # CompAuxLib
                        ecriture.piece_justificative or '',
                        ecriture.date_ecriture.strftime('%Y%m%d'),
                        ligne.libelle,
                        f"{ligne.debit:.2f}".replace('.', ','),
                        f"{ligne.credit:.2f}".replace('.', ','),
                        '', # EcritureLet
                        '', # DateLet
                        ecriture.date_validation.strftime('%Y%m%d') if ecriture.date_validation else '',
                        '', # Montantdevise
                        '' # Idevise
                    ])
            
            # Créer la réponse
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/plain; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=FEC_{datetime.now().strftime("%Y%m%d")}.txt'
            
            return response
        
        else:
            return jsonify({
                'success': False,
                'error': f'Format non supporté: {format_export}',
                'formats_supportes': ['csv', 'fec']
            }), 400
        
    except Exception as e:
        print(f"❌ Erreur export écritures: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'export des écritures'
        }), 500

@import_export_bp.route('/import/ecritures', methods=['POST'])
def import_ecritures():
    """Importe des écritures comptables depuis un fichier CSV"""
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Aucun fichier sélectionné'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Type de fichier non autorisé',
                'types_autorises': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Paramètres d'import
        exercice_id = request.form.get('exercice_id', type=int)
        mode_import = request.form.get('mode', 'validation')  # validation, force
        delimiter = request.form.get('delimiter', ',')
        
        if not exercice_id:
            return jsonify({
                'success': False,
                'error': 'exercice_id requis'
            }), 400
        
        # Vérifier que l'exercice existe
        exercice = ExerciceComptable.query.get(exercice_id)
        if not exercice:
            return jsonify({
                'success': False,
                'error': f'Exercice {exercice_id} non trouvé'
            }), 404
        
        print(f"📥 Import écritures - Exercice: {exercice.libelle}")
        
        # Lire le fichier CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream, delimiter=delimiter)
        
        # Valider les en-têtes requis
        required_headers = [
            'date_ecriture', 'journal', 'libelle_ecriture', 'numero_compte',
            'libelle_ligne', 'debit', 'credit'
        ]
        
        is_valid, error_msg = validate_csv_headers(csv_reader.fieldnames, required_headers)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Traitement des données
        ecritures_data = {}
        erreurs = []
        ligne_num = 1
        
        for row in csv_reader:
            ligne_num += 1
            
            try:
                # Grouper les lignes par écriture
                key = f"{row['date_ecriture']}_{row['journal']}_{row['libelle_ecriture']}"
                
                if key not in ecritures_data:
                    ecritures_data[key] = {
                        'date_ecriture': row['date_ecriture'],
                        'journal': row['journal'],
                        'libelle': row['libelle_ecriture'],
                        'piece_justificative': row.get('piece_justificative', ''),
                        'lignes': []
                    }
                
                # Valider le compte
                compte = PlanComptable.query.filter_by(numero_compte=row['numero_compte']).first()
                if not compte:
                    erreurs.append(f"Ligne {ligne_num}: Compte {row['numero_compte']} non trouvé")
                    continue
                
                # Valider les montants
                try:
                    debit = Decimal(row['debit']) if row['debit'] else Decimal('0')
                    credit = Decimal(row['credit']) if row['credit'] else Decimal('0')
                except:
                    erreurs.append(f"Ligne {ligne_num}: Montants invalides")
                    continue
                
                if debit < 0 or credit < 0:
                    erreurs.append(f"Ligne {ligne_num}: Montants négatifs non autorisés")
                    continue
                
                if debit > 0 and credit > 0:
                    erreurs.append(f"Ligne {ligne_num}: Une ligne ne peut avoir à la fois débit et crédit")
                    continue
                
                if debit == 0 and credit == 0:
                    erreurs.append(f"Ligne {ligne_num}: Montant requis (débit ou crédit)")
                    continue
                
                # Ajouter la ligne
                ecritures_data[key]['lignes'].append({
                    'compte_id': compte.id,
                    'libelle': row['libelle_ligne'],
                    'debit': float(debit),
                    'credit': float(credit)
                })
                
            except Exception as e:
                erreurs.append(f"Ligne {ligne_num}: Erreur {str(e)}")
        
        # Vérifier les erreurs
        if erreurs and mode_import != 'force':
            return jsonify({
                'success': False,
                'error': 'Erreurs de validation détectées',
                'erreurs': erreurs,
                'message': 'Utilisez mode=force pour ignorer les erreurs'
            }), 400
        
        # Créer les écritures
        ecritures_creees = []
        
        for key, ecriture_data in ecritures_data.items():
            try:
                # Vérifier l'équilibre de l'écriture
                total_debit = sum(ligne['debit'] for ligne in ecriture_data['lignes'])
                total_credit = sum(ligne['credit'] for ligne in ecriture_data['lignes'])
                
                if abs(total_debit - total_credit) > 0.01:
                    if mode_import != 'force':
                        erreurs.append(f"Écriture {key}: Déséquilibre {total_debit - total_credit:.2f}")
                        continue
                
                # Créer l'écriture
                ecriture = EcritureComptable(
                    date_ecriture=datetime.strptime(ecriture_data['date_ecriture'], '%Y-%m-%d').date(),
                    journal=ecriture_data['journal'],
                    libelle=ecriture_data['libelle'],
                    piece_justificative=ecriture_data['piece_justificative'],
                    exercice_id=exercice_id,
                    statut='brouillard'
                )
                
                db.session.add(ecriture)
                db.session.flush()  # Pour obtenir l'ID
                
                # Créer les lignes
                for ligne_data in ecriture_data['lignes']:
                    ligne = LigneEcriture(
                        ecriture_id=ecriture.id,
                        compte_id=ligne_data['compte_id'],
                        libelle=ligne_data['libelle'],
                        debit=Decimal(str(ligne_data['debit'])),
                        credit=Decimal(str(ligne_data['credit']))
                    )
                    db.session.add(ligne)
                
                ecritures_creees.append(ecriture.id)
                
            except Exception as e:
                erreurs.append(f"Écriture {key}: Erreur création {str(e)}")
        
        db.session.commit()
        
        print(f"✅ Import terminé: {len(ecritures_creees)} écritures créées")
        
        return jsonify({
            'success': True,
            'data': {
                'ecritures_creees': len(ecritures_creees),
                'ecritures_ids': ecritures_creees,
                'erreurs': erreurs if mode_import == 'force' else []
            },
            'message': f'{len(ecritures_creees)} écritures importées avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur import écritures: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'import des écritures'
        }), 500

@import_export_bp.route('/export/balance', methods=['GET'])
def export_balance():
    """Exporte la balance comptable"""
    try:
        format_export = request.args.get('format', 'csv').lower()
        exercice_id = request.args.get('exercice_id', type=int)
        date_fin = request.args.get('date_fin', datetime.now().strftime('%Y-%m-%d'))
        
        print(f"📤 Export balance (format: {format_export})")
        
        # Calculer la balance
        from api.comptabilite import calculer_balance_detaillee
        balance_data = calculer_balance_detaillee(exercice_id=exercice_id, date_fin=date_fin)
        
        if format_export == 'csv':
            # Export CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # En-têtes CSV
            headers = [
                'numero_compte', 'libelle_compte', 'classe',
                'debit_precedent', 'credit_precedent', 'solde_precedent',
                'debit_periode', 'credit_periode', 'mouvement_periode',
                'debit_cumule', 'credit_cumule', 'solde_final'
            ]
            writer.writerow(headers)
            
            # Données
            for compte in balance_data.get('comptes', []):
                writer.writerow([
                    compte['numero_compte'],
                    compte['libelle_compte'],
                    compte['classe'],
                    compte.get('debit_precedent', 0),
                    compte.get('credit_precedent', 0),
                    compte.get('solde_precedent', 0),
                    compte.get('debit_periode', 0),
                    compte.get('credit_periode', 0),
                    compte.get('mouvement_periode', 0),
                    compte.get('debit_cumule', 0),
                    compte.get('credit_cumule', 0),
                    compte.get('solde_final', 0)
                ])
            
            # Créer la réponse
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=balance_{datetime.now().strftime("%Y%m%d")}.csv'
            
            return response
        
        else:
            return jsonify({
                'success': False,
                'error': f'Format non supporté: {format_export}',
                'formats_supportes': ['csv']
            }), 400
        
    except Exception as e:
        print(f"❌ Erreur export balance: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'export de la balance'
        }), 500

@import_export_bp.route('/templates/import-ecritures', methods=['GET'])
def get_template_import_ecritures():
    """Génère un modèle CSV pour l'import d'écritures"""
    try:
        print("📋 Génération template import écritures")
        
        # Créer le template CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        headers = [
            'date_ecriture', 'journal', 'libelle_ecriture', 'piece_justificative',
            'numero_compte', 'libelle_ligne', 'debit', 'credit'
        ]
        writer.writerow(headers)
        
        # Exemples de données
        exemples = [
            ['2025-01-15', 'DON', 'Don de Jean Dupont', 'DON-2025-001', '571', 'Encaissement don', '100.00', '0'],
            ['2025-01-15', 'DON', 'Don de Jean Dupont', 'DON-2025-001', '7561', 'Don manuel', '0', '100.00'],
            ['2025-01-16', 'ACH', 'Achat fournitures bureau', 'FACT-2025-001', '6063', 'Fournitures administratives', '50.00', '0'],
            ['2025-01-16', 'ACH', 'Achat fournitures bureau', 'FACT-2025-001', '401', 'Fournisseur ABC', '0', '50.00']
        ]
        
        for exemple in exemples:
            writer.writerow(exemple)
        
        # Créer la réponse
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=template_import_ecritures.csv'
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur génération template: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération du template'
        }), 500

@import_export_bp.route('/formats', methods=['GET'])
def get_formats_supportes():
    """Retourne la liste des formats d'import/export supportés"""
    try:
        formats = {
            'import': {
                'ecritures': ['csv'],
                'plan_comptable': ['csv', 'json']
            },
            'export': {
                'plan_comptable': ['csv', 'json'],
                'ecritures': ['csv', 'fec'],
                'balance': ['csv'],
                'etats_financiers': ['csv', 'json']
            },
            'templates': {
                'import_ecritures': 'csv'
            }
        }
        
        return jsonify({
            'success': True,
            'data': formats,
            'message': 'Formats supportés récupérés'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la récupération des formats'
        }), 500