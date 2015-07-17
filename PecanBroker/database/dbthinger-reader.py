from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

##from sqlalchemy.ext.declarative import declarative_base

from dbmodel import Server, Volume

#engine = create_engine('sqlite:///sqlalchemy_example.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
#Base.metadata.bind = engine
##Base = declarative_base()

engine = create_engine('sqlite:///sqlalchemy_example.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()

server = session.query(Server).filter(Server.ip=='127.0.0.1').one()
vols = session.query(Volume).filter(Volume.server_id == server.id).filter(Volume.uuid=='aa-bb-cc-dd-01')
for v in vols:
    print v
