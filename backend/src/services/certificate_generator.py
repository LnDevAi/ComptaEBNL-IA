"""
Service de génération de certificats PDF pour ComptaEBNL-IA
Génère des certificats officiels avec design professionnel et QR code de vérification
"""

import os
import io
import qrcode
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class CertificateGenerator:
    """Générateur de certificats PDF professionnels"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.width, self.height = landscape(A4)  # Format paysage
        
        # Couleurs de la charte graphique EBNL-OHADA
        self.colors = {
            'primary': HexColor('#1E3A8A'),      # Bleu foncé
            'secondary': HexColor('#3B82F6'),    # Bleu
            'accent': HexColor('#F59E0B'),       # Doré
            'success': HexColor('#10B981'),      # Vert
            'text': HexColor('#1F2937'),         # Gris foncé
            'border': HexColor('#E5E7EB'),       # Gris clair
            'background': HexColor('#F9FAFB')    # Blanc cassé
        }
        
        # Chemins des ressources
        self.assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'certificates')
        os.makedirs(self.assets_dir, exist_ok=True)
        
    def generate_certificate(self, certificat_data, output_path=None):
        """
        Génère un certificat PDF
        
        Args:
            certificat_data (dict): Données du certificat
            output_path (str): Chemin de sortie (optionnel)
            
        Returns:
            bytes: Contenu du PDF généré
        """
        # Préparer le buffer
        buffer = io.BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Créer le contenu
        story = []
        
        # En-tête avec logos
        self._add_header(story, certificat_data)
        
        # Titre principal
        self._add_title(story, certificat_data)
        
        # Corps du certificat
        self._add_body(story, certificat_data)
        
        # Informations de validation
        self._add_validation(story, certificat_data)
        
        # QR Code de vérification
        self._add_qr_code(story, certificat_data)
        
        # Pied de page
        self._add_footer(story, certificat_data)
        
        # Construire le PDF
        doc.build(story, onFirstPage=self._add_watermark, onLaterPages=self._add_watermark)
        
        # Récupérer le contenu
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Sauvegarder si chemin spécifié
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_content)
        
        return pdf_content
    
    def _add_header(self, story, data):
        """Ajoute l'en-tête avec logos et institutions"""
        styles = getSampleStyleSheet()
        
        # Style pour l'en-tête
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.colors['text'],
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # En-tête institutionnel
        header_text = """
        <b>ORGANISATION POUR L'HARMONISATION EN AFRIQUE DU DROIT DES AFFAIRES</b><br/>
        <i>Système Comptable des Entités à But Non Lucratif (SYCEBNL)</i><br/>
        <b>ComptaEBNL-IA - Plateforme de Formation Certifiante</b>
        """
        
        story.append(Paragraph(header_text, header_style))
        story.append(Spacer(1, 0.5*cm))
        
    def _add_title(self, story, data):
        """Ajoute le titre principal du certificat"""
        styles = getSampleStyleSheet()
        
        # Style du titre principal
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            fontSize=28,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        # Style du sous-titre
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=self.colors['accent'],
            alignment=TA_CENTER,
            spaceAfter=40,
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph("CERTIFICAT DE FORMATION", title_style))
        story.append(Paragraph("Comptabilité des Entités à But Non Lucratif", subtitle_style))
        
    def _add_body(self, story, data):
        """Ajoute le corps principal du certificat"""
        styles = getSampleStyleSheet()
        
        # Style pour le texte principal
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=self.colors['text'],
            alignment=TA_CENTER,
            leading=20,
            spaceAfter=20
        )
        
        # Style pour le nom du bénéficiaire
        name_style = ParagraphStyle(
            'NameStyle',
            parent=styles['Normal'],
            fontSize=22,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=20,
            spaceBefore=20
        )
        
        # Style pour la formation
        formation_style = ParagraphStyle(
            'FormationStyle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=self.colors['secondary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=30
        )
        
        # Texte de certification
        certification_text = "Certifie que"
        story.append(Paragraph(certification_text, body_style))
        
        # Nom du bénéficiaire
        nom_beneficiaire = data.get('nom_beneficiaire', 'N/A')
        story.append(Paragraph(f"<u>{nom_beneficiaire}</u>", name_style))
        
        # Texte de réussite
        success_text = "a suivi avec succès la formation"
        story.append(Paragraph(success_text, body_style))
        
        # Titre de la formation
        titre_formation = data.get('formation_titre', 'Formation EBNL')
        story.append(Paragraph(f'"{titre_formation}"', formation_style))
        
        # Catégorie et durée
        categorie = data.get('categorie_nom', 'Comptabilité EBNL')
        duree = data.get('duree_formation', 0)
        details_text = f"<b>Catégorie:</b> {categorie} | <b>Durée:</b> {duree} heures"
        story.append(Paragraph(details_text, body_style))
        
    def _add_validation(self, story, data):
        """Ajoute les informations de validation"""
        styles = getSampleStyleSheet()
        
        # Style pour les détails
        detail_style = ParagraphStyle(
            'DetailStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=self.colors['text'],
            alignment=TA_LEFT,
            spaceAfter=10
        )
        
        # Créer un tableau pour les informations de validation
        validation_data = [
            ['Numéro de certificat:', data.get('numero_certificat', 'N/A')],
            ['Date d\'obtention:', self._format_date(data.get('date_obtention'))],
            ['Note finale:', f"{data.get('note_finale', 0) * 20:.1f}/20"],
            ['Mention:', data.get('mention', 'N/A')],
            ['Validité:', self._format_date(data.get('date_expiration')) if data.get('date_expiration') else 'Permanente']
        ]
        
        validation_table = Table(validation_data, colWidths=[4*cm, 6*cm])
        validation_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), self.colors['primary']),
            ('TEXTCOLOR', (1, 0), (1, -1), self.colors['text']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(Spacer(1, 1*cm))
        story.append(validation_table)
        
    def _add_qr_code(self, story, data):
        """Ajoute un QR code pour la vérification en ligne"""
        # URL de vérification
        numero_certificat = data.get('numero_certificat', '')
        verification_url = f"https://comptaebnl-ia.com/verify/{numero_certificat}"
        
        try:
            # Générer le QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=3,
                border=2,
            )
            qr.add_data(verification_url)
            qr.make(fit=True)
            
            # Créer l'image du QR code en mémoire
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir en bytes pour ReportLab
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            # Créer l'image ReportLab à partir du buffer
            qr_image = RLImage(qr_buffer, width=2*cm, height=2*cm)
            
            # Table pour positionner le QR code
            qr_data = [
                [qr_image, "Vérifiez l'authenticité de ce certificat\nen scannant ce QR code\nou sur comptaebnl-ia.com/verify"]
            ]
            
            qr_table = Table(qr_data, colWidths=[3*cm, 8*cm])
            qr_table.setStyle(TableStyle([
                ('FONT', (1, 0), (1, 0), 'Helvetica'),
                ('FONTSIZE', (1, 0), (1, 0), 9),
                ('TEXTCOLOR', (1, 0), (1, 0), self.colors['text']),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(Spacer(1, 0.5*cm))
            story.append(qr_table)
            
        except Exception as e:
            # En cas d'erreur, ajouter juste le texte de vérification
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            styles = getSampleStyleSheet()
            error_style = ParagraphStyle(
                'ErrorStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=self.colors['text'],
                alignment=TA_CENTER,
                spaceAfter=10
            )
            
            verification_text = f"Vérifiez l'authenticité de ce certificat sur<br/>comptaebnl-ia.com/verify/{numero_certificat}"
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph(verification_text, error_style))
            
    def _add_footer(self, story, data):
        """Ajoute le pied de page avec signatures"""
        styles = getSampleStyleSheet()
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.colors['text'],
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        # Date et lieu
        date_emission = datetime.now().strftime("%d/%m/%Y")
        footer_text = f"""
        <br/><br/>
        Fait à Abidjan, le {date_emission}<br/>
        <b>ComptaEBNL-IA</b> - Plateforme certifiée OHADA<br/>
        <i>Ce certificat est vérifiable en ligne sur comptaebnl-ia.com</i>
        """
        
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(footer_text, footer_style))
        
    def _add_watermark(self, canvas_obj, doc):
        """Ajoute un filigrane et des bordures décoratives"""
        canvas_obj.saveState()
        
        # Bordure décorative
        canvas_obj.setStrokeColor(self.colors['accent'])
        canvas_obj.setLineWidth(3)
        
        # Bordure extérieure
        margin = 1*cm
        canvas_obj.rect(margin, margin, self.width - 2*margin, self.height - 2*margin)
        
        # Bordure intérieure
        inner_margin = 1.5*cm
        canvas_obj.setLineWidth(1)
        canvas_obj.setStrokeColor(self.colors['border'])
        canvas_obj.rect(inner_margin, inner_margin, 
                       self.width - 2*inner_margin, self.height - 2*inner_margin)
        
        # Motifs décoratifs dans les coins
        self._draw_corner_decorations(canvas_obj)
        
        canvas_obj.restoreState()
        
    def _draw_corner_decorations(self, canvas_obj):
        """Dessine des motifs décoratifs dans les coins"""
        canvas_obj.setStrokeColor(self.colors['accent'])
        canvas_obj.setLineWidth(2)
        
        corner_size = 0.8*cm
        margin = 1.2*cm
        
        # Coin supérieur gauche
        canvas_obj.line(margin, self.height - margin, 
                       margin + corner_size, self.height - margin)
        canvas_obj.line(margin, self.height - margin, 
                       margin, self.height - margin - corner_size)
        
        # Coin supérieur droit
        canvas_obj.line(self.width - margin, self.height - margin, 
                       self.width - margin - corner_size, self.height - margin)
        canvas_obj.line(self.width - margin, self.height - margin, 
                       self.width - margin, self.height - margin - corner_size)
        
        # Coin inférieur gauche
        canvas_obj.line(margin, margin, margin + corner_size, margin)
        canvas_obj.line(margin, margin, margin, margin + corner_size)
        
        # Coin inférieur droit
        canvas_obj.line(self.width - margin, margin, 
                       self.width - margin - corner_size, margin)
        canvas_obj.line(self.width - margin, margin, 
                       self.width - margin, margin + corner_size)
        
    def _format_date(self, date_str):
        """Formate une date pour l'affichage"""
        if not date_str:
            return "N/A"
        
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = date_str
            return date_obj.strftime("%d/%m/%Y")
        except:
            return str(date_str)
            
    def generate_certificate_preview(self, certificat_data):
        """Génère un aperçu du certificat (image PNG)"""
        # Créer une image avec Pillow pour l'aperçu
        img_width, img_height = 1200, 850  # Résolution pour aperçu
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Charger une police (par défaut si non disponible)
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            # Police par défaut si les autres ne sont pas disponibles
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Dessiner le contenu
        y_pos = 50
        
        # Titre
        title = "CERTIFICAT DE FORMATION"
        draw.text((img_width//2, y_pos), title, font=title_font, fill='#1E3A8A', anchor='mt')
        y_pos += 80
        
        # Sous-titre
        subtitle = "Comptabilité des Entités à But Non Lucratif"
        draw.text((img_width//2, y_pos), subtitle, font=body_font, fill='#F59E0B', anchor='mt')
        y_pos += 100
        
        # Corps
        body_text = "Certifie que"
        draw.text((img_width//2, y_pos), body_text, font=body_font, fill='black', anchor='mt')
        y_pos += 60
        
        # Nom
        nom = certificat_data.get('nom_beneficiaire', 'Nom du bénéficiaire')
        draw.text((img_width//2, y_pos), nom, font=title_font, fill='#1E3A8A', anchor='mt')
        y_pos += 80
        
        # Formation
        formation = f'"{certificat_data.get("formation_titre", "Formation EBNL")}"'
        draw.text((img_width//2, y_pos), formation, font=body_font, fill='#3B82F6', anchor='mt')
        y_pos += 150
        
        # Informations
        numero = f"N° {certificat_data.get('numero_certificat', 'CEBNL-2025-XXX')}"
        draw.text((100, y_pos), numero, font=small_font, fill='black')
        
        date_str = self._format_date(certificat_data.get('date_obtention'))
        draw.text((img_width - 100, y_pos), f"Le {date_str}", font=small_font, fill='black', anchor='rt')
        
        # Bordure
        draw.rectangle([20, 20, img_width-20, img_height-20], outline='#F59E0B', width=3)
        
        return img

# Fonction utilitaire pour usage direct
def generate_certificate_pdf(certificat_data, output_path=None):
    """
    Fonction utilitaire pour générer un certificat PDF
    
    Args:
        certificat_data (dict): Données du certificat
        output_path (str): Chemin de sortie optionnel
        
    Returns:
        bytes: Contenu du PDF
    """
    generator = CertificateGenerator()
    return generator.generate_certificate(certificat_data, output_path)