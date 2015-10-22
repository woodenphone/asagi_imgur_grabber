#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     15/06/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import logging
import imgurpython# Imgur API
from imgurpython.helpers.error import ImgurClientError
from utils import *
import config

client = None# Keep client cached to avoid needing to reconnect


def download_image(url,output_dir):
    """ONLY FOR IMGUR due to assumptions made"""
    filename = url.split("/")[-1]# Should work for imgur because they use systematic filenames without special chars
    data = get_url(url)
    save_file(
    	file_path=os.path.join(output_dir, filename),
    	data=data,
    	force_save=True,
    	allow_fail=False
        )
    return


def get_imgur_client(max_attempts=10):
    """Wrap imgur client setup to make it more fault-tolerant"""
    attempt_counter = 0
    while attempt_counter <= max_attempts:
        attempt_counter += 1
        try:
             client = imgurpython.ImgurClient(config.imgur_client_id, config.imgur_client_secret)
             return client
        except ImgurClientError, err:
            logging.exception(err)
            logging.error("err:"+repr(err))
            continue
    return None


def save_album(album_link,output_dir):
    """Save the contents of an album"""
    # Extract album ID
    # http://imgur.com/a/AMibi#0
    album_id_search = re.search("""imgur.com/a/([a-zA-Z0-9]+)""", album_link, re.DOTALL)
    if album_id_search:
        album_id = album_id_search.group(1)
    else:
        logging.error("Could not parse album link! "+repr(album_link))
        assert(False)# we need to fix things if this happens
    try:
        # Load album from API
        client = get_imgur_client(max_attempts=10)
        if client is None:# Handle failure to setup client
            return []
        album = client.get_album(album_id)
    except ImgurClientError, err:
            logging.exception(err)
            logging.error("err:"+repr(err))
            return []# Empty because the album cant be retreived
    # Download each image in the album
    media_id_list = []
    for image in album.images:
        media_url = image["link"]
        download_image(
            url = media_url,
            output_dir = output_dir,
            )
    return media_id_list


def save_imgur_images(link,output_dir):
    """Process a url and save the image ids from it"""
    # http://imgur.com/UQ1j8OT,2PvFmxV#1
    # Grab image ids
    # imgur.com/([a-zA-Z0-9,]+)
    image_id_search = re.search("""imgur.com/([a-zA-Z0-9,]+)""", link, re.DOTALL)
    if image_id_search:
        unprocessed_image_ids = image_id_search.group(1)
    elif (link[-10:] == "imgur.com/"):# Handle links that are to imgur non-image pages
        logging.debug("Link is to an imgur non-image page, skipping: "+repr(link))
        return []
    else:
        logging.error("Could not parse image(s) link! "+repr(link))
        assert(False)# we need to fix things if this happens
    # Split image ids
    image_ids = unprocessed_image_ids.split(",")
    logging.debug("save_imgur_images() image_ids:"+repr(image_ids))
    # Initialise client
    client = get_imgur_client(max_attempts=10)
    if client is None:# Handle failure to setup client
        return []
    # Process each image id
    media_id_list = []
    for image_id in image_ids:
        try:
            logging.debug("save_imgur_images() image_id:"+repr(image_id))
            image = client.get_image(image_id)
            media_url = image.link
            download_image(
                url = media_url,
                output_dir = output_dir,
                )

        except ImgurClientError, err:
            logging.exception(err)
            logging.error("err:"+repr(err))
    return media_id_list



def save_imgur(link,output_dir):
    """Save any imgur link"""
    logging.debug("Handling imgur link:"+repr(link))
    # Check if album
    # http://imgur.com/a/AMibi#0
    if "imgur.com/a/" in link:
        return save_album(link,output_dir)
    # Check if multiple image ids in url
    return save_imgur_images(link,output_dir)
    # Let us know if we fail to process a link


def debug():
    """For WIP, debug, ect function calls"""
    print "foo"

    # Album
    save_album(
        album_link = "http://imgur.com/a/AMibi#0",
        output_dir=os.path.join("debug", "imgur")
        )

    # Multiple image link
    save_imgur(
        link = "http://imgur.com/UQ1j8OT,2PvFmxV#1",
        output_dir=os.path.join("debug", "imgur")
        )

    # Single image link
    save_imgur(
        link = "http://imgur.com/UQ1j8OT",
        output_dir=os.path.join("debug", "imgur")
        )

    logging.debug(repr(locals()))
    return


def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","imgur_log.txt"))
        debug()
    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()
