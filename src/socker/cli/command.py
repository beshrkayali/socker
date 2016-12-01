"""
Start the socker websocket server

Usage:
  socker [options]
  socker -? | --help
  socker --version

Options:
  -i INTERFACE    Listening interface [default: localhost]
  -p PORT         Listening port [default: 8765]

  -v              Enable verbose output

  --auth-backend=PATH           Auth backend path
                                [default: socker.auth:default_backend]

  --redis-host=HOST             Redis host [default: localhost]
  --redis-port=PORT             Redis port [default: 6379]
  --redis-db=DB                 Redis database [default: 0]
  --redis-password=PASSWORD     Redis password

  --ssl-certfile=PATH           Path to cert file (Enable secure websocket)
  --ssl-pkeyfile=PATH           Path to pkey file

  --logto FILE    Log output to FILE instead of console

  --version       show version
  -? --help       Show this screen

"""
import asyncio
import logging
import signal
from docopt import docopt

from . import log
from .. import server
from ..version import __version__
import ssl

logger = logging.getLogger(__name__)


class Interface(object):

    def __init__(self):
        self.opts = docopt(__doc__, version='socker v{}'.format(__version__))
        self.setup_logging()
        self.register_signals()
        self.start()

    def setup_logging(self):
        filename = self.opts['--logto']
        verbose = self.opts['-v']
        log.configure(filename, verbose)

    def register_signals(self):
        # 1; Reload
        signal.signal(signal.SIGHUP, lambda *args: self.reload())
        # 2; Interrupt, ctrl-c
        signal.signal(signal.SIGINT, lambda *args: self.abort())
        # 15; Stop
        signal.signal(signal.SIGTERM, lambda *args: self.stop())

    def start(self):
        additional_opts = {k.replace('--', '').replace('-', '_'): v
                           for k, v in self.opts.items()
                           if '--redis-' in k}

        for key in ['redis_port', 'redis_db']:  # Integer arguments
            additional_opts[key] = int(additional_opts[key])

        if self.opts.get('--ssl-certfile'):
            certfile_path = self.opts['--ssl-certfile']
            keyfile_path = self.opts['--ssl-pkeyfile']

            c = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            c.load_cert_chain(certfile=certfile_path, keyfile=keyfile_path)
            additional_opts['ssl'] = c

        server.main(
            interface=self.opts['-i'],
            port=int(self.opts['-p']),
            debug=self.opts['-v'],
            auth_backend=self.opts['--auth-backend'],
            **additional_opts)

    def reload(self):
        logger.warn('--- SIGHUP ---')
        pass  # TODO: Implement

    def abort(self):
        logger.warn('--- SIGINT ---')
        self.safe_quit()

    def stop(self):
        logger.warn('--- SIGTERM ---')
        # Cold exit.
        self.quit()

    def safe_quit(self):
        # TODO: Implement safer way to exit
        logger.info('Closing event loop...')
        asyncio.get_event_loop().stop()

    @staticmethod
    def quit(exit_code=0):
        logger.debug('Pending tasks at exit: %s',
                     asyncio.Task.all_tasks(asyncio.get_event_loop()))
        logger.info('Bye!')
        exit(exit_code)
