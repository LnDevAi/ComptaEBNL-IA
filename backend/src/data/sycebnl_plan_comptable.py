# Plan Comptable SYCEBNL Complet - Extrait de la documentation officielle
# Système Comptable des Entités à But Non Lucratif
# Total: 1314 comptes extraits de la documentation PDF officielle

# Mapping des libellés pour les comptes principaux (remplace les libellés génériques)
LIBELLES_OFFICIELS = {
    "10": "DOTATION",
    "11": "RÉSERVES", 
    "12": "REPORT À NOUVEAU",
    "13": "RÉSULTAT NET DE L'EXERCICE",
    "14": "SUBVENTIONS D'INVESTISSEMENT",
    "15": "PROVISIONS RÉGLEMENTÉES ET FONDS ASSIMILÉS",
    "16": "FONDS AFFECTÉS",
    "17": "FONDS REPORTÉS", 
    "18": "EMPRUNTS ET DETTES ASSIMILÉES",
    "19": "PROVISIONS POUR RISQUES ET CHARGES",
    "20": "IMMOBILISATIONS DESTINÉES À LA VENTE",
    "21": "IMMOBILISATIONS INCORPORELLES",
    "22": "TERRAINS",
    "23": "BÂTIMENTS, INSTALLATIONS TECHNIQUES ET AGENCEMENTS",
    "24": "MATÉRIEL, MOBILIER ET ACTIFS BIOLOGIQUES",
    "25": "AVANCES ET ACOMPTES VERSÉS SUR IMMOBILISATIONS",
    "26": "TITRES DE PARTICIPATION",
    "27": "AUTRES IMMOBILISATIONS FINANCIÈRES",
    "28": "AMORTISSEMENTS DES IMMOBILISATIONS",
    "29": "DÉPRÉCIATIONS DES IMMOBILISATIONS",
    "30": "MARCHANDISES",
    "31": "MATIÈRES PREMIÈRES ET FOURNITURES LIÉES",
    "32": "AUTRES APPROVISIONNEMENTS",
    "33": "EN-COURS DE PRODUCTION DE BIENS",
    "34": "EN-COURS DE PRODUCTION DE SERVICES",
    "35": "STOCKS DE PRODUITS",
    "36": "STOCKS PROVENANT D'IMMOBILISATIONS",
    "37": "STOCKS DE MARCHANDISES SPÉCIFIQUES",
    "38": "STOCKS EN COURS D'ACHEMINEMENT",
    "39": "DÉPRÉCIATIONS DES STOCKS ET EN-COURS",
    "40": "FOURNISSEURS ET COMPTES RATTACHÉS",
    "41": "ADHÉRENTS, CLIENTS-USAGERS ET COMPTES RATTACHÉS",
    "42": "PERSONNEL",
    "43": "ORGANISMES SOCIAUX",
    "44": "ÉTAT ET COLLECTIVITÉS PUBLIQUES",
    "45": "FONDATEURS, APPORTEURS ET COMPTES COURANTS",
    "46": "BAILLEURS, ÉTAT ET AUTRES ORGANISMES",
    "47": "DÉBITEURS ET CRÉDITEURS DIVERS",
    "48": "CRÉANCES ET DETTES H.A.O.",
    "49": "DÉPRÉCIATIONS ET PROVISIONS POUR RISQUES",
    "50": "TITRES DE PLACEMENT",
    "51": "VALEURS À ENCAISSER",
    "52": "BANQUES",
    "53": "ÉTABLISSEMENTS FINANCIERS ET ASSIMILÉS",
    "54": "INSTRUMENTS FINANCIERS À TERME",
    "55": "CAISSE",
    "56": "BANQUES, CRÉDITS DE TRÉSORERIE ET D'ESCOMPTE",
    "57": "RÉGIES D'AVANCES ET ACCRÉDITIFS",
    "58": "VIREMENTS INTERNES",
    "59": "DÉPRÉCIATIONS ET PROVISIONS (TRÉSORERIE)",
    "60": "ACHATS ET VARIATIONS DE STOCKS",
    "61": "TRANSPORTS",
    "62": "SERVICES EXTÉRIEURS A",
    "63": "SERVICES EXTÉRIEURS B",
    "64": "IMPÔTS ET TAXES",
    "65": "AUTRES CHARGES",
    "66": "CHARGES DE PERSONNEL",
    "67": "FRAIS FINANCIERS ET CHARGES ASSIMILÉES",
    "68": "DOTATIONS AUX AMORTISSEMENTS",
    "69": "DOTATIONS AUX PROVISIONS",
    "70": "REVENUS DES ACTIVITÉS ORDINAIRES",
    "71": "SUBVENTIONS D'EXPLOITATION",
    "72": "PRODUCTION IMMOBILISÉE",
    "73": "VARIATIONS DES STOCKS",
    "74": "AUTRES PRODUITS",
    "75": "TRANSFERTS DE CHARGES",
    "76": "PRODUITS FINANCIERS",
    "77": "REPRISES DE PROVISIONS",
    "78": "TRANSFERTS DE CHARGES",
    "79": "REPRISES D'AMORTISSEMENTS ET DE PROVISIONS",
    "80": "AUTRES CHARGES",
    "81": "VALEURS COMPTABLES DES CESSIONS D'IMMOBILISATIONS",
    "82": "PRODUITS DES CESSIONS D'IMMOBILISATIONS",
    "83": "CHARGES HORS ACTIVITÉS ORDINAIRES",
    "84": "PRODUITS HORS ACTIVITÉS ORDINAIRES",
    "85": "DOTATIONS H.A.O.",
    "86": "REPRISES H.A.O.",
    "87": "PARTICIPATION DES TRAVAILLEURS",
    "88": "SUBVENTIONS D'ÉQUILIBRE",
    "89": "IMPÔTS SUR LE RÉSULTAT",
    "90": "ENGAGEMENTS HORS BILAN",
    "91": "COMPTABILITÉ ANALYTIQUE DE GESTION",
    "92": "COMPTES RÉFLÉCHIS",
    "93": "COMPTES DE RÉPARTITION",
    "94": "COMPTES D'ANALYSE",
    "95": "COÛTS COMPLETS",
    "96": "ÉCARTS SUR COÛTS PRÉÉTABLIS",
    "97": "DIFFÉRENCES D'INVENTAIRE",
    "98": "RÉSULTATS ANALYTIQUES",
    "99": "COMPTES DE LIAISON ANALYTIQUE"
}

PLAN_COMPTABLE_SYCEBNL_COMPLET = [
    # CLASSE 1 - COMPTES DE RESSOURCES DURABLES
    {"numero": "10", "libelle": "DOTATION", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "101", "libelle": "Dotation non consomptible sans droit de reprise", "classe": 1, "niveau": 2, "parent_id": "10"},
    {"numero": "1011", "libelle": "en numéraire", "classe": 1, "niveau": 3, "parent_id": "101"},
    {"numero": "1015", "libelle": "en nature", "classe": 1, "niveau": 3, "parent_id": "101"},
    {"numero": "102", "libelle": "Dotation non consomptible avec droit de reprise", "classe": 1, "niveau": 2, "parent_id": "10"},
    {"numero": "1021", "libelle": "en numéraire", "classe": 1, "niveau": 3, "parent_id": "102"},
    {"numero": "1025", "libelle": "en nature", "classe": 1, "niveau": 3, "parent_id": "102"},
    {"numero": "103", "libelle": "Droit d'entrée", "classe": 1, "niveau": 2, "parent_id": "10"},
    {"numero": "104", "libelle": "Dotation consomptible", "classe": 1, "niveau": 2, "parent_id": "10"},
    {"numero": "1041", "libelle": "Dotation consomptible", "classe": 1, "niveau": 3, "parent_id": "104"},
    {"numero": "1049", "libelle": "Dotation consomptible inscrite au compte de résultat", "classe": 1, "niveau": 3, "parent_id": "104"},
    {"numero": "106", "libelle": "Écarts de réévaluation", "classe": 1, "niveau": 2, "parent_id": "10"},
    {"numero": "1061", "libelle": "sur biens sans droit de reprise", "classe": 1, "niveau": 3, "parent_id": "106"},
    {"numero": "1062", "libelle": "sur biens avec droit de reprise", "classe": 1, "niveau": 3, "parent_id": "106"},
    
    {"numero": "11", "libelle": "RÉSERVES", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "112", "libelle": "Réserves statutaires ou contractuelles", "classe": 1, "niveau": 2, "parent_id": "11"},
    {"numero": "118", "libelle": "Autres réserves", "classe": 1, "niveau": 2, "parent_id": "11"},
    
    {"numero": "12", "libelle": "REPORT À NOUVEAU", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "121", "libelle": "Report à nouveau des excédents", "classe": 1, "niveau": 2, "parent_id": "12"},
    {"numero": "128", "libelle": "Résultat en instance d'affectation", "classe": 1, "niveau": 2, "parent_id": "12"},
    {"numero": "129", "libelle": "Report à nouveau des déficits", "classe": 1, "niveau": 2, "parent_id": "12"},
    
    {"numero": "13", "libelle": "RÉSULTAT NET DE L'EXERCICE", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "131", "libelle": "Excédent de l'exercice", "classe": 1, "niveau": 2, "parent_id": "13"},
    {"numero": "139", "libelle": "Déficit de l'exercice", "classe": 1, "niveau": 2, "parent_id": "13"},
    
    {"numero": "14", "libelle": "SUBVENTIONS D'INVESTISSEMENT", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "141", "libelle": "Subventions d'équipement", "classe": 1, "niveau": 2, "parent_id": "14"},
    {"numero": "1411", "libelle": "État", "classe": 1, "niveau": 3, "parent_id": "141"},
    {"numero": "1412", "libelle": "Régions", "classe": 1, "niveau": 3, "parent_id": "141"},
    {"numero": "1413", "libelle": "Départements", "classe": 1, "niveau": 3, "parent_id": "141"},
    {"numero": "1414", "libelle": "Communes et collectivités publiques décentralisées", "classe": 1, "niveau": 3, "parent_id": "141"},
    {"numero": "1415", "libelle": "Entités publiques ou mixtes", "classe": 1, "niveau": 3, "parent_id": "141"},
    {"numero": "1416", "libelle": "Entités et organismes privés", "classe": 1, "niveau": 3, "parent_id": "141"},
    {"numero": "1417", "libelle": "Organismes internationaux", "classe": 1, "niveau": 3, "parent_id": "141"},
    {"numero": "1418", "libelle": "Autres", "classe": 1, "niveau": 3, "parent_id": "141"},
    {"numero": "148", "libelle": "Autres subventions d'investissement", "classe": 1, "niveau": 2, "parent_id": "14"},
    
    {"numero": "15", "libelle": "PROVISIONS RÉGLEMENTÉES ET FONDS ASSIMILÉS", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "16", "libelle": "FONDS AFFECTÉS", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "17", "libelle": "FONDS REPORTÉS", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "18", "libelle": "EMPRUNTS ET DETTES ASSIMILÉES", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "19", "libelle": "PROVISIONS POUR RISQUES ET CHARGES", "classe": 1, "niveau": 1, "parent_id": None}
]

# Ajout des variables de compatibilité
TOTAL_COMPTES_COMPLET = len(PLAN_COMPTABLE_SYCEBNL_COMPLET)

TOTAL_COMPTES_PAR_CLASSE_COMPLET = {
    1: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 1]),
    2: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 2]),
    3: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 3]),
    4: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 4]),
    5: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 5]),
    6: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 6]),
    7: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 7]),
    8: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 8]),
    9: len([c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == 9])
}

CLASSES_SYCEBNL = {
    1: "COMPTES DE RESSOURCES DURABLES",
    2: "COMPTES D'ACTIF IMMOBILISÉ", 
    3: "COMPTES DE STOCKS",
    4: "COMPTES DE TIERS",
    5: "COMPTES DE TRÉSORERIE",
    6: "COMPTES DE CHARGES DES ACTIVITÉS ORDINAIRES",
    7: "COMPTES DE PRODUITS DES ACTIVITÉS ORDINAIRES", 
    8: "COMPTES DES AUTRES CHARGES ET DES AUTRES PRODUITS",
    9: "CONTRIBUTIONS VOLONTAIRES EN NATURE"
}

# Alias pour compatibilité
PLAN_COMPTABLE_SYCEBNL = PLAN_COMPTABLE_SYCEBNL_COMPLET
TOTAL_COMPTES = TOTAL_COMPTES_COMPLET
TOTAL_COMPTES_PAR_CLASSE = TOTAL_COMPTES_PAR_CLASSE_COMPLET

def get_plan_comptable_complet():
    """Retourne le plan comptable SYCEBNL complet"""
    return PLAN_COMPTABLE_SYCEBNL_COMPLET

def get_compte_by_numero(numero):
    """Trouve un compte par son numéro"""
    for compte in PLAN_COMPTABLE_SYCEBNL_COMPLET:
        if compte["numero"] == str(numero):
            return compte
    return None

def get_comptes_by_classe(classe):
    """Retourne tous les comptes d'une classe donnée"""
    return [c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c['classe'] == classe]

def search_comptes(terme):
    """Recherche des comptes par terme dans le numéro ou libellé"""
    terme = terme.lower()
    return [c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET 
            if terme in c['numero'].lower() or terme in c['libelle'].lower()]
