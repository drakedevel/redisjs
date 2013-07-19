import json
import logging
import os
import sys
import threading

import redis
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import Application, RedirectHandler, RequestHandler, asynchronous

manager = None

class RedisSubscriptionWorker(threading.Thread):
    def __init__(self, conn, channel):
        super(RedisSubscriptionWorker, self).__init__()
        self._callbacks = []
        self._callbacks_lock = threading.Lock()
        self._pubsub = conn.pubsub()
        self._pubsub.subscribe(channel)
        self.setDaemon(True)

    def get_messages(self, callback):
        with self._callbacks_lock:
            self._callbacks.append(callback)

    def run(self):
        while True:
            for message in self._pubsub.listen():
                logging.info("Got pubsub message %s", message)
                with self._callbacks_lock:
                    callbacks = list(self._callbacks)
                for cb in callbacks:
                    IOLoop.instance().add_callback(lambda: cb(message))

class RedisSubscriptionManager(object):
    def __init__(self):
        self._channels = {}
        self._redis = redis.Redis()

    def get_messages(self, channel, callback):
        if channel not in self._channels:
            self._channels[channel] = RedisSubscriptionWorker(self._redis, channel)
            self._channels[channel].start()
        self._channels[channel].get_messages(callback)

class SubscribeHandler(RequestHandler):
    @asynchronous
    @gen.engine
    def get(self, channel):
        def on_result(message):
            logging.info("Writing results to client: %s", message)
            self.write("%s\n" % (json.dumps({ 'channel': message['channel'],
                                              'data': message['data'] })))
            self.flush()
        manager.get_messages(channel, on_result)

def main():
    global manager
    manager = RedisSubscriptionManager()

    logging.basicConfig(level=logging.INFO)
    app = Application([
            (r'/', RedirectHandler, { 'url': '/static/index.htm' }),
            (r'/subscribe/(.+)', SubscribeHandler),
            ],
            debug=True,
            static_path=os.path.join(os.path.dirname(sys.argv[0]), 'static'))
    app.listen(8080)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
