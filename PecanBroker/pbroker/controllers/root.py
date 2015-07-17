import pecan
import logging

from pecan import rest, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database.dbmodel import Server, Volume

logger = logging.getLogger(__name__)

engine = create_engine(pecan.conf.database['engine'])
DBSession = sessionmaker(bind=engine)
session = DBSession()

class RegistrationController(rest.RestController):
    @pecan.expose(content_type="text/plain")
    def post(self):
        if not pecan.conf.app['registrationmode']:
            logger.warning("Registration requested when not enabled.")
            abort(404)

        registrationkey = pecan.request.POST.get("registrationkey")
        if registrationkey != pecan.conf.app['registrationkey']:
            logger.warning("registrationkey not provided")
            abort(404)

        required = ['addr','uuid','keymat']
        for req in required:
            if req not in pecan.request.POST:
                logger.error("Missing %s from POST data" % req)
                abort(404)

        # A host can register other server, so we get the addr from it's
        # POST request rather than from it's source addr (this plays better
        # with web proxies too).
        _addr = pecan.request.POST.get("addr")
        _uuid = pecan.request.POST.get("uuid")
        _keymaterial = pecan.request.POST.get("keymat")

        volume = Volume(uuid=_uuid, keymaterial=_keymaterial)
        session.add(volume)

        try:
            server = session.query(Server).filter(Server.ip==_addr).one()
            logger.debug("Found server with address %s" % _addr)
        except NoResultFound, e:
            server = Server(ip=_addr)
            #session.add(server)
            logger.debug("Created a server with address %s" % _addr)

        server.volumes.append(volume)
        session.add(server)

        session.commit()
        session.close()

        return

class KeyController(rest.RestController):
    @pecan.expose(content_type="text/plain")
    def get(self):
        uuid = pecan.request.GET.get('uuid')
        addr = pecan.request.remote_addr
        #XXX: Arggggg.
        #This allows the broker to positioned behind a TLS Load Balancer
        #However, I'm concerned that it could be abused in some configurations
        #Allowing some host to request key material for another host
        #Though that would still require the attacker to know a valid disk UUID
        if 'X-Forwarded-For' in pecan.request.headers:
                addr = pecan.request.headers['X-Forwarded-For']

        try:
            server = session.query(Server).filter(Server.ip==addr).one()
        except NoResultFound, e:
            logger.warning("%s not found inDB" % addr)
            abort(404)

        try:
            vol = session.query(Volume).filter(Volume.server_id == server.id).filter(Volume.uuid==uuid).one()
        except NoResultFound, e:
            logger.warning("%s requested %s but no match in DB" % (addr,uuid))
            abort(404)

        return vol.keymaterial

class RootController(object):
    key = KeyController()
    registration = RegistrationController()
