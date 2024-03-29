from __future__ import unicode_literals

from decimal import Decimal
import random
import os

from waff.utils import get_setting, keyfmt


VERSION = (0, 11)
__version__ = '.'.join(map(str, VERSION))


def parse_env_vars(var_name):
    """
    Takes the name of an environment variable that should be expressed as a
    comma separated list of items. Returns the equivalent Python data
    structure.
    """
    value = os.getenv(var_name, '')
    if value:
        return [x for x in value.split(',') if x]
    return []

"""
We default the settings derived from environment vars so the app can't break
when it's started because we've forgotton to configure something. Rather, it'll
just assume an 'all flags off' policy.

There are three arbitrary buckets: ALPHA, BETA and ALL. ALPHA and BETA have
named users associated with them and flags set for each bucket will only be
active for those users. ALL related flags apply to all users.
"""
USE_ENV_VARS = os.getenv('WAFF_USE_ENV_VARS', True)
if USE_ENV_VARS:
    ALPHA_USERS = parse_env_vars('WAFF_ALPHA_USERS')
    BETA_USERS = parse_env_vars('WAFF_BETA_USERS')
    ALPHA_FLAGS = parse_env_vars('WAFF_ALPHA_FLAGS')
    BETA_FLAGS = parse_env_vars('WAFF_BETA_FLAGS')
    ALL_FLAGS = parse_env_vars('WAFF_ALL_FLAGS')
    SWITCHES = parse_env_vars('WAFF_SWITCHES')
    SAMPLES = parse_env_vars('WAFF_SAMPLES')


class DoesNotExist(object):
    """The record does not exist."""
    @property
    def active(self):
        return get_setting('SWITCH_DEFAULT')


def set_flag(request, flag_name, active=True, session_only=False):
    """Set a flag value on a request object."""
    if not hasattr(request, 'waffles'):
        request.waffles = {}
    request.waffles[flag_name] = [active, session_only]


def flag_is_active(request, flag_name):
    """
    Given the context of the request, indicate if the flag identified by the
    flag_name is active.

    This wraps two functions that use either the "normal" database method or
    one based upon environment variables.
    """
    if USE_ENV_VARS:
        return flag_is_active_from_env(request, flag_name)
    return flag_is_active_from_database(request, flag_name)


def flag_is_active_from_env(request, flag_name):
    """
    A flag_name indicates that a referenced feature is active. The boolean
    response depends on several things:

    * The flag group the flag_name is found in.
    * The membership of associated user buckets for the requesting user.

    There are three flag groups: ALPHA, BETA and ALL. The ALPHA and BETA flag
    groups refer to associated user buckets. ALL flags are applied to all
    users.

    Ergo, flags are explicitly set for ALPHA and BETA but flags set in ALL are
    universal. For example, a flag called 'foo' set in the ALPHA_FLAGS group
    will only be seen by members of the ALPHA_USERS bucket. However, if a flag
    'bar' is set in the ALL_FLAGS group ALL users will see it.
    """
    # Check there are flags set via the environment variables.
    if not (ALPHA_FLAGS or BETA_FLAGS or ALL_FLAGS):
        return False
    # If the flag is an ALL flag, it's on for everyone!
    if ALL_FLAGS and flag_name in ALL_FLAGS:
        return True
    # User may not be logged in.
    if hasattr(request, 'user'):
        username = request.user.username
        # Arbitrary decision that ALPHA takes precedence.
        if ALPHA_FLAGS and flag_name in ALPHA_FLAGS:
            return username in ALPHA_USERS
        elif BETA_FLAGS and flag_name in BETA_FLAGS:
            return username in BETA_USERS
    return False


def flag_is_active_from_database(request, flag_name):
    """
    A regular waffle.
    """
    from .models import cache_flag, Flag
    from .compat import cache

    flag = cache.get(keyfmt(get_setting('FLAG_CACHE_KEY'), flag_name))
    if flag is None:
        try:
            flag = Flag.objects.get(name=flag_name)
            cache_flag(instance=flag)
        except Flag.DoesNotExist:
            return get_setting('FLAG_DEFAULT')

    if get_setting('OVERRIDE'):
        if flag_name in request.GET:
            return request.GET[flag_name] == '1'

    if flag.everyone:
        return True
    elif flag.everyone is False:
        return False

    if flag.testing:  # Testing mode is on.
        tc = get_setting('TEST_COOKIE') % flag_name
        if tc in request.GET:
            on = request.GET[tc] == '1'
            if not hasattr(request, 'waffle_tests'):
                request.waffle_tests = {}
            request.waffle_tests[flag_name] = on
            return on
        if tc in request.COOKIES:
            return request.COOKIES[tc] == 'True'

    user = request.user

    if flag.authenticated and user.is_authenticated():
        return True

    if flag.staff and user.is_staff:
        return True

    if flag.superusers and user.is_superuser:
        return True

    if flag.languages:
        languages = flag.languages.split(',')
        if (hasattr(request, 'LANGUAGE_CODE') and
                request.LANGUAGE_CODE in languages):
            return True

    flag_users = cache.get(keyfmt(get_setting('FLAG_USERS_CACHE_KEY'),
                                              flag.name))
    if flag_users is None:
        flag_users = flag.users.all()
        cache_flag(instance=flag)
    if user in flag_users:
        return True

    flag_groups = cache.get(keyfmt(get_setting('FLAG_GROUPS_CACHE_KEY'),
                                   flag.name))
    if flag_groups is None:
        flag_groups = flag.groups.all()
        cache_flag(instance=flag)
    user_groups = user.groups.all()
    for group in flag_groups:
        if group in user_groups:
            return True

    if flag.percent and flag.percent > 0:
        if not hasattr(request, 'waffles'):
            request.waffles = {}
        elif flag_name in request.waffles:
            return request.waffles[flag_name][0]

        cookie = get_setting('COOKIE') % flag_name
        if cookie in request.COOKIES:
            flag_active = (request.COOKIES[cookie] == 'True')
            set_flag(request, flag_name, flag_active, flag.rollout)
            return flag_active

        if Decimal(str(random.uniform(0, 100))) <= flag.percent:
            set_flag(request, flag_name, True, flag.rollout)
            return True
        set_flag(request, flag_name, False, flag.rollout)

    return False


def switch_is_active(switch_name):
    from .models import cache_switch, Switch
    from .compat import cache

    switch = cache.get(keyfmt(get_setting('SWITCH_CACHE_KEY'), switch_name))
    if switch is None:
        try:
            switch = Switch.objects.get(name=switch_name)
            cache_switch(instance=switch)
        except Switch.DoesNotExist:
            switch = DoesNotExist()
            switch.name = switch_name
            cache_switch(instance=switch)
    return switch.active


def sample_is_active(sample_name):
    from .models import cache_sample, Sample
    from .compat import cache

    sample = cache.get(keyfmt(get_setting('SAMPLE_CACHE_KEY'), sample_name))
    if sample is None:
        try:
            sample = Sample.objects.get(name=sample_name)
            cache_sample(instance=sample)
        except Sample.DoesNotExist:
            return get_setting('SAMPLE_DEFAULT')

    return Decimal(str(random.uniform(0, 100))) <= sample.percent
