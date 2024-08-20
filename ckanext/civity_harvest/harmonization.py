#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

log = logging.getLogger(__name__)

FIELDS_NOT_IN_SCHEMA = {
    'dataset_fields': [
        {
            'field_name': 'id',
            'harmonized_field_name': 'id'
        },
        {
            'field_name': 'metadata_created',
            'harmonized_field_name': 'metadata_created'
        },
        {
            'field_name': 'metadata_modified',
            'harmonized_field_name': 'metadata_modified'
        },
        {
            'field_name': 'type',
            'harmonized_field_name': 'type'
        },
        {
            'field_name': 'state',
            'harmonized_field_name': 'state'
        }
    ],
    'resource_fields': [
        {
            'field_name': 'id',
            'harmonized_field_name': 'id'
        },
        {
            'field_name': 'package_id',
            'harmonized_field_name': 'package_id'
        },
        {
            'field_name': 'metadata_created',
            'harmonized_field_name': 'metadata_created'
        },
        {
            'field_name': 'metadata_modified',
            'harmonized_field_name': 'metadata_modified'
        },
        {
            'field_name': 'state',
            'harmonized_field_name': 'state'
        }
    ]
}


# HARMONIZE

def harmonize_package_fields(mapping_schema, pkg_dict):
    '''
    Transforms a pkg_dict into an harmonized version of it.

    :param mapping_schema : ckanext-scheming schema for the package type
    :param pkg_dict

    :return harmonized pkg_dict
    '''
    # Questions:
    #   If there is no "harmonized field" should it be included or not?
    #     Should there be an param to enable/disable these

    # TODO add fields not present in schema
    # fields_in_schema_that_should_not_be_visible = ["tag_string" (needs adjustment) "owner_org" (convert to dict)]
    # fields_not_in_schema_that_should_be_visible = [
    #     {"name": "metadata_created", "label": {"en": "Metadata Created", "nl": "Gecreëerd"}},
    #     {"name": "metadata_modified", "label": {"en": "Metadata Modified", "nl": "Laatst gewijzigd"}},
    #     {"name": "license_title", "label": {"en": "License", "nl": "Licentie"}},
    # ]

    pkg_harmonized_fields = {}

    for field_schema in FIELDS_NOT_IN_SCHEMA['dataset_fields']:
        pkg_harmonized_fields.update(harmonize_field(field_schema, pkg_dict))

    for field_schema in mapping_schema['dataset_fields']:
        pkg_harmonized_fields.update(harmonize_field(field_schema, pkg_dict))

    pkg_harmonized_fields['resources'] = []
    for resource_dict in pkg_dict['resources']:
        pkg_harmonized_fields['resources'].append(harmonize_resource_fields(mapping_schema, resource_dict))

    return pkg_harmonized_fields


def harmonize_resource_fields(mapping_schema, resource_dict):
    '''
    Transforms a resource_dict into an harmonized version of it.

    :param mapping_schema : ckanext-scheming schema for the package type
    :param resource_dict

    :return harmonized resource_dict
    '''

    resource_harmonized_fields = {}

    for field_schema in FIELDS_NOT_IN_SCHEMA['resource_fields']:
        resource_harmonized_fields.update(harmonize_field(field_schema, resource_dict))

    for field_schema in mapping_schema['resource_fields']:
        resource_harmonized_fields.update(harmonize_field(field_schema, resource_dict))

    return resource_harmonized_fields


def harmonize_field(field_schema, data_dict):
    '''
    Uses the field_schema to harmonize the field name and value.

    :param field_schema : schema of that particular field
    :param data_dict : dictionary where the data is available

    :return harmonize_field : dict with key = harmonized_field_name and the value = harmonized_value
    '''

    harmonized_field = {}

    if 'harmonized_field_name' in field_schema:

        '''
            We identified to cases of nested values in incoming harvested data.
            example1: the attribute/key called 'contact_point_name' instead of being { "contact_point_name": "George"} 
            is of structure { "contact_point_name": [{"name": "George"}]} -> nested dict inside a list 
            example2: of structure { "contact_point_name": {"name": "George"}} -> nested dict.

            For the above, a first implementation is to provide a structure to our schema_preset to identify this nested
            configuration for:
            - example1 the preset configuration will go like this: { "field_name": {"contact_point_name": [{"key": "name"}]}} and for
            - example2 the preset configuration will go like this: { "field_name": {"contact_point_name": {"key": "name"}}}
        '''

        if isinstance(field_schema['field_name'], dict):
            nested_field_name = list(field_schema['field_name'].keys())[0]
            if isinstance(field_schema['field_name'][nested_field_name], list):
                field_key = field_schema['field_name'][nested_field_name][0][u'key']
                field_value = json.loads(data_dict[nested_field_name].replace("'", '"'))[0][field_key]
            elif isinstance(field_schema['field_name'][nested_field_name], dict):
                field_key = field_schema['field_name'][nested_field_name][u'key']
                field_value = json.loads(data_dict[nested_field_name].replace("'", '"'))[field_key]
            # elif isinstance(field_schema['field_name'][nested_field_name], str):
            #     field_key = nested_field_name
            #     if field_schema['field_name'][nested_field_name] == 'multi':
            #         field_multi = json.loads(data_dict[nested_field_name].replace("'", '"'))
            #         field_value = [keys.values()[0] for keys in field_multi]

            # assign as new unnested dict element
            data_dict[field_key] = field_value
        else:
            field_key = field_schema['field_name']

        if field_key in data_dict:
            harmonized_field[field_schema['harmonized_field_name']] = harmonize_value(field_schema,
                                                                                      data_dict[
                                                                                          field_key])

        else:
            # if its not in the pkg_dict but is required, populate with harmonized_default_value
            log.debug('Add mandatory field {} with harmonized_default_value'.format(field_schema['field_name']))
            if field_schema.get('required', False) is True:
                harmonized_field[field_schema['harmonized_field_name']] = field_schema.get('harmonized_default_value',
                                                                                           None)
    return harmonized_field


def harmonize_value(field_schema, value):
    '''
    Harmonize a value based on it's field_schema.
    Takes into account the values from "harmonized_value_mapping" and  "harmonized_default_value" to
    decide on what values to harmonize to.
    Detail:
        harmonized_value_mapping: Dict with the mappings of unharmonized (keys) to harmonized_values (values)
        harmonized_default_value: a value to use in the default case

    :param field_schema : schema of that particular field
    :param value : value to harmonize

    :return harmonized value
    '''

    harmonized_value_mapping = field_schema.get('harmonized_value_mapping', None)
    harmonized_default_value = field_schema.get('harmonized_default_value', None)

    if harmonized_value_mapping is not None:
        if value in harmonized_value_mapping.keys():
            result = harmonized_value_mapping[value]
        else:
            result = harmonized_default_value
    else:
        # TODO: current logic will replace 'False' with the harmonized default.
        if not value and harmonized_default_value:
            result = harmonized_default_value
        else:
            result = value

    return result


# UNHARMONIZE

def unharmonize_package_fields(mapping_schema, harmonized_pkg_dict):
    '''
    Transforms a harmonized_pkg_dict into an unharmonized version of it.

    :param mapping_schema : ckanext-scheming schema for the package type
    :param harmonized_pkg_dict

    :return harmonized pkg_dict
    '''

    unharmonized_pkg_fields = {}
    for field_schema in mapping_schema['dataset_fields']:
        unharmonized_pkg_fields.update(unharmonize_field(field_schema, harmonized_pkg_dict))

    unharmonized_pkg_fields['resources'] = []
    for resource_dict in harmonized_pkg_dict['resources']:
        unharmonized_pkg_fields['resources'].append(unharmonize_resource_fields(mapping_schema, resource_dict))

    return unharmonized_pkg_fields


def unharmonize_resource_fields(mapping_schema, harmonized_resource_dict):
    '''
    Transforms a harmonized_resource_dict into an unharmonized version of it.

    :param mapping_schema : ckanext-scheming schema for the package type
    :param harmonized_resource_dict

    :return unharmonized resource_dict
    '''

    unharmonized_resource_fields = {}
    for field_schema in mapping_schema['resource_fields']:
        unharmonized_resource_fields.update(unharmonize_field(field_schema, harmonized_resource_dict))

    return unharmonized_resource_fields


def unharmonize_field(field_schema, harmonized_data_dict):
    '''
    Uses the field_schema to unharmonize the field name and value.

    :param field_schema : schema of that particular field
    :param harmonized_data_dict : dictionary where the data is available

    :return unharmonize_field : dict with key = unharmonized_field_name and the value = unharmonized_value
    '''

    unharmonized_field = {}

    if 'harmonized_field_name' in field_schema and field_schema['harmonized_field_name'] in harmonized_data_dict:
        unharmonized_field[field_schema['field_name']] = unharmonize_value(field_schema,
                                                                           harmonized_data_dict[
                                                                               field_schema['harmonized_field_name']])
    return unharmonized_field


def unharmonize_value(field_schema, value):
    '''
    Unharmonize a value based on it's field_schema.
    Takes into account the values from "harmonized_value_mapping" and  "harmonized_default_value" to
    decide on what values to unharmonize to.
    Detail:
        harmonized_value_mapping: Dict with the mappings of unharmonized (keys) to harmonized_values (values)
        harmonized_default_value: a value to use in the default case

    :param field_schema : schema of that particular field
    :param value : value to unharmonize

    :return unharmonized value
    '''

    is_required = field_schema.get('required', False)
    harmonized_value_mapping = field_schema.get('harmonized_value_mapping', None)
    default_value = field_schema.get('default_value', None)
    unharmonized_default_value = field_schema.get('unharmonized_default_value', None)

    if harmonized_value_mapping is not None:
        for key, v in harmonized_value_mapping.items():
            if v == value:
                return key
        result = default_value
    else:
        if not value and unharmonized_default_value:
            result = unharmonized_default_value
        elif not value and default_value:
            result = default_value
        else:
            result = value

    return result