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
Controls kmotion daemons allowing daemon starting, stopping, checking of status
and config reloading
"""

import time, os, ConfigParser
from subprocess import * # breaking habit of a lifetime !
import logger, init_core, mutex

log_level = 'WARNING'
logger = logger.Logger('daemon_whip', log_level)


def start_daemons():
    """ 
    Check and start all the kmotion daemons

    args    : 
    excepts : 
    return  : none
    """ 
    
    logger.log('start_daemons() - starting daemons ...', 'DEBUG')
    kmotion_dir = load_rc()[0]
    
    p_objs = Popen('ps ax | grep kmotion_hkd1.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    if p_objs.stdout.readline() == '':   
        Popen('nohup %s/core/kmotion_hkd1.py >/dev/null 2>&1 &' % kmotion_dir, shell=True) 
        logger.log('start_daemons() - starting kmotion_hkd1', 'DEBUG')

    p_objs = Popen('ps ax | grep kmotion_hkd2.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    if p_objs.stdout.readline() == '':   
        Popen('nohup %s/core/kmotion_hkd2.py >/dev/null 2>&1 &' % kmotion_dir, shell=True)
        logger.log('start_daemons() - starting kmotion_hkd2', 'DEBUG')

    p_objs = Popen('ps ax | grep kmotion_fund.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    if p_objs.stdout.readline() == '':   
        Popen('nohup %s/core/kmotion_fund.py >/dev/null 2>&1 &' % kmotion_dir, shell=True)
        logger.log('start_daemons() - starting kmotion_fund', 'DEBUG')
        
    p_objs = Popen('ps ax | grep kmotion_setd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    if p_objs.stdout.readline() == '':  
        Popen('nohup %s/core/kmotion_setd.py >/dev/null 2>&1 &' % kmotion_dir, shell=True)
        logger.log('start_daemons() - starting kmotion_setd', 'DEBUG')
        
    p_objs = Popen('ps ax | grep kmotion_ptzd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    if p_objs.stdout.readline() == '': 
        Popen('nohup %s/core/kmotion_ptzd.py >/dev/null 2>&1 &' % kmotion_dir, shell=True)
        logger.log('start_daemons() - starting kmotion_ptzd', 'DEBUG')
    
    # check for a 'motion.conf' file before starting 'motion'
    if os.path.isfile('%s/core/motion_conf/motion.conf' % kmotion_dir):
            
        p_objs = Popen('/bin/ps ax | /bin/grep [m]otion\ -c', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        if p_objs.stdout.readline() == '': 
            init_core.init_motion_out(kmotion_dir) # clear 'motion_out'
            Popen('nohup motion -c %s/core/motion_conf/motion.conf 2>&1 | grep --line-buffered -v \'saved to\' >> %s/www/motion_out &' % (kmotion_dir, kmotion_dir), shell=True)
            logger.log('start_daemons() - starting motion', 'DEBUG')
            
    else:
        logger.log('start_daemons() - no motion.conf, motion not started', 'CRIT')


def kill_daemons():
    """ 
    Kill all the kmotion daemons 

    args    : 
    excepts : 
    return  : none
    """
    
    logger.log('kill_daemons() - killing daemons ...', 'DEBUG')
    Popen('killall -q motion', shell=True)
    Popen('pkill -f \'python.+kmotion_hkd2.py\'', shell=True)
    Popen('pkill -f \'python.+kmotion_fund.py\'', shell=True)
    Popen('pkill -f \'python.+kmotion_setd.py\'', shell=True)
    Popen('pkill -f \'python.+kmotion_ptzd.py\'', shell=True)
    # orderd thus because kmotion_hkd1.py needs to call this function  
    Popen('pkill -f \'python.+kmotion_hkd1.py\'', shell=True)
    
    time.sleep(1) 
    while not no_daemons_running():
        logger.log('kill_daemons() - resorting to kill -9 ... ouch !', 'DEBUG')
        Popen('killall -9 -q motion', shell=True) # if motion hangs get nasty !
    
    # to kill off any 'cat' zombies ...
    Popen('pkill -f \'cat.+/www/fifo_ptz\'', shell=True) 
    Popen('pkill -f \'cat.+/www/fifo_ptz_preset\'', shell=True) 
    Popen('pkill -f \'cat.+/www/fifo_settings_wr\'', shell=True) 
    Popen('pkill -f \'cat.+/www/fifo_func\'', shell=True) 
        
    logger.log('kill_daemons() - daemons killed ...', 'DEBUG')


def all_daemons_running():
    """ 
    Check to see if all kmotion daemons are running

    args    : 
    excepts : 
    return  : bool ... true if all daemons are running
    """
    
    p_objs = Popen('ps ax | grep kmotion_hkd1.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout1 = p_objs.stdout.readline()
    
    p_objs = Popen('ps ax | grep kmotion_hkd2.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout2 = p_objs.stdout.readline()
        
    p_objs = Popen('ps ax | grep kmotion_fund.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout3 = p_objs.stdout.readline()
    
    p_objs = Popen('ps ax | grep kmotion_setd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout4 = p_objs.stdout.readline()
    
    p_objs = Popen('ps ax | grep kmotion_ptzd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout5 = p_objs.stdout.readline()
    
    p_objs = Popen('/bin/ps ax | /bin/grep [m]otion\ -c', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout6 = p_objs.stdout.readline()
    
    return (stdout1 != '' and stdout2 != '' and stdout3 != '' and stdout4 != '' 
            and stdout5 != '' and stdout6 != '')


def no_daemons_running():
    """ 
    Check to see if any kmotion daemons are running

    args    : 
    excepts : 
    return  : bool ... true if no daemons are running
    """
    
    p_objs = Popen('ps ax | grep kmotion_hkd1.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout1 = p_objs.stdout.readline()
    
    p_objs = Popen('ps ax | grep kmotion_hkd2.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout2 = p_objs.stdout.readline()
        
    p_objs = Popen('ps ax | grep kmotion_fund.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout3 = p_objs.stdout.readline()
    
    p_objs = Popen('ps ax | grep kmotion_setd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout4 = p_objs.stdout.readline()
    
    p_objs = Popen('ps ax | grep kmotion_ptzd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout5 = p_objs.stdout.readline()
    
    p_objs = Popen('/bin/ps ax | /bin/grep [m]otion\ -c', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout6 = p_objs.stdout.readline()
    
    return (stdout1 == '' and stdout2 == '' and stdout3 == '' and stdout4 == '' 
            and stdout5 == '' and stdout6 == '')


def daemon_status():
    """ 
    Check to see if kmotion daemons are running

    args    : 
    excepts : 
    return  : dict ... a dict of daemon names as keys and bool for daemons 
                       running
    """
    
    status = {}
    
    p_objs = Popen('ps ax | grep kmotion_hkd1.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    status['kmotion_hkd1'] = not (p_objs.stdout.readline() == '')

    p_objs = Popen('ps ax | grep kmotion_hkd2.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    status['kmotion_hkd2'] = not (p_objs.stdout.readline() == '')

    p_objs = Popen('ps ax | grep kmotion_fund.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    status['kmotion_fund'] = not (p_objs.stdout.readline() == '')
        
    p_objs = Popen('ps ax | grep kmotion_setd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    status['kmotion_setd'] = not (p_objs.stdout.readline() == '')
        
    p_objs = Popen('ps ax | grep kmotion_ptzd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    status['kmotion_ptzd'] = not (p_objs.stdout.readline() == '')
    
    p_objs = Popen('/bin/ps ax | /bin/grep [m]otion\ -c', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    status['motion'] = not (p_objs.stdout.readline() == '')

    return status


def reload_all_configs():
    """ 
    Force daemons to reload all configs 

    args    : 
    excepts : 
    return  : none
    """
    
    reload_ptz_config()
    reload_motion_config()
    # kmotion_fund and kmotion_setd have no SIGHUP handlers
    Popen('pkill -SIGHUP -f python.+kmotion_hkd1.py', shell=True) 
    Popen('pkill -SIGHUP -f python.+kmotion_hkd2.py', shell=True)
       
    
def reload_ptz_config():
    """ 
    Force ptz to reload configs 

    args    : 
    excepts : 
    return  : none
    """

    kmotion_dir = load_rc()[0]
    # a workaround. because 'kmotion_ptzd' is threaded the only way
    # to get the threads to reliably reload their config is to kill and 
    # restart else they languish in a sleep state for ? secs. so sending 
    # a SIGHUP to 'kmotion_ptzd' kills the script
    Popen('pkill -SIGHUP -f python.+kmotion_ptzd.py', shell=True)  
    while True:
        p_objs = Popen('ps ax | grep kmotion_ptzd.py$', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        stdout = p_objs.stdout.readline()
        if stdout == '': break
        time.sleep(0.1)
    Popen('nohup %s/core/kmotion_ptzd.py >/dev/null 2>&1 &' % kmotion_dir, shell=True)

    
def reload_motion_config():
    """ 
    Force motion to reload configs. The 'motion_reload_bug' flags whether a 
    SIGHUP is sufficient to reload motions configs or whether motion needs to be 
    stopped and restarted.

    Unfortunately motion appears not to look at its /dev/* files on receiving a 
    SIGHUP so a once connected device is assumed to be still there.
    
    args    : 
    excepts : 
    return  : none
    """

    rc = load_rc()
    kmotion_dir = rc[0]
    motion_reload_bug = rc[1]
    init_core.init_motion_out(kmotion_dir) # clear 'motion_out'
    if motion_reload_bug: # motion_reload_bug workaround
        trys = 0
        while True:
            
            trys += 1
            if trys < 4:
                Popen('killall -q motion', shell=True)
            else: 
                logger.log('reload_motion_config() - resorting to kill -9 ... ouch !', 'DEBUG')
                Popen('killall -9 -q motion', shell=True) # if motion hangs get nasty !
            
            p_objs = Popen('/bin/ps ax | /bin/grep [m]otion\ -c', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            stdout = p_objs.stdout.readline()
            if stdout == '': break
            
            time.sleep(1)       
            logger.log('reload_motion_config() - motion not killed - retrying ...', 'DEBUG')
            
        logger.log('reload_motion_configs() - motion killed', 'DEBUG')
    
        # check for a 'motion.conf' file before starting 'motion'
        if os.path.isfile('%s/core/motion_conf/motion.conf' % kmotion_dir):
                
            logger.log('reload_motion_configs() - pausing for 2 seconds ...', 'DEBUG')
            time.sleep(2)
            init_core.init_motion_out(kmotion_dir) # clear 'motion_out'
            Popen('nohup motion -c %s/core/motion_conf/motion.conf 2>&1 | grep --line-buffered -v \'saved to\' >> %s/www/motion_out &' % (kmotion_dir, kmotion_dir), shell=True)
            logger.log('reload_motion_configs() - restarting motion', 'DEBUG')
                
        else:
            logger.log('reload_motion_configs() - no motion.conf, motion not restarted', 'CRIT')
        
    else:        
        init_core.init_motion_out(kmotion_dir) # clear 'motion_out'
        os.popen('killall -s SIGHUP motion')
        logger.log('reload_motion_configs() - motion sent SIGHUP signal', 'DEBUG')
    
      
def load_rc():
    """
    Calculate kmotion dir and read core_rc  

    args    : 
    excepts : 
    return  : tuple ... (kmotion_dir, motion_reload_bug)
    """
    
    kmotion_dir = os.getcwd()[:-5]
    try:
        mutex.acquire(kmotion_dir, 'core_rc')   
        parser = ConfigParser.SafeConfigParser()
        parser.read('./core_rc') 
    finally:
        mutex.release(kmotion_dir, 'core_rc')
    
    return (kmotion_dir, 
            parser.get('workaround', 'motion_reload_bug') == 'True')

