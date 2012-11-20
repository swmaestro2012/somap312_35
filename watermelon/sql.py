""":mod:`watermelon.sql` --- Database Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.functions import now
from sqlalchemy.types import DateTime, Text, UnicodeText, Integer, BigInteger

from orm import Base


class User(Base):
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
   
    __tablename__ = 'user'
    
    def __repr__(self):
        return '<User %r>' % self.name
    
class PlayList(Base):
    id = Column(Integer, primary_key=True)
    owner = Column(BigInteger, ForeignKey('user.id'))
    name = Column(UnicodeText, nullable=False)
    play_list = Column(UnicodeText, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
   
    __tablename__ = 'playlist'
    
    def __repr__(self):
        return '<User %r\'s %r>' % (self.owner, self.name)