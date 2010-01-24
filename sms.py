#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import getopt
import urllib2
import urllib
import sys
import ConfigParser


# TODO:
# - Sanitize input


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
    #verbose = False

    # Check if need for check on getopts is cleared by exceptions above ...
    for opt, arg in opts:
        if opt == '-t':
            to_nmbr = arg
        elif opt == '-f':
            from_nmbr = arg
        elif opt == '-m':
            message = arg.strip()
        elif opt == '--test':
            test = True
        else:
            assert False, "Yo, fubar! There's a unhandled option"

    # Check that we have enough variables to act.
    if to_nmbr and len(message) > 1:
        (url, settings) = compile_settings(to_nmbr, from_nmbr, message)
        if check_message(settings): # Split up into more than one message (160 chars per msg)
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
    config = ConfigParser.ConfigParser()
    config.read('sms.config')

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
    print "* To: %s -- From: %s\n* Message [%s]: %s" % (settings['to'], settings['from'], len(settings['text']), settings['text'])
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
Usage: %s [OPTION]... TEXT \n\
\n\
Report bugs to jabr@pludre.net" % sys.argv[0]


if __name__ == "__main__":
    main(sys.argv[1:])