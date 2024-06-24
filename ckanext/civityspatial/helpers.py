from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl, parse_qs
from lxml.etree import XMLSyntaxError
from owslib import wfs
from owslib import wms
from owslib.util import ServiceException
import ckan.plugins.toolkit as toolkit


DEFAULT_WMS_VERSION = '1.1.0'
DEFAULT_WFS_VERSION = '2.0.0'
DEFAULT_WMS_GETMAP_WIDTH = 768
DEFAULT_WMS_GETMAP_HEIGHT = 384
DEFAULT_WMS_SRS = 'EPSG:4326'
DEFAULT_WMS_SRS_INT = '4326'
DEFAULT_GLOBE_BBOX_STR = '[-90,-180,90,180]'

import logging
log = logging.getLogger(__name__)

def populate_metadata_from_external_ows_resource(resource_dict):
    """
    - check if most recent version is available for WMS
    - check if WMS layers exist
    """
    resource_format = resource_dict['format'].lower()
    resource_url = resource_dict.get('url', '')
    stripped_url, layer_name_param, wms_version_param, wfs_version_param = strip_ows_url(resource_url)

    log.debug('OWS URL: [{}], layer name: [{}], WMS version: [{}], WFS version: [{}]'
              .format(stripped_url, layer_name_param, wms_version_param, wfs_version_param))

    if resource_format == 'wms':
        if layer_name_param:
            wms_layer = validate_wms_layer(stripped_url, layer_name_param, wms_version_param)
            if wms_layer:
                wfs_layer = generate_wfs_layer(stripped_url, wms_layer, wfs_version_param)
                resource_dict.update({
                    "name": wms_layer.get('title'),
                    "description": get_layer_description(wms_layer, resource_dict),
                    "datastore_active": False,
                    "ows_layer": wms_layer.get('name'),
                    "ows_url": stripped_url,
                    "wms_url": wms_layer.get('wms_url'),
                    "wfs_url": wfs_layer.get('wfs_url'),
                    "layer_srid": wms_layer.get('layer_srid'),
                    "layer_extent": wms_layer.get('layer_extent')
                })
                log.debug('[WMS layer] metadata acquired')
                if not wfs_layer:
                    warning_feedback('Failed retrieving generated WFS service content.')
            else:
                warning_feedback('Failed retrieving WMS service content.')
                log.debug('{} --> {}'.format(layer_name_param, stripped_url))

        else:
            resource_dict.update({
                "datastore_active": False,
                "ows_layer": None,
                "ows_url": None,
                "wms_url": "Failed retrieving param 'layerName' from resource URL.",
                "wfs_url": None,
                "layer_srid": None,
                "layer_extent": None,
            })
            warning_feedback('Failed retrieving param "layerName" from resource URL')

    elif resource_format == 'wfs':
        if layer_name_param:
            wfs_layer = validate_wfs_layer(resource_url, layer_name_param, wfs_version_param)
            if wfs_layer:
                wms_layer = generate_wms_layer(stripped_url, layer_name_param, wms_version_param)
                resource_dict.update({
                    "name": wfs_layer.get('type_name'),
                    "description": get_layer_description(wms_layer, resource_dict),
                    "datastore_active": False,
                    "ows_layer": wms_layer.get('name'),
                    "ows_url": stripped_url,
                    "wms_url": wms_layer.get('wms_url'),
                    "wfs_url": wfs_layer.get('wfs_url'),
                    "layer_srid": wms_layer.get('layer_srid'),
                    "layer_extent": wms_layer.get('layer_extent')
                })
                log.debug('[WFS layer] metadata acquired')
                if not wms_layer:
                    warning_feedback('Failed retrieving generated WMS service content.')
            else:
                warning_feedback('Failed retrieving WFS service content.')
                log.debug('{} --> {}'.format(layer_name_param, stripped_url))
        else:
            resource_dict.update({
                "datastore_active": False,
                "ows_layer": None,
                "ows_url": None,
                "wms_url": None,
                "wfs_url": "Failed retrieving param 'layerName' from resource URL.",
                "layer_srid": None,
                "layer_extent": None,
            })
            warning_feedback('Failed retrieving param "layerName" from resource URL')
    return resource_dict


def strip_ows_url(resource_url):
    url_params_raw = urlparse(resource_url).query
    url_params_dict = dict(parse_qsl(url_params_raw))

    # Name of the layer as provided by the user
    layer_name_param = url_params_dict.get('layerName', url_params_dict.get('layername'))

    # WMS version
    wms_version_param = url_params_dict.get('wmsVersion', DEFAULT_WMS_VERSION)

    # WFS version
    wfs_version_param = url_params_dict.get('wfsVersion', DEFAULT_WFS_VERSION)

    # Derive online resource URL
    stripped_url = resource_url.split('?')[0]

    # Accommodate for MapServer WMS's (see DEV-5516). Add additional parameters.
    stripped_url += "?"
    for key in url_params_dict:
        if key.lower() != 'layername' and key.lower() != 'wmsversion' and key.lower() != 'wfsversion':
            stripped_url += key + '=' + url_params_dict.get(key) + '&'

    return stripped_url, layer_name_param, wms_version_param, wfs_version_param


def populate_metadata_from_wms_resource_without_capabilities(resource_dict):
    resource_url = resource_dict.get('url', '')
    url_params_raw = urlparse(resource_url).query
    url_params_dict = dict(parse_qsl(url_params_raw))
    layer_name_param = url_params_dict.get('layerName', url_params_dict.get('layername'))
    wms_version_param = url_params_dict.get('wmsVersion', DEFAULT_WMS_VERSION)
    stripped_url = resource_url.split('?')[0]
    params_dict = {
        'service': 'WMS',
        'version': wms_version_param,
        'request': 'GetMap',
        'layers': layer_name_param,
        'bbox': resource_dict.get('layer_extent', DEFAULT_GLOBE_BBOX_STR).strip('[]'),
        'width': DEFAULT_WMS_GETMAP_WIDTH,
        'height': DEFAULT_WMS_GETMAP_HEIGHT,
        'srs': 'EPSG:{layer_srid}'.format(layer_srid=resource_dict.get('layer_srid', DEFAULT_WMS_SRS_INT)),
        'styles': '',
        'format': 'image/png'
    }
    params = urlencode(params_dict)
    wms_url = '{url}?{params}'.format(url=stripped_url, params=params)
    resource_dict.update({
        "wms_url": wms_url,
    })
    return resource_dict

def get_layer_description(wms_layer, resource_dict):
    if wms_layer.get('abstract'):
        return wms_layer.get('abstract')
    elif resource_dict.get('description'):
        return resource_dict.get('description')
    else:
        return  toolkit._('No description')


def generate_wms_layer(wfs_url, type_name, wms_version):
    if "service=wfs" in wfs_url: # Geoserver
        generated_wms_url = wfs_url.replace('service=wfs', 'service=wms')
    elif "MapServer/WFSServer" in wfs_url: # ArcGIS
        generated_wms_url = wfs_url.replace('MapServer/WFSServer', 'MapServer/WMSServer')
    else:
        generated_wms_url = wfs_url
    try:
        wms_layer_object = wms.WebMapService(generated_wms_url)
        wms_layers = wms_layer_object.contents
        layer_name = get_layer_name_from_type_name(type_name)
        wms_layer = {}
        if layer_name in wms_layers:
            log.debug('[Generated WMS layer] exists')
            wms_layer.update({
                "abstract": wms_layer_object[layer_name].abstract,
                "layer_extent": list(wms_layer_object[layer_name].boundingBoxWGS84),
                "layer_srid": DEFAULT_WMS_SRS_INT,
                "name": wms_layer_object[layer_name].name,
                "wms_url": build_external_wms_url(wms_layer_object, generated_wms_url, layer_name)
                })
        else:
            log.warning('[Generated WMS layer] not found')
        return wms_layer
    except ServiceException as service_error:
        log.error(service_error)
        return {}
    except HTTPError as http_error:
        log.error(http_error)
        return {}


def generate_wfs_layer(url, wms_layer, wfs_version):
    wms_name = wms_layer.get('name')
    if "service=wms" in url: # Geoserver
        generated_wfs_url = url.replace('service=wms', 'service=wfs')
    elif "MapServer/WMSServer" in url: # ArcGIS
        generated_wfs_url = url.replace('MapServer/WMSServer', 'MapServer/WFSServer')
    else:
        generated_wfs_url = url
    try:
        wfs_service = wfs.WebFeatureService(generated_wfs_url, version=wfs_version)
        wfs_contents_with_stripped_namespace = [layer.split(':')[1] for layer in list(wfs_service.contents)]
        wms_strip_whitespaces = wms_name.replace(' ', '_')
        wfs_layer = {}
        if wms_strip_whitespaces in wfs_contents_with_stripped_namespace:
            log.debug('[Generated WFS layer] exists')
            type_name = [layer for layer in list(wfs_service.contents) if layer.split(':')[1] == wms_strip_whitespaces][0]

            wfs_layer.update({
                "wfs_url": build_external_wfs_url(wfs_service, generated_wfs_url, type_name)
                })
        else:
            log.warning('[Generated WFS layer] not found')
        return wfs_layer
    except AttributeError as attribute_error:
        # WFS service exists but does not include any feature layers
        log.error(attribute_error)
        return {}
    except ServiceException as service_error:
        log.error(service_error)
        return {}
    except HTTPError as http_error:
        log.error(http_error)
        return {}


def get_layer_name_from_type_name(type_name):
    layer_name_raw = type_name.split(':')[1]
    if layer_name_raw[:5] != 'ckan_': #TODO load from Geoserver prefix
        layer_name = layer_name_raw.replace("_", " ")
    else:
        layer_name = layer_name_raw
    return layer_name


def validate_wms_layer(url, layer_name, wms_version):
    wms_layer = {}
    wms_layer_object = is_wms_layer(url, layer_name, wms_version)
    if wms_layer_object:
        log.debug('[WMS layer] exists')
        # wms_service = wms_service_with_latest_supported_version(url)
        wms_layer.update({
            "url": wms_layer_object.url,
            "name": wms_layer_object[layer_name].name,
            "title": wms_layer_object[layer_name].title,
            "abstract": wms_layer_object[layer_name].abstract,
            "wms_url": build_external_wms_url(wms_layer_object, url, layer_name),
            "layer_extent": list(wms_layer_object[layer_name].boundingBoxWGS84),
            "layer_srid": DEFAULT_WMS_SRS_INT
            })
    else:
        log.warning('[WMS layer] not found')
    return wms_layer


def validate_wfs_layer(url, type_name, wfs_version):
    wfs_layer = {}
    wfs_layer_object = is_wfs_layer(url, type_name, wfs_version)
    if wfs_layer_object:
        log.debug('[WFS layer] exists')
        # wfs_service = wfs_service_with_latest_supported_version(url)
        wfs_layer.update({
            "wfs_url": build_external_wfs_url(wfs_layer_object, url, type_name),
            "type_name": type_name
            })
    else:
        log.warning('[WFS layer] not found')
    return wfs_layer

def is_wms_layer(url, layer_name, wms_version):
    try:
        wms_service = wms.WebMapService(url=url)
        if wms_service and layer_name in list(wms_service.contents):
            return wms_service
        else:
            return None
    except ServiceException as service_error:
        log.error(service_error)
    except HTTPError as http_error:
        log.error(http_error)
    except URLError as url_error:
        log.error(url_error)
    except XMLSyntaxError as syntax_error:
        log.error(syntax_error)
    except Exception as e:
        log.error(e)

def is_wfs_layer(url, layer_name, wfs_version):
    try:
        wfs_service = wfs.WebFeatureService(url, version=wfs_version)
        if wfs_service and layer_name in list(wfs_service.contents):
            return wfs_service
        else:
            return None
    except ServiceException as service_error:
        log.error(service_error)

    except HTTPError as http_error:
        log.error(http_error)

    except URLError as url_error:
        log.error(url_error)


def build_external_wms_url(wms_service, url, layer_name):
    ref_sys_name = 'srs'
    ref_sys_value = DEFAULT_WMS_SRS
    if wms_service.version == '1.3.0':
        ref_sys_name = 'crs'
        ref_sys_value = DEFAULT_WMS_SRS_INT
    params_dict = {
        'service': 'WMS',
        'version': wms_service.version,
        'request': 'GetMap',
        'layers': layer_name,
        'bbox': bbox_to_str(wms_service[layer_name].boundingBoxWGS84),
        'width': DEFAULT_WMS_GETMAP_WIDTH,
        'height': DEFAULT_WMS_GETMAP_HEIGHT,
        ref_sys_name: ref_sys_value,
        'styles': '',
        'format': 'image/png'
    }
    params = urlencode(params_dict)
    result = '{url}{params}'.format(url=url, params=params)
    return result


def build_external_wfs_url(wfs_service, url, layer_name):
    output_format ='application/json'
    if "MapServer/WFSServer" in url or 'FeatureServer/WFSServer' in url:
        output_format = 'geojson'
    params_dict = {
        'service': 'WFS',
        'version': wfs_service.version,
        'request': 'GetFeature',
        'typeName': layer_name,
        'maxFeatures': 50,
        'outputFormat': output_format
    }
    params = urlencode(params_dict)
    result = '{url}{params}'.format(url=url, params=params)
    return result


def warning_feedback(text):
    log.warning(text)
    try:
        toolkit.h.flash_notice(text, allow_html=True)
    except TypeError:
        log.debug('This is not UI action, skipping flash notice')


def bbox_to_str(bbox_raw):
    if isinstance(bbox_raw, (list, tuple)):
        bbox = ','.join(str(e) for e in bbox_raw)
    elif (isinstance(bbox_raw, str)) or (isinstance(bbox_raw, str)):
        bbox = bbox_raw.strip('[]')
    else:
        bbox = None
    return bbox


def get_capabilities_url(resource_dict, service):
    ows_url = resource_dict.get('ows_url', None)
    if not is_valid_url(ows_url):
        return None

    if service == 'wms' and is_valid_url(resource_dict.get('wms_url', None)):
        return generate_capabilities_url(ows_url, service)

    if service == 'wfs' and is_valid_url(resource_dict.get('wfs_url', None)):
        return generate_capabilities_url(ows_url, service)

    return None


def generate_capabilities_url(ows_url, service):
    parsed_url = urlparse(ows_url)
    # Retrieve existing params, if any
    existing_params = parse_qs(parsed_url.query)
    capabilities_params = {
        "service": service,
        "request": "GetCapabilities"
    }
    # concatenate existing and new params
    existing_params.update(capabilities_params)
    # Encode the updated params
    encoded_params = urlencode(existing_params, doseq=True)
    # construct url with new params
    capabilities_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        encoded_params,
        parsed_url.fragment
    ))
    return capabilities_url


def is_valid_url(url):
    # Check the url string is not empty and validate with core helper
    valid_url = url and toolkit.h.is_url(url, None)
    return valid_url

# def wms_service_with_latest_supported_version(url):
#     wms_versions = ['1.3.0', '1.1.1', '1.1.0', '1.0.0']
#     wms_service = None
#     for version in wms_versions:
#         try:
#             wms_service = wms.WebMapService(url)
#             log.debug('WMS version {version}.'.format(version=version))
#             break
#         except NotImplementedError:
#             log.debug('WMS version {version} is not implemented.'.format(version=version))
#             continue
#     if wms_service:
#         return wms_service
#
#
# def wfs_service_with_latest_supported_version(url):
#     wfs_versions = ['2.0.0', '1.1.0', '1.0.0']
#     wfs_service = None
#     for version in wfs_versions:
#         try:
#             wfs_service = wfs.WebFeatureService(url, version=version)
#             log.debug('WFS version {version}.'.format(version=version))
#             break
#         except NotImplementedError:
#             log.debug('WFS version {version} is not implemented.'.format(version=version))
#             continue
#     if wfs_service:
#         return wfs_service
