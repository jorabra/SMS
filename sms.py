#! /usr/bin/python
# -*- coding: utf-8 -*-

# A simple SMS application for sending SMS through a SMS gateway using the HTTP
# protocol. This implementation is spesific to Clickatell, but the data
# dictionary in compile_settings() can be tuned to use other gateways accepting
# the HTTP protocol. 
#
# Author: Jørgen Abrahamsen <jabr@pludre.net>
#

import os
import getopt
import urllib2
import urllib
import sys
import ConfigParser


# Configuration files
config_file = 'sms.config'
config_file_local = 'sms.local.config'

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 't:m:f:', ['test'])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    # Input variables
    to_nmbr = None
    from_nmbr = None
    message = None
    test = False

    for opt, arg in opts:
        if opt == '-t':
            to_nmbr = arg
        elif opt == '-f':
            from_nmbr = arg
        elif opt == '-m':
            message = arg.strip().decode('utf-8').encode('iso-8859-1')
        elif opt == '--test':
            test = True
        else:
            assert False, "Yo, fubar! There's a unhandled option"

    if to_nmbr and len(message) > 1:
        (url, settings) = compile_settings(to_nmbr, from_nmbr, message)
        if check_message(settings):
            if test:
                print settings
                data = urllib.urlencode(settings)
                print data
                sys.exit(0)
            send_request(url, settings)
    else:
        usage()
        sys.exit(2)

    sys.exit(0)



def compile_settings(to_nmbr, from_nmbr, message):
    if not os.path.exists(config_file):
        sys.exit("Configuration file %s not found!" % config_file)

    config = ConfigParser.ConfigParser()
    config.read(config_file)

    # Overload local configuration
    if os.path.exists(config_file_local):
        config.read(config_file_local)

    data = None
    url = None
    try:
        data = {
            'user': config.get('main', 'user'),
            'password': config.get('main', 'password'),
            'api_id': config.get('main', 'api_id'),
            'from': config.get('main', 'from'),
            'concat': 3,
            'to': to_nmbr,
            'text': message,
        }
        url = config.get('main', 'url')
    except Exception, err:
        print str(err)
        sys.exit(2)

    if from_nmbr:
        data['from'] = from_nmbr

    return (url, data)


def calculate_nmbr_msgs(len_msg, len_limit):
    nmbr = len_msg / len_limit
    if len_msg % len_limit > 0:
        nmbr += 1

    return nmbr
    

def check_message(settings):
    print "* To: %s -- From: %s\n* Message [%s]: %s" % (settings['to'], settings['from'], len(settings['text']), settings['text'].decode('iso-8859-1'))
    answer = None
    while True:
        answer = raw_input("[%s] Send %s message(s)? [y/n]: " % (len(settings['text']), calculate_nmbr_msgs(len(settings['text']), 160)))
        answer.strip()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False

    return True


def send_request(url, settings):
    data = urllib.urlencode(settings)
    response = urllib2.urlopen(url, data)
    print response.read()


def usage():
    print >> sys.stderr, "\
Usage: %s [OPTION]... \n\
\n\
Report bugs to jabr@pludre.net" % sys.argv[0]


if __name__ == "__main__":
    main(sys.argv[1:])
