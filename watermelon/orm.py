""":mod:`watermelon.orm` --- Initializing database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#: The declarative abstract base class for object-relational mapping.
Base = declarative_base()


#: SQLAlchemy session class.
Session = sessionmaker()