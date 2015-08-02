# encoding: utf-8
import os
from gevent import monkey; monkey.patch_all()
from base import app


if __name__ == '__main__':
    import werkzeug.serving
    from gevent.wsgi import WSGIServer

    from werkzeug.debug import DebuggedApplication
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    @werkzeug.serving.run_with_reloader
    def run():
        app.debug = True
        dapp = DebuggedApplication(app, evalex=True)
        http_server = WSGIServer(('', 5000), dapp)
        http_server.serve_forever()

    run()