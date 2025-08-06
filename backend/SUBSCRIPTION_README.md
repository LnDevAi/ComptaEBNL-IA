# 💳 Système d'Abonnement ComptaEBNL-IA

## 🚀 Vue d'ensemble

ComptaEBNL-IA intègre un système d'abonnement SaaS complet avec :
- **3 plans d'abonnement** (Gratuit, Professionnel, Enterprise)
- **Paiements Multi-plateformes** (Stripe, PayPal, Mobile Money)
- **Gestion des quotas** automatique
- **Middleware de contrôle d'accès** aux fonctionnalités
- **Interface de facturation** moderne

## 📋 Plans d'Abonnement

### 🆓 Plan Gratuit
- **Prix**: 0€/mois
- **Entités EBNL**: 1
- **Écritures**: 100/mois
- **Utilisateurs**: 1
- **Documents**: 10/mois
- **Fonctionnalités**: Base uniquement

### 💼 Plan Professionnel - 30€/mois
- **Prix**: 30€/mois ou 300€/an (2 mois gratuits)
- **Entités EBNL**: 3
- **Écritures**: Illimitées
- **Utilisateurs**: 5
- **Documents**: 500/mois
- **Fonctionnalités**: ✅ IA avancée, ✅ OCR, ✅ États financiers avancés, ✅ Rapprochement bancaire

### 🏢 Plan Enterprise - 100€/mois
- **Prix**: 100€/mois ou 1000€/an (2 mois gratuits)
- **Tout illimité**
- **Fonctionnalités**: ✅ Toutes + Audit trail + Support prioritaire + API

## 💳 Méthodes de Paiement

### 🌍 Classiques
- **Stripe**: Cartes bancaires internationales
- **PayPal**: Paiements sécurisés

### 📱 Mobile Money (Afrique)
- **MTN Mobile Money**: *126# - Cameroun, Côte d'Ivoire, Ghana, Ouganda
- **Orange Money**: #144# - Sénégal, Mali, Burkina Faso, Niger
- **Wave**: App mobile - Sénégal, Côte d'Ivoire, Mali
- **Moov Money**: Bénin, Togo, Côte d'Ivoire
- **Airtel Money**: Plusieurs pays africains

## 🏗️ Architecture Technique

### Backend (Python/Flask)

#### 📁 Structure des fichiers
```
backend/
├── src/
│   ├── models.py                    # Modèles BDD (Abonnement, Paiement, etc.)
│   ├── api/subscription.py          # API REST abonnements
│   ├── middleware/
│   │   └── subscription_middleware.py  # Contrôle d'accès et quotas
│   └── app.py                       # Application principale
├── init_subscription_data.py        # Script d'initialisation
└── SUBSCRIPTION_README.md           # Cette documentation
```

#### 🗃️ Modèles de données

**PlanAbonnement**
```python
- nom, type_plan, prix_mensuel, prix_annuel
- max_entites, max_ecritures_mois, max_utilisateurs
- ia_avancee, ocr_documents, audit_trail, etc.
```

**Abonnement**
```python
- utilisateur_id, plan_id, statut, dates
- stripe_subscription_id, paypal_subscription_id
- ecritures_utilisees_mois, documents_utilises_mois
```

**Paiement**
```python
- montant, methode_paiement, statut
- transaction_id_externe, numero_telephone
- date_creation, date_traitement
```

**UtilisationQuota**
```python
- abonnement_id, annee, mois
- ecritures_utilisees, documents_traites
- appels_api, stockage_utilise_mb
```

#### 🛡️ Middleware et Décorateurs

```python
# Vérifier abonnement actif
@subscription_required
def create_ecriture():
    pass

# Vérifier fonctionnalité du plan
@feature_required('ia_avancee')
def ai_analyze():
    pass

# Vérifier et consommer quota
@quota_required('ecritures', 1)
def add_ecriture():
    pass

# Exiger niveau de plan minimum
@plan_required(TypePlan.ENTERPRISE)
def admin_features():
    pass
```

### Frontend (React/TypeScript)

#### 📁 Structure des composants
```
frontend/src/
├── pages/
│   ├── Pricing/Pricing.tsx         # Page tarification
│   └── Billing/BillingDashboard.tsx # Tableau de bord facturation
├── components/
│   └── Layout/Sidebar.tsx           # Navigation mise à jour
└── App.tsx                          # Routes ajoutées
```

#### 🎨 Fonctionnalités UI
- **Page de tarification** responsive avec switch mensuel/annuel
- **Dialog de paiement** avec sélection de méthode
- **Support Mobile Money** avec champ téléphone
- **Tableau de bord facturation** avec historique et statistiques
- **Barres de progression** pour les quotas
- **Alertes de limitation** automatiques

## 🚀 Installation et Utilisation

### 1. Initialiser les données

```bash
cd backend
python init_subscription_data.py
```

### 2. Démarrer le backend

```bash
cd backend/src
python app.py
```

### 3. Démarrer le frontend

```bash
cd frontend
npm start
```

### 4. Accéder aux fonctionnalités

- **Plans**: http://localhost:3000/pricing
- **Facturation**: http://localhost:3000/billing
- **API Plans**: http://localhost:5000/api/v1/plans

## 🔌 API Endpoints

### Plans et Abonnements
```
GET    /api/v1/plans                 # Liste des plans
GET    /api/v1/plans/{id}            # Détail d'un plan
GET    /api/v1/mon-abonnement        # Abonnement actuel
POST   /api/v1/souscrire             # Créer abonnement
```

### Paiements
```
POST   /api/v1/webhooks/stripe       # Webhook Stripe
POST   /api/v1/webhooks/mobile-money # Webhook Mobile Money
POST   /api/v1/coupons/verifier      # Vérifier coupon
```

### Administration
```
GET    /api/v1/admin/statistiques    # Stats abonnements
```

## 💡 Exemples d'utilisation

### Créer un abonnement avec Mobile Money

```javascript
const subscriptionData = {
  plan_id: 2,
  periode: 'mensuel',
  methode_paiement: 'mtn_mobile_money',
  numero_telephone: '+221771234567',
  devise: 'EUR'
};

const response = await apiClient.post('/api/v1/souscrire', subscriptionData);
```

### Vérifier un quota côté backend

```python
from middleware.subscription_middleware import QuotaManager

# Vérifier si l'utilisateur peut créer une écriture
if QuotaManager.check_quota(abonnement, 'ecritures', 1):
    # Créer l'écriture
    # Incrémenter le quota
    QuotaManager.increment_usage(abonnement.id, 'ecritures', 1)
```

### Utiliser un coupon de réduction

```javascript
const couponData = {
  code: 'LAUNCH2024',
  montant: 30
};

const response = await apiClient.post('/api/v1/coupons/verifier', couponData);
// Retourne la réduction calculée
```

## 🧪 Données de Test

Le script d'initialisation crée :

### Plans par défaut
- Gratuit (0€)
- Professionnel (30€/mois)
- Enterprise (100€/mois)

### Coupons de test
- `LAUNCH2024`: 50% de réduction
- `FIRST10`: 10€ de réduction
- `EBNL2024`: 30% de réduction

### Simulation de paiements
- Tous les paiements sont simulés en mode développement
- Les webhooks retournent des succès automatiques
- Les transactions Mobile Money génèrent des IDs de test

## 🔒 Sécurité

### Validation des paiements
- **Webhooks sécurisés** avec vérification de signature
- **Timeout automatique** des sessions de paiement
- **Chiffrement** des données sensibles

### Contrôle d'accès
- **Middleware automatique** sur toutes les routes
- **Vérification des quotas** en temps réel
- **Expiration automatique** des abonnements

### Mobile Money
- **Validation des numéros** de téléphone
- **Codes de transaction** uniques
- **Timeout** des paiements en attente

## 📈 Métriques et Analytics

### Tracking automatique
- Utilisation des quotas par mois
- Méthodes de paiement populaires
- Taux de conversion par plan
- Géolocalisation des paiements Mobile Money

### Tableaux de bord
- **Utilisateur**: Utilisation et facturation
- **Admin**: Revenus et statistiques

## 🌍 Internationalisation

### Devises supportées
- **EUR** (Euro) - Principal
- **XOF** (Franc CFA Ouest)
- **XAF** (Franc CFA Central)
- **USD** (Dollar US)

### Pays ciblés Mobile Money
- **Afrique de l'Ouest**: Sénégal, Mali, Burkina Faso, Côte d'Ivoire
- **Afrique Centrale**: Cameroun, Tchad
- **Afrique de l'Est**: Ouganda, Ghana

## 🛠️ Développement et Maintenance

### Tests
```bash
# Tester les endpoints
curl -X GET http://localhost:5000/api/v1/plans

# Tester un paiement Mobile Money
curl -X POST http://localhost:5000/api/v1/souscrire \
  -H "Content-Type: application/json" \
  -d '{"plan_id":2,"periode":"mensuel","methode_paiement":"mtn_mobile_money","numero_telephone":"+221771234567"}'
```

### Monitoring
- Logs automatiques des transactions
- Alertes pour échecs de paiement
- Surveillance des quotas

### Mise à jour des prix
- Modification via l'admin Django
- Migration automatique des abonnements existants
- Notification des utilisateurs

## 🚀 Déploiement Production

### Variables d'environnement
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
MTN_MOMO_API_KEY=...
ORANGE_MONEY_API_KEY=...
```

### Webhooks à configurer
- Stripe: `https://votre-domaine.com/api/v1/webhooks/stripe`
- PayPal: `https://votre-domaine.com/api/v1/webhooks/paypal`
- Mobile Money: `https://votre-domaine.com/api/v1/webhooks/mobile-money`

## 📞 Support

### Pour les développeurs
- Documentation API complète
- Exemples de code
- Tests automatisés

### Pour les utilisateurs
- Support par plan (communautaire → prioritaire)
- FAQ Mobile Money
- Guides de paiement par pays

---

🎉 **Le système d'abonnement ComptaEBNL-IA est maintenant prêt !**

Transformez votre comptabilité EBNL en SaaS monétisable avec support Mobile Money pour l'Afrique ! 🌍💰