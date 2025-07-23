import random
import re
import string
from datetime import datetime

from flask import url_for

from . import db
from .constants import (
    MAX_CUSTOM_ID_LENGTH,
    MIN_CUSTOM_ID_LENGTH,
    CUSTOM_ID_REGEX,
    FORBIDDEN_NAMES,
)
from .error_handlers import InvalidAPIUsage


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
        }

    def from_dict(self, data: dict):
        for field in ['original', 'short', 'filename']:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def get_unique_short_id(length=6):
        chars = string.ascii_letters + string.digits
        while True:
            short_id = ''.join(random.choices(chars, k=length))
            if (short_id not in FORBIDDEN_NAMES and
                    not URLMap.query.filter_by(short=short_id).first()):
                return short_id

    @staticmethod
    def create(original, custom_id=None, filename=None):
        if not original:
            raise InvalidAPIUsage('"url" является обязательным полем!')

        if custom_id:

            if custom_id.lower() in FORBIDDEN_NAMES:
                raise InvalidAPIUsage(
                    'Предложенный вариант короткой ссылки уже существует.')

            if not (
                MIN_CUSTOM_ID_LENGTH <= len(custom_id) <= MAX_CUSTOM_ID_LENGTH
            ) or not re.fullmatch(CUSTOM_ID_REGEX, custom_id):
                raise InvalidAPIUsage(
                    'Указано недопустимое имя для короткой ссылки')

            if URLMap.query.filter_by(short=custom_id).first():
                raise InvalidAPIUsage(
                    'Предложенный вариант короткой ссылки уже существует.')

            short_id = custom_id
        else:
            short_id = URLMap.get_unique_short_id()

        url_map = URLMap(original=original, short=short_id, filename=filename)
        db.session.add(url_map)
        db.session.commit()
        return url_map