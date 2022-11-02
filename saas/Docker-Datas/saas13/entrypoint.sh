#!/bin/bash

#set -e

echo "Entering The entrypoint.sh"
echo "Setting up Pip3 dependency if any"

if [ -f /mnt/extra-addons/requirements.txt ];
then
        pip3 install -r /mnt/extra-addons/requirements.txt
fi

echo "Call sent for starting Tele"

/bin/bash run_tele.sh; echo "Tele Exited";


echo "Start the Exta bash"
exec /bin/bash
