# -*- coding: utf-8 -*-
from utils.db import db
from sqlalchemy.orm import backref
from sqlalchemy import BigInteger
from datetime import datetime, timezone 
from sqlalchemy import desc, func, String, case, literal_column  
from sqlalchemy.ext.hybrid import hybrid_property 
from sqlalchemy.sql.expression import null 

class Diputadoelecto(db.Model):
    __tablename__ = 'diputadoelecto'
    id = db.Column(db.Integer, primary_key=True)
    diputado_PPSO = db.Column(db.Integer())
    diputado_NR = db.Column(db.Integer())
    diputado_PNG = db.Column(db.Integer())
    diputado_PLN = db.Column(db.Integer())
    diputado_UP = db.Column(db.Integer())
    diputado_PLP = db.Column(db.Integer())
    diputado_FA = db.Column(db.Integer())
    diputado_CAC = db.Column(db.Integer())
    diputado_PEN = db.Column(db.Integer())
    diputado_PSD = db.Column(db.Integer())
    diputado_Avanza = db.Column(db.Integer())
    diputado_PUSC = db.Column(db.Integer())
    diputado_PIN = db.Column(db.Integer())
    diputado_ACRM = db.Column(db.Integer())
    diputado_CDS = db.Column(db.Integer())
    diputado_CR1 = db.Column(db.Integer())
    diputado_PJSC = db.Column(db.Integer())
    diputado_UCD = db.Column(db.Integer())
    diputado_PEL = db.Column(db.Integer())
    diputado_PT = db.Column(db.Integer())
    diputado_PACO = db.Column(db.Integer())
    diputado_CU = db.Column(db.Integer())
    diputado_Compatriotas = db.Column(db.Integer())
    diputado_ActuemosYa = db.Column(db.Integer())
    diputado_Otro = db.Column(db.Integer())
    state = db.Column(db.String(255))
    createdby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    modifiedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.relationship('User', backref='created_diputadoselectos', foreign_keys=[createdby_id])
    modifiedby = db.relationship('User', backref='modified_diputadoselectos', foreign_keys=[modifiedby_id])
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
    fields = {'diputado_PPSO': {'id': 226, 'type': 'Integer', 'name': 'diputado_PPSO', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PPSO', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_NR': {'id': 227, 'type': 'Integer', 'name': 'diputado_NR', 'maxlength': None, 'connected_table': None, 'label': 'Diputado NR', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PNG': {'id': 228, 'type': 'Integer', 'name': 'diputado_PNG', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PNG', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PLN': {'id': 229, 'type': 'Integer', 'name': 'diputado_PLN', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PLN', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_UP': {'id': 230, 'type': 'Integer', 'name': 'diputado_UP', 'maxlength': None, 'connected_table': None, 'label': 'Diputado UP', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PLP': {'id': 231, 'type': 'Integer', 'name': 'diputado_PLP', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PLP', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_FA': {'id': 232, 'type': 'Integer', 'name': 'diputado_FA', 'maxlength': None, 'connected_table': None, 'label': 'Diputado FA', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_CAC': {'id': 233, 'type': 'Integer', 'name': 'diputado_CAC', 'maxlength': None, 'connected_table': None, 'label': 'Diputado CAC', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PEN': {'id': 234, 'type': 'Integer', 'name': 'diputado_PEN', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PEN', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PSD': {'id': 235, 'type': 'Integer', 'name': 'diputado_PSD', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PSD', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_Avanza': {'id': 236, 'type': 'Integer', 'name': 'diputado_Avanza', 'maxlength': None, 'connected_table': None, 'label': 'Diputado Avanza', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PUSC': {'id': 237, 'type': 'Integer', 'name': 'diputado_PUSC', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PUSC', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PIN': {'id': 238, 'type': 'Integer', 'name': 'diputado_PIN', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PIN', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_ACRM': {'id': 239, 'type': 'Integer', 'name': 'diputado_ACRM', 'maxlength': None, 'connected_table': None, 'label': 'Diputado ACRM', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_CDS': {'id': 240, 'type': 'Integer', 'name': 'diputado_CDS', 'maxlength': None, 'connected_table': None, 'label': 'Diputado CDS', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_CR1': {'id': 241, 'type': 'Integer', 'name': 'diputado_CR1', 'maxlength': None, 'connected_table': None, 'label': 'Diputado CR1', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PJSC': {'id': 242, 'type': 'Integer', 'name': 'diputado_PJSC', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PJSC', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_UCD': {'id': 243, 'type': 'Integer', 'name': 'diputado_UCD', 'maxlength': None, 'connected_table': None, 'label': 'Diputado UCD', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PEL': {'id': 244, 'type': 'Integer', 'name': 'diputado_PEL', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PEL', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PT': {'id': 245, 'type': 'Integer', 'name': 'diputado_PT', 'maxlength': None, 'connected_table': None, 'label': 'Diputado PT', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_PACO': {'id': 246, 'type': 'Integer', 'name': 'diputado_PACO', 'maxlength': None, 'connected_table': None, 'label': 'Diputado Partido Anticorrupción Costarricense', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_CU': {'id': 247, 'type': 'Integer', 'name': 'diputado_CU', 'maxlength': None, 'connected_table': None, 'label': 'Diputado Partido Comunal Unido', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_Compatriotas': {'id': 248, 'type': 'Integer', 'name': 'diputado_Compatriotas', 'maxlength': None, 'connected_table': None, 'label': 'Diputado Partido Compatriotas', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_ActuemosYa': {'id': 249, 'type': 'Integer', 'name': 'diputado_ActuemosYa', 'maxlength': None, 'connected_table': None, 'label': 'Diputado Partido Actuemos Ya', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'diputado_Otro': {'id': 250, 'type': 'Integer', 'name': 'diputado_Otro', 'maxlength': None, 'connected_table': None, 'label': 'Diputado Otro', 'input': 'number', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': '0', 'select_options': None, 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}, 'state': {'id': 251, 'type': 'String', 'name': 'state', 'maxlength': None, 'connected_table': None, 'label': None, 'input': 'select', 'sort': None, 'required': True, 'hidden': False, 'publicBlob': False, 'default_value': None, 'select_options': '{\r\n"San José":"san-jose",\r\n"Alajuela":"alajuela",\r\n"Heredia":"heredia",\r\n"Cartago":"cartago",\r\n"Guanacaste":"guanacaste",\r\n"Puntarenas":"puntarenas",\r\n"Limón":"limon"\r\n}', 'extraclass': None, 'hasManyValues': False, 'readOnly': False, 'calculate_file': None, 'calculate_function': None, 'helper': None}}
    return fields


def get_relevants():
    relevants = {}
    return relevants
