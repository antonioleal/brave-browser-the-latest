#!/bin/bash

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

rm -rf /opt/brave-browser-the-latest
rm -rf /usr/share/pixmaps/brave-bowser-the-latest.png
rm -rf /usr/share/applications/brave-bowser-the-latest.desktop
rm -rf /etc/cron.hourly/brave-bowser-the-latest-cron.sh

