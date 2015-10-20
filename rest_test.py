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

import imgur
import config # Settings and configuration
import lockfiles # MutEx lockfiles
from utils import * # General utility functions
from bs4 import BeautifulSoup


link_set = set()

counter = -1
while counter < 10000:
    counter += 1

    search_url = "https://desustorage.org/_/api/chan/search/?board=mlp&text=imgur&page="+str(counter)
    r=requests.get(url)
    data=r.text
    soup = BeautifulSoup(data)

    #check whether archive.moe still returns results:
    abort = str(soup.find('h4'))
    if abort=='<h4 class="alert-heading">Error!</h4>':
        break

    #find  links and add them to their respective sets:
    link_search_results = soup.find_all(href=re.compile('http://pastebin.com'))
    for link_search_result in link_search_results:
        link_url = link_search_result.get('href')
        if not link_url in link_set:
            found_links.add(pastebinLink)
            link_set.add(link_url)
    continue







def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","foolfuuka_imgur_grabber-log.txt"))

        session = sql_functions.connect_to_db()
        scan_db(
            session=session,
            output_dir = config.output_dir,
            start_id = config.start_id,
            stop_id = config.stop_id,
            step_number = config.step_number
            )

    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()