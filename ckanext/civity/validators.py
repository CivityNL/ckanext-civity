# -*- coding: utf-8 -*-

import re
from ckan.plugins.toolkit import Invalid, _, missing
import logging
import ckan.logic as logic
from ckan.lib.navl.dictization_functions import StopOnError
import json

log = logging.getLogger(__name__)


def url_checker(key, data, errors, context):
    url = data.get(key, None)

    if url:
        # DJango Regular Expression to check URLs
        regex = re.compile(
            r'^https?://'  # scheme is validated separately
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if regex.match(url) is None:
            errors[key].append(_('The URL "%s" is not valid.') % url)


def custom_url_resource_validator(key, data, errors, context):
    # TODO check if this library would be helpfull https://github.com/includesecurity/safeurl-python
    # Internal RFC1918 private addresses should be blocked,
    # as well as IPv4/IPv6 loopback addresses like localhost, 127.0.0.1 and ::1

    ''' Checks that the provided value (if it is present) is a valid URL '''
    ''' Blacklists local networks and IPv4/IPv6 loopback addresses '''

    import urlparse
    import string
    import re

    # log.info('key = {0}'.format(key))
    # log.info('data = {0}'.format(data))
    url = data.get(key, None)
    # log.info('URL = {0}'.format(url))
    if not url:
        return

    pieces = urlparse.urlparse(url)

    # For Development reasons both the url_blacklist and rfc1918_pattern were altered
    # The commented code represents the original and secure restrictions.

    url_blacklist = []

    rfc1918_pattern = re.compile("^(?:10|127|172\.(?:1[6-9]|2[0-9]|3[01])|193\.168)\..*")

    valid_netloc = True

    if pieces.netloc:
        if any(word in pieces.netloc for word in url_blacklist) or rfc1918_pattern.match(pieces.netloc):
            valid_netloc = False
            log.info('valid_netloc = {0}'.format(valid_netloc))
    else:
        if any(word in pieces.path for word in url_blacklist) or rfc1918_pattern.match(pieces.path):
            valid_netloc = False
            log.info('valid_netloc = {0}'.format(valid_netloc))

    if all([pieces.scheme, pieces.netloc]) and \
            set(pieces.netloc) <= set(string.letters + string.digits + '-.:') and \
            pieces.scheme in ['http', 'https', 'ftp'] and \
            valid_netloc:
        return

    # is a File Upload
    if valid_netloc and ":" not in url:
        return

    raise Invalid("Please provide a valid URL")


def non_empty_org_validator(key, data, errors, context):
    # data[('id',)] holds the previous value of the URL, while
    # data[('name',)] the new value that is going to be applied.
    # The validation here is to check these two values are not equal, if the organization does contain any datasets and if the user is not a sysadmin.
    # if yes, don't update organization data and flash user an 'invalid' message.

    def org_not_empty(org_id):
        # check if organization contains datasets
        organization_dict = logic.get_action(u'organization_show')(context, {u'id': org_id})
        org_datasets = organization_dict.get('package_count')
        if org_datasets != 0:
            return True
        else:
            return False

    # check if sysadmin rights
    is_sysadmin = context['auth_user_obj'].sysadmin
    current_org_id = data.get(('id',))
    new_org_id = data.get(('name',))
    # check if URL has changed
    org_id_changed = current_org_id != new_org_id

    if org_id_changed and org_not_empty(current_org_id) and not is_sysadmin:
        raise Invalid(_('You cannot change the URL of an organization containing datasets'))
    return


def ignore_missing_but_allow_empty(key, data, errors, context):
    '''If the key is missing from the data, ignore the rest of the key's
    schema.

    By putting ignore_missing at the start of the schema list for a key,
    you can allow users to post a dict without the key and the dict will pass
    validation. But if they post a dict that does contain the key, then any
    validators after ignore_missing in the key's schema list will be applied.

    :raises ckan.lib.navl.dictization_functions.StopOnError: if ``data[key]``
        is :py:data:`ckan.lib.navl.dictization_functions.missing` or ``None``

    :returns: ``None``

    '''
    value = data.get(key)

    if value is missing:
        data.pop(key, None)
        raise StopOnError
