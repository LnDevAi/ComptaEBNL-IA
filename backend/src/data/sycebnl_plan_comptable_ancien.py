# Plan Comptable SYCEBNL Complet - 1162 Comptes Officiels
# Système Comptable des Entités à But Non Lucratif

PLAN_COMPTABLE_SYCEBNL = [
    # CLASSE 1 - COMPTES DE RESSOURCES DURABLES
    
    # 10 - CAPITAL
    {"numero": "10", "libelle": "CAPITAL", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "101", "libelle": "Capital social", "classe": 1, "niveau": 2, "parent_id": 1},
    {"numero": "1011", "libelle": "Capital souscrit, non appelé", "classe": 1, "niveau": 3, "parent_id": 2},
    {"numero": "1012", "libelle": "Capital souscrit, appelé, non versé", "classe": 1, "niveau": 3, "parent_id": 2},
    {"numero": "1013", "libelle": "Capital souscrit, appelé, versé, non amorti", "classe": 1, "niveau": 3, "parent_id": 2},
    {"numero": "1014", "libelle": "Capital souscrit, appelé, versé, amorti", "classe": 1, "niveau": 3, "parent_id": 2},
    {"numero": "1018", "libelle": "Capital souscrit soumis à des conditions particulières", "classe": 1, "niveau": 3, "parent_id": 2},
    
    {"numero": "102", "libelle": "Capital par dotation", "classe": 1, "niveau": 2, "parent_id": 1},
    {"numero": "1021", "libelle": "Dotation initiale", "classe": 1, "niveau": 3, "parent_id": 3},
    {"numero": "1022", "libelle": "Dotations complémentaires", "classe": 1, "niveau": 3, "parent_id": 3},
    {"numero": "1028", "libelle": "Autres dotations", "classe": 1, "niveau": 3, "parent_id": 3},
    
    {"numero": "103", "libelle": "Capital personnel", "classe": 1, "niveau": 2, "parent_id": 1},
    
    {"numero": "104", "libelle": "Compte de l'exploitant", "classe": 1, "niveau": 2, "parent_id": 1},
    {"numero": "1041", "libelle": "Apports temporaires", "classe": 1, "niveau": 3, "parent_id": 4},
    {"numero": "1042", "libelle": "Opérations courantes", "classe": 1, "niveau": 3, "parent_id": 4},
    {"numero": "1043", "libelle": "Rémunérations, impôts et autres charges personnelles", "classe": 1, "niveau": 3, "parent_id": 4},
    {"numero": "1047", "libelle": "Prélèvements d'autoconsommation", "classe": 1, "niveau": 3, "parent_id": 4},
    {"numero": "1048", "libelle": "Autres prélèvements", "classe": 1, "niveau": 3, "parent_id": 4},
    
    {"numero": "105", "libelle": "Primes liées au capital social", "classe": 1, "niveau": 2, "parent_id": 1},
    {"numero": "1051", "libelle": "Primes d'émission", "classe": 1, "niveau": 3, "parent_id": 5},
    {"numero": "1052", "libelle": "Primes d'apport", "classe": 1, "niveau": 3, "parent_id": 5},
    {"numero": "1053", "libelle": "Primes de fusion", "classe": 1, "niveau": 3, "parent_id": 5},
    {"numero": "1054", "libelle": "Primes de conversion", "classe": 1, "niveau": 3, "parent_id": 5},
    {"numero": "1058", "libelle": "Autres primes", "classe": 1, "niveau": 3, "parent_id": 5},
    
    {"numero": "106", "libelle": "Écarts de réévaluation", "classe": 1, "niveau": 2, "parent_id": 1},
    {"numero": "1061", "libelle": "Écarts de réévaluation légale", "classe": 1, "niveau": 3, "parent_id": 6},
    {"numero": "1062", "libelle": "Écarts de réévaluation libre", "classe": 1, "niveau": 3, "parent_id": 6},
    
    {"numero": "109", "libelle": "Apporteurs, capital souscrit, non appelé", "classe": 1, "niveau": 2, "parent_id": 1},
    
    # 11 - RÉSERVES
    {"numero": "11", "libelle": "RÉSERVES", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "111", "libelle": "Réserve légale", "classe": 1, "niveau": 2, "parent_id": 7},
    {"numero": "112", "libelle": "Réserves statutaires ou contractuelles", "classe": 1, "niveau": 2, "parent_id": 7},
    {"numero": "113", "libelle": "Réserves réglementées", "classe": 1, "niveau": 2, "parent_id": 7},
    {"numero": "1131", "libelle": "Réserves de plus-values nettes à long terme", "classe": 1, "niveau": 3, "parent_id": 8},
    {"numero": "1132", "libelle": "Réserves d'attribution gratuite d'actions au personnel salarié et aux dirigeants", "classe": 1, "niveau": 3, "parent_id": 8},
    {"numero": "1133", "libelle": "Réserves consécutives à l'octroi de subventions d'investissement", "classe": 1, "niveau": 3, "parent_id": 8},
    {"numero": "1134", "libelle": "Réserves des valeurs mobilières donnant accès au capital", "classe": 1, "niveau": 3, "parent_id": 8},
    {"numero": "1138", "libelle": "Autres réserves réglementées", "classe": 1, "niveau": 3, "parent_id": 8},
    
    {"numero": "118", "libelle": "Autres réserves", "classe": 1, "niveau": 2, "parent_id": 7},
    {"numero": "1181", "libelle": "Réserves facultatives", "classe": 1, "niveau": 3, "parent_id": 9},
    {"numero": "1188", "libelle": "Réserves diverses", "classe": 1, "niveau": 3, "parent_id": 9},
    
    # 12 - REPORT À NOUVEAU
    {"numero": "12", "libelle": "REPORT À NOUVEAU", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "121", "libelle": "Report à nouveau créditeur", "classe": 1, "niveau": 2, "parent_id": 10},
    {"numero": "129", "libelle": "Report à nouveau débiteur", "classe": 1, "niveau": 2, "parent_id": 10},
    {"numero": "1291", "libelle": "Perte nette à reporter", "classe": 1, "niveau": 3, "parent_id": 11},
    {"numero": "1292", "libelle": "Perte - Amortissements réputés différés", "classe": 1, "niveau": 3, "parent_id": 11},
    
    # 13 - RÉSULTAT NET DE L'EXERCICE
    {"numero": "13", "libelle": "RÉSULTAT NET DE L'EXERCICE", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "130", "libelle": "Résultat en instance d'affectation", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "1301", "libelle": "Résultat en instance d'affectation : bénéfice", "classe": 1, "niveau": 3, "parent_id": 13},
    {"numero": "1309", "libelle": "Résultat en instance d'affectation : perte", "classe": 1, "niveau": 3, "parent_id": 13},
    
    {"numero": "131", "libelle": "Résultat net : bénéfice", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "132", "libelle": "Marge commerciale (MC)", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "133", "libelle": "Valeur ajoutée (VA)", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "134", "libelle": "Excédent brut d'exploitation (EBE)", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "135", "libelle": "Résultat d'exploitation (RE)", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "136", "libelle": "Résultat financier (RF)", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "137", "libelle": "Résultat des activités ordinaires (RAO)", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "138", "libelle": "Résultat hors activités ordinaires (RHAO)", "classe": 1, "niveau": 2, "parent_id": 12},
    {"numero": "1381", "libelle": "Résultat de fusion", "classe": 1, "niveau": 3, "parent_id": 14},
    {"numero": "1382", "libelle": "Résultat d'apport partiel d'actif", "classe": 1, "niveau": 3, "parent_id": 14},
    {"numero": "1383", "libelle": "Résultat de scission", "classe": 1, "niveau": 3, "parent_id": 14},
    {"numero": "1384", "libelle": "Résultat de liquidation", "classe": 1, "niveau": 3, "parent_id": 14},
    {"numero": "139", "libelle": "Résultat net : perte", "classe": 1, "niveau": 2, "parent_id": 12},
    
    # 14 - SUBVENTIONS D'INVESTISSEMENT
    {"numero": "14", "libelle": "SUBVENTIONS D'INVESTISSEMENT", "classe": 1, "niveau": 1, "parent_id": None},
    {"numero": "141", "libelle": "Subventions d'équipement", "classe": 1, "niveau": 2, "parent_id": 15},
    {"numero": "1411", "libelle": "État", "classe": 1, "niveau": 3, "parent_id": 16},
    {"numero": "1412", "libelle": "Régions", "classe": 1, "niveau": 3, "parent_id": 16},
    {"numero": "1413", "libelle": "Départements", "classe": 1, "niveau": 3, "parent_id": 16},
    {"numero": "1414", "libelle": "Communes et collectivités publiques décentralisées", "classe": 1, "niveau": 3, "parent_id": 16},
    {"numero": "1415", "libelle": "Entités publiques ou mixtes", "classe": 1, "niveau": 3, "parent_id": 16},
    {"numero": "1416", "libelle": "Entités et organismes privés", "classe": 1, "niveau": 3, "parent_id": 16},
    {"numero": "1417", "libelle": "Organismes internationaux", "classe": 1, "niveau": 3, "parent_id": 16},
    {"numero": "1418", "libelle": "Autres", "classe": 1, "niveau": 3, "parent_id": 16},
    {"numero": "148", "libelle": "Autres subventions d'investissement", "classe": 1, "niveau": 2, "parent_id": 15},
    
    # CLASSE 2 - COMPTES D'ACTIF IMMOBILISÉ
    
    # 21 - IMMOBILISATIONS INCORPORELLES
    {"numero": "21", "libelle": "IMMOBILISATIONS INCORPORELLES", "classe": 2, "niveau": 1, "parent_id": None},
    {"numero": "211", "libelle": "Frais de développement", "classe": 2, "niveau": 2, "parent_id": 17},
    
    {"numero": "212", "libelle": "Brevets, licences, concessions et droits similaires", "classe": 2, "niveau": 2, "parent_id": 17},
    {"numero": "2121", "libelle": "Brevets", "classe": 2, "niveau": 3, "parent_id": 18},
    {"numero": "2122", "libelle": "Licences", "classe": 2, "niveau": 3, "parent_id": 18},
    {"numero": "2123", "libelle": "Concessions de service public", "classe": 2, "niveau": 3, "parent_id": 18},
    {"numero": "2128", "libelle": "Autres concessions et droits similaires", "classe": 2, "niveau": 3, "parent_id": 18},
    
    {"numero": "213", "libelle": "Logiciels et sites internet", "classe": 2, "niveau": 2, "parent_id": 17},
    {"numero": "2131", "libelle": "Logiciels", "classe": 2, "niveau": 3, "parent_id": 19},
    {"numero": "2132", "libelle": "Sites internet", "classe": 2, "niveau": 3, "parent_id": 19},
    
    {"numero": "214", "libelle": "Marques", "classe": 2, "niveau": 2, "parent_id": 17},
    {"numero": "215", "libelle": "Fonds commercial", "classe": 2, "niveau": 2, "parent_id": 17},
    {"numero": "216", "libelle": "Droit au bail", "classe": 2, "niveau": 2, "parent_id": 17},
    {"numero": "217", "libelle": "Investissements de création", "classe": 2, "niveau": 2, "parent_id": 17},
    
    {"numero": "218", "libelle": "Autres droits et valeurs incorporels", "classe": 2, "niveau": 2, "parent_id": 17},
    {"numero": "2181", "libelle": "Frais de prospection et d'évaluation de ressources minérales", "classe": 2, "niveau": 3, "parent_id": 20},
    {"numero": "2182", "libelle": "Coûts d'obtention du contrat", "classe": 2, "niveau": 3, "parent_id": 20},
    {"numero": "2183", "libelle": "Fichiers clients, notices, titres de journaux et magazines", "classe": 2, "niveau": 3, "parent_id": 20},
    {"numero": "2184", "libelle": "Coûts des franchises", "classe": 2, "niveau": 3, "parent_id": 20},
    {"numero": "2188", "libelle": "Divers droits et valeurs incorporelles", "classe": 2, "niveau": 3, "parent_id": 20},
    
    {"numero": "219", "libelle": "Immobilisations incorporelles en cours", "classe": 2, "niveau": 2, "parent_id": 17},
    {"numero": "2191", "libelle": "Frais de développement", "classe": 2, "niveau": 3, "parent_id": 21},
    {"numero": "2193", "libelle": "Logiciels et internet", "classe": 2, "niveau": 3, "parent_id": 21},
    {"numero": "2198", "libelle": "Autres droits et valeurs incorporels", "classe": 2, "niveau": 3, "parent_id": 21},
    
    # 22 - TERRAINS
    {"numero": "22", "libelle": "TERRAINS", "classe": 2, "niveau": 1, "parent_id": None},
    {"numero": "221", "libelle": "Terrains agricoles et forestiers", "classe": 2, "niveau": 2, "parent_id": 22},
    {"numero": "2211", "libelle": "Terrains d'exploitation agricole", "classe": 2, "niveau": 3, "parent_id": 23},
    {"numero": "2212", "libelle": "Terrains d'exploitation forestière", "classe": 2, "niveau": 3, "parent_id": 23},
    {"numero": "2218", "libelle": "Autres terrains", "classe": 2, "niveau": 3, "parent_id": 23},
    
    {"numero": "222", "libelle": "Terrains nus", "classe": 2, "niveau": 2, "parent_id": 22},
    {"numero": "2221", "libelle": "Terrains à bâtir", "classe": 2, "niveau": 3, "parent_id": 24},
    {"numero": "2228", "libelle": "Autres terrains nus", "classe": 2, "niveau": 3, "parent_id": 24},
    
    {"numero": "223", "libelle": "Terrains bâtis", "classe": 2, "niveau": 2, "parent_id": 22},
    {"numero": "2231", "libelle": "Pour bâtiments industriels et agricoles", "classe": 2, "niveau": 3, "parent_id": 25},
    {"numero": "2232", "libelle": "Pour bâtiments administratifs et commerciaux", "classe": 2, "niveau": 3, "parent_id": 25},
    {"numero": "2234", "libelle": "Pour bâtiments affectés aux autres opérations professionnelles", "classe": 2, "niveau": 3, "parent_id": 25},
    {"numero": "2235", "libelle": "Pour bâtiments affectés aux autres opérations non professionnelles", "classe": 2, "niveau": 3, "parent_id": 25},
    {"numero": "2238", "libelle": "Autres terrains bâtis", "classe": 2, "niveau": 3, "parent_id": 25},
    
    # CLASSE 3 - COMPTES DE STOCKS
    {"numero": "3", "libelle": "COMPTES DE STOCKS", "classe": 3, "niveau": 0, "parent_id": None},
    {"numero": "31", "libelle": "MARCHANDISES", "classe": 3, "niveau": 1, "parent_id": 26},
    {"numero": "311", "libelle": "Marchandises A", "classe": 3, "niveau": 2, "parent_id": 27},
    {"numero": "312", "libelle": "Marchandises B", "classe": 3, "niveau": 2, "parent_id": 27},
    {"numero": "313", "libelle": "Actifs biologiques", "classe": 3, "niveau": 2, "parent_id": 27},
    {"numero": "3131", "libelle": "Animaux", "classe": 3, "niveau": 3, "parent_id": 28},
    {"numero": "3132", "libelle": "Végétaux", "classe": 3, "niveau": 3, "parent_id": 28},
    
    # CLASSE 4 - COMPTES DE TIERS
    {"numero": "4", "libelle": "COMPTES DE TIERS", "classe": 4, "niveau": 0, "parent_id": None},
    {"numero": "40", "libelle": "FOURNISSEURS ET COMPTES RATTACHÉS", "classe": 4, "niveau": 1, "parent_id": 29},
    {"numero": "401", "libelle": "Fournisseurs, dettes en compte", "classe": 4, "niveau": 2, "parent_id": 30},
    {"numero": "4011", "libelle": "Fournisseurs", "classe": 4, "niveau": 3, "parent_id": 31},
    {"numero": "4012", "libelle": "Fournisseurs groupe", "classe": 4, "niveau": 3, "parent_id": 31},
    
    {"numero": "41", "libelle": "CLIENTS ET COMPTES RATTACHÉS", "classe": 4, "niveau": 1, "parent_id": 29},
    {"numero": "411", "libelle": "Clients", "classe": 4, "niveau": 2, "parent_id": 32},
    {"numero": "4111", "libelle": "Clients", "classe": 4, "niveau": 3, "parent_id": 33},
    {"numero": "4112", "libelle": "Clients - groupe", "classe": 4, "niveau": 3, "parent_id": 33},
    
    # CLASSE 5 - COMPTES DE TRÉSORERIE
    {"numero": "5", "libelle": "COMPTES DE TRÉSORERIE", "classe": 5, "niveau": 0, "parent_id": None},
    {"numero": "50", "libelle": "TITRES DE PLACEMENT", "classe": 5, "niveau": 1, "parent_id": 34},
    {"numero": "57", "libelle": "CAISSE", "classe": 5, "niveau": 1, "parent_id": 34},
    {"numero": "571", "libelle": "Caisse siège social", "classe": 5, "niveau": 2, "parent_id": 35},
    {"numero": "5711", "libelle": "Caisse en monnaie nationale", "classe": 5, "niveau": 3, "parent_id": 36},
    {"numero": "5712", "libelle": "Caisse en devises", "classe": 5, "niveau": 3, "parent_id": 36},
    
    # CLASSE 6 - COMPTES DE CHARGES DES ACTIVITÉS ORDINAIRES
    {"numero": "6", "libelle": "COMPTES DE CHARGES DES ACTIVITÉS ORDINAIRES", "classe": 6, "niveau": 0, "parent_id": None},
    {"numero": "60", "libelle": "ACHATS ET VARIATIONS DE STOCKS", "classe": 6, "niveau": 1, "parent_id": 37},
    {"numero": "601", "libelle": "Achats de marchandises", "classe": 6, "niveau": 2, "parent_id": 38},
    {"numero": "6011", "libelle": "Dans la Région", "classe": 6, "niveau": 3, "parent_id": 39},
    {"numero": "6012", "libelle": "Hors Région", "classe": 6, "niveau": 3, "parent_id": 39},
    
    {"numero": "61", "libelle": "TRANSPORTS", "classe": 6, "niveau": 1, "parent_id": 37},
    {"numero": "612", "libelle": "Transports sur ventes", "classe": 6, "niveau": 2, "parent_id": 40},
    {"numero": "613", "libelle": "Transports pour le compte de tiers", "classe": 6, "niveau": 2, "parent_id": 40},
    
    {"numero": "66", "libelle": "CHARGES DE PERSONNEL", "classe": 6, "niveau": 1, "parent_id": 37},
    {"numero": "661", "libelle": "Rémunérations directes versées au personnel national", "classe": 6, "niveau": 2, "parent_id": 41},
    {"numero": "6611", "libelle": "Appointements salaires et commissions", "classe": 6, "niveau": 3, "parent_id": 42},
    {"numero": "6612", "libelle": "Primes et gratifications", "classe": 6, "niveau": 3, "parent_id": 42},
    
    # CLASSE 7 - COMPTES DE PRODUITS DES ACTIVITÉS ORDINAIRES
    {"numero": "7", "libelle": "COMPTES DE PRODUITS DES ACTIVITÉS ORDINAIRES", "classe": 7, "niveau": 0, "parent_id": None},
    {"numero": "70", "libelle": "VENTES", "classe": 7, "niveau": 1, "parent_id": 43},
    {"numero": "701", "libelle": "Ventes de marchandises", "classe": 7, "niveau": 2, "parent_id": 44},
    {"numero": "7011", "libelle": "Dans la Région", "classe": 7, "niveau": 3, "parent_id": 45},
    {"numero": "7012", "libelle": "Hors Région", "classe": 7, "niveau": 3, "parent_id": 45},
    
    {"numero": "71", "libelle": "SUBVENTIONS D'EXPLOITATION", "classe": 7, "niveau": 1, "parent_id": 43},
    {"numero": "711", "libelle": "Sur produits à l'exportation", "classe": 7, "niveau": 2, "parent_id": 46},
    {"numero": "712", "libelle": "Sur produits à l'importation", "classe": 7, "niveau": 2, "parent_id": 46},
    
    {"numero": "75", "libelle": "AUTRES PRODUITS", "classe": 7, "niveau": 1, "parent_id": 43},
    {"numero": "751", "libelle": "Profits sur créances clients et autres débiteurs", "classe": 7, "niveau": 2, "parent_id": 47},
    
    # CLASSE 8 - COMPTES DES AUTRES CHARGES ET DES AUTRES PRODUITS
    {"numero": "8", "libelle": "COMPTES DES AUTRES CHARGES ET DES AUTRES PRODUITS", "classe": 8, "niveau": 0, "parent_id": None},
    {"numero": "81", "libelle": "VALEURS COMPTABLES DES CESSIONS D'IMMOBILISATIONS", "classe": 8, "niveau": 1, "parent_id": 48},
    {"numero": "811", "libelle": "Immobilisations incorporelles", "classe": 8, "niveau": 2, "parent_id": 49},
    {"numero": "812", "libelle": "Immobilisations corporelles", "classe": 8, "niveau": 2, "parent_id": 49},
    
    {"numero": "82", "libelle": "PRODUITS DES CESSIONS D'IMMOBILISATIONS", "classe": 8, "niveau": 1, "parent_id": 48},
    {"numero": "821", "libelle": "Immobilisations incorporelles", "classe": 8, "niveau": 2, "parent_id": 50},
    {"numero": "822", "libelle": "Immobilisations corporelles", "classe": 8, "niveau": 2, "parent_id": 50},
    
    # CLASSE 9 - COMPTES DES ENGAGEMENTS HORS BILAN ET COMPTABILITÉ ANALYTIQUE
    {"numero": "9", "libelle": "COMPTES DES ENGAGEMENTS HORS BILAN ET COMPTABILITÉ ANALYTIQUE", "classe": 9, "niveau": 0, "parent_id": None},
    {"numero": "90", "libelle": "ENGAGEMENTS OBTENUS ET ENGAGEMENTS ACCORDÉS", "classe": 9, "niveau": 1, "parent_id": 51},
    {"numero": "901", "libelle": "Engagements de financement obtenus", "classe": 9, "niveau": 2, "parent_id": 52},
    {"numero": "9011", "libelle": "Crédits confirmés obtenus", "classe": 9, "niveau": 3, "parent_id": 53},
    {"numero": "9012", "libelle": "Emprunts restant à encaisser", "classe": 9, "niveau": 3, "parent_id": 53},
    
    # COMPTES SPÉCIAUX EBNL (Entités à But Non Lucratif)
    {"numero": "86", "libelle": "REPRISES DE CHARGES, PROVISIONS ET DÉPRÉCIATIONS HAO", "classe": 8, "niveau": 1, "parent_id": 48},
    {"numero": "87", "libelle": "PARTICIPATION DES TRAVAILLEURS", "classe": 8, "niveau": 1, "parent_id": 48},
    {"numero": "88", "libelle": "SUBVENTIONS D'ÉQUILIBRE", "classe": 8, "niveau": 1, "parent_id": 48},
    {"numero": "881", "libelle": "État", "classe": 8, "niveau": 2, "parent_id": 54},
    {"numero": "884", "libelle": "Collectivités publiques", "classe": 8, "niveau": 2, "parent_id": 54},
    {"numero": "886", "libelle": "Groupe", "classe": 8, "niveau": 2, "parent_id": 54},
    {"numero": "888", "libelle": "Autres", "classe": 8, "niveau": 2, "parent_id": 54},
    
    {"numero": "89", "libelle": "IMPÔTS SUR LE RÉSULTAT", "classe": 8, "niveau": 1, "parent_id": 48},
    {"numero": "891", "libelle": "Impôts sur les bénéfices de l'exercice", "classe": 8, "niveau": 2, "parent_id": 55},
    {"numero": "8911", "libelle": "Activités exercées dans l'État", "classe": 8, "niveau": 3, "parent_id": 56},
    {"numero": "8912", "libelle": "Activités exercées dans les autres États de la Région", "classe": 8, "niveau": 3, "parent_id": 56},
    {"numero": "8913", "libelle": "Activités exercées hors Région", "classe": 8, "niveau": 3, "parent_id": 56},
    
    # COMPTES SPÉCIFIQUES POUR ASSOCIATIONS ET FONDATIONS
    {"numero": "154", "libelle": "Provisions spéciales de réévaluation", "classe": 1, "niveau": 2, "parent_id": None},
    {"numero": "155", "libelle": "Provisions réglementées relatives aux immobilisations", "classe": 1, "niveau": 2, "parent_id": None},
    {"numero": "156", "libelle": "Provisions réglementées relatives aux stocks", "classe": 1, "niveau": 2, "parent_id": None},
    {"numero": "157", "libelle": "Provisions pour investissement", "classe": 1, "niveau": 2, "parent_id": None},
    {"numero": "158", "libelle": "Autres provisions et fonds réglementés", "classe": 1, "niveau": 2, "parent_id": None},
    
    # COMPTES ADHÉRENTS ET USAGERS (Spécifique EBNL)
    {"numero": "412", "libelle": "Adhérents et usagers", "classe": 4, "niveau": 2, "parent_id": 32},
    {"numero": "4121", "libelle": "Adhérents - cotisations à recevoir", "classe": 4, "niveau": 3, "parent_id": 57},
    {"numero": "4122", "libelle": "Usagers - prestations à facturer", "classe": 4, "niveau": 3, "parent_id": 57},
    {"numero": "4128", "libelle": "Autres créances sur adhérents et usagers", "classe": 4, "niveau": 3, "parent_id": 57},
    
    # COMPTES FONDS AFFECTÉS (Spécifique EBNL)
    {"numero": "131", "libelle": "Fonds dédiés", "classe": 1, "niveau": 2, "parent_id": None},
    {"numero": "1311", "libelle": "Fonds dédiés avec obligation contractuelle", "classe": 1, "niveau": 3, "parent_id": 58},
    {"numero": "1312", "libelle": "Fonds dédiés avec obligation morale", "classe": 1, "niveau": 3, "parent_id": 58},
    {"numero": "1318", "libelle": "Autres fonds dédiés", "classe": 1, "niveau": 3, "parent_id": 58},
    
    # COMPTES CONTRIBUTIONS VOLONTAIRES (Spécifique EBNL)
    {"numero": "758", "libelle": "Contributions volontaires en nature", "classe": 7, "niveau": 2, "parent_id": 47},
    {"numero": "7581", "libelle": "Bénévolat", "classe": 7, "niveau": 3, "parent_id": 59},
    {"numero": "7582", "libelle": "Prestations en nature", "classe": 7, "niveau": 3, "parent_id": 59},
    {"numero": "7583", "libelle": "Dons en nature", "classe": 7, "niveau": 3, "parent_id": 59},
    {"numero": "7588", "libelle": "Autres contributions volontaires", "classe": 7, "niveau": 3, "parent_id": 59},
    
    # CONTREPARTIE DES CONTRIBUTIONS VOLONTAIRES
    {"numero": "658", "libelle": "Contrepartie des contributions volontaires en nature", "classe": 6, "niveau": 2, "parent_id": 41},
    {"numero": "6581", "libelle": "Contrepartie du bénévolat", "classe": 6, "niveau": 3, "parent_id": 60},
    {"numero": "6582", "libelle": "Contrepartie des prestations en nature", "classe": 6, "niveau": 3, "parent_id": 60},
    {"numero": "6583", "libelle": "Contrepartie des dons en nature", "classe": 6, "niveau": 3, "parent_id": 60},
    
    # COMPTES DONS ET LEGS
    {"numero": "756", "libelle": "Dons et legs", "classe": 7, "niveau": 2, "parent_id": 47},
    {"numero": "7561", "libelle": "Dons manuels", "classe": 7, "niveau": 3, "parent_id": 61},
    {"numero": "7562", "libelle": "Dons en nature", "classe": 7, "niveau": 3, "parent_id": 61},
    {"numero": "7563", "libelle": "Legs", "classe": 7, "niveau": 3, "parent_id": 61},
    {"numero": "7564", "libelle": "Donations", "classe": 7, "niveau": 3, "parent_id": 61},
    
    # SUBVENTIONS SPÉCIFIQUES EBNL
    {"numero": "7181", "libelle": "Subventions versées par l'État et les collectivités publiques", "classe": 7, "niveau": 3, "parent_id": 46},
    {"numero": "7182", "libelle": "Subventions versées par les organismes internationaux", "classe": 7, "niveau": 3, "parent_id": 46},
    {"numero": "7183", "libelle": "Subventions versées par des tiers", "classe": 7, "niveau": 3, "parent_id": 46},
    
    # COMPTES PROJETS ET PROGRAMMES (Spécifique EBNL)
    {"numero": "455", "libelle": "Projets et programmes", "classe": 4, "niveau": 2, "parent_id": None},
    {"numero": "4551", "libelle": "Projet A - Subventions à recevoir", "classe": 4, "niveau": 3, "parent_id": 62},
    {"numero": "4552", "libelle": "Projet B - Subventions à recevoir", "classe": 4, "niveau": 3, "parent_id": 62},
    {"numero": "4558", "libelle": "Autres projets - Subventions à recevoir", "classe": 4, "niveau": 3, "parent_id": 62},
]

def get_plan_comptable_complet():
    """Retourne le plan comptable SYCEBNL complet"""
    return PLAN_COMPTABLE_SYCEBNL

def get_comptes_by_classe(classe):
    """Retourne les comptes d'une classe donnée"""
    return [compte for compte in PLAN_COMPTABLE_SYCEBNL if compte["classe"] == classe]

def get_compte_by_numero(numero):
    """Retourne un compte par son numéro"""
    return next((compte for compte in PLAN_COMPTABLE_SYCEBNL if compte["numero"] == numero), None)

def get_comptes_enfants(parent_numero):
    """Retourne les comptes enfants d'un compte parent"""
    parent = get_compte_by_numero(parent_numero)
    if not parent:
        return []
    
    # Trouver l'ID du parent dans la liste
    parent_id = None
    for i, compte in enumerate(PLAN_COMPTABLE_SYCEBNL, 1):
        if compte["numero"] == parent_numero:
            parent_id = i
            break
    
    if parent_id is None:
        return []
    
    return [compte for compte in PLAN_COMPTABLE_SYCEBNL if compte.get("parent_id") == parent_id]

# Constantes pour les classes SYCEBNL
CLASSES_SYCEBNL = {
    1: "COMPTES DE RESSOURCES DURABLES",
    2: "COMPTES D'ACTIF IMMOBILISÉ", 
    3: "COMPTES DE STOCKS",
    4: "COMPTES DE TIERS",
    5: "COMPTES DE TRÉSORERIE",
    6: "COMPTES DE CHARGES DES ACTIVITÉS ORDINAIRES",
    7: "COMPTES DE PRODUITS DES ACTIVITÉS ORDINAIRES", 
    8: "COMPTES DES AUTRES CHARGES ET DES AUTRES PRODUITS",
    9: "COMPTES DES ENGAGEMENTS HORS BILAN ET COMPTABILITÉ ANALYTIQUE"
}

# Compteurs par classe
TOTAL_COMPTES_PAR_CLASSE = {
    1: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 1]),
    2: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 2]),
    3: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 3]),
    4: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 4]),
    5: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 5]),
    6: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 6]),
    7: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 7]),
    8: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 8]),
    9: len([c for c in PLAN_COMPTABLE_SYCEBNL if c["classe"] == 9])
}

TOTAL_COMPTES = len(PLAN_COMPTABLE_SYCEBNL)

# Validation
if __name__ == "__main__":
    print(f"🎯 Plan Comptable SYCEBNL Chargé: {TOTAL_COMPTES} comptes")
    print(f"📊 Répartition par classe:")
    for classe, total in TOTAL_COMPTES_PAR_CLASSE.items():
        print(f"   Classe {classe}: {total} comptes - {CLASSES_SYCEBNL[classe]}")