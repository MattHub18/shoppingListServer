python3 -m pip install -r requirements.txt
python3 manage.py makemigrations api
python3 manage.py migrate api
python3 manage.py collectstatic --noinput
