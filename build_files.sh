pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
chmod +x build_files.sh
