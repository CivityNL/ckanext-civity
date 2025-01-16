import ckan.plugins as plugins
import ckanext.civityspatial.helpers as h

import logging

log = logging.getLogger(__name__)


class CivitySpatialPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IResourceController, inherit=True)

    # IResourceController
    def before_create(self, context, resource):
        resource_format = resource.get('format', None)
        if resource_format:
            if resource_format.lower() in ['wms', 'wfs']:
                resource.update(h.populate_metadata_from_external_ows_resource(resource))
            elif resource_format.lower() in ['wms_without_capabilities']:
                resource.update(h.populate_metadata_from_wms_resource_without_capabilities(resource))

    def before_update(self, context, current, resource):
        resource_format = resource.get('format', None)
        if resource_format:
            if resource_format.lower() in ['wms', 'wfs']:
                resource.update(h.populate_metadata_from_external_ows_resource(resource))
            elif resource_format.lower() in ['wms_without_capabilities']:
                resource.update(h.populate_metadata_from_wms_resource_without_capabilities(resource))

    def before_show(self, resource_dict):
        # populate wms_capabilities_url, wfs_capabilities_url metadata, if available
        for service in ['wms', 'wfs']:
            capabilities_url = h.get_capabilities_url(resource_dict, service)
            if capabilities_url:
                capabilities_url_key = '{}_capabilities_url'.format(service)
                resource_dict[capabilities_url_key] = capabilities_url
        return resource_dict
