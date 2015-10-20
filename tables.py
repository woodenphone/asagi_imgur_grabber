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


# SQLAlchemy table setup
Base = declarative_base()

class Board(Base):
    """Class that defines the boards table in the DB"""
    __tablename__ = config.target_table_name
    # Columns
    doc_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    comment = sqlalchemy.Column(sqlalchemy.UnicodeText())
    thread_num = sqlalchemy.Column(sqlalchemy.Integer)


# /SQLAlchemy table setup





def main():
    setup_logging(log_file_path=os.path.join("debug","tables-log.txt"))
    create_example_db_postgres()

if __name__ == '__main__':
    main()
