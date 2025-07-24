import re
from http import HTTPStatus

from flask import request, jsonify

from . import app
from .constants import (
    FORBIDDEN_NAMES,
    MIN_CUSTOM_ID_LENGTH,
    MAX_CUSTOM_ID_LENGTH,
    CUSTOM_ID_REGEX
)
from .error_handlers import InvalidAPIUsage
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_id():
    """Обрабатывает POST-запрос на создание новой короткой ссылки."""
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')

    url = data.get('url')
    custom_id = data.get('custom_id')

    if not url:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    if custom_id:
        if custom_id.lower() in FORBIDDEN_NAMES:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )

        if not (
            MIN_CUSTOM_ID_LENGTH <= len(custom_id) <= MAX_CUSTOM_ID_LENGTH
        ) or not re.fullmatch(CUSTOM_ID_REGEX, custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if URLMap.get_by_short_id(custom_id):
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )

    url_map = URLMap.create(original=url, custom_id=custom_id)
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    """
    Обрабатывает GET-запрос для получения
    оригинальной ссылки по короткому идентификатору.
    """
    url_map = URLMap.get_by_short_id(short_id)
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), HTTPStatus.OK