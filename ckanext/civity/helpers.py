# encoding: utf-8
from ckan.plugins import toolkit
import logging
import ckanext.civity.resources.vocabularies.get as vocabulary_get

log = logging.getLogger(__name__)

ERROR_DICT = {
    # TODO Populate with more codes if needed
    "403": {"title": "Forbidden", "explanation": "Access was denied to this resource."},
    "404": {"title": "Not Found", "explanation": "The resource could not be found."},
    "500": {"title": "Internal Server Error"}
}


def donl_language_list_choices(field):
    language_dict = vocabulary_get.get_donl_language_dict()
    choices = []
    for language in language_dict:
        choice = dict(value=language.get('value'), label=language.get('label'))
        choices.append(choice)
    return choices


def donl_theme_list_choices(field):
    """
    Get the Group List and converts it to the Scheming Choices format
    """

    theme_dict = vocabulary_get.get_donl_theme_dict()
    choices = []
    context = {'user': toolkit.c.user}
    groups = toolkit.get_action('group_list')(context, {'all_fields': True})

    for group in groups:
        choice_value = theme_dict.get(group['name']) if theme_dict.get(group['name']) else group['name']
        choice_label = group['display_name']

        choice = dict(value=choice_value, label=choice_label)
        choices.append(choice)

    return choices


def donl_authority_list_choices(field):
    authority_dict = vocabulary_get.get_donl_authority_dict()
    choices = []
    for authority in authority_dict:
        choice = dict(value=authority.get('value'), label=authority.get('label'))
        choices.append(choice)

    return choices


def donl_spatial_scheme_list_choices(field):
    spatial_scheme_dict = vocabulary_get.get_donl_spatial_scheme_dict()
    choices = []
    for spatial_scheme in spatial_scheme_dict:
        choice = dict(value=spatial_scheme.get('value'), label=spatial_scheme.get('label'))
        choices.append(choice)

    return choices


def donl_spatial_value_list_choices(field):
    choices = []

    choice = dict(
        value="http://standaarden.overheid.nl/owms/4.0/doc/syntax-codeerschemas/overheid.postcodehuisnummer",
        label="PostcodeHuisnummer",
        parent="PostcodeHuisnummer"
    )
    choices.append(choice)

    choice = dict(
        value="http://standaarden.overheid.nl/owms/4.0/doc/syntax-codeerschemas/overheid.epsg28992",
        label="EPSG:28992",
        parent="EPSG:28992"
    )
    choices.append(choice)

    # Adding list options from --> https://waardelijsten.dcat-ap-donl.nl/overheid_spatial_gemeente.json
    spatial_value_gemeente_dict = vocabulary_get.get_donl_spatial_value_gemeente_dict()
    for spatial_value_gemeente in spatial_value_gemeente_dict:
        choice = dict(
            value=spatial_value_gemeente.get('value'),
            label=spatial_value_gemeente.get('label'),
            parent="Gemeente"
        )
        choices.append(choice)

    # Adding list options from --> https://waardelijsten.dcat-ap-donl.nl/overheid_spatial_koninkrijksdeel.json
    spatial_value_koninkrijksdeel_dict = vocabulary_get.get_donl_spatial_value_koninkrijksdeel_dict()
    for spatial_value_koninkrijksdeel in spatial_value_koninkrijksdeel_dict:
        choice = dict(
            value=spatial_value_koninkrijksdeel.get('value'),
            label=spatial_value_koninkrijksdeel.get('label'),
            parent="Koninkrijksdeel"
        )
        choices.append(choice)

    # Adding list options from --> https://waardelijsten.dcat-ap-donl.nl/overheid_spatial_provincie.json
    spatial_value_provincie_dict = vocabulary_get.get_donl_spatial_value_provincie_dict()
    for spatial_value_provincie in spatial_value_provincie_dict:
        choice = dict(
            value=spatial_value_provincie.get('value'),
            label=spatial_value_provincie.get('label'),
            parent="Provincie"
        )
        choices.append(choice)

    # Adding list options from --> https://waardelijsten.dcat-ap-donl.nl/overheid_spatial_waterschap.json
    spatial_value_waterschap_dict = vocabulary_get.get_donl_spatial_value_waterschap_dict()
    for spatial_value_waterschap in spatial_value_waterschap_dict:
        choice = dict(
            value=spatial_value_waterschap.get('value'),
            label=spatial_value_waterschap.get('label'),
            parent="Waterschap"
        )
        choices.append(choice)

    return choices


