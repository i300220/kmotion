#!/bin/bash
/usr/bin/ffmpeg -y -r 4 -f image2 -pattern_type glob -i "/home/shizuma/kmotion/images_dbase/`date +%Y%m%d`/03/smovie/*/0[0-9].jpg" /tmp/cam3.avi