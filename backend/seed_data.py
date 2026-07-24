"""PowerShell uchun tavsiya: py manage.py seed_languages"""
from django.core.management import call_command

call_command('seed_languages')
