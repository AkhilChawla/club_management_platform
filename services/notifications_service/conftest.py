"""Pytest configuration for the notifications service."""

import os

import django

# Ensure Django settings are configured before importing app code.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notifications_service.settings")
django.setup()
