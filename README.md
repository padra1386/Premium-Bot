cd Premium Bot

pip install -r requirements.txt

sudo apt update

sudo apt install postgresql postgresql-contrib

sudo systemctl start postgresql.service

sudo -u postgres createuser --interactive

sudo -u postgres createdb premiumbot

sudo adduser padra

sudo -u padra psql