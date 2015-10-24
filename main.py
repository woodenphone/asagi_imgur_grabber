#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     20/10/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import logging
import re
import os
import requests
import copy
from datetime import datetime
import sys
from bs4 import BeautifulSoup


import imgur
import config # Settings and configuration
import lockfiles # MutEx lockfiles
from utils import * # General utility functions




def find_imgur_links_in_string(to_scan):
    """Take a string, such as an archived post's comment,
     and find imgur links in it if there are any"""
    # Example links that we need to find
    # http://imgur.com/a/AMibi#0
    # http://imgur.com/UQ1j8OT,2PvFmxV#1
    # http://imgur.com/UQ1j8OT
    # (imgur\.com/(?:a/)?[\w#,]+)
    imgur_links = re.findall("""(imgur\.com/(?:a/)?[\w#,]+)""", to_scan, re.DOTALL)
    #logging.debug("imgur_links: "+repr(imgur_links))
    return imgur_links



def ruett_scan(search_term="imgur",link_pattern="(?:http://)?(?:www.)?(?:i.)?imgur.com"):
    """Conversion from code by DER RUETTLER to do what we want"""
    currentYear=datetime.datetime.now().year
    currentMonth=datetime.datetime.now().month
    year=2012
    month=2
    year2=2012
    month2=3

    link_set = set()# For cheap deduplication
    link_list = []# So we can preserve order

    #This loop is executed as long as month and year are below a certain treshold
    while year*12+month <= currentYear*12+currentMonth:
        print()
        logging.info('Timeframe: '+repr(month)+repr(year)+' - '+repr(month2)+repr(year2))
        #200=maximum number of pages returned by archive.moe
        for i in range(200):
            logging.info('Extracting from page '+str(i+1))
            #constructing the URL:
            url = "https://desustorage.org/mlp/search/text/"+search_term+"/start/"+str(year)+"-"+str(month)+"-1/end/"+str(year2)+"-"+str(month2)+"-1/page/"+str(i+1)+"/#"
            logging.debug("url: "+repr(url))
            #getting the source code:
            attempt_counter = 0
            while attempt_counter < 10:
                attempt_counter += 1
                try:
                    r=requests.get(url)
                    data=r.text
                    save_file(
                        file_path = os.path.join("debug","ruett_scan.htm"),
                        data = data.encode("iso-8859-15", "replace"),
                        force_save = True,
                        allow_fail = False
                        )
                    break
                except requests.exceptions.SSLError, err:
                    logging.exception(err)
                    continue

            #transforming the source code into a tree of objects:
            soup = BeautifulSoup(data)

            #check whether archive.moe still returns results:
            abort = str(soup.find('h4'))
            if abort=='<h4 class="alert-heading">Error!</h4>':
                break

            #find pastebin links and add them to their respective sets:
            for link_result in soup.find_all(href=re.compile(link_pattern)):
                link = link_result.get('href')
                if not link in link_set:
                    logging.debug("Adding new link: "+repr(link))
                    link_set.add(link)
                    link_list.append(link)
        month=month+1
        month2=month2+1
        if month==13:
            month=1
            year=year+1
        if month2==13:
            month2=1
            year2=year2+1

    logging.info('Extraction finished')
    return link_list



def scan_to_file(list_path):
    found_links_set = ruett_scan()
    found_links = list(found_links_set)
    appendlist(
        lines=found_links,
        list_file_path=os.path.join("debug","fould_imgur_links.txt"),
        initial_text="# List of completed items.\n"
        )
    return


def download_link_list(list_path,output_path):
    logging.debug("Downloading imgur link list...")
    saved_links = set()# Low quality, but low memory dedupe of links
    with open(list_path, "r") as f:
        for line in f:
            logging.debug("line: "+repr(line))
            if line[0] == "#":# Skip comments
                continue
            stripped_url = line.strip("\r\n\t ")
            if line not in saved_links:# Low quality, but low memory dedupe of links
                imgur.save_imgur(
                    link=stripped_url,
                    output_dir=output_path
                    )
            continue
    logging.debug("Finished downloading imgur link list.")
    return


def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","foolfuuka_imgur_grabber-log.txt"))

        list_path = os.path.join("fould_imgur_links.txt")
        scan_to_file(list_path)
        download_link_list(
            list_path,
            output_path=os.path.join("output")
            )


    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()