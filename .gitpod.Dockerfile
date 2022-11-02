FROM gitpod/workspace-postgres

USER gitpod

RUN sudo apt-get update && \
    sudo DEBIAN_FRONTEND=noninteractive  sudo apt-get install -y --no-install-recommends apt-utils  && \
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y wkhtmltopdf

# ---- Install tool packages ----
RUN sudo DEBIAN_FRONTEND=noninteractive sudo apt-get install wget git bzr python3-pip gdebi-core libpq-dev -y

# -- Other packages (Only ubuntu >= 18.04) ---
RUN sudo apt install python3-pip wget python3-dev python3-venv python3-wheel libxml2-dev libpq-dev libjpeg8-dev liblcms2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev build-essential git libssl-dev libffi-dev libmysqlclient-dev libjpeg-dev libblas-dev libatlas-base-dev -y 


# ---- Install python packages LDAP based on OpenLDAP ----
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get install python-dev libldap2-dev libsasl2-dev gcc -y

# ---- Install zbar packages ----
RUN sudo DEBIAN_FRONTEND=noninteractive sudo apt-get install zbar-tools -y

# ---- Install python libraries ----
# This is for compatibility with Ubuntu 16.04. Will work on 14.04, 15.04 and 16.04
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get install python3-suds -y

# --- Install other required packages (node, less) ----
RUN sudo DEBIAN_FRONTEND=noninteractive sudo apt-get install node-clean-css node-less -y

RUN psql -c "create user tele with encrypted password 'telepwd';"
RUN psql -c "ALTER ROLE tele WITH SUPERUSER;"
RUN psql -c "GRANT ALL PRIVILEGES ON DATABASE template0 TO tele;"
RUN psql -c "GRANT ALL PRIVILEGES ON DATABASE template1 TO tele;"

# Upgrade pip
RUN python -m pip install --upgrade pip

# Upgrade pip

RUN python -m pip install --upgrade pip

RUN pip3 install wheel
RUN pip3 install -U -r requirements.txt
