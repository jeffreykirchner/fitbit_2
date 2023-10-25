echo "*** Startup.sh ***"
echo "Run Migrations:"
python manage.py migrate
echo "Install htop:"
apt-get -y install htop
echo "Install redis"
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
apt-get update
apt-get -y install redis
echo "Start Daphne:"
redis-server & daphne -b 0.0.0.0 _fitbit_2.asgi:application