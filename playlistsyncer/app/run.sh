#!/bin/sh


CONFIG_PATH=/data/options.json
CRON_TASK=$(jq --raw-output ".schedule" $CONFIG_PATH)

# apply cron schedule to crontab file
echo "Using cron schedule: $CRON_TASK"
rm /etc/crontabs/root
cronjob1="$CRON_TASK python /usr/src/app/playlistsyncer.py > /proc/1/fd/1 2>/proc/1/fd/2"
cronjob2="@reboot python /usr/src/app/playlistsyncer.py > /proc/1/fd/1 2>/proc/1/fd/2"
echo -e "$cronjob1\n$cronjob2\n" >> /etc/crontabs/root

# start crond with log level 8 in foreground, output to stderr
crond -f -d 8