# -*- coding: utf-8 -*-
from utils.db import db
from datetime import datetime, timezone 
class Surveymarch(db.Model):
    __tablename__ = 'surveymarch'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    party = db.Column(db.String(255))
    chavesParty = db.Column(db.String(255))
    plnElections = db.Column(db.String(255))
    plnCandidate = db.Column(db.String(255))
    generalElections = db.Column(db.String(255))
    chavesSupport = db.Column(db.String(255))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_surveysmarch', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_surveysmarch', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f" ID {self.id if self.id is not None else ''} - Usuario: {self.createdby_id if self.createdby_id is not None else ''} - Fecha {self. created_at if self. created_at is not None else ''}"
