#!/usr/bin/env python
#! -*- coding: utf-8 -*-

# Google Play Scraper v0.1
# Copyright (c) 2015, Jan Nejtek <jan.nejtek@outlook.com>

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

""" This script fetches basic app information from Google Play
    and outputs it in either human readable form or in JSON for
    piping into other programs and scripts. """

import urllib2
import sys
import os
import json
import getopt
from bs4 import BeautifulSoup

# --- DEFAULT VALUES ---
ENCODING = 'utf-8'
LANGUAGE = 'en-US'
USERAGENT = 'Ultron v1.0.1337'
# --- END DEFAULT VALUES ---

def print_help():
    """ Prints out information about the program and how to use it. """
    print 'Google Play Scraper v0.1 - Jan Nejtek, 2015'
    print 'Usage: ' + os.path.basename(sys.argv[0]) + ' -i [appid] [options]'
    print '-h        : Prints this message; also --help'
    print '-j        : Outputs JSON instead of human readable info; also --json'
    print '-i id     : Required. ID of the app to get info on; also --id'
    print '-e coding : Sets the encoding to use, default is ' + ENCODING + '; also --encoding'
    print '-l locale : Sets the language to use, default is ' + LANGUAGE + '; also --locale '
    print '            Accepted codes are according to ISO 639-1'

def print_human(name, description, publisher, rawprice, iconlink):
    """ Prints out a human readable description of the app. """
    print 'Name: ' + name
    print 'Description: ' + description
    print 'Publisher: ' + publisher
    print 'Price: ' + rawprice
    print 'Icon link: ' + iconlink

def print_human_error(err_type, err_code):
    """ Prints out a human readable description of the error. """
    print 'Error: ' + err_type
    print 'Error code: ' + str(err_code)

def print_json(name, description, publisher, rawprice, iconlink):
    """ Prints out a short JSON containing the app details. """
    print json.dumps({'name':name, 'description':description, 'publisher':publisher, 'rawPrice':rawprice, 'iconLink':iconlink}, ensure_ascii=False)

def print_json_error(err_type, err_code):
    """ Prints out a short JSON containing the error details. """
    print json.dumps({'error':err_type, 'code':err_code})

def main():
    """ Main function. Beware, this script is NOT intended to be imported as a module. """
    global ENCODING, LANGUAGE
    usejson = False

    # Grab the arguments with getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hji:l:e:', ['help', 'json', 'id=', 'locale=', 'encoding='])
    except getopt.GetoptError, exc:
        print str(exc)
        print_help()
        sys.exit(2)

    storeid = ""

    # Check the arguments
    for o, a in opts:
        if o in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif o in ('-j', '--json'):
            usejson = True
        elif o in ('-i', '--id'):
            storeid = a
        elif o in ('-l', '--locale'):
            LANGUAGE = a
        elif o in ('-e', '--ENCODING'):
            ENCODING = a

    # Set ENCODING
    reload(sys)
    sys.setdefaultencoding(ENCODING)

    # If the user didn't supply the app ID, end the script.
    if storeid == "":
        if usejson:
            print_json_error(err_type='ArgumentError', err_code=2)
            sys.exit(2)
        else:
            print 'option -i or --id is required to supply the app id.'
            print 'without it there is nothing to scrape :('
            print_help()
            sys.exit(2)

    # Build the URL and request header.
    # Windows Store returns error 403 if you use the default urllib user agent.
    # Not sure about Google Play...
    url = 'https://play.google.com/store/apps/details?id=' + storeid + '&hl=' + LANGUAGE.lower()
    request = urllib2.Request(url, headers={'User-Agent' : USERAGENT})

    # Try to open a connection to Google Play and pull the data. Prepare for problems.
    try:
        connnection = urllib2.urlopen(request)
    except urllib2.HTTPError, exc:
        if usejson:
            print_json_error(err_type='HTTPError', err_code=exc.code)
        else:
            print_human_error(err_type='HTTPError', err_code=exc.code)
        sys.exit(1)
    except urllib2.URLError, exc:
        if usejson:
            print_json_error(err_type='URLError', err_code=exc.code)
        else:
            print_human_error(err_type='URLError', err_code=exc.code)
        sys.exit(1)

    # If the connection succeeds, read the contents and feed them to BeautifulSoup.
    html = connnection.read()
    soup = BeautifulSoup(html, 'html.parser')

    # Finally, extract the good stuff. HTML element positions as of 7.9.2015
    name = soup.h1.get_text()
    description = soup.find_all('div',{'class':'id-app-orig-desc'}, limit=1)[0].get_text()
    publisher = soup.find_all('a',{'class':'document-subtitle primary'}, limit=1)[0].get_text().strip()
    rawprice = soup.find_all('button',{'class':'price'}, limit=1)[0].get_text().strip().split()[0]
    icon = soup.img['src']

    # Since the Google Play writes "Install" on the download button instead of "Free",
    # we need to do a little parsing of the price. If it contains a decimal separator,
    # then it is most likely paid. We cater for both possible decimal separators.
    if ',' in rawprice or '.' in rawprice:
        price = rawprice
    else:
        price = '0'

	# Print the results
    if usejson:
        print_json(name=name, description=description, publisher=publisher, rawprice=price, iconlink=icon)
    else:
        print_human(name=name, description=description, publisher=publisher, rawprice=price, iconlink=icon)

if __name__ == "__main__":
    main()
