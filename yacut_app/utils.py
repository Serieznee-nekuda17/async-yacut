import random
import string

from .models import URLMap
from . import db


def get_unique_short_id(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choices(chars, k=length))
        if not db.session.query(URLMap).filter_by(short=short_id).first():
            return short_id