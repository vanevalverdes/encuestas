# -*- coding: utf-8 -*-
from utils.db import db
from sqlalchemy.orm import backref
from sqlalchemy import BigInteger
from datetime import datetime, timezone 
from sqlalchemy import desc, func, String, case, literal_column  
from sqlalchemy.ext.hybrid import hybrid_property 
from sqlalchemy.sql.expression import null 

class Electoralday(db.Model):
    __tablename__ = 'electoralday'
    id = db.Column(db.Integer, primary_key=True)
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_electoraldays', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_electoraldays', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


    @hybrid_property
    def full_repr(self):
        result = f'''{self.id if self.id is not None else ''}'''
        return result.strip()

    @full_repr.expression
    def full_repr(cls):
        return (
            literal_column("") + literal_column("''")  + func.coalesce(cls.id, literal_column("''"))  + literal_column("''")
        )

    def __repr__(self) -> str:
        return self.full_repr 
    __default_ordering__ = [desc('id')]

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }


def get_fields():
    fields = {}
    return fields


def get_relevants():
    relevants = {}
    return relevants
