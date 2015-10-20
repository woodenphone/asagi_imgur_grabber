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

import imgur
import config # Settings and configuration
import lockfiles # MutEx lockfiles
from utils import * # General utility functions
from bs4 import BeautifulSoup

def scan_site():
    target_board_shortnames = set(["mlp","tg"])
    target_field_names = set(["comment", "title", "email"])
    link_set = set()
    counter = -1
    while counter < 20:
        counter += 1
        logging.debug("Page: "+repr(counter))

        search_url = ("https://desustorage.org/_/api/chan/search/?board=mlp&text=imgur&start="+
            str(start_year)+"-"+str(start_month)+"-1&end="+
            str(end_year)+"-"+str(end_month)+"-1&page="+str(counter))
        r=requests.get(search_url)
        data=r.text
        #logging.debug("data: "+repr(data))
        soup = BeautifulSoup(data, "lxml")
        #logging.debug("soup: "+repr(soup))

        decoded_page = json.loads(data)
        posts = decoded_page[0]["posts"]
        for post_dict in posts:
            board_shortname = post_dict["board"]["shortname"]
            if board_shortname in target_board_shortnames:
                for target_field_name in target_field_names:
                    field_data = post_dict[target_field_name]
                    if field_data is None:# Prevent None object from being sent to regex stuff
                        continue
                    logging.debug("field_data: "+repr(field_data))
                    link_urls = find_imgur_links_in_string(field_data)
                    for link_url in link_urls:
                        if not link_url in link_set:
                            logging.debug("Adding new link: "+repr(link_url))
                            link_set.add(link_url)
            else:
                logging.error("Board was not correct, fix URL")

        #check whether archive.moe still returns results:
        abort = str(soup.find('h4'))
        if abort=='<h4 class="alert-heading">Error!</h4>':
            logging.debug("Stopping because abort string was found")
            break
    return link_set


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



def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","foolfuuka_imgur_grabber-log.txt"))

        found_links_set = scan_site()
        found_links = list(found_links_set)
        appendlist(
            lines=found_links,
            list_file_path=os.path.join("debug","fould_imgur_links.txt"),
            initial_text="# List of completed items.\n"
            )

    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()