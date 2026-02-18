web: gunicorn aimesite.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 60 --access-logfile - --error-logfile -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
