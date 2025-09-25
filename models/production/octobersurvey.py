# -*- coding: utf-8 -*-
from utils.db import db
from datetime import datetime, timezone 
class Octobersurvey(db.Model):
    __tablename__ = 'octobersurvey'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    religion = db.Column(db.String(255))
    county = db.Column(db.String(255))
    state = db.Column(db.String(255))
    education = db.Column(db.String(255))
    party = db.Column(db.String(255))
    chavesSupport = db.Column(db.String(255))
    chavesScale = db.Column(db.String(255))
    nationalElection = db.Column(db.String(255))
    nationalElectionSecond = db.Column(db.String(255))
    congressParty = db.Column(db.String(255))
    conoceJuanCarlos = db.Column(db.String(255))
    opinionJuanCarlos = db.Column(db.String(255))
    conoceWalter = db.Column(db.String(255))
    opinionWalter = db.Column(db.String(255))
    conoceLauraFernandez = db.Column(db.String(255))
    opinionLauraFernandez = db.Column(db.String(255))
    conoceNataliaDiaz = db.Column(db.String(255))
    opinionNataliaDiaz = db.Column(db.String(255))
    conoceArielRobles = db.Column(db.String(255))
    opinionArielRobles = db.Column(db.String(255))
    contact = db.Column(db.String(255))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_octobersurveys', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_octobersurveys', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f" {self.id if self.id is not None else ''}- {self.created_at if self.created_at is not None else ''}"

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
