import sqlite3
import web
from web.wsgiserver import CherryPyWSGIServer as serv

serv.ssl_certificate = "../CA/server.crt"
serv.ssl_private_key = "../CA/server.key"

urls = (
    "/key", "key",
    "/.*", "hello",
    )

app = web.application(urls, globals())

class helloworld:
    def GET(self):
        return "Hello, world!"

class key:
    def GET(self):
        conn = sqlite3.connect('brokerdb')
        c = conn.cursor()
        uuid = web.input(uuid="No UUID")['uuid']

        working_src = web.ctx['ip']
        print "Got working IP %s" % working_src

        XFWD = web.ctx.env.get('X-FORWARD-FOR')
        if XFWD:
            working_src = XFWD

        # According to https://docs.python.org/2/library/sqlite3.html
        # This is the safe way to handle parameters
        params = (working_src, uuid,)
        c.execute("SELECT * FROM mapping where ip=? AND uuid=?",params)
        entry = c.fetchone()
        assert c.fetchone() == None

        c.close()
        if entry:
            return entry[2]  # Relies on schema+ordering being correct
        else:
            print "Request from %s uuid %s: no key found" % (working_src, uuid)
            return app.notfound()

if __name__ == "__main__":
    app.run()
