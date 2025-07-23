from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL


class ShortLinkForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(require_tld=True, message='Введите корректный URL')
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=16, message='Не более 16 символов'),
            Regexp(r'^[a-zA-Z0-9]+$', message='Только буквы и цифры')
        ]
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    files = MultipleFileField('Выберите файлы', validators=[DataRequired()])
    submit = SubmitField('Загрузить')