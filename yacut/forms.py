from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL

from .constants import MAX_CUSTOM_ID_LENGTH, CUSTOM_ID_REGEX


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
            Length(max=MAX_CUSTOM_ID_LENGTH, message='Не более 16 символов'),
            Regexp(CUSTOM_ID_REGEX, message='Только буквы и цифры')
        ]
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    files = MultipleFileField('Выберите файлы', validators=[DataRequired()])
    submit = SubmitField('Загрузить')