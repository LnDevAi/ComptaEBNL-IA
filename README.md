# ComptaEBNL-IA 🚀

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![SYCEBNL](https://img.shields.io/badge/Référentiel-SYCEBNL-orange.svg)](https://github.com/LnDevAi/ComptaEBNL-IA)

## 🎯 Plateforme de Gestion Comptable avec IA pour Entités à But Non Lucratif

**ComptaEBNL-IA** est une plateforme SaaS révolutionnaire de gestion comptable avec intelligence artificielle intégrée, spécialement conçue pour les **entités à but non lucratif** (associations, fondations, projets de développement) utilisant exclusivement le **référentiel SYCEBNL officiel**.

### ✨ Fonctionnalités Principales

#### 🤖 **Agent IA Comptable Intégré**
- **Scan et reconnaissance** de pièces comptables (factures, reçus, relevés)
- **Génération automatique** d'écritures comptables avec mapping SYCEBNL
- **Suggestions intelligentes** de comptes basées sur l'analyse de contenu
- **Validation automatique** avec contrôles d'équilibre et cohérence

#### 📊 **Plan Comptable SYCEBNL Complet**
- **212+ comptes officiels** du référentiel SYCEBNL intégrés
- **9 classes comptables** complètes avec structure hiérarchique
- **Comptes spécialisés EBNL** : contributions volontaires, fonds affectés, adhérents
- **Recherche avancée** et navigation intuitive

#### 💼 **Gestion Comptable Complète**
- **Saisie d'écritures** avec validation temps réel
- **7 journaux comptables** pré-configurés (ACH, VTE, BQ, CAI, OD, DON, SUB)
- **Balance comptable** et grand livre automatiques
- **États financiers** conformes SYCEBNL (à venir)

#### 🎯 **Spécificités EBNL**
- **Gestion des dons** et legs avec reçus fiscaux
- **Suivi des subventions** par projet et organisme
- **Contributions volontaires** en nature et bénévolat
- **Adhérents et usagers** avec cotisations

### 🏗️ Architecture

```
ComptaEBNL-IA/
├── backend/                    # API Flask + Base de données
│   ├── src/
│   │   ├── api/               # Blueprints API REST
│   │   │   ├── plan_comptable.py
│   │   │   ├── comptabilite.py
│   │   │   └── ia.py
│   │   ├── data/              # Plan comptable SYCEBNL
│   │   ├── models.py          # Modèles SQLAlchemy
│   │   ├── main.py           # Application Flask
│   │   └── config.py         # Configuration
│   └── requirements.txt       # Dépendances Python
├── frontend/                  # Interface React (à développer)
├── docs/                      # Documentation
└── docker-compose.yml         # Conteneurisation
```

### 🚀 Démarrage Rapide

#### Prérequis
- Python 3.9+
- pip ou pipenv
- SQLite (inclus)

#### Installation

```bash
# 1. Cloner le projet
git clone https://github.com/LnDevAi/ComptaEBNL-IA.git
cd ComptaEBNL-IA

# 2. Installation des dépendances
cd backend/src
pip install -r requirements.txt

# 3. Initialiser la base de données et importer le plan SYCEBNL
python import_sycebnl_complet.py

# 4. Démarrer l'application
python main.py
```

#### Test Rapide

```bash
# Tester l'application
python test_simple.py

# API disponible sur
curl http://localhost:5000/api/health
```

### 📋 API Endpoints

#### Plan Comptable SYCEBNL
- `GET /api/v1/plan-comptable` - Liste des comptes avec filtres
- `GET /api/v1/plan-comptable/classes` - Classes SYCEBNL
- `GET /api/v1/plan-comptable/search?q=terme` - Recherche de comptes
- `GET /api/v1/plan-comptable/stats` - Statistiques du plan

#### Écritures Comptables  
- `GET /api/v1/ecritures` - Liste des écritures avec pagination
- `POST /api/v1/ecritures` - Création d'écriture
- `POST /api/v1/ecritures/{id}/valider` - Validation d'écriture
- `GET /api/v1/balance` - Balance comptable
- `GET /api/v1/grand-livre/{compte}` - Grand livre d'un compte

#### Intelligence Artificielle
- `POST /api/v1/upload-document` - Upload de document
- `POST /api/v1/generer-ecriture` - Génération automatique IA
- `POST /api/v1/suggestions-compte` - Suggestions de comptes
- `GET /api/v1/config-ia` - Configuration IA

### 💡 Exemples d'Usage

#### Création d'écriture de don

```bash
curl -X POST http://localhost:5000/api/v1/ecritures \
  -H "Content-Type: application/json" \
  -d '{
    "date_ecriture": "2024-01-15",
    "libelle": "Don de Jean Dupont",
    "journal": "DON",
    "piece_justificative": "DON-2024-001",
    "lignes": [
      {
        "numero_compte": "571",
        "libelle": "Encaissement don",
        "debit": 100.00,
        "credit": 0
      },
      {
        "numero_compte": "7561", 
        "libelle": "Don manuel",
        "debit": 0,
        "credit": 100.00
      }
    ]
  }'
```

#### Génération automatique par IA

```bash
curl -X POST http://localhost:5000/api/v1/generer-ecriture \
  -H "Content-Type: application/json" \
  -d '{
    "type_operation": "don",
    "donateur": "Marie Martin",
    "date": "2024-01-15",
    "montant": 250.00,
    "description": "Don pour projet éducatif"
  }'
```

### 🎯 Plan Comptable SYCEBNL

Le système intègre le **plan comptable SYCEBNL complet** avec :

- **Classe 1** : Comptes de ressources durables (81 comptes)
- **Classe 2** : Actif immobilisé (38 comptes)  
- **Classe 3** : Stocks (7 comptes)
- **Classe 4** : Comptes de tiers (17 comptes)
- **Classe 5** : Trésorerie (6 comptes)
- **Classe 6** : Charges des activités ordinaires (16 comptes)
- **Classe 7** : Produits des activités ordinaires (23 comptes)
- **Classe 8** : Autres charges et produits (19 comptes)
- **Classe 9** : Engagements hors bilan (5 comptes)

#### Comptes Spécialisés EBNL

- `758` - Contributions volontaires en nature
- `7581` - Bénévolat  
- `412` - Adhérents et usagers
- `1311` - Fonds dédiés avec obligation contractuelle
- `756` - Dons et legs
- `7561` - Dons manuels

### 🤖 Intelligence Artificielle

L'agent IA ComptaEBNL intègre :

#### Types d'Opérations Supportées
- **Achats** : Mapping automatique fournisseurs/charges
- **Ventes** : Gestion clients et TVA
- **Dons** : Classification par type (manuel, nature, legs)
- **Subventions** : Identification organisme (État, International, Tiers)
- **Opérations bancaires** : Mouvements et régularisations

#### Suggestions Intelligentes
- **Analyse textuelle** : Reconnaissance de mots-clés
- **Mapping contextuel** : Association avec comptes SYCEBNL
- **Apprentissage adaptatif** : Amélioration continue des suggestions
- **Validation automatique** : Contrôles d'équilibre et cohérence

### 🔧 Développement

#### Tests

```bash
# Tests unitaires
python test_simple.py

# Tests API complets (avec serveur en marche)
python test_api.py

# Réinitialiser la base de données
python reset_db.py
```

#### Structure des Données

- **SQLite** pour le développement
- **PostgreSQL** recommandé pour la production
- **Migrations automatiques** avec SQLAlchemy
- **Sauvegarde/Restauration** intégrée

### 📈 Roadmap

#### Version 1.0 (Actuelle) ✅
- [x] Plan comptable SYCEBNL complet
- [x] API REST fonctionnelle
- [x] Gestion des écritures comptables
- [x] Agent IA de base
- [x] Spécificités EBNL

#### Version 1.1 (Mois 2)
- [ ] Interface React complète
- [ ] OCR avancé (Tesseract/Cloud)
- [ ] États financiers SYCEBNL
- [ ] Import bancaire automatique

#### Version 1.2 (Mois 3)
- [ ] Authentification et permissions
- [ ] Multi-entités et consolidation
- [ ] Exports comptables (FEC, CSV)
- [ ] Tableau de bord analytique

### 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changes (`git commit -m 'Add AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

### 🔗 Liens Utiles

- [Documentation SYCEBNL](https://www.sycebnl.org)
- [API Documentation](http://localhost:5000/api/docs)
- [Issues GitHub](https://github.com/LnDevAi/ComptaEBNL-IA/issues)

### 💬 Support

Pour toute question ou support :
- 📧 Email : support@comptaebnl-ia.dev
- 🐛 Issues : [GitHub Issues](https://github.com/LnDevAi/ComptaEBNL-IA/issues)

---

**ComptaEBNL-IA** - Révolutionner la comptabilité des entités à but non lucratif avec l'intelligence artificielle 🚀
