# -*- coding: utf-8 -*-
from utils.db import db
from datetime import datetime, timezone 
class Survey(db.Model):
    __tablename__ = 'survey'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    state = db.Column(db.String(255))
    party = db.Column(db.String(255))
    partyAndChaves = db.Column(db.String(255))
    conoceRodrigoChaves = db.Column(db.String(255))
    opinionRodrigoChaves = db.Column(db.String(255))
    conoceMauricioBatalla = db.Column(db.String(255))
    opinionMauricioBatalla = db.Column(db.String(255))
    conoceLauraFernandez = db.Column(db.String(255))
    opinionLauraFernandez = db.Column(db.String(255))
    conoceAlvaroRamos = db.Column(db.String(255))
    opinionAlvaroRamos = db.Column(db.String(255))
    conoceGilbertJimenez = db.Column(db.String(255))
    opinionGilbertJimenez = db.Column(db.String(255))
    conoceCarolinaDelgado = db.Column(db.String(255))
    opinionCarolinaDelgado = db.Column(db.String(255))
    conoceMarvinTaylor = db.Column(db.String(255))
    opinionMarvinTaylor = db.Column(db.String(255))
    conoceRolandoArayaMonge = db.Column(db.String(255))
    opinionRolandoArayaMonge = db.Column(db.String(255))
    chavesParty = db.Column(db.String(255))
    chavesCandidate = db.Column(db.String(255))
    plnElections = db.Column(db.String(255))
    plnCandidate = db.Column(db.String(255))
    generalElections = db.Column(db.String(255))
    chavesSupport = db.Column(db.String(255))
    chavesScale = db.Column(db.String(255))
    contact = db.Column(db.String(255))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_surveys', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_surveys', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f" {self.id if self.id is not None else ''} - Usuario: {self.createdby if self.createdby is not None else ''}"

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
