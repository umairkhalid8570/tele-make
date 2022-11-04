#!/bin/sh

set -e

TELE_CONFIGURATION_DIR=/etc/tele
TELE_CONFIGURATION_FILE=$TELE_CONFIGURATION_DIR/tele.conf
TELE_DATA_DIR=/var/lib/tele
TELE_GROUP="tele"
TELE_LOG_DIR=/var/log/tele
TELE_LOG_FILE=$TELE_LOG_DIR/tele-server.log
TELE_USER="tele"
ABI=$(rpm -q --provides python3 | uniq | awk '/abi/ {print $NF}')

if ! getent passwd | grep -q "^tele:"; then
    groupadd $TELE_GROUP
    adduser --system --no-create-home $TELE_USER -g $TELE_GROUP
fi
# Register "$TELE_USER" as a postgres user with "Create DB" role attribute
su - postgres -c "createuser -d -R -S $TELE_USER" 2> /dev/null || true
# Configuration file
mkdir -p $TELE_CONFIGURATION_DIR
# can't copy debian config-file as applets_path is not the same
if [ ! -f $TELE_CONFIGURATION_FILE ]
then
    echo "[options]
; This is the password that allows database operations:
; admin_passwd = admin
db_host = False
db_port = False
db_user = $TELE_USER
db_password = False
applets_path = /usr/lib/python${ABI}/site-packages/tele/applets
" > $TELE_CONFIGURATION_FILE
    chown $TELE_USER:$TELE_GROUP $TELE_CONFIGURATION_FILE
    chmod 0640 $TELE_CONFIGURATION_FILE
fi
# Log
mkdir -p $TELE_LOG_DIR
chown $TELE_USER:$TELE_GROUP $TELE_LOG_DIR
chmod 0750 $TELE_LOG_DIR
# Data dir
mkdir -p $TELE_DATA_DIR
chown $TELE_USER:$TELE_GROUP $TELE_DATA_DIR

INIT_FILE=/lib/systemd/system/tele.service
touch $INIT_FILE
chmod 0700 $INIT_FILE
cat << EOF > $INIT_FILE
[Unit]
Description=Tele
After=network.target

[Service]
Type=simple
User=tele
Group=tele
ExecStart=/usr/bin/tele --config $TELE_CONFIGURATION_FILE --logfile $TELE_LOG_FILE
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF
