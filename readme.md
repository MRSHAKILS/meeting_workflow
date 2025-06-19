

source meeting_venv/bin/activate

python manage.py migrate   
python manage.py start_scheduler
python manage.py runserver
