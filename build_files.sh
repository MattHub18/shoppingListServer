python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput
gunicorn django_project.wsgi --log-file