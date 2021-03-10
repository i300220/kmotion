#!/usr/bin/env python

# Copyright 2008 David Selby dave6502@googlemail.com

# This file is part of kmotion.

# kmotion is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# kmotion is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with kmotion.  If not, see <http://www.gnu.org/licenses/>.

"""
Exports various methods used to initialize motion configuration. These methods
have been moved to this seperate module to reduce issues when the motion API
changes. All changes should be in just this module.
"""

import os, ConfigParser
import logger, mutex

log_level = 'WARNING'
logger = logger.Logger('init_motion', log_level)


def gen_motion_configs(kmotion_dir):   
    """
    Generates the motion.conf and thread??.conf files from www_rc and virtual
    motion conf files
            
    args    : kmotion_dir ... the 'root' directory of kmotion
    excepts : 
    return  : none
    """
    
    # delete all files in motion_conf skipping .svn directories
    for del_file in [del_file for del_file in os.listdir('%s/core/motion_conf' % kmotion_dir) 
                  if os.path.isfile('%s/core/motion_conf/%s' % (kmotion_dir, del_file))]:
        os.remove('%s/core/motion_conf/%s' % (kmotion_dir, del_file))
	
    parser = ConfigParser.SafeConfigParser()
    parser.read('%s/kmotion_rc' % kmotion_dir)
    images_dbase_dir = parser.get('dirs', 'images_dbase_dir')     
            
    parser = mutex_core_parser_rd(kmotion_dir)
    ramdisk_dir = parser.get('dirs', 'ramdisk_dir')     
            
    parser = mutex_www_parser_rd(kmotion_dir)
    feed_list = [feed for feed in range(1, 17) 
                 if parser.get('motion_feed%02i' % feed, 'feed_enabled') == 'true']
    
    if len(feed_list) > 0: # only populate 'motion_conf' if valid feeds
        gen_motion_conf(kmotion_dir, feed_list)
        gen_threads_conf(kmotion_dir, feed_list, ramdisk_dir, images_dbase_dir, parser)
      
    
def gen_motion_conf(kmotion_dir, feed_list):
    """
    Generates the motion.conf file from www_rc and the virtual motion conf files
            
    args    : kmotion_dir ... the 'root' directory of kmotion
              feed_list ...   a list of enabled feeds
              ramdisk_dir ... the ramdisk directory
    excepts : 
    return  : none
    """
    
    f_obj1 = open('%s/core/motion_conf/motion.conf' % kmotion_dir, 'w')
    print >> f_obj1, '''
# ------------------------------------------------------------------------------
# This config file has been automatically generated by kmotion
# Do __NOT__ modify it in any way.
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# 'default' section
# ------------------------------------------------------------------------------

quiet on

# ------------------------------------------------------------------------------
# 'user' section from 'virtual_motion_conf/motion.conf'
# ------------------------------------------------------------------------------
'''
    # this is a user changable file so error trap
    try:
        f_obj2 = open('%s/virtual_motion_conf/motion.conf' % kmotion_dir)
        user_conf = f_obj2.read()
        f_obj2.close()
    except IOError:   
        print >> f_obj1, '# virtual_motion_conf/motion.conf not readable - ignored'
        logger.log('no motion.conf readable in virtual_motion_conf dir - none included in final motion.conf', 'CRIT')
    else:
        print >> f_obj1, user_conf
    
    print >> f_obj1, '''
# ------------------------------------------------------------------------------
# 'override' section
# ------------------------------------------------------------------------------

daemon off
webcontrol_port 8080
webcontrol_localhost on
'''
    
    for feed in feed_list:
        print >> f_obj1, 'camera %s/core/motion_conf/camera%02i.conf\n' % (kmotion_dir, feed)
    f_obj1.close()
    
      
def gen_threads_conf(kmotion_dir, feed_list, ramdisk_dir, images_dbase_dir, parser):
    """
    Generates the thread??.conf files from www_rc and the virtual motion conf 
    files
            
    args    : kmotion_dir ...      the 'root' directory of kmotion
              feed_list ...        a list of enabled feeds
              ramdisk_dir ...      the ram disk directory
              images_dbase_dir ... the images dbase directory
    excepts : 
    return  : none
    """
    
    for feed in feed_list:
        f_obj1 = open('%s/core/motion_conf/camera%02i.conf' % (kmotion_dir, feed), 'w')
        print >> f_obj1,  '''
# ------------------------------------------------------------------------------
# This config file has been automatically generated by kmotion
# Do __NOT__ modify it in any way.
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# 'default' section
# ------------------------------------------------------------------------------

event_gap 2
pre_capture 1
#post_capture 16
post_capture 4

# ------------------------------------------------------------------------------
# 'user' section from 'virtual_motion_conf/thread%02i.conf'
# ------------------------------------------------------------------------------
''' % feed
    
        # this is a user changable file so error trap
        try:
            f_obj2 = open('%s/virtual_motion_conf/thread%02i.conf' % (kmotion_dir, feed))
            user_conf = f_obj2.read()
            f_obj2.close()
        except IOError:   
            print >> f_obj1, '# virtual_motion_conf/thread%02i.conf not readable - ignored' % feed
            logger.log('no feed%02i.conf readable in virtual_motion_conf dir - none included in final motion.conf' % feed, 'CRIT')
        else:
            print >> f_obj1, user_conf
        
        print >> f_obj1, '''
# ------------------------------------------------------------------------------
# 'override' section
# ------------------------------------------------------------------------------

movie_codec swf
snapshot_interval 1
stream_localhost on 
'''
        print >> f_obj1, 'target_dir %s' % ramdisk_dir
        
        # device and input
        feed_device = int(parser.get('motion_feed%02i' % feed, 'feed_device'))
        if feed_device != 16: # /dev/cam? device
            print >> f_obj1, 'videodevice /dev/cam%s' % feed_device
            print >> f_obj1, 'input %s' % parser.get('motion_feed%02i' % feed, 'feed_input')
            
        else: # netcam
            print >> f_obj1, 'netcam_url  %s' % parser.get('motion_feed%02i' % feed, 'feed_url')
            print >> f_obj1, 'netcam_proxy %s' % parser.get('motion_feed%02i' % feed, 'feed_proxy')
            print >> f_obj1, 'netcam_userpass %s:%s' % (parser.get('motion_feed%02i' % feed, 'feed_lgn_name'), parser.get('motion_feed%02i' % feed, 'feed_lgn_pw'))
            
        print >> f_obj1, 'width %s' % parser.get('motion_feed%02i' % feed, 'feed_width') 
        print >> f_obj1, 'height %s' % parser.get('motion_feed%02i' % feed, 'feed_height') 
        print >> f_obj1, 'picture_quality %s' % parser.get('motion_feed%02i' % feed, 'feed_quality')
        
        # show motion box
        if parser.get('motion_feed%02i' % feed, 'feed_show_box') == 'true': 
            print >> f_obj1, 'locate_motion_mode on'
             
        # ptz enabled, if 'ptz_track_type' == 9, useing plugins, disable here
        if parser.get('motion_feed%02i' % feed, 'ptz_enabled') == 'true' and int(parser.get('motion_feed%02i' % feed, 'ptz_track_type')) < 9: 
            print >> f_obj1, 'track_type %s' % parser.get('motion_feed%02i' % feed, 'ptz_track_type')
            
        # framerate
        if (parser.get('motion_feed%02i' % feed, 'feed_smovie_enabled') == 'true' or 
            parser.get('motion_feed%02i' % feed, 'feed_movie_enabled') == 'true'):
            print >> f_obj1, 'framerate %s' % parser.get('motion_feed%02i' % feed, 'feed_fps')
        elif parser.get('motion_feed%02i' % feed, 'feed_updates') == 'true':
            print >> f_obj1, 'framerate 5' # rapid feed updates enabled
        else:
            print >> f_obj1, 'framerate 1'
            
        # smovie mode or feed updates
        if (parser.get('motion_feed%02i' % feed, 'feed_smovie_enabled') == 'true' or 
            parser.get('motion_feed%02i' % feed, 'feed_updates') == 'true'):
            print >> f_obj1, 'picture_output on'
        else:
            print >> f_obj1, 'picture_output off'

        # movie mode
        if parser.get('motion_feed%02i' % feed, 'feed_movie_enabled') == 'true': 
            print >> f_obj1, 'ffmpeg_bps %s000' % parser.get('motion_feed%02i' % feed, 'feed_kbs')
            print >> f_obj1, 'movie_output on'
        else:
            print >> f_obj1, 'movie_output off'
            
        print >> f_obj1, '' 
            
        # feed mask
        if parser.get('motion_feed%02i' % feed, 'feed_mask') != '0#0#0#0#0#0#0#0#0#0#':
            print >> f_obj1, 'mask_file %s/core/masks/mask%0.2d.pgm' % (kmotion_dir, feed)            
            
        # prefix to 'walk backwards' from the 'target_dir'
        rel_prefix = ('../' * len(ramdisk_dir.split('/')))[:-1]
        
        # special case of smovie mode disabled and feed updates
        if (parser.get('motion_feed%02i' % feed, 'feed_smovie_enabled') == 'false' and 
            parser.get('motion_feed%02i' % feed, 'feed_updates') == 'true'):
            print >> f_obj1, 'picture_filename tmp/%%H%%M%%S%%q%0.2d' % feed
        else:
            print >> f_obj1, 'picture_filename %s%s/%%Y%%m%%d/%0.2d/smovie/%%H%%M%%S/%%q' % (rel_prefix, images_dbase_dir, feed)
        
        print >> f_obj1, 'movie_filename %s%s/%%Y%%m%%d/%0.2d/movie/%%H%%M%%S' % (rel_prefix, images_dbase_dir, feed)
        print >> f_obj1, 'snapshot_filename %0.2d/%%Y%%m%%d%%H%%M%%S' % feed
        # 'on_movie_start' not recorded, uses 'movie_filename' for more accuracy
        #print >> f_obj1, 'on_movie_start echo \'$%%H%%M%%S\' >> %s/%%Y%%m%%d/%0.2d/movie_journal' % (images_dbase_dir, feed)
        print >> f_obj1, 'on_movie_end echo \'$%%H%%M%%S\' >> %s/%%Y%%m%%d/%0.2d/movie_journal' % (images_dbase_dir, feed)
        print >> f_obj1, 'on_event_start %s/core/event_start.py %d' % (kmotion_dir, feed)
        print >> f_obj1, 'on_event_end %s/core/event_end.py %d' % (kmotion_dir, feed)
        print >> f_obj1, 'on_picture_save echo %%f > %s/%0.2d/last_jpeg' % (ramdisk_dir, feed)
        
        f_obj1.close()
        
    
def mutex_www_parser_rd(kmotion_dir):
    """
    Safely generate a parser instance and under mutex control read 'www_rc'
    returning the parser instance.
    
    args    : kmotion_dir ... the 'root' directory of kmotion   
    excepts : 
    return  : parser ... a parser instance
    """
    
    parser = ConfigParser.SafeConfigParser()
    try:
        mutex.acquire(kmotion_dir, 'www_rc')
        parser.read('%s/www/www_rc' % kmotion_dir)
    finally:
        mutex.release(kmotion_dir, 'www_rc')
    return parser


def mutex_core_parser_rd(kmotion_dir):
    """
    Safely generate a parser instance and under mutex control read 'core_rc'
    returning the parser instance.
    
    args    : kmotion_dir ... the 'root' directory of kmotion   
    excepts : 
    return  : parser ... a parser instance
    """
    
    parser = ConfigParser.SafeConfigParser()
    try:
        mutex.acquire(kmotion_dir, 'core_rc')
        parser.read('%s/core/core_rc' % kmotion_dir)
    finally:
        mutex.release(kmotion_dir, 'core_rc')
    return parser
     


# Module test code

if __name__ == '__main__':
    
    print '\nModule self test ... generating motion.conf and threads\n'
    gen_motion_configs('%s/..' % os.getcwd())
    
