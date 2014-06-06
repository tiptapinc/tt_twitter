import json

from src import TwitterClient

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - "
           "%(message)s - [%(name)s:%(funcName)s]"
)
log = logging.getLogger(__name__)

margins = dict(timeMargin=3, countMargin=2)
tc = TwitterClient("GPJQs1Wc0giwiq79COe11tUMc", "AAAAAAAAAAAAAAAAAAAAAAOnXAAAAAAASZNnmrS1An3JOfWFkK2W8smLlow%3DZqKAvffXe3nn3cpFxCyed0M0oF2DYX3Ki3tbYUu6dfUeg6FA3y", margins)

resultCode, page = tc.get_user_timeline(None, "FgsFrank")
print json.dumps(page, indent=4)

resultCode, page = tc.get_user_timeline(None, "itsadivathingx")
print json.dumps(page[:2], indent=4)

resultCode, response = tc.show_user(None, "itsadivathingx")
print "show_user", json.dumps(response, indent=4)

resultCode, response = tc.get_followers_ids("burberry", 10)
print "followers_ids", json.dumps(response)

followersIds = [str(id) for id in response['ids']]
resultCode, response = tc.lookup_user(followersIds, None)

print "list_user", json.dumps(response, indent=4)
