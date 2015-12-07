==================
Waff Only Features
==================

Waff is a feature flagger based upon Waffle. It introduces a single additional
capability to those found within Waffle: it works with "stateless" websites and
those without a "conventional" database backend. Three arbitrary "buckets" are
used for specifying flags: ALPHA, BETA and ALL. The buckets are defined by
environment variables (so no code change is needed to re-configure such
settings - just a simple re-specification of the environment variables and a
restart is required).

Why?
====

People want to use feature flags and Waffle is wonderful. Not all websites are
"typical" in that they use a database that works with Django's ORM for storing
state. Waff solves this problem with some opinionated configurations.

How?
====

There are three arbitrary buckets: ALPHA, BETA and ALL.

ALPHA and BETA have named users associated with them and flags set for each
bucket will only be active for those users.

ALL related flags apply to all users.

The choice of arbitrary bucket names was made to reflect the common pattern of
rolling out a feature first in "alpha", then "beta" and then to "all" users.

It is assumed that once a feature has been around long enough and there's no
requirement for it to be on/off at short notice, then the flag related code
should be removed from this feature.

We use the following environment variables for specifying flag/user state:

* `WAFF_USE_ENV_VARS`_ - a simple truthy flag to indicate that Waff should use the environment variables instead of the database when checking if a `flag_is_active`_.
* `WAFF_ALPHA_USERS`_ - a comma separated list of usernames for those in the ALPHA bucket (the stateless Django app will need to implement a faux-request.user.username to identify the individual users).
* `WAFF_BETA_USERS`_ - as with WAFFLE_ALPHA_USERS but for BETA users.
* `WAFF_ALPHA_FLAGS`_ - a comma separated list of flags in the ALPHA bucket.
* `WAFF_BETA_FLAGS`_ - a comma separated list of flags in the BETA bucket.
* `WAFF_ALL_FLAGS`_ - a comma separated list of flags in the ALL bucket.
