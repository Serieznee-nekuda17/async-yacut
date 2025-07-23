from datetime import datetime

from flask import url_for

from yacut_app import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(2048), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(256))

    def to_dict(self):
        return {
            'short_link': url_for(
                'short_redirect', short=self.short, _external=True),
            'url': self.original,
            'filename': self.filename
        }

    def from_dict(self, data: dict):
        for field in ['original', 'short', 'filename']:
            if field in data:
                setattr(self, field, data[field])
