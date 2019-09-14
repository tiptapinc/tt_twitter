#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2014 tiptap. All rights reserved.

"""
import time
import traceback
import twython

import logging
log = logging.getLogger(__name__)

RATE_LIMIT_RESOURCES = ["statuses", "followers", "search", "users"]


class TwitterClient(object):
    def __init__(self, appKey, accessToken, margins):
        self.appKey = appKey
        self.accessToken = accessToken

        self.twitter = twython.Twython(
            self.appKey,
            access_token=self.accessToken,
            client_args=dict(timeout=30)
        )
        self._init_rate_limits(margins)

    def get_user_timeline(self, twitterId, twitterName, **kwargs):
        params = {k: v for k, v in kwargs.iteritems() if v}

        params['count'] = params.get('count') or 200
        params['include_rts'] = "false"
        params['tweet_mode'] = "extended"

        if twitterId:
            params['user_id'] = twitterId
        elif twitterName:
            params['screen_name'] = twitterName
        else:
            log.info("get_user_timeline needs twitterId or twitterName")

        log.info("get_user_timeline, params: %s" % params)
        return self._do_twitter(
            "get_user_timeline",
            "statuses",
            "user_timeline",
            **params
        )

    def get_followers_ids(self, twitterName, count, **kwargs):
        params = dict(
            screen_name=twitterName,
            count=count
        )
        params.update(kwargs)

        log.info("get_followers_ids, params: %s" % params)
        return self._do_twitter(
            "get_followers_ids",
            "followers",
            "ids",
            **params
        )

    def lookup_user(self, twitterIds, twitterNames):
        params = {}
        if twitterIds:
            params['user_id'] = ",".join(twitterIds)

        if twitterNames:
            params['screen_name'] = ",".join(twitterNames)

        if not twitterIds and not twitterNames:
            log.info("lookup_user needs twitterIds or twitterNames")

        log.info("lookup_users, params: %s" % params)
        return self._do_twitter(
            "lookup_user",
            "users",
            "lookup",
            **params
        )

    def show_user(self, twitterId, twitterName):
        if twitterId:
            params = dict(user_id=twitterId)
        elif twitterName:
            params = dict(screen_name=twitterName)
        else:
            log.info("show_user needs twitterId or twitterName")

        log.info("show_users, params: %s" % params)
        return self._do_twitter(
            "show_user",
            "users",
            "show",
            **params
        )

    def search(self, query, **kwargs):
        params = dict(q=query)
        params.update(kwargs)

        log.info("search, params: %s" % params)
        return self._do_twitter(
            "search",
            "search",
            "tweets",
            **params
        )

    def _do_twitter(self, functionName, resource, method, **params):
        if self.limits[resource][method]['remaining'] <= 0:
            return 429, None

        apiClient = twython.Twython(
            app_key=self.appKey,
            access_token=self.accessToken,
            client_args=dict(timeout=30)
        )

        function = getattr(apiClient, functionName)
        result = None

        try:
            result = function(**params)
            resultCode = 200

        except twython.TwythonRateLimitError as error:
            self._hit_rate_limit(resource, method)
            resultCode = error.error_code

        except (twython.TwythonError, twython.TwythonAuthError) as error:
            log.info("Twitter error: %s" % error.msg)
            resultCode = error.error_code

        except:
            log.error(
                "unexpected error accessing Twitter API, %s" %
                traceback.format_exc()
            )

        self._update_rate_limit(apiClient, resource, method)
        return resultCode, result

    def get_rate_limits(self, resource, method):
        limits = self.limits[resource][method]

        if time.time() > limits['reset'] + self.timeMargin:
            limits['remaining'] = limits['limit']

        return dict(
            remaining=(limits['remaining'] - self.countMargin),
            reset=(limits['reset'] + self.timeMargin),
            limit=limits['limit']
        )

    def _init_rate_limits(self, margins):
        apiClient = twython.Twython(
            app_key=self.appKey,
            access_token=self.accessToken,
            client_args=dict(timeout=30)
        )

        params = dict(resources=",".join(RATE_LIMIT_RESOURCES))
        body = apiClient.get_application_rate_limit_status(**params)

        self.limits = {}
        for resource in body['resources'].keys():
            self.limits[resource] = {}
            for location in body['resources'][resource]:
                method = location.split('/')[2]
                methodLimits = body['resources'][resource][location]
                self.limits[resource][method] = dict(
                    remaining=methodLimits['remaining'],
                    reset=methodLimits['reset'],
                    limit=methodLimits['limit']
                )

        self.timeMargin = margins['timeMargin']
        self.countMargin = margins['countMargin']

    def _update_rate_limit(self, apiClient, resource, method):
        limits = self.limits[resource][method]
        header = apiClient.get_lastfunction_header(
            'x-rate-limit-remaining'
        )
        if header:
            limits['remaining'] = int(header)

        header = apiClient.get_lastfunction_header(
            'x-rate-limit-reset'
        )
        if header:
            limits['reset'] = int(header)

        remainingTime = limits['reset'] - time.time()
        log.info(
            "window remaining: %s calls, %d seconds" %
            (limits['remaining'], remainingTime)
        )

    def _hit_rate_limit(self, resource, method):
        log.warning("Pissed off Twitter!  Rate limit (429) response")
        self.limits[resource][method]['remaining'] = 0
