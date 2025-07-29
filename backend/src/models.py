from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class PlanComptable(db.Model):
    __tablename__ = 'plan_comptable'

    id = db.Column(db.Integer, primary_key=True)
    numero_compte = db.Column(db.String(10), unique=True, nullable=False, index=True)
    libelle_compte = db.Column(db.String(255), nullable=False)
    classe = db.Column(db.Integer, nullable=False, index=True)
    niveau = db.Column(db.Integer, nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('plan_comptable.id'), nullable=True)
    observations = db.Column(db.Text, nullable=True)
    actif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    enfants = db.relationship('PlanComptable', backref=db.backref('parent', remote_side=[id]))

    def to_dict(self):
        return {
            'id': self.id,
            'numero_compte': self.numero_compte,
            'libelle_compte': self.libelle_compte,
            'classe': self.classe,
            'niveau': self.niveau,
            'parent_id': self.parent_id,
            'observations': self.observations,
            'actif': self.actif
        }
