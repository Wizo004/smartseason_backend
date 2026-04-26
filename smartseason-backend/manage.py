#!/usr/bin/env python
"""Django command-line utility (entry point for runserver, migrate, etc.)."""
import os, sys

def main():
    # Default to dev settings; override with DJANGO_SETTINGS_MODULE in prod.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartseason.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django. Activate your venv?") from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
