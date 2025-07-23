from http import HTTPStatus

from flask import request, jsonify

from . import app
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

    url_map = URLMap.create(original=url, custom_id=custom_id)
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    """
    Обрабатывает GET-запрос для получения
    оригинальной ссылки по короткому идентификатору.
    """
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), HTTPStatus.OK