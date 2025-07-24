import random
import string
from datetime import datetime

from flask import url_for

from . import db
from .constants import (
    FORBIDDEN_NAMES,
    MAX_ORIGINAL_LENGTH,
    MAX_SHORT_LENGTH,
)
from .error_handlers import InvalidAPIUsage


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(db.String(MAX_SHORT_LENGTH), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'short_link': url_for(
                'short_redirect', short=self.short, _external=True),
            'url': self.original,
        }

    def from_dict(self, data: dict):
        for field in ['original', 'short']:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def get_by_short_id(short_id):
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def get_unique_short_id(length=6):
        chars = string.ascii_letters + string.digits
        while True:
            short_id = ''.join(random.choices(chars, k=length))
            if (short_id not in FORBIDDEN_NAMES
                    and not URLMap.get_by_short_id(short_id)):
                return short_id

    @staticmethod
    def create(original, custom_id=None):
        short_id = custom_id or URLMap.get_unique_short_id()

        if custom_id:
            if (custom_id.lower() in FORBIDDEN_NAMES
                    or URLMap.get_by_short_id(short_id)):
                raise InvalidAPIUsage(
                    'Предложенный вариант короткой ссылки уже существует.'
                )

        url_map = URLMap(original=original, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        return url_map