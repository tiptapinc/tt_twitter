## v0.0.13
* replace .iteritems method with .items (python 3 fix)

## v0.0.12
* added support for python 3

## v0.0.11:
* pass **kwargs to get_user_timeline
* set 'tweet_mode' to 'extended' in get_user_timeline

## v0.0.10
* create new Twython instance for every call

## v0.0.9
* fix error handling for _do_twitter unexpected error condition

## v0.0.8
* set requests timeout when initializing Twython

## v0.0.7
* added **kwargs to arguments for "get_followers_ids"

## v0.0.6
* added "limit" field to return value from "get_rate_limits"

## v0.0.5
* added "search" method

## v0.0.4

* lookup_user can have both user_id & screen_name parameters in a single call

## v0.0.3

* reset "remaining" rate limit when window expires


##v0.0.2

* cleaned up log messages


## v0.0.1:

* Initial release
