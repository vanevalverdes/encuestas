# -*- coding: utf-8 -*-
from utils.db import db
from sqlalchemy.orm import backref
from sqlalchemy import BigInteger
from datetime import datetime, timezone 
from sqlalchemy import desc, func, String, case, literal_column  
from sqlalchemy.ext.hybrid import hybrid_property 
from sqlalchemy.sql.expression import null 

class Party(db.Model):
    __tablename__ = 'party'
    id = db.Column(db.Integer, primary_key=True)
    flag_id = db.Column(db.Integer, db.ForeignKey('blob.id'), nullable=True)
    flag = db.relationship('Blob', foreign_keys=[flag_id], lazy='joined')
    type = db.Column(db.String(255))
    state = db.Column(db.String(255))
    president = db.Column(db.String(255))
    presidentImage_id = db.Column(db.Integer, db.ForeignKey('blob.id'), nullable=True)
    presidentImage = db.relationship('Blob', foreign_keys=[presidentImage_id], lazy='joined')
    name = db.Column(db.String(255))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_parties', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_parties', foreign_keys=[modifiedby_id])
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
    __default_ordering__ = [name]

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }


def get_fields():
    fields = {'flag': {'id': 118, 'type': 'blob', 'name': 'flag', 'maxlength': None, 'connected_table': None, 'label': 'Bandera', 'input': 'image', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'type': {'id': 119, 'type': 'String', 'name': 'type', 'maxlength': None, 'connected_table': None, 'label': 'Tipo', 'input': 'select', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': '{\r\n"Nacional":"Nacional",\r\n"Provincial":"Provincial"\r\n}', 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'state': {'id': 120, 'type': 'String', 'name': 'state', 'maxlength': None, 'connected_table': None, 'label': 'Provincia', 'input': 'select', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': '{\r\n"San José":"San José",\r\n"Alajuela":"Alajuela",\r\n"Heredia":"Heredia",\r\n"Cartago":"Cartago",\r\n"Puntarenas":"Puntarenas",\r\n"Limón":"Limón",\r\n"Guanacaste":"Guanacaste"\r\n}', 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'president': {'id': 121, 'type': 'String', 'name': 'president', 'maxlength': None, 'connected_table': None, 'label': 'Candidato Presidencial', 'input': 'text', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'presidentImage': {'id': 122, 'type': 'blob', 'name': 'presidentImage', 'maxlength': None, 'connected_table': None, 'label': 'Foto Presidente', 'input': 'image', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'name': {'id': 123, 'type': 'String', 'name': 'name', 'maxlength': None, 'connected_table': None, 'label': 'Nombre', 'input': 'text', 'sort': None, 'required': False, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}}
    return fields


def get_relevants():
    relevants = {}
    return relevants
