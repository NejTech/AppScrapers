#!/usr/bin/env python
#! -*- coding: utf-8 -*-

# Windows Store Scraper v0.1
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

""" This script fetches basic app information from Windows Store
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
    print 'Windows Store Scraper v0.1 - Jan Nejtek, 2015'
    print 'Usage: ' + os.path.basename(sys.argv[0]) + ' -i [appid] [options]'
    print '-h        : Prints this message; also --help'
    print '-j        : Outputs JSON instead of human readable info; also --json'
    print '-i id     : Required. ID of the app to get info on; also --id'
    print '-e coding : Sets the ENCODING to use, default is ' + ENCODING + '; also --encoding'
    print '-l locale : Sets the locale to use, default is ' + LANGUAGE + '; also --locale '
    print '            Usable values: http://msdn.microsoft.com/en-us/library/ee825488.aspx'

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
    url = 'http://apps.microsoft.com/windows/' + LANGUAGE.lower() + '/app/' + storeid
    request = urllib2.Request(url, headers={'User-Agent' : USERAGENT, 'Accept-Language' : LANGUAGE})

    # Try to open a connection to Windows Store and pull the data. Prepare for problems.
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

    # Since Windows Store doesn't return 404 on non-existing apps, we need to check it ourselves
    if len(soup.find_all('meta', {'name':'ms.prod'})) == 0:
        if usejson:
            print_json_error(err_type='HTTPError', err_code=404)
        else:
            print_human_error(err_type='HTTPError', err_code=404)
        sys.exit(1)

    # Finally, extract the good stuff. HTML element positions as of 7.9.2015
    name = soup.find_all('meta', {'name':'ms.prod'}, limit=1)[0]['content']
    description = soup.p.string
    publisher = soup.find_all('section', {'class':'srv_detailsTable section'}, limit=1)[0].find('dd').find('div').string.strip()
    price = soup.find_all('div', {'class':'price'}, limit=1)[0].span.string
    icon = 'http:' + soup.find_all('img', {'class':'cli_image m-b-lg'})[0]['src']

    # Print the results
    if usejson:
        print_json(name=name, description=description, publisher=publisher, rawprice=price, iconlink=icon)
    else:
        print_human(name=name, description=description, publisher=publisher, rawprice=price, iconlink=icon)

if __name__ == "__main__":
    main()
