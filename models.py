
from datetime import datetime
from enum import unique

from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Table, MetaData
from sqlalchemy.sql.sqltypes import DateTime

from db import Base, engine, db_session

# таблица для связи many2many

note_m2m_tag = Table(
    "note_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("note", Integer, ForeignKey("notes.id")),
    Column("tag", Integer, ForeignKey("tags.id")),
)


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    created = Column(DateTime, default=datetime.now())
    description = Column(String(150), nullable=False)
    done = Column(Boolean, default=False)
    tags = relationship("Tag", secondary=note_m2m_tag, cascade="all, delete", backref="notes")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, unique=True)
    notes = relationship("Note", secondary=note_m2m_tag, cascade="all, delete", backref="tags")

    def __repr__(self) -> str:
        return self.name


class Address_book(Base):
    __tablename__= "addressbook"
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    records = relationship("Record", cascade="all, delete", backref="book")

class Record(Base):
    __tablename__= "record"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    birthday = relationship("Birthday", cascade="all, delete", backref="user", uselist=False)
    phones = relationship("Phone", cascade="all, delete", backref="user")
    addresses = relationship("Address", cascade="all, delete", backref="user")
    emails = relationship("Email", cascade="all, delete", backref="user")
    book_id = Column(Integer, ForeignKey(Address_book.id, ondelete="CASCADE"))

class Birthday(Base):
    __tablename__= "birthday"
    id = Column(Integer, primary_key=True)
    bd_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey(Record.id, ondelete="CASCADE"))

class Phone(Base):
    __tablename__= "phone"
    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)
    user_id = Column(Integer, ForeignKey(Record.id, ondelete="CASCADE"))

class Address(Base):
    __tablename__= "address"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey(Record.id, ondelete="CASCADE"))

class Email(Base):
    __tablename__= "email"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey(Record.id, ondelete="CASCADE"))


if __name__ == "__main__":
    Base.metadata.create_all(engine)