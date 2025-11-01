# do not pre-load
import datetime
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from docassemble.base.util import Thing, as_datetime
from docassemble.base.sql import alchemy_url, connect_args, upgrade_db, SQLObject

__all__ = ['Birthday']

Base = declarative_base()


class BirthdayModel(Base):
    __tablename__ = 'birthday'
    id = Column(Integer, primary_key=True)
    dob = Column(Date)
    name = Column(String(250), unique=True)

url = alchemy_url('demo db')

conn_args = connect_args('demo db')
if url.startswith('postgres'):
    engine = create_engine(url, connect_args=conn_args, pool_pre_ping=False)
else:
    engine = create_engine(url, pool_pre_ping=False)

Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)()

upgrade_db(url, __file__, engine, version_table='auto', conn_args=conn_args)


class Birthday(Thing, SQLObject):
    _model = BirthdayModel
    _session = DBSession
    _required = ['name', 'dob']
    _uid = 'name'

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # This runs necessary SQLObject initialization code for the instance
        self.sql_init()

    def db_get(self, column):
        if column == 'name':
            return self.name.text
        if column == 'dob':
            return datetime.date(self.dob.year, self.dob.month, self.dob.day)
        raise Exception("Invalid column " + column)

    def db_set(self, column, value):
        if column == 'name':
            self.name.text = value
        elif column == 'dob':
            self.dob = as_datetime(value)
        else:
            raise Exception("Invalid column " + column)

    def db_null(self, column):
        if column == 'name':
            del self.name.text
        elif column == 'dob':
            del self.dob
        else:
            raise Exception("Invalid column " + column)
