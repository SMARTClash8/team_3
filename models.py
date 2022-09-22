from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Table, MetaData
from sqlalchemy.sql.sqltypes import DateTime

from db import Base, engine, db_session



# таблица для связи many2many

note_m2m_tag = Table(
    "note_m2m_tag",
    Base.metadata,
    Column("note", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# notes_user = Table(
#     "notes_user",
#     Base.metadata,
#     Column("user_id", Integer, ForeignKey("user.id")),
#     Column("note_id", Integer, ForeignKey("notes.id")))

adbooks_user = Table(
    "adbook_user",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("addressbook_id", Integer, ForeignKey("addressbook.id")))

tags_user = Table(
    "tags_user",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")))

files_user = Table(
    'files_user',
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("files_id", Integer, ForeignKey("file.id")))

class User(Base, UserMixin):

    __tablename__ = "user"
    __table_args__ = {'sqlite_autoincrement': True} 
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    addressbooks = relationship("Address_book", secondary=adbooks_user, backref="user", lazy='dynamic')
    notes = relationship("Note", cascade="all, delete, delete-orphan", backref="user", lazy='dynamic')
    tags = relationship("Tag", secondary=tags_user, backref="user")
    files = relationship("File", secondary=files_user, backref="user")


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {'sqlite_autoincrement': True} 
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    created = Column(DateTime, default=datetime.now())
    description = Column(String(150), nullable=False)
    done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    tags = relationship("Tag", secondary=note_m2m_tag, back_populates="notes", cascade="all, delete")


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {'sqlite_autoincrement': True} 
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, unique=True)
    notes = relationship("Note", secondary=note_m2m_tag, back_populates="tags", cascade="all, delete")

    def __repr__(self) -> str:
        return self.name


class Address_book(Base):
    __tablename__= "addressbook"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    records = relationship("Record", cascade="all, delete", backref="book")

class Record(Base):
    __tablename__= "record"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    birthday = relationship("Birthday", cascade="all, delete", backref="user", uselist=False)
    phones = relationship("Phone", cascade="all, delete", backref="user")
    addresses = relationship("Address", cascade="all, delete", backref="user")
    emails = relationship("Email", cascade="all, delete", backref="user")
    book_id = Column(Integer, ForeignKey(Address_book.id, ondelete="CASCADE"))

class File(Base):
    __tablename__ = "file"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    file_name = Column(String(50), nullable=False, unique=True)

class Birthday(Base):
    __tablename__= "birthday"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    bd_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey(Record.id, ondelete="CASCADE"))

class Phone(Base):
    __tablename__= "phone"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)
    user_id = Column(Integer, ForeignKey(Record.id, ondelete="CASCADE"))

class Address(Base):
    __tablename__= "address"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey(Record.id, ondelete="CASCADE"))

class Email(Base):
    __tablename__= "email"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey(Record.id, ondelete="CASCADE"))


if __name__ == "__main__":
    Base.metadata.create_all(engine)