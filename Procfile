web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn lmevents.wsgi --workers 3 --bind 0.0.0.0:$PORT --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput
