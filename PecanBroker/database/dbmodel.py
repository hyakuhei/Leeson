from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, func, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import datetime,sys

Base = declarative_base()

class Server(Base):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    ip = Column(String, nullable=False, unique=True)
    volumes = relationship("Volume", backref='server')

    def __str__(self):
        return "Server %s has %i volumes" % (self.ip,len(self.volumes))

class Volume(Base):
    __tablename__ = 'volume'
    id = Column(Integer,primary_key=True)
    uuid = Column(String,nullable=False, unique=True)
    keymaterial = Column(String,nullable=False, unique=True)
    server_id = Column(Integer, ForeignKey('server.id'))

    def __str__(self):
        return "UUID: '%s' - Key: '%s'" % (self.uuid,self.keymaterial)

class AuditType(Base):
    __tablename__ = 'audittype'
    id = Column(Integer, primary_key=True)
    text = Column(String)

class AuditItem(Base):
    __tablename__ = 'audit'
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime(timezone=False), default=func.now())
    volume_id = Column(Integer, ForeignKey('volume.id'))
    audittype_id = Column(Integer, ForeignKey('audittype.id'))

if __name__ == "__main__":
    print "===Creating a database for key management==="
    print """
        Running this script directly will create a database schema
        and populate it with some test information including a few servers
        and assign multiple volumes to each server.

        importing this module into applications will allow them to read the
        database using sqlalchemy
        """

    #TODO: Make databse location a configuration item
    engine = create_engine('sqlite:///pbroker.db')
    DBSession = sessionmaker()
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    session = DBSession()

    vol1 = Volume(uuid='aa-bb-cc-dd-01', keymaterial='DEADBEEF')
    vol2 = Volume(uuid='aa-bb-cc-dd-02', keymaterial='CAFEBABE')
    vol3 = Volume(uuid='aa-bb-cc-dd-03', keymaterial='33333333')
    vol4 = Volume(uuid='aa-bb-cc-dd-04', keymaterial='44444444')
    vol5 = Volume(uuid='aa-bb-cc-dd-05', keymaterial='BEEFCA4E')

    session.add(vol1)
    session.add(vol2)
    session.add(vol3)
    session.add(vol4)
    session.add(vol5)
    session.commit()

    # Insert an Address in the address table
    s1 = Server(ip='127.0.0.1',volumes=[vol1,vol2])
    s2 = Server(ip='127.0.0.2',volumes=[vol3,vol4,vol5])

    session.add(s1)
    session.add(s2)
    session.commit()

    for ip in ['127.0.0.1', '127.0.0.2']:
        server = session.query(Server).filter(Server.ip == ip).one()
        print server
        vols = session.query(Volume).filter(Volume.server_id == server.id)
        for v in vols:
            print v
        print "\n"

    session.close()
