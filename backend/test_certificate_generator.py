#!/usr/bin/env python3
"""
Test du générateur de certificats PDF ComptaEBNL-IA
Teste la génération de certificats avec différents scénarios
"""

import sys
import os
from datetime import datetime, timedelta

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from services.certificate_generator import CertificateGenerator
    print("✅ Import du générateur de certificats réussi")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous d'avoir installé les dépendances: pip install reportlab Pillow qrcode[pil]")
    sys.exit(1)

def test_certificate_generation():
    """Test de génération de certificats"""
    print("\n🏆 TESTS GÉNÉRATION CERTIFICATS PDF")
    print("=" * 50)
    
    # Données de test
    test_cases = [
        {
            'nom': 'Formation Fondamentaux EBNL',
            'data': {
                'numero_certificat': 'CEBNL-2025-F001-TEST001',
                'nom_beneficiaire': 'Jean KOUADIO',
                'formation_titre': 'Fondamentaux de la comptabilité EBNL',
                'categorie_nom': 'Comptabilité Générale',
                'duree_formation': 20,
                'date_obtention': datetime.now().isoformat(),
                'note_finale': 0.85,
                'mention': 'Très Bien'
            }
        },
        {
            'nom': 'Formation Plan Comptable',
            'data': {
                'numero_certificat': 'CEBNL-2025-F002-TEST002',
                'nom_beneficiaire': 'Marie TRAORE',
                'formation_titre': 'Maîtrise du Plan Comptable SYCEBNL',
                'categorie_nom': 'Plan Comptable',
                'duree_formation': 15,
                'date_obtention': datetime.now().isoformat(),
                'note_finale': 0.92,
                'mention': 'Excellent',
                'date_expiration': (datetime.now() + timedelta(days=365*3)).isoformat()
            }
        },
        {
            'nom': 'Formation États Financiers',
            'data': {
                'numero_certificat': 'CEBNL-2025-F003-TEST003',
                'nom_beneficiaire': 'Ahmed DIALLO',
                'formation_titre': 'Élaboration des États Financiers EBNL',
                'categorie_nom': 'États Financiers',
                'duree_formation': 25,
                'date_obtention': datetime.now().isoformat(),
                'note_finale': 0.78,
                'mention': 'Bien'
            }
        }
    ]
    
    generator = CertificateGenerator()
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['nom']}")
        print("-" * 30)
        
        try:
            # Générer le PDF
            pdf_content = generator.generate_certificate(test_case['data'])
            
            # Sauvegarder pour inspection
            output_file = f"test_certificat_{i}.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_content)
            
            # Vérifications
            file_size = len(pdf_content)
            
            print(f"✅ PDF généré avec succès")
            print(f"   📄 Fichier: {output_file}")
            print(f"   📊 Taille: {file_size:,} bytes")
            print(f"   👤 Bénéficiaire: {test_case['data']['nom_beneficiaire']}")
            print(f"   🎓 Formation: {test_case['data']['formation_titre']}")
            print(f"   📈 Note: {test_case['data']['note_finale']*20:.1f}/20 ({test_case['data']['mention']})")
            print(f"   🔢 Numéro: {test_case['data']['numero_certificat']}")
            
            results.append({
                'test': test_case['nom'],
                'success': True,
                'file_size': file_size,
                'output_file': output_file
            })
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {str(e)}")
            results.append({
                'test': test_case['nom'],
                'success': False,
                'error': str(e)
            })
    
    return results

def test_certificate_preview():
    """Test de génération d'aperçu"""
    print("\n🖼️ TEST GÉNÉRATION APERÇU")
    print("=" * 30)
    
    try:
        generator = CertificateGenerator()
        
        # Données de test pour l'aperçu
        preview_data = {
            'numero_certificat': 'CEBNL-2025-PREVIEW',
            'nom_beneficiaire': 'Aperçu CERTIFICAT',
            'formation_titre': 'Formation Exemple EBNL',
            'categorie_nom': 'Aperçu',
            'date_obtention': datetime.now().isoformat()
        }
        
        # Générer l'aperçu
        preview_img = generator.generate_certificate_preview(preview_data)
        
        # Sauvegarder l'image
        preview_img.save('test_certificat_apercu.png')
        
        print("✅ Aperçu généré avec succès")
        print("   🖼️ Fichier: test_certificat_apercu.png")
        print(f"   📐 Dimensions: {preview_img.size}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération d'aperçu: {str(e)}")
        return False

def test_qr_code_generation():
    """Test de génération de QR codes"""
    print("\n🔳 TEST GÉNÉRATION QR CODE")
    print("=" * 30)
    
    try:
        import qrcode
        
        # Test simple de QR code
        test_url = "https://comptaebnl-ia.com/verify/CEBNL-2025-TEST"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(test_url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save('test_qr_code.png')
        
        print("✅ QR Code généré avec succès")
        print("   🔳 Fichier: test_qr_code.png")
        print(f"   🔗 URL: {test_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération de QR code: {str(e)}")
        return False

def generate_test_report(results):
    """Génère un rapport de test"""
    print("\n📊 RAPPORT DE TEST")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"📈 Tests exécutés: {total_tests}")
    print(f"✅ Réussis: {successful_tests}")
    print(f"❌ Échoués: {failed_tests}")
    print(f"📊 Taux de réussite: {(successful_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ TESTS ÉCHOUÉS:")
        for result in results:
            if not result['success']:
                print(f"   • {result['test']}: {result.get('error', 'Erreur inconnue')}")
    
    print("\n✅ TESTS RÉUSSIS:")
    total_size = 0
    for result in results:
        if result['success']:
            size = result.get('file_size', 0)
            total_size += size
            print(f"   • {result['test']}: {size:,} bytes")
    
    if total_size > 0:
        print(f"\n📊 Taille totale des PDFs: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    print("\n📁 FICHIERS GÉNÉRÉS:")
    print("   • test_certificat_*.pdf - Certificats de test")
    print("   • test_certificat_apercu.png - Aperçu d'image")
    print("   • test_qr_code.png - QR code de test")

def main():
    """Fonction principale"""
    print("🏆 TEST GÉNÉRATEUR CERTIFICATS COMPTAEBNL-IA")
    print("=" * 60)
    print("Tests du système de génération de certificats PDF")
    print("Spécialisé dans les EBNL de l'espace OHADA")
    print("")
    
    try:
        # Tests de génération de certificats
        results = test_certificate_generation()
        
        # Test d'aperçu
        preview_success = test_certificate_preview()
        
        # Test QR code
        qr_success = test_qr_code_generation()
        
        # Rapport final
        generate_test_report(results)
        
        # Vérifications additionnelles
        print("\n🔍 VÉRIFICATIONS ADDITIONNELLES:")
        print(f"   📷 Génération aperçu: {'✅' if preview_success else '❌'}")
        print(f"   🔳 Génération QR code: {'✅' if qr_success else '❌'}")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS:")
        print("   1. Ouvrez les fichiers PDF générés pour vérifier la qualité")
        print("   2. Testez le QR code avec un lecteur mobile")
        print("   3. Vérifiez que tous les textes sont lisibles")
        print("   4. Contrôlez l'alignement et la mise en page")
        
        success_rate = len([r for r in results if r['success']]) / len(results)
        if success_rate == 1.0 and preview_success and qr_success:
            print("\n🎉 TOUS LES TESTS RÉUSSIS ! Générateur opérationnel.")
            return 0
        else:
            print(f"\n⚠️ Quelques tests ont échoué. Vérifiez les erreurs ci-dessus.")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERREUR CRITIQUE: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())