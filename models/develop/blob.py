# -*- coding: utf-8 -*-
from utils.db import db
from sqlalchemy.orm import backref
from datetime import datetime, timezone 

class Blob(db.Model):
    __tablename__ = "blob"
    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    def __repr__(self) -> str:
        return f" {self.original_name if self.original_name is not None else ''}"
