import asyncio
from flask import abort
from flask import flash, redirect, render_template

from settings import Config
from . import app, db
from .error_handlers import InvalidAPIUsage
from .forms import FileUploadForm, ShortLinkForm
from .models import URLMap
from .ya_disk import upload_file_to_yadisk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница с формой для создания короткой ссылки."""
    form = ShortLinkForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    custom_id = form.custom_id.data
    original_link = form.original_link.data

    try:
        url_map = URLMap.create(original=original_link, custom_id=custom_id)
    except InvalidAPIUsage:
        flash('Предложенный вариант короткой ссылки уже существует.')
        return render_template('index.html', form=form)

    return render_template(
        'index.html',
        form=form,
        short_link=url_map.to_dict()['short_link']
    )


@app.route('/<short>')
def short_redirect(short):
    """Перенаправляет с короткой ссылки на оригинальный URL."""
    url_map = URLMap.get_by_short_id(short)
    if url_map is None:
        abort(404)
    return redirect(url_map.original)


@app.route('/files', methods=['GET', 'POST'])
def files():
    """Страница для загрузки файлов и получения коротких ссылок на них."""
    form = FileUploadForm()
    files_info = []
    if form.validate_on_submit():
        for file_storage in form.files.data:
            short_id = URLMap.get_unique_short_id()
            filename = file_storage.filename
            public_url = asyncio.run(
                upload_file_to_yadisk(
                    file_storage, Config.DISK_TOKEN, filename)
            )
            url_map = URLMap(
                original=public_url, short=short_id
            )
            db.session.add(url_map)
            files_info.append(
                {
                    'filename': filename,
                    'short': short_id,
                    'public_url': public_url
                }
            )
        db.session.commit()
        flash('Файлы успешно загружены!')
    return render_template('files.html', form=form, files=files_info)