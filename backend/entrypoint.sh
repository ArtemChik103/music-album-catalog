#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Checking if database needs demo seeding..."
python manage.py shell -c "
from catalog.models import Album
if Album.objects.count() == 0:
    from django.core.management import call_command
    call_command('seed_data')
"

echo "Starting server..."
exec "$@"
