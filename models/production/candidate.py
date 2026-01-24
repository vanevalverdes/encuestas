# -*- coding: utf-8 -*-
from utils.db import db
from sqlalchemy.orm import backref
from sqlalchemy import BigInteger
from datetime import datetime, timezone 
from sqlalchemy import desc, func, String, case, literal_column  
from sqlalchemy.ext.hybrid import hybrid_property 
from sqlalchemy.sql.expression import null 

class Candidate(db.Model):
    __tablename__ = 'candidate'
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('blob.id'), nullable=True)
    image = db.relationship('Blob', foreign_keys=[image_id], lazy='joined')
    name = db.Column(db.String(255))
    party_id = db.Column(db.Integer, db.ForeignKey('party.id', ondelete='CASCADE'), nullable=True)
    party = db.relationship('Party', backref=backref('candidates', order_by='Candidate.order',cascade='all, delete-orphan', passive_deletes=True))
    order = db.Column(db.String(255))
    state = db.Column(db.String(255))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_candidates', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_candidates', foreign_keys=[modifiedby_id])
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


    @hybrid_property
    def full_repr(self):
        result = f'''{self.name if self.name is not None else ''}'''
        return result.strip()

    @full_repr.expression
    def full_repr(cls):
        return (
            literal_column("") + literal_column("''")  + func.coalesce(cls.name, literal_column("''"))  + literal_column("''")
        )

    def __repr__(self) -> str:
        return self.full_repr 
    __default_ordering__ = [order]

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }


def get_fields():
    fields = {'image': {'id': 114, 'type': 'blob', 'name': 'image', 'maxlength': None, 'connected_table': None, 'label': 'Imagen', 'input': 'image', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'name': {'id': 115, 'type': 'String', 'name': 'name', 'maxlength': None, 'connected_table': None, 'label': 'Nombre', 'input': 'text', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'party': {'id': 116, 'type': 'connected_table', 'name': 'party', 'maxlength': None, 'connected_table': 7, 'label': 'Partido', 'input': 'connected_table', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'order': {'id': 117, 'type': 'String', 'name': 'order', 'maxlength': None, 'connected_table': None, 'label': 'Ordenar', 'input': 'float', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'state': {'id': 124, 'type': 'String', 'name': 'state', 'maxlength': None, 'connected_table': None, 'label': 'Provincia', 'input': 'select', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': '{\r\n"San José":"San José",\r\n"Alajuela":"Alajuela",\r\n"Heredia":"Heredia",\r\n"Cartago":"Cartago",\r\n"Puntarenas":"Puntarenas",\r\n"Limón":"Limón",\r\n"Guanacaste":"Guanacaste"\r\n}', 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}}
    return fields


def get_relevants():
    relevants = {}
    return relevants
