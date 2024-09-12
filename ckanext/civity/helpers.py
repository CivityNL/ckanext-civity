# encoding: utf-8
import ckan.model as model
from ckan.plugins import toolkit
import json
import logging
import ckanext.civity.resources.vocabularies.get as vocabulary_get
from datetime import datetime
from urllib.parse import urlparse
import uuid

log = logging.getLogger(__name__)

ERROR_DICT = {
    # TODO Populate with more codes if needed
    "403": {"title": "Forbidden", "explanation": "Access was denied to this resource."},
    "404": {"title": "Not Found", "explanation": "The resource could not be found."},
    "500": {"title": "Internal Server Error"}
}


def group_list():
    """
    Calls the Action group_list
    """
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user, 'for_view': True,
               'with_private': False}
    if toolkit.c.userobj:
        context['user_id'] = toolkit.c.userobj.id
        context['user_is_admin'] = toolkit.c.userobj.sysadmin

    data_dict = {'all_fields': True}
    groups = toolkit.get_action('group_list')(context, data_dict)

    return groups


def choices_to_json(choices):
    # TODO Re-ealuate the necessity of this helper function
    return json.dumps(choices)


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
    groups = toolkit.get_action('group_list')(None, {'all_fields': True})

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


# TODO: this is deprecated, to be removed after all old swedish instances are removed
def sweden_theme_list_choices(field):
    """
    Get the Group List and converts it to the Scheming Choices format
    """

    theme_dict = {
        "jordbruk": "http://publications.europa.eu/resource/authority/data-theme/AGRI",
        "ekonomi": "http://publications.europa.eu/resource/authority/data-theme/ECON",
        "utbildning": "http://publications.europa.eu/resource/authority/data-theme/EDUC",
        "energi": "http://publications.europa.eu/resource/authority/data-theme/ENER",
        "miljo": "http://publications.europa.eu/resource/authority/data-theme/ENVI",
        "regeringen": "http://publications.europa.eu/resource/authority/data-theme/GOVE",
        "halsa": "http://publications.europa.eu/resource/authority/data-theme/HEAL",
        "internationella-fragor": "http://publications.europa.eu/resource/authority/data-theme/INTR",
        "rattvisa": "http://publications.europa.eu/resource/authority/data-theme/JUST",
        "regioner": "http://publications.europa.eu/resource/authority/data-theme/REGI",
        "befolkning": "http://publications.europa.eu/resource/authority/data-theme/SOCI",
        "vetenskap": "http://publications.europa.eu/resource/authority/data-theme/TECH",
        "transport": "http://publications.europa.eu/resource/authority/data-theme/TRAN",
        "temporary": "http://publications.europa.eu/resource/authority/data-theme/OP_DATPRO"}

    choices = []
    # TODO make this a config option. or try to solve it differently
    context = {'user': 'admingil'}
    groups = toolkit.get_action('group_list')(context, {'all_fields': True})

    for group in groups:
        # log.info(group['name'])
        choice = dict(value=theme_dict[str(group['name'])], label=group['display_name'])
        choices.append(choice)

    return choices


def get_matomo_id():
    """
    Return the config option "ckanext.civity.civity.matomo_id" that will be a unique Matomo id.
    """
    matomo_id = toolkit.config.get('ckanext.civity.civity.matomo_id', None)
    return matomo_id


def get_matomo_url():
    """
    Return the config option "ckanext.civity.civity.matomo_url" which will contain the base matomo URL to be used.
    """
    matomo_url = toolkit.config.get('ckanext.civity.civity.matomo_url', None)
    if matomo_url and not matomo_url.endswith("/"):
        matomo_url += "/"
    return matomo_url


def get_matomo_custom_url():
    """
    Returns a custom url which should be used when tracking searching in Matomo. Based on the documentation in:
    - https://matomo.org/faq/reports/tracking-site-search-keywords/
    """
    custom_url = None
    page = getattr(toolkit.g, "page", None)
    q = getattr(toolkit.g, "q", None)

    if q and page is not None:
        # need to remove all existing query parameters from the request url, as those will be added by add_url_param
        # not the prettiest code, but at least without any new imports
        custom_url = toolkit.h.add_url_param(
            alternative_url=urlparse(toolkit.request.url)._replace(query=None).geturl(),
            new_params={"search_count": page.item_count}
        )

    return custom_url


def get_siteimprove_src():
    """
    Return the config option "ckanext.civity.civity.siteimprove_src". An endpoint to the SiteImprove source js.
    """
    siteimprove_src = toolkit.config.get('ckanext.civity.civity.siteimprove_src', None)
    return siteimprove_src


def create_group_memberships_from_theme(context, pkg_dict):
    # TODO Check for values/Error Handling
    theme_language = toolkit.config.get('ckanext.civity.theme_language', 'en')
    package_id = pkg_dict.get('id')

    if 'theme' not in pkg_dict:
        log.debug('Schema field "theme" does not exist.')
        return

    package_theme = pkg_dict.get('theme')

    if not package_theme:
        log.debug('Schema field "theme" contains zero values.')
        return

    # solution for all environments, either single or multi schema
    raw_theme_list = []
    try:
        # if multi, convert string list to proper list of elements
        raw_theme_list = json.loads(package_theme)
    except ValueError:
        # if it fails, append the only string the only list element
        raw_theme_list.append(package_theme)

    if not raw_theme_list:
        log.debug('Schema field "theme" value parsing failed.')
        return

    package_dict = toolkit.get_action('package_show')(context, {'id': package_id})
    # populate a list with only names of the group dicts
    package_group_memberships = [group.get("name") for group in package_dict.get('groups')]
    harmonized_theme_list = get_harmonized_theme_list(raw_theme_list, theme_language)

    # Erase deprecated subscriptions
    for group in package_group_memberships:
        if group in harmonized_theme_list:
            continue
        else:
            delete_membership_payload = get_membership_payload(group, package_id)
            toolkit.get_action('member_delete')(context, delete_membership_payload)

    # Insert new subscriptions
    for theme in harmonized_theme_list:
        if theme in package_group_memberships:
            continue
        else:
            create_membership_payload = get_membership_payload(theme, package_id)
            toolkit.get_action('member_create')(context, create_membership_payload)


def get_harmonized_theme_list(raw_theme_list, theme_language):
    theme_list = []
    for theme in raw_theme_list:
        if is_a_url(theme):
            # Uses package_theme as a key in the reversed theme_dict to get the theme name
            if theme_language == 'nl':
                donl_theme_dict = {v: k for k, v in vocabulary_get.get_donl_theme_dict().items()}
                theme_name = donl_theme_dict.get(theme)
            elif theme_language == 'sv':
                sweden_theme_dict = {v: k for k, v in vocabulary_get.get_eu_themes_dict_sv().items()}
                theme_name = sweden_theme_dict.get(theme)
            else:
                theme_name = None
        else:
            theme_name = theme
        theme_list.append(theme_name)
    return theme_list


def get_membership_payload(object_id, object_name, object_type="package", capacity="member"):
    payload = {
        "id": object_id,
        "object": object_name,
        "object_type": object_type,
        "capacity": capacity
    }
    return payload


def is_a_url(value):
    parse_reulst = urlparse(value)

    if parse_reulst.scheme and parse_reulst.netloc:
        return True

    return False


def get_scheming_package_types_list():
    package_types_list = []

    scheming_package_types = toolkit.get_action('scheming_dataset_schema_list')()

    for package_type in scheming_package_types:
        dataset_schema = toolkit.get_action('scheming_dataset_schema_show')(None, {'type': package_type})

        display_text = dataset_schema['about']

        package_type_dict = {
            'display_text': display_text,
            'package_type': package_type
        }
        package_types_list.append(package_type_dict)

    return package_types_list


def get_now_date():
    return datetime.today().strftime('%Y-%m-%d')


def get_package_title(package_id_or_name):
    context = {'user': toolkit.c.user}
    data_dict = {'id': package_id_or_name}
    pkg_dict = toolkit.get_action('package_show')(context, data_dict)

    return pkg_dict.get('title', '')


def get_package_notes(package_id_or_name):
    context = {'user': toolkit.c.user}
    data_dict = {'id': package_id_or_name}
    pkg_dict = toolkit.get_action('package_show')(context, data_dict)

    return pkg_dict.get('notes', '')


def legacy_pager(self, *args, **kwargs):
    from ckan.lib.helpers import Page
    kwargs.update(
        format=u"<div class='pagination-wrapper pagination'><ul>"
               "$link_previous ~2~ $link_next</ul></div>",
        symbol_previous=u'«', symbol_next=u'»',
        curpage_attr={'class': 'active'}, link_attr={}
    )
    return super(Page, self).pager(*args, **kwargs)


def sanitize_id(id_):
    '''Given an id (uuid4), if it has any invalid characters it raises
    ValueError.
    '''
    try:
        return str(uuid.UUID(id_))
    except Exception as exception:
        replace_characters = [' ', '[', ']', '(', ')', '{', '}', ':', ';', ',', '.']
        result = id_
        for character in replace_characters:
            result = result.replace(character, '')
        return result


def i18n_error_document(code, content):
    content_str = content.encode('ascii', 'replace')

    try:
        error_dict = ERROR_DICT[code[0]]
        # identify title/explanation per code and replace with translation.
        for attr in error_dict.keys():
            attr_value = error_dict.get(attr)
            content_str = content_str.replace(attr_value, toolkit._(attr_value))
    except:
        log.info('Unable to translate error code {}. Default text loaded.'.format(code))
        pass
    # rebuild literal object
    result = toolkit.literal(content_str)
    return result
