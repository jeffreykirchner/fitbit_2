echo "*** Startup.sh ***"
echo "deb http://archive.debian.org/debian stretch main contrib non-free" > /etc/apt/sources.list
apt-get update
echo "Run Migrations:"
python manage.py migrate
echo "Install htop:"
apt-get -y install htop
echo "Install redis"
apt-get -y install redis
echo "Start Server:"
redis-server & daphne -b 0.0.0.0 _fitbit_2.asgi:application