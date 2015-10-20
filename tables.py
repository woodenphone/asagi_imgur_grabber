#-------------------------------------------------------------------------------
# Name:        tables
# Purpose:  define the database for SQLAlchemy
#
# Author:      User
#
# Created:     08/04/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sqlalchemy# Database library
from sqlalchemy.ext.declarative import declarative_base# Magic for ORM
import sqlalchemy.dialects.postgresql # postgreSQL ORM (JSON, JSONB)

import config # Settings and configuration
from utils import * # General utility functions



##class Example(Base):
##     """Class that defines the media table in the DB"""
##     __tablename__ = "example"
##     # Columns
##     # Locally generated
##     primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)# Only used as a primary key
##     date_added = sqlalchemy.Column(sqlalchemy.BigInteger)# The unix time the media was saved
##     media_url = sqlalchemy.Column(sqlalchemy.UnicodeText())# Should have a constant length since it's a hash
##     sha512base64_hash = sqlalchemy.Column(sqlalchemy.String(88))
##     sha512base64_hash = sqlalchemy.Column(sqlalchemy.dialects.postgresql.CHAR(88))
##     local_filename = sqlalchemy.Column(sqlalchemy.String(250))# Filename on local storage, file path is deterministically generated from this
##     remote_filename = sqlalchemy.Column(sqlalchemy.UnicodeText())# Filename from original location (If any)
##     file_extention = sqlalchemy.Column(sqlalchemy.String(25))# ex. png, jpeg
##     extractor_used = sqlalchemy.Column(sqlalchemy.String(250))# internal name of the extractor used (function name of extractor)
##     # Video and Audio use these
##     yt_dl_info_json = sqlalchemy.Column(sqlalchemy.UnicodeText())
##     video_id = sqlalchemy.Column(sqlalchemy.UnicodeText())# The ID of the video used by the originating site
##     audio_id = sqlalchemy.Column(sqlalchemy.UnicodeText())# The ID of the audio used by the originating site
##     annotations = sqlalchemy.Column(sqlalchemy.UnicodeText())

# SQLAlchemy table setup
Base = declarative_base()

class Board(Base):
    """Class that defines the boards table in the DB"""
    __tablename__ = config.target_table_name
    # Columns
    doc_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)# Local primary key
    comment = sqlalchemy.Column(sqlalchemy.UnicodeText())


# /SQLAlchemy table setup





def main():
    setup_logging(log_file_path=os.path.join("debug","tables-log.txt"))
    create_example_db_postgres()

if __name__ == '__main__':
    main()
