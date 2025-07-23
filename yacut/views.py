import asyncio
from settings import Config
from flask import flash, render_template, url_for, redirect

from .forms import FileUploadForm, ShortLinkForm
from .models import URLMap
from .utils import get_unique_short_id
from .ya_disk import upload_file_to_yadisk
from . import db, app


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = ShortLinkForm()
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        original_link = form.original_link.data

        if custom_id and custom_id.lower() == 'files':
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('index.html', form=form)

        if custom_id:
            if URLMap.query.filter_by(short=custom_id).first():
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('index.html', form=form)
            short_id = custom_id
        else:
            short_id = get_unique_short_id()

        url_map = URLMap(original=original_link, short=short_id)
        db.session.add(url_map)
        db.session.commit()

        return render_template(
            'index.html', form=form,
            short_link=url_for(
                'short_redirect', short=short_id, _external=True
            )
        )
    return render_template('index.html', form=form)


@app.route('/<short>')
def short_redirect(short):
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)


@app.route('/files', methods=['GET', 'POST'])
def files():
    form = FileUploadForm()
    files_info = []
    if form.validate_on_submit():
        for file_storage in form.files.data:
            short_id = get_unique_short_id()
            filename = file_storage.filename
            public_url = asyncio.run(
                upload_file_to_yadisk(
                    file_storage, Config.DISK_TOKEN, filename)
            )
            url_map = URLMap(
                original=public_url, short=short_id, filename=filename
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
    files_list = URLMap.query.filter(
        URLMap.filename.isnot(None)).all()
    return render_template('files.html', form=form, files=files_list)