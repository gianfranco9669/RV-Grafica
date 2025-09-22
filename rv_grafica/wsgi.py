"""WSGI config for rv_grafica project."""
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rv_grafica.settings")

application = get_wsgi_application()
