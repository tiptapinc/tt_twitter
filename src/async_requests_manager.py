#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2014 tiptap. All rights reserved.

"""
import time
import tornado.httpclient
import tornado.ioloop

import logging
log = logging.getLogger(__name__)


RESEND_INTERVAL = 60
MAX_SENDS = 3


class AsyncRequestsManager(object):
    """
    Manages asynchronous requests in Tornado framework
    """
    def __init__(self, maxOutstanding):
        self.maxOutstanding = maxOutstanding
        self.outstanding = {}
        self.pending = []

        self.heartbeatTimer = tornado.ioloop.PeriodicCallback(
            self._heartbeat,
            5 * 1000
        )
        self.heartbeatTimer.start()

    def _heartbeat(self):
        now = time.time()
        for request in self.outstanding.keys():
            outstanding = self.outstanding[request]
            if outstanding['lastSendTime'] + RESEND_INTERVAL < now:
                if outstanding['sendCount'] >= MAX_SENDS:
                    log.info(
                        "callback to %s expired - too many retries" %
                        request.url
                    )
                    self.outstanding.pop(request)
                else:
                    log.info(
                        "retrying callback to %s" %
                        request.url
                    )
                    self._send(request)

        self._send_pending()

    def initiate(self, request):
        self.pending.append(request)
        self._send_pending()

    def _send_pending(self):
        while (
            len(self.pending) > 0 and
            len(self.outstanding) < self.maxOutstanding
        ):
            request = self.pending.pop()
            self.outstanding[request] = dict(sendCount=0)
            self._send(request)

    def _send(self, request):
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(request, self._request_complete)
        self.outstanding[request]['sendCount'] += 1
        self.outstanding[request]['lastSendTime'] = time.time()

    def _request_complete(self, response):
        log.info(
            "completed async request to %s with response %s" %
            (response.request.url, response.code)
        )
        if response.code < 400:
            self.outstanding.pop(response.request, None)
            self._send_pending()
