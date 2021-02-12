#!/bin/bash
/usr/bin/ffmpeg -y -r 8 -f image2 -pattern_type glob -i "/home/shizuma/kmotion/images_dbase/`/bin/date +%Y%m%d`/01/smovie/*/0[0-9].jpg" /tmp/cam1.avi