import re
from flask import request, jsonify
from .models import URLMap
from .error_handlers import InvalidAPIUsage
from .utils import get_unique_short_id
from . import app, db


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)
    url = data.get('url')
    custom_id = data.get('custom_id')

    if not url:
        raise InvalidAPIUsage('"url" является обязательным полем!', 400)

    if custom_id:
        if len(custom_id) > 16 or not re.fullmatch(r'[a-zA-Z0-9]+', custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки', 400)

        exists = URLMap.query.filter_by(short=custom_id).first()
        if exists:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.', 400)
        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    url_map = URLMap(original=url, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    return jsonify({
        'url': url,
        'short_link': request.host_url + short_id
    }), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200