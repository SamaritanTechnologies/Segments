# Segments
#Install requirements
pip install -r requirements.txt

#migrations
python manage.py makemigrations
python manage.py migrate

Running celery in Background

celery -A Segments worker -l info
Running celery beat in Background

celery -A Segments beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler