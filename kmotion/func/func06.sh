#!/bin/bash
/usr/bin/ffmpeg -y -r 8 -f image2 -pattern_type glob -i "/home/shizuma/kmotion/images_dbase/`date +%Y%m%d`/06/smovie/*/0[0-9].jpg" /tmp/cam6.avi