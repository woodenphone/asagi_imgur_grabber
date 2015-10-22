#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     15/10/2015
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



def find_imgur_links_in_db(session,start_id,stop_id,output_dir):
    assert(False)# TODO
    """Scan through an asagi database and find vocaroo links.
    return a list of links"""
    logging.info("Starting to process posts from the DB. ("+repr(start_id)+" to "+repr(stop_id)+")")
    # Request the posts from the DB
    posts_query = sqlalchemy.select([Board]).\
        where(Board.doc_id >= start_id).\
        where(Board.doc_id <= stop_id)
    post_rows = session.execute(posts_query)

    # Scan each post requested, downloading any found links
    post_counter = 0
    for post_row in post_rows:
        post_counter += 1
        logging.debug("post_counter: "+repr(post_counter))
        comment = post_row["comment"]
        thread_number = post_row["thread_num"]
        logging.debug("comment: "+repr(comment))
        if comment is None:# Skip post if no comment
            continue
        assert_is_string(comment)

        # Find links
        links = find_imgur_links_in_string(to_scan=comment)
        number_of_links_found = len(links)
        logging.debug("links: "+repr(links))

        post_output_path = os.path.join(output_dir, str(thread_number))

        # Save links
        for link in links:
            imgur.save_imgur(
                link,
                post_output_path
                )
        continue
    logging.info("Finished processing this batch of posts. ("+repr(start_id)+" to "+repr(stop_id)+")")
    return number_of_links_found


def scan_db(session,output_dir,start_id=0,stop_id=None,step_number=1000):
    """Scan over a DB table of arbitrary size and process all rows"""
    logging.info("Scanning DB...")

    # Find lowest ID in DB
    lowest_id_query = sqlalchemy.select([Board]).\
        order_by(sqlalchemy.asc(Board.doc_id)).\
        limit(1)
    lowest_id_rows = session.execute(lowest_id_query)
    lowest_id_row = lowest_id_rows.fetchone()
    lowest_id_in_table = lowest_id_row["doc_id"]
    logging.info("lowest_id_in_table: "+repr(lowest_id_in_table))

    # Find highest ID in DB
    highest_id_query = sqlalchemy.select([Board]).\
        order_by(sqlalchemy.desc(Board.doc_id)).\
        limit(1)
    highest_id_rows = session.execute(highest_id_query)
    highest_id_row = highest_id_rows.fetchone()
    highest_id_in_table = highest_id_row["doc_id"]
    logging.info("highest_id_in_table: "+repr(highest_id_in_table))

    # If stop_id isn't set, use the highest currently existing ID in the table
    if stop_id is None:
        stop_id = highest_id_in_table

    # Prevent the start_id from being too low
    if start_id < lowest_id_in_table:
        logging.warning("Start number was lower than the lowest ID in the table!")
        if start_id <= stop_id:
            start_id = lowest_id_in_table
        else:
            logging.error("Start ID was greater than stop ID!")
            assert(False)
            return

    # Setup id number values for initial group
    low_id = start_id
    high_id = start_id +step_number

    total_number_of_links_found = 0
    # Loop to process posts in batches to keep memory use lower
    while low_id <= stop_id:
        logging.debug("low_id: "+repr(low_id)+" , high_id:"+repr(high_id))
        # Process this group of rows
        number_of_links_found = find_imgur_links_in_db(
            session=session,
            start_id=low_id,
            stop_id=high_id,
            output_dir=output_dir,
            )
        total_number_of_links_found += number_of_links_found
        # Increase ID numbers
        low_id = high_id
        high_id += step_number
        continue

    logging.info("total_number_of_links_found: "+repr(total_number_of_links_found))
    logging.info("Finished scanning DB")
    return total_number_of_links_found


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



def find_vocaroo_links_in_string(to_scan):
    """Take a string, such as an archived post's comment,
     and find vocaroo links in it if there are any"""
    # http://vocaroo.com/i/s0xtktsit8rE
    # (?:https?://)?(?:www\.)?vocaroo.com/i/\w+
    vocaroo_links = re.findall("""(?:https?://)?(?:www\.)?vocaroo.com/i/\w+""", to_scan, re.DOTALL)
    #logging.debug("vocaroo_links: "+repr(vocaroo_links))
    return vocaroo_links


def rest_search():
    pass



def debug():
    """where stuff is called to debug and test"""
    session = sql_functions.connect_to_db()
    scan_db(
        session=session,
        output_dir=os.path.join("output"),
        start_id=0,
        stop_id=None,
        step_number=1000
        )
    return



def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","asagi_imgur_grabber-log.txt"))

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
