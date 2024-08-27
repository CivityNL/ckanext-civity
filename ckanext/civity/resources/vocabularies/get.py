import os
import json


def get_donl_theme_dict():
    json_dict = load_dictionary('overheid_taxonomiebeleidsagenda.json')

    theme_dict = {}
    for key in json_dict.keys():

        if json_dict[key]['parent'] is None:
            name = json_dict[key]['labels']['nl-NL'].lower().replace(' ', '-')
            theme_dict[name] = key

    # include a geen-thema option
    theme_dict['geen-thema'] = 'geen-thema'

    return theme_dict


def get_donl_authority_dict():
    json_dict = load_dictionary('donl_organization.json')

    authority_dict = []
    for key in json_dict.keys():
        authority_label = json_dict[key]['labels']['nl-NL']
        authority_type = json_dict[key]['type']

        authority_dict.append({
            "label": authority_label,
            "value": key,
            "type": authority_type
        })
    authority_dict_label_asc = sorted(authority_dict, key=lambda i: i['label'])
    return authority_dict_label_asc


def get_donl_spatial_scheme_dict():
    json_dict = load_dictionary('donl_spatial_scheme.json')

    spatial_scheme_dict = []
    for key in json_dict.keys():
        spatial_scheme_label = json_dict[key]['labels']['nl-NL']

        spatial_scheme_dict.append({
            "label": spatial_scheme_label,
            "value": key
        })
    spatial_scheme_dict_label_asc = sorted(spatial_scheme_dict, key=lambda i: i['label'])
    return spatial_scheme_dict_label_asc


def get_donl_spatial_value_gemeente_dict():
    json_dict = load_dictionary('donl_spatial_value_gemeente.json')

    spatial_value_gemeente_dict = []
    for key in json_dict.keys():
        spatial_value_gemeente_label = json_dict[key]['labels']['nl-NL']

        spatial_value_gemeente_dict.append({
            "label": spatial_value_gemeente_label,
            "value": key
        })
    spatial_value_gemeente_dict_label_asc = sorted(spatial_value_gemeente_dict, key=lambda i: i['label'])
    return spatial_value_gemeente_dict_label_asc


def get_donl_spatial_value_koninkrijksdeel_dict():
    json_dict = load_dictionary('donl_spatial_value_koninkrijksdeel.json')

    spatial_value_koninkrijksdeel_dict = []
    for key in json_dict.keys():
        spatial_value_koninkrijksdeel_label = json_dict[key]['labels']['nl-NL']

        spatial_value_koninkrijksdeel_dict.append({
            "label": spatial_value_koninkrijksdeel_label,
            "value": key
        })
    spatial_value_koninkrijksdeel_dict_label_asc = sorted(spatial_value_koninkrijksdeel_dict, key=lambda i: i['label'])
    return spatial_value_koninkrijksdeel_dict_label_asc


def get_donl_spatial_value_provincie_dict():
    json_dict = load_dictionary('donl_spatial_value_provincie.json')

    spatial_value_provincie_dict = []
    for key in json_dict.keys():
        spatial_value_provincie_label = json_dict[key]['labels']['nl-NL']

        spatial_value_provincie_dict.append({
            "label": spatial_value_provincie_label,
            "value": key
        })
    spatial_value_provincie_dict_label_asc = sorted(spatial_value_provincie_dict, key=lambda i: i['label'])
    return spatial_value_provincie_dict_label_asc


def get_donl_spatial_value_waterschap_dict():
    json_dict = load_dictionary('donl_spatial_value_waterschap.json')

    spatial_value_waterschap_dict = []
    for key in json_dict.keys():
        spatial_value_waterschap_label = json_dict[key]['labels']['nl-NL']

        spatial_value_waterschap_dict.append({
            "label": spatial_value_waterschap_label,
            "value": key
        })
    spatial_value_waterschap_dict_label_asc = sorted(spatial_value_waterschap_dict, key=lambda i: i['label'])
    return spatial_value_waterschap_dict_label_asc


def get_donl_subtheme_dict():
    json_dict = load_dictionary('overheid_taxonomiebeleidsagenda.json')

    dutch_theme_dict = get_donl_theme_dict()
    reversed_theme_dict = {v: k for k, v in dutch_theme_dict.items()}

    subtheme_dict = []
    for key in json_dict.keys():

        subtheme_label = json_dict[key]['labels']['nl-NL']
        subtheme_parent = reversed_theme_dict[json_dict[key]['parent']]

        if json_dict[key]['parent'] != None:
            subtheme_dict.append({
                "label": subtheme_label,
                "value": key,
                "parent": subtheme_parent
            })

    # also append a geen-thema/subthema option
    subtheme_dict.append({
        "label": 'geen-subthema',
        "value": 'geen-subthema',
        "parent": 'geen-thema'
    })

    return subtheme_dict


def get_donl_language_dict():
    json_dict = load_dictionary('donl_language.json')

    language_dict = []
    for key in json_dict.keys():
        nl_label = json_dict[key]['labels']['nl-NL']
        en_label = json_dict[key]['labels']['en-US']

        language_dict.append({
            "label": dict(en=en_label, nl=nl_label),
            "value": key
        })

    language_dict_label_asc = sorted(language_dict, key=lambda i: i['label']['en'])
    return language_dict_label_asc


def get_eu_themes_dict_sv():
    europa_data_themes_sv = load_dictionary('eu_themes_sv.json')
    return europa_data_themes_sv


def load_dictionary(json_file):
    filepath = os.path.join(os.path.dirname(__file__), json_file)
    with open(filepath, 'r', encoding='utf-8') as file_contents:
        json_dict = json.loads(file_contents.read())
    return json_dict
