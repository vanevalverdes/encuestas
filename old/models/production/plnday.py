# -*- coding: utf-8 -*-
from utils.db import db
from datetime import datetime, timezone 
class Plnday(db.Model):
    __tablename__ = 'plnday'
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(255))
    alvaroramos = db.Column(db.Integer())
    gilberthjimenez = db.Column(db.Integer())
    carolinadelgado = db.Column(db.Integer())
    marvintaylor = db.Column(db.Integer())
    blank = db.Column(db.Integer())
    nulled = db.Column(db.Integer())
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_plndays', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_plndays', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f" {self.id if self.id is not None else ''} - {self.state if self.state is not None else ''} - Usuario: {self.createdby_id if self.createdby_id is not None else ''} - {self.created_at if self.created_at is not None else ''} "

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
