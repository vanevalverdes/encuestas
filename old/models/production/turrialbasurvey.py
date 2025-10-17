# -*- coding: utf-8 -*-
from utils.db import db
from datetime import datetime, timezone 
class Turrialbasurvey(db.Model):
    __tablename__ = 'turrialbasurvey'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    conoceCarlos = db.Column(db.String(255))
    opinionCarlos = db.Column(db.String(255))
    conoceRodrigoChaves = db.Column(db.String(255))
    opinionRodrigoChaves = db.Column(db.String(255))
    apoyaAlcalde = db.Column(db.String(255))
    muniScale = db.Column(db.String(255))
    apoyaRodrigoChaves = db.Column(db.String(255))
    chavesParty = db.Column(db.String(255))
    contact = db.Column(db.String(255))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_TurrialbaSurveys', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_TurrialbaSurveys', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f" {self.id if self.id is not None else ''} - Encuestador {self.createdby_id if self.createdby_id is not None else ''} - {self.created_at if self.created_at is not None else ''}"

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
