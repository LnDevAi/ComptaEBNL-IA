# Documentation API ComptaOHADA-IA

## 🎯 Vue d'ensemble

L'API ComptaOHADA-IA est une API REST moderne développée avec FastAPI, conforme aux standards OpenAPI 3.0. Elle fournit toutes les fonctionnalités nécessaires pour la gestion comptable des entités à but non lucratif selon les normes SYSCEBNL/OHADA.

## 📋 Informations générales

- **URL de base** : `http://localhost:8000` (développement)
- **Version** : 2.0.0
- **Format** : JSON
- **Authentification** : JWT Bearer Token
- **Documentation interactive** : `/docs` (Swagger UI)
- **Schéma OpenAPI** : `/openapi.json`

## 🔐 Authentification

### JWT Bearer Token

Toutes les routes protégées nécessitent un token JWT dans l'en-tête :

```http
Authorization: Bearer <votre_token_jwt>
```

### Endpoints d'authentification

#### POST `/api/auth/register`
Inscription d'un nouvel utilisateur

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "password": "motdepasse123",
  "country_code": "CI",
  "language": "fr"
}
```

#### POST `/api/auth/login`
Connexion utilisateur

```json
{
  "email": "user@example.com",
  "password": "motdepasse123"
}
```

**Réponse :**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET `/api/auth/me`
Informations utilisateur connecté (protégé)

## 🏢 Gestion des organisations

### GET `/api/organizations/`
Liste des organisations de l'utilisateur

### POST `/api/organizations/`
Création d'une nouvelle organisation

```json
{
  "name": "Association XYZ",
  "organization_type": "association",
  "country_code": "CI",
  "registration_number": "CI-ASS-2024-001",
  "email": "contact@association-xyz.ci",
  "currency": "XOF"
}
```

### GET `/api/organizations/{organization_id}`
Détails d'une organisation

### PUT `/api/organizations/{organization_id}`
Mise à jour d'une organisation

### DELETE `/api/organizations/{organization_id}`
Suppression d'une organisation (soft delete)

## 📊 Plan comptable SYSCEBNL

### GET `/api/plan-comptable/`
Liste des comptes du plan comptable

**Paramètres :**
- `classe` (optionnel) : Filtrer par classe (1-9)
- `niveau` (optionnel) : Filtrer par niveau
- `actif_only` (optionnel) : Comptes actifs uniquement (défaut: true)

### GET `/api/plan-comptable/classes`
Liste des classes comptables SYSCEBNL

**Réponse :**
```json
[
  {
    "numero": 1,
    "libelle": "RESSOURCES DURABLES",
    "type": "bilan"
  },
  {
    "numero": 6,
    "libelle": "CHARGES DES ACTIVITES ORDINAIRES",
    "type": "resultat"
  }
]
```

### GET `/api/plan-comptable/search`
Recherche de comptes

**Paramètres :**
- `q` : Terme de recherche (numéro ou libellé)
- `limit` : Nombre de résultats (défaut: 20)

### POST `/api/plan-comptable/`
Création d'un nouveau compte

```json
{
  "numero_compte": "6011",
  "libelle_compte": "Achats de marchandises",
  "classe": 6,
  "niveau": 4,
  "sens": "debit",
  "type_compte": "resultat",
  "lettrable": false,
  "syscebnl_code": "6011"
}
```

### POST `/api/plan-comptable/import-syscebnl`
Importation du plan comptable SYSCEBNL standard

## 📝 Écritures comptables

### GET `/api/ecritures/`
Liste des écritures comptables (en développement)

## 👥 Gestion des tiers

### GET `/api/tiers/`
Liste des tiers (adhérents, donateurs, fournisseurs)

## 🎯 Projets et fonds affectés

### GET `/api/projets/`
Liste des projets EBNL

## 📄 Gestion documentaire

### GET `/api/documents/`
Liste des documents (avec OCR)

## 📈 Rapports et états financiers

### GET `/api/reports/`
Liste des rapports disponibles

```json
{
  "reports": [
    {"name": "bilan", "label": "Bilan"},
    {"name": "compte_resultat", "label": "Compte de résultat"},
    {"name": "flux_tresorerie", "label": "Flux de trésorerie"},
    {"name": "annexes", "label": "Annexes"}
  ]
}
```

## 🤖 Assistant IA

### GET `/api/ai/`
Informations sur l'assistant IA

```json
{
  "ai_features": [
    "OCR automatique",
    "Génération d'écritures",
    "Analyse de documents",
    "Suggestions comptables",
    "Détection d'anomalies"
  ],
  "status": "available"
}
```

## 🔧 Endpoints système

### GET `/`
Informations générales de l'API

### GET `/health`
État de santé du système

```json
{
  "status": "healthy",
  "database": "connected",
  "statistics": {
    "organizations": 5,
    "users": 12
  },
  "services": {
    "database": "ok",
    "ai_assistant": "ok",
    "ocr": "ok",
    "email": "not_configured",
    "stripe": "ok"
  }
}
```

### GET `/info`
Informations détaillées sur l'API

```json
{
  "app": "ComptaOHADA-IA",
  "version": "2.0.0",
  "features": {
    "multi_tenant": true,
    "ai_integration": true,
    "ocr_support": true,
    "syscebnl_compliance": true,
    "ohada_standards": true
  },
  "supported_countries": ["BJ", "BF", "CM", "..."],
  "compliance": {
    "syscebnl": "2024",
    "ohada": "2024",
    "ifrs": "partial_support"
  }
}
```

## 🐛 Endpoints de débogage (développement uniquement)

### GET `/debug/models`
Liste des modèles de données

### GET `/debug/config`
Configuration actuelle (données sensibles masquées)

## 📋 Codes de réponse HTTP

| Code | Signification |
|------|---------------|
| 200  | Succès |
| 201  | Créé |
| 400  | Requête invalide |
| 401  | Non authentifié |
| 403  | Accès interdit |
| 404  | Non trouvé |
| 422  | Erreur de validation |
| 500  | Erreur serveur |

## 📝 Format des erreurs

```json
{
  "error": true,
  "message": "Description de l'erreur",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔒 Sécurité

### Authentification JWT

- **Algorithme** : HS256
- **Durée de vie access token** : 30 minutes
- **Durée de vie refresh token** : 7 jours

### CORS

Les origines autorisées sont configurées dans `settings.cors_origins`.

### Rate Limiting

À implémenter selon les besoins de production.

## 📊 Modèles de données principaux

### User
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "country_code": "CI",
  "subscription_plan": "starter",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Organization
```json
{
  "id": 1,
  "name": "Association XYZ",
  "slug": "association-xyz",
  "organization_type": "association",
  "country_code": "CI",
  "currency": "XOF",
  "is_active": true
}
```

### PlanComptable
```json
{
  "id": 1,
  "numero_compte": "6011",
  "libelle_compte": "Achats de marchandises",
  "classe": 6,
  "niveau": 4,
  "sens": "debit",
  "type_compte": "resultat",
  "lettrable": false,
  "actif": true
}
```

## 🌍 Support OHADA

### Pays supportés

L'API supporte tous les 17 pays de l'espace OHADA :

- 🇧🇯 Bénin (BJ)
- 🇧🇫 Burkina Faso (BF)
- 🇨🇲 Cameroun (CM)
- 🇨🇫 Centrafrique (CF)
- 🇹🇩 Tchad (TD)
- 🇰🇲 Comores (KM)
- 🇨🇮 Côte d'Ivoire (CI)
- 🇨🇩 RD Congo (CD)
- 🇬🇶 Guinée Équatoriale (GQ)
- 🇬🇦 Gabon (GA)
- 🇬🇳 Guinée (GN)
- 🇬🇼 Guinée-Bissau (GW)
- 🇲🇱 Mali (ML)
- 🇳🇪 Niger (NE)
- 🇨🇬 Congo (CG)
- 🇸🇳 Sénégal (SN)
- 🇹🇬 Togo (TG)

### Monnaies supportées

- **XOF** : Franc CFA (UEMOA)
- **XAF** : Franc CFA (CEMAC)
- **KMF** : Franc comorien
- **CDF** : Franc congolais

## 📞 Support

- **Documentation interactive** : http://localhost:8000/docs
- **Email** : support@comptaohada.ai
- **GitHub Issues** : https://github.com/LnDevAi/ComptaOHADA-IA/issues

---

*API développée avec ❤️ pour l'écosystème OHADA*