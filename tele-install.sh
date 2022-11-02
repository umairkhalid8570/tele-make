USER="tele"
PASSWD="tele"
# DB_NAME="tele_db"

# Create a DB user
psql -c "create user tele with encrypted password 'telepwd';"
psql -c "ALTER ROLE tele WITH SUPERUSER;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE template0 TO tele;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE template1 TO tele;"

# Create a database
# psql -c "CREATE DATABASE $DB_NAME WITH OWNER $USER;"
# psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $USER;"


# Upgrade pip
python -m pip install --upgrade pip


# Upgrade pip
python -m pip install --upgrade pip

pip3 install wheel
pip3 install -U -r tele/requirements.txt

