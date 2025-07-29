from main import create_app
from models import db, PlanComptable
import pandas as pd


def import_plan_comptable():
    app = create_app()

    with app.app_context():
        # Données du plan comptable SYCEBNL (échantillon pour test)
        comptes_test = [
            {'numero_compte': '1', 'libelle_compte': 'COMPTES DE RESSOURCES DURABLES', 'classe': 1, 'niveau': 0,
             'parent_id': None},
            {'numero_compte': '10', 'libelle_compte': 'DOTATIONS', 'classe': 1, 'niveau': 1, 'parent_id': 1},
            {'numero_compte': '101', 'libelle_compte': 'Dotations initiales', 'classe': 1, 'niveau': 2, 'parent_id': 2},
            {'numero_compte': '1011', 'libelle_compte': 'Dotations en numéraire', 'classe': 1, 'niveau': 3,
             'parent_id': 3},
            {'numero_compte': '2', 'libelle_compte': 'COMPTES D\'ACTIF IMMOBILISE', 'classe': 2, 'niveau': 0,
             'parent_id': None},
            {'numero_compte': '20', 'libelle_compte': 'IMMOBILISATIONS INCORPORELLES', 'classe': 2, 'niveau': 1,
             'parent_id': 5},
        ]

        # Suppression des données existantes
        PlanComptable.query.delete()

        # Insertion des comptes
        for compte_data in comptes_test:
            compte = PlanComptable(**compte_data)
            db.session.add(compte)

        db.session.commit()
        print(f"✅ {len(comptes_test)} comptes importés avec succès!")


if __name__ == '__main__':
    import_plan_comptable()
