#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ckan.plugins.toolkit as toolkit
from ckan.logic.schema import update_configuration_schema
import logging
log = logging.getLogger(__name__)


@toolkit.side_effect_free
def config_option_list(context, data_dict):
    ''' Does the same as the original call but returns the result sorted by key.
    '''

    toolkit.check_access('config_option_list', context, data_dict)

    schema = update_configuration_schema()

    result = schema.keys()
    result.sort()
    return result
