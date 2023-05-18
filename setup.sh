echo "setup template"
sudo service postgresql restart
echo "drop template db: enter db password"
dropdb fitbit_2 -U dbadmin -h localhost -i
echo "create database: enter db password"
createdb -h localhost -U dbadmin -O dbadmin fitbit_2
echo "create virtual environment"
rm -rf _fitbit_2_env
virtualenv --python=python3.9 _fitbit_2_env
source _fitbit_2_env/bin/activate
echo "install requirements"
pip install -r requirements.txt
python manage.py migrate
echo "create super user"
python manage.py createsuperuser 
echo "load fixtures"
python manage.py loaddata main.json
echo "setup done"
python manage.py runserver