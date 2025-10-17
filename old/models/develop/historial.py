# -*- coding: utf-8 -*-
from utils.db import db
from datetime import datetime, timezone 
class Historial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataRequest = db.Column(db.Text)
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_historials', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_historials', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
