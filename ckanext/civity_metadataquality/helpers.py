from ckan.plugins import toolkit
import ckan.model as model


FIELD_NAMES_VS_PACKAGE_ATTRIBUTES = {
    'tag_string': 'tags'
}

def _dict_has_value_for_key(dict, key):
    '''
    This method checks if a dictionary has a value for a specific key. In this case it has a value if the field
    exists and has a value different then None or '' (empty string)
    :param dict:    The dictionary to look in
    :param key:     The key to look for
    :return:        True if a value exists for this key and dictionary, otherwise False
    '''
    has_value = False
    if key in dict:
        value = dict.get(key)
        if value is not None and value != '':
            has_value = True
    return has_value


def validate_metadata_quality(pkg_dict):
    '''
    This method takes an package dictionary and based on the belonging schema it will check how many fields based on
    that schema have a value in the package. It will return the results as a dictionary in 3 groups:
        total: based on all the fields
        mandatory: based on all required fields
        optional: based on all non-required fields
    For each group it will return:
        number: the total number of fields
        valid: the number of valid fields (for which the package has a value)
        score: valid divided by number
    :param pkg_dict:
    :return:
    '''
    context = {
        'model': model, 'session': model.Session,
        'user': toolkit.c.user, 'auth_user_obj': toolkit.c.userobj
    }

    try:
        schemas_dict = toolkit.get_action('scheming_dataset_schema_show')(context, {'type': pkg_dict.get('type')})
    except toolkit.ObjectNotFound:
        return None

    field_list = schemas_dict['dataset_fields']
    required_valid = 0
    required_total = 0
    not_required_valid = 0
    not_required_total = 0

    # TODO: actual validate the values instead of just check if their not None or empty

    for field in field_list:
        if 'required' in field:
            required = field.get('required')
            field_name = field.get('field_name')
            # Not all field names in the schema correspond with an package attribute with the same name
            if field_name in FIELD_NAMES_VS_PACKAGE_ATTRIBUTES:
                field_name = FIELD_NAMES_VS_PACKAGE_ATTRIBUTES.get(field_name)
            if required:
                required_total = required_total + 1
                if _dict_has_value_for_key(pkg_dict, field_name):
                    required_valid = required_valid + 1
            elif not required:
                not_required_total = not_required_total + 1
                if _dict_has_value_for_key(pkg_dict, field_name):
                    not_required_valid = not_required_valid + 1

    return {
        'total': {
            'score': float(required_valid + not_required_valid) / (required_total + not_required_total),
            'number': required_total + not_required_total,
            'valid': required_valid + not_required_valid
        },
        'mandatory': {
            'score': float(required_valid) / required_total,
            'number': required_total,
            'valid': required_valid
        },
        'optional': {
            'score': float(not_required_valid) / not_required_total,
            'number': not_required_total,
            'valid': not_required_valid
        }
    }
