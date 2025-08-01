# -*- coding: utf-8 -*-
from utils.db import db
from datetime import datetime, timezone 
class Augustsurvey(db.Model):
    __tablename__ = 'augustsurvey'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    county = db.Column(db.String(255))
    party = db.Column(db.String(255))
    chavesSupport = db.Column(db.String(255))
    nationalElection = db.Column(db.String(255))
    contact = db.Column(db.String(255))
    state = db.Column(db.String(255))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_augustsurveys', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_augustsurveys', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f" {self.id if self.id is not None else ''}- {self.created_at if self.created_at is not None else ''}"

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
