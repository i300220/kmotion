#!/usr/bin/env python

# Copyright 2008 David Selby dave6502googlemail.com

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
Waits on the 'fifo_settings_wr' fifo until data received then parse the data
and modifiy 'www_rc', also updates 'feeds_cache'
"""

import sys, os.path, subprocess, ConfigParser, logger, time, cPickle, traceback
import sort_rc, daemon_whip, init_motion, mutex

log_level = 'WARNING'
logger = logger.Logger('kmotion_setd', log_level)


def main():  
    """
    Waits on the 'fifo_settings_wr' fifo until data received then parse the data
    and modifiy 'www_rc', also updates 'feeds_cache'
    
    ine ... interleave enabled
    fse ... full screen enabled
    lbe ... low bandwidth enabled
    lce ... low CPU enabled
    skf ... skip archive frames
    are ... archive button enabled
    lge ... logs button enabled
    coe ... config button enabled
    fue ... func button enabled
    spa ... msg button enabled
    abe ... about button enabled
    loe ... logout button enabled
    
    sec ... secure config
    coh ... config hash code
    
    fma ... feed mask
    
    fen ... feed enabled
    fde ... feed device
    fin ... feed input
    ful ... feed url
    fpr ... feed proxy
    fln ... feed loggin name
    flp ... feed loggin password
    fwd ... feed width
    fhe ... feed height
    fna ... feed name
    fbo ... feed show box
    ffp ... feed fps
    fqu ... feed quality
    fkb ... feed kbs
    fpe ... feed snap enabled
    fsn ... feed snap interval
    ffe ... feed smovie enabled
    fme ... feed movie enabled
    fup ... feed updates
    
    psx ... PTZ step x
    psy ... PTZ step y
    ptt ... PTZ track type
    pte ... PTZ enabled
    ptc ... PTZ calib first
    pts ... PTZ servo settle
    ppe ... PTZ park enabled
    ppd ... PTZ park delay
    ppx ... PTZ park x
    ppy ... PTZ park y
    p1x ... PTZ preset 1 x
    p1y ... PTZ preset 1 y
    p2x ... PTZ preset 2 x
    p2y ... PTZ preset 2 y
    p3x ... PTZ preset 3 x
    p3y ... PTZ preset 3 y
    p4x ... PTZ preset 4 x
    p4y ... PTZ preset 4 y
    
    dif ... display feeds
    col ... color select
    dis ... display select
    
    chk ... length check
    
    args    : 
    excepts : 
    return  : none
    """
    
    logger.log('starting daemon ...', 'CRIT')
    kmotion_dir = os.getcwd()[:-5]
    
    reload_ptz_config = False
    reload_all_config = False
    
    RELOAD_PTZ =  ['psx', 'psy', 'ptc', 'pts', 'ppe', 'ppd', 'ppx', 'ppy',
                   'p1x', 'p1y', 'p2x', 'p2y', 'p3x', 'p3y', 'p4x', 'p4y']
    
    RELOAD_ALL =  ['fma', 'fen', 'fde', 'fin', 'ful', 'fpr', 'fln', 'flp', 
                   'fwd', 'fhe', 'fbo', 'ffp', 'fpe', 'fsn', 'ffe', 'fme', 
                   'fup', 'fmk', 'ptt', 'pte']
    
    update_feeds_cache(kmotion_dir)

    while True:
        
        logger.log('waiting on FIFO pipe data', 'DEBUG')
        data = subprocess.Popen(['cat', '%s/www/fifo_settings_wr' % kmotion_dir], stdout=subprocess.PIPE).communicate()[0]
        data = data.rstrip()
        logger.log('FIFO pipe data: %s' % data, 'DEBUG')
        
        if len(data) < 8:
            continue
        
        if len(data) > 7 and data[-8:] == '99999999': # FIFO purge
            logger.log('FIFO purge', 'DEBUG')
            continue

        if int(data[-8:]) != len(data) - 13: # filter checksum
            logger.log('data checksum error - rejecting data', 'CRIT')
            continue
        
        masks_modified = [] # reset masks changed list
        parser = mutex_www_parser_rd(kmotion_dir)
        for raw_data in data.split('$'):
            if raw_data == '': continue # filter starting ''
            split_data = raw_data.split(':')

            if len(split_data[0]) > 3:
                key = split_data[0][:3]
                index = int(split_data[0][3:])
            else:
                key = split_data[0] # the 3 digit key ie 'fen' or 'fha'
                index = 0           # optional list pointer for the id
            value = split_data[1]
            if key == 'ine': # interleave
                parser.set('misc', 'misc1_interleave', num_bool(value))
            elif key == 'fse': # full screen
                parser.set('misc', 'misc1_full_screen', num_bool(value))
            elif key == 'lbe': # low bandwidth
                parser.set('misc', 'misc1_low_bandwidth', num_bool(value))
            elif key == 'lce': # low cpu
                parser.set('misc', 'misc1_low_cpu', num_bool(value))
            elif key == 'skf': # skip archive frames enabled
                parser.set('misc', 'misc1_skip_frames', num_bool(value))
            elif key == 'are': # archive button enabled
                parser.set('misc', 'misc2_archive_button_enabled', num_bool(value))
            elif key == 'lge': # logs button enabled
                parser.set('misc', 'misc2_logs_button_enabled', num_bool(value))
            elif key == 'coe': # config button enabled
                parser.set('misc', 'misc2_config_button_enabled', num_bool(value))
            elif key == 'fue': # function button enabled
                parser.set('misc', 'misc2_func_button_enabled', num_bool(value))
            elif key == 'spa': # update button enabled
                parser.set('misc', 'misc2_msg_button_enabled', num_bool(value))
            elif key == 'abe': # about button enabled
                parser.set('misc', 'misc2_about_button_enabled', num_bool(value))
            elif key == 'loe': # logout button enabled
                parser.set('misc', 'misc2_logout_button_enabled', num_bool(value))

            elif key == 'sec': # secure config
                parser.set('misc', 'misc3_secure', num_bool(value))
            elif key == 'coh': # config hash
                parser.set('misc', 'misc3_config_hash', value)
        
            elif key == 'fma': # feed mask
                parser.set('motion_feed%02i' % index, 'feed_mask', value)
                masks_modified.append((index, value))
        
            elif key == 'fen': # feed enabled
                parser.set('motion_feed%02i' % index, 'feed_enabled', num_bool(value))
            elif key == 'fde': # feed device
                parser.set('motion_feed%02i' % index, 'feed_device', value)
            elif key == 'fin': # feed input
                parser.set('motion_feed%02i' % index, 'feed_input', value)
            elif key == 'ful': # feed url
                parser.set('motion_feed%02i' % index, 'feed_url', de_sanitise(value))
            elif key == 'fpr': # feed proxy
                parser.set('motion_feed%02i' % index, 'feed_proxy', de_sanitise(value))
            elif key == 'fln': # feed loggin name
                parser.set('motion_feed%02i' % index, 'feed_lgn_name', de_sanitise(value))
            elif key == 'flp': # feed loggin password
                # check to see if default *'d password is returned
                if de_sanitise(value) != '*' * len(parser.get('motion_feed%02i' % index, 'feed_lgn_pw')):
                    parser.set('motion_feed%02i' % index, 'feed_lgn_pw', de_sanitise(value))
            elif key == 'fwd': # feed width
                parser.set('motion_feed%02i' % index, 'feed_width', value)
            elif key == 'fhe': # feed height
                parser.set('motion_feed%02i' % index, 'feed_height', value)
            elif key == 'fna': # feed name
                parser.set('motion_feed%02i' % index, 'feed_name', de_sanitise(value))
            elif key == 'fbo': # feed show box
                parser.set('motion_feed%02i' % index, 'feed_show_box', num_bool(value))
            elif key == 'ffp': # feed fps
                parser.set('motion_feed%02i' % index, 'feed_fps', value)
            elif key == 'fqu': # feed quality
                parser.set('motion_feed%02i' % index, 'feed_quality', value)
            elif key == 'fkb': # feed kbs
                parser.set('motion_feed%02i' % index, 'feed_kbs', value)
            elif key == 'fpe': # feed snap enabled
                parser.set('motion_feed%02i' % index, 'feed_snap_enabled', num_bool(value))
            elif key == 'fsn': # feed snap interval
                parser.set('motion_feed%02i' % index, 'feed_snap_interval', value)
            elif key == 'ffe': # feed smovie enabled
                parser.set('motion_feed%02i' % index, 'feed_smovie_enabled', num_bool(value))
            elif key == 'fme': # feed movie enabled
                parser.set('motion_feed%02i' % index, 'feed_movie_enabled', num_bool(value))
            elif key == 'fup': # feed updates
                parser.set('motion_feed%02i' % index, 'feed_updates', num_bool(value))
                
            elif key == 'psx': # ptz step x
                parser.set('motion_feed%02i' % index, 'ptz_step_x', value)                
            elif key == 'psy': # ptz step y
                parser.set('motion_feed%02i' % index, 'ptz_step_y', value)
            elif key == 'ptt': # ptz calib first
                parser.set('motion_feed%02i' % index, 'ptz_track_type', value)
        
            elif key == 'pte': # ptz enabled
                parser.set('motion_feed%02i' % index, 'ptz_enabled', num_bool(value))
            elif key == 'ptc': # ptz calib first
                parser.set('motion_feed%02i' % index, 'ptz_calib_first', num_bool(value))
            elif key == 'pts': # ptz servo settle
                parser.set('motion_feed%02i' % index, 'ptz_servo_settle', value)
            elif key == 'ppe': # ptz park enable
                parser.set('motion_feed%02i' % index, 'ptz_park_enabled', num_bool(value))
            elif key == 'ppd': # ptz park delay
                parser.set('motion_feed%02i' % index, 'ptz_park_delay', value)
            elif key == 'ppx': # ptz park x
                parser.set('motion_feed%02i' % index, 'ptz_park_x', value)
            elif key == 'ppy': # ptz park y
                parser.set('motion_feed%02i' % index, 'ptz_park_y', value)
            elif key == 'p1x': # ptz preset 1 x
                parser.set('motion_feed%02i' % index, 'ptz_preset1_x', value)                
            elif key == 'p1y': # ptz preset 1 y
                parser.set('motion_feed%02i' % index, 'ptz_preset1_y', value)
            elif key == 'p2x': # ptz preset 2 x
                parser.set('motion_feed%02i' % index, 'ptz_preset2_x', value)                
            elif key == 'p2y': # ptz preset 2 y
                parser.set('motion_feed%02i' % index, 'ptz_preset2_y', value)
            elif key == 'p3x': # ptz preset 3 x
                parser.set('motion_feed%02i' % index, 'ptz_preset3_x', value)                
            elif key == 'p3y': # ptz preset 3 y
                parser.set('motion_feed%02i' % index, 'ptz_preset3_y', value)
            elif key == 'p4x': # ptz preset 4 x
                parser.set('motion_feed%02i' % index, 'ptz_preset4_x', value)                
            elif key == 'p4y': # ptz preset 4 y
                parser.set('motion_feed%02i' % index, 'ptz_preset4_y', value)
        
            elif key == 'dif': # display feeds
                parser.set('misc', 'misc4_display_feeds_%02i' % index, value)
            elif key == 'col': # color select
                parser.set('misc', 'misc4_color_select', value)
            elif key == 'dis': # display select
                parser.set('misc', 'misc4_display_select', value)
                
            # if key fits flag for reload everything including the ptz daemon, 
            # motion and everything else, slow and painfull
            if key in RELOAD_ALL : reload_all_config = True
            
            # if key fits flag for reload the ptz daemon only. the ptz daemon is
            # quick to reload and does not have the crashy pants of a motion 
            # reload !
            if key in RELOAD_PTZ : reload_ptz_config = True
            
        mutex_www_parser_wr(kmotion_dir, parser)
        mutex.acquire(kmotion_dir, 'www_rc')
        sort_rc.sort_rc('%s/www/www_rc' % kmotion_dir)
        mutex.release(kmotion_dir, 'www_rc')
        update_feeds_cache(kmotion_dir)
        
        # has to be here, image width, height have to be written to 'www_rc'
        # before mask can be made
        for i in range(len(masks_modified)):
            create_mask(kmotion_dir, masks_modified[i][0], masks_modified[i][1])
        
        if reload_all_config: 
            init_motion.gen_motion_configs(kmotion_dir)
            daemon_whip.reload_all_configs()
            reload_all_config = False
            reload_ptz_config = False
            continue # skip 'reload_ptz_config', already done
    
        if reload_ptz_config: 
            daemon_whip.reload_ptz_config()
            reload_ptz_config = False 


def num_bool(num):
    """
    Converts a 1 or 0 to a 'true' or 'false' string 

    args    : int ... 1 for 'true', 0 for 'false'bool_str
    excepts : 
    return  : 'true' or 'false' string 
    """
    
    if int(num) == 1: return 'true'
    return 'false'


def de_sanitise(text):
    """
    Converts sanitised <...> to troublesome characters

    args    : text ... the text to be de-sanitised
    excepts : 
    return  : text ... the de-sanitised text
    """
    
    text = text.replace('<amp>', '&')
    text = text.replace('<que>', '?')
    text = text.replace('<col>', ':')
    return text


def create_mask(kmotion_dir, feed, mask_hex_str):   
    """
    Create a motion PGM mask from 'mask_hex_string' for feed 'feed'. Save it
    as ../core/masks/mask??.png.
    
    args    : kmotion_dir ...  the 'root' directory of kmotion 
              feed ...         the feed number
              mask_hex_str ... the encoded mask hex string
    excepts : 
    return  : none
    """
    
    logger.log('create_mask() - mask hex string: %s' % mask_hex_str, 'DEBUG')
    parser = mutex_www_parser_rd(kmotion_dir)
    image_width =  int(parser.get('motion_feed%02i' % feed, 'feed_width')) 
    image_height = int(parser.get('motion_feed%02i' % feed, 'feed_height')) 
    logger.log('create_mask() - width: %s height: %s' % (image_width, image_height), 'DEBUG')
    
    black_px = '\x00' 
    white_px = '\xFF' 
    
    mask = ''
    mask_hex_split = mask_hex_str.split('#')
    px_yptr = 0
    
    for y in range(10):
        
        tmp_dec = int(mask_hex_split[y], 16)
        px_xptr = 0
        image_line = ''
        
        for x in range(10, 0, -1):
        
            px_mult = (image_width - px_xptr) / x
            px_xptr += px_mult
            
            bin_ = tmp_dec & 512
            tmp_dec <<= 1
            
            if bin_ == 512:
                image_line += black_px * px_mult
            else:
                image_line += white_px * px_mult
        
                
        px_mult = (image_height - px_yptr) / (10 - y)
        px_yptr += px_mult
            
        mask += image_line * px_mult
        
    f_obj = open('%s/core/masks/mask%0.2d.pgm' % (kmotion_dir, feed), mode='wb')
    print >> f_obj, 'P5'
    print >> f_obj, '%d %d' % (image_width, image_height)
    print >> f_obj, '255'
    print >> f_obj, mask
    f_obj.close()
    logger.log('create_mask() - mask written', 'DEBUG')
    
    
def update_feeds_cache(kmotion_dir):
    """
    Update 'feeds_cache' pickle on a config change so 'xmlHttp_feeds' is up to 
    date. Pickle is of format ...
    ['ramdisk_dir', 'feed 1 enabled', 'feed 2 enabled', .....]
    
    args    : kmotion_dir ... the 'root' directory of kmotion   
    excepts : 
    return  : 
    """
    
    cache = []
    logger.log('update_feeds_cache() - updateing cache', 'DEBUG')
    parser = mutex_www_parser_rd(kmotion_dir)
    
    cache.append(parser.get('system', 'ramdisk_dir'))
    for feed in range(1, 17):
        if parser.get('motion_feed%02i' % feed, 'feed_enabled') == 'true':
            cache.append(True)
        else:
            cache.append(False)
            
    f_obj = open('%s/www/feeds_cache' % kmotion_dir, 'w')
    cPickle.dump(cache, f_obj)
    f_obj.close()
            
    
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


def mutex_www_parser_wr(kmotion_dir, parser):
    """
    Safely write a parser instance to 'www_rc' under mutex control.
    
    args    : kmotion_dir ... the 'root' directory of kmotion
              parser      ... the parser instance 
    excepts : 
    return  : 
    """

    try:
        mutex.acquire(kmotion_dir, 'www_rc')
        f_obj = open('%s/www/www_rc' % kmotion_dir, 'w')
        parser.write(f_obj)
        f_obj.close()
    finally:
        mutex.release(kmotion_dir, 'www_rc')



# it is CRUCIAL that this code is bombproof

while True:
    try:    
        main()
    except: # global exception catch
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exc_trace = traceback.extract_tb(exc_traceback)[-1]
        exc_loc1 = '%s' % exc_trace[0]
        exc_loc2 = '%s(), Line %s, "%s"' % (exc_trace[2], exc_trace[1], exc_trace[3])
        
        logger.log('** CRITICAL ERROR ** kmotion_setd crash - type: %s' 
                   % exc_type, 'CRIT')
        logger.log('** CRITICAL ERROR ** kmotion_setd crash - value: %s' 
                   % exc_value, 'CRIT')
        logger.log('** CRITICAL ERROR ** kmotion_setd crash - traceback: %s' 
                   %exc_loc1, 'CRIT')
        logger.log('** CRITICAL ERROR ** kmotion_setd crash - traceback: %s' 
                   %exc_loc2, 'CRIT') 
        time.sleep(60)


