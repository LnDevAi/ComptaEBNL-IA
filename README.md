# Plateforme ComptaOHADA-IA

## 🏛️ Plateforme de Comptabilité en Ligne pour l'Espace OHADA avec IA Intégrée

**ComptaOHADA-IA** est une plateforme SaaS révolutionnaire de gestion comptable avec intelligence artificielle intégrée, spécialement conçue pour les entités à but non lucratif (associations, fondations, ONG) de l'espace OHADA utilisant les normes du SYSCEBNL (Système Comptable des Entités à But Non Lucratif).

### 🌍 Conformité OHADA & SYSCEBNL

- **📋 Normes SYSCEBNL** : Plan comptable officiel des entités à but non lucratif OHADA
- **🏛️ Conformité OHADA** : Respect total des normes comptables de l'espace OHADA
- **📊 États Financiers Conformes** : Bilan, compte de résultat, annexes selon normes OHADA
- **💰 Multi-devises** : Support des monnaies de l'espace OHADA (FCFA, etc.)

### 🚀 Fonctionnalités Principales

#### 🤖 Intelligence Artificielle Intégrée
- **📱 Scan de pièces** : OCR et extraction automatique des données comptables
- **✏️ Saisie assistée** : Génération automatique d'écritures comptables
- **🔍 Analyse prédictive** : Détection d'anomalies et suggestions d'amélioration
- **📈 Rapports intelligents** : Génération automatique de rapports conformes

#### 📊 Gestion Comptable Complète
- **📋 Plan comptable SYSCEBNL** : 1162 comptes officiels intégrés
- **📝 Saisie des écritures** : Interface intuitive avec contrôles automatiques
- **🔄 Lettrage automatique** : Rapprochement bancaire et lettrage des comptes
- **📊 États financiers** : Bilan, compte de résultat, flux de trésorerie, annexes

#### 🏢 Spécificités EBNL (Entités à But Non Lucratif)
- **👥 Gestion des adhérents** : Suivi des cotisations et contributions
- **💝 Fonds affectés** : Gestion des projets et subventions spécifiques
- **📋 Contributions volontaires** : Suivi des dons et legs
- **📊 Reporting spécialisé** : Rapports adaptés aux besoins des EBNL

#### 💳 Système d'Abonnement SaaS
- **📱 Multi-tenant** : Isolement complet des données par organisation
- **💳 Facturation automatique** : Stripe integration pour les paiements
- **📊 Plans flexibles** : Starter, Professional, Enterprise
- **🔐 Sécurité avancée** : Chiffrement, audit trail, conformité RGPD

### 🛠️ Architecture Technique

#### Backend
- **⚡ FastAPI** : API REST moderne et performante
- **🗄️ PostgreSQL** : Base de données robuste avec support JSON
- **🔍 Alembic** : Migrations de base de données
- **🤖 OpenAI GPT** : Intelligence artificielle pour l'assistance comptable
- **📄 Tesseract OCR** : Reconnaissance optique de caractères
- **🔐 JWT Authentication** : Authentification sécurisée

#### Frontend
- **⚛️ Next.js 14** : Framework React moderne avec App Router
- **🎨 Tailwind CSS** : Framework CSS utilitaire
- **📊 Chart.js** : Graphiques et visualisations
- **📱 Responsive Design** : Compatible mobile et desktop
- **🌐 PWA Ready** : Progressive Web App

#### Infrastructure
- **🐳 Docker** : Containerisation complète
- **☁️ AWS/Azure** : Déploiement cloud
- **🔄 CI/CD** : Pipeline automatisé avec GitHub Actions
- **📊 Monitoring** : Logs et métriques en temps réel

### 🚀 Démarrage Rapide

```bash
# Cloner le projet
git clone https://github.com/LnDevAi/ComptaOHADA-IA.git
cd ComptaOHADA-IA

# Démarrer avec Docker
docker-compose up -d

# Ou démarrage manuel
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
./run_local.bat
```

### 📋 Plans d'Abonnement

#### 🆓 Plan Starter (Gratuit)
- 1 organisation
- 50 écritures/mois
- États financiers de base
- Support email

#### 💼 Plan Professional (50€/mois)
- 5 organisations
- Écritures illimitées
- IA assistant intégrée
- Support prioritaire
- Rapports avancés

#### 🏢 Plan Enterprise (Sur devis)
- Organisations illimitées
- API personnalisée
- Intégrations sur mesure
- Support dédié 24/7
- Formation incluse

### 🌍 Espace OHADA Couvert

17 pays membres de l'OHADA :
🇧🇯 Bénin • 🇧🇫 Burkina Faso • 🇨🇲 Cameroun • 🇨🇫 Centrafrique • 🇹🇩 Tchad • 🇰🇲 Comores • 🇨🇮 Côte d'Ivoire • 🇨🇩 RD Congo • 🇬🇶 Guinée Équatoriale • 🇬🇦 Gabon • 🇬🇳 Guinée • 🇬🇼 Guinée-Bissau • 🇲🇱 Mali • 🇳🇪 Niger • 🇨🇬 Congo • 🇸🇳 Sénégal • 🇹🇬 Togo

### 📞 Support & Contact

- 📧 Email : support@comptaohada.ai
- 🌐 Site web : https://comptaohada.ai
- 📞 Téléphone : +33 1 XX XX XX XX
- 💬 Chat en ligne : 24/7 disponible

### 🔐 Sécurité & Conformité

- ✅ Conformité RGPD
- 🔒 Chiffrement AES-256
- 🛡️ Audit trail complet
- 🏛️ Hébergement européen
- 📋 Certification ISO 27001

---

*Développé avec ❤️ pour l'écosystème OHADA*
