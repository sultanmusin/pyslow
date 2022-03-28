#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



import getopt
import glob 
import logging 
import os
import sys
import re
from datetime import datetime

# interesting lines look like: 2022-03-09 06:38:51,018 | INFO | Going to set corrected ped v of module 141 to 41.91 (2417)
regex_correction = re.compile('^(\d\d\d\d-\d\d-\d\d \d+:\d+:\d+,\d+) .* ped v of module (\d+) to ([^\s]+) .*$')


def print_usage():
    print('Usage: log_parse.py  [-c config] -d <datetime> [-m <module>]  [<logfile(s)>]')
    print('   datetime format 2022-01-31-10-30-00')
    print('   logfile(s) default to logs/*.txt\n')
    print('Examples:')
    print('   log_parse.py -c Hodo -m 141 -d 2022-03-26-00-00-00')
    print('   Search all logfiles under logs/ with Hodo* config file looking for last setting of module 141\n')
    print('   log_parse.py -m 141 logs/dcs_log_2022-03-08-21-08-50.txt')
    print('   Search certain logfile for all setting of module 141\n')

    

    sys.exit()


def get_options(argv):
    opts, args = getopt.getopt(argv,"hc:d:m:",["config=","datetime=","module="])

    config = None
    when = None
    module = None

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
        elif opt in ("-c", "--config"):
            config = arg
        elif opt in ("-d", "--datetime"):
            when = datetime.strptime(arg, '%Y-%m-%d-%H-%M-%S')
        elif opt in ("-m", "--modlue"):
            module = arg

    logfiles = args if len(args) > 0 else glob.glob("logs/*.txt")

    return (config, when, module, logfiles)


def process_file(path, config_mask, when, module):
    with open(path) as f:
        first_line = f.readline()

        parts = first_line.split(' ')
        config_file = parts[-1].split('/')[-1].rstrip()

        if config_mask is not None and config_file.count(config_mask) == 0:
#            logging.info("Skipping")
            return


        #logging.info('Reading %s'%(path))
        #logging.info('Config %s'%(config_file))
        #logging.info('From %s'%(get_datetime(first_line)))

        # interesting lines look like: 2022-03-09 06:38:51,018 | INFO | Going to set corrected ped v of module 141 to 41.91 (2417)
        line = ''
        best_match = {}
        for line in f:
            match = regex_correction.match(line)
            if match:
                dt = get_datetime(match.group(1))
                mod = match.group(2)
                voltage = match.group(3)
                if (module is None or module == mod) and (when is None or dt < when):
                    best_match[mod] = 'At %s: set module %s to %s'%(dt, mod, voltage)
                    if when is None: 
                        print(best_match[mod])

        if when is not None and len(best_match)>0:
            print('\n'.join(best_match.values()))
        #last_line = line
        #logging.info('To %s'%(get_datetime(last_line)))


def get_datetime(line):
    try:
        parts = line.split(' ')
        text = ' '.join(parts[0:2])
        #print(line)
        #datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
        return datetime.strptime(text, '%Y-%m-%d %H:%M:%S,%f')
    except ValueError:
        return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    (config, when, module, logfiles) = get_options(sys.argv[1:])

    for path in logfiles:
        process_file(path, config, when, module)
