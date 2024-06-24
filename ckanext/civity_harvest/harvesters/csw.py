from ckanext.spatial.harvesters import CSWHarvester
import logging
import urllib
import re
from ckan import model
from urllib.parse import urlparse
from string import Template
from ckan import plugins as p
from ckan.lib.helpers import json
from ckanext.harvest.harvesters.base import munge_tag
from ckanext.spatial.harvesters.base import guess_resource_format
from ckanext.civityspatial.helpers import populate_metadata_from_external_ows_resource
log = logging.getLogger(__name__)

class CivityCSWHarvester(CSWHarvester):
    """
    This class is an extension of the CSWHarvester of the CKAN spatial extension
    """

    def info(self):
        return {
            'name': 'civity_csw',
            'title': 'Civity CSW Server',
            'description': 'A server that implements OGC\'s Catalog Service for the Web (CSW) standard'
            }

    def fetch_stage(self,harvest_object):
        """
        This method is (roughly) 99% the same as the original fetch_stage of the CSWHarvester. The only difference is
        that the received identifier is URL encoded before sending it to the CSW getrecordbyid method. This has been
        implemented due to DEV-3503 where identifiers showed up containing curly braces.
        """
        # Check harvest object status
        status = self._get_object_extra(harvest_object, 'status')

        if status == 'delete':
            # No need to fetch anything, just pass to the import stage
            return True

        log = logging.getLogger(__name__ + '.CSW.fetch')
        log.debug('CswHarvester fetch_stage for object: %s', harvest_object.id)

        url = harvest_object.source.url
        try:
            self._setup_csw_client(url)
        except Exception as e:
            self._save_object_error('Error contacting the CSW server: %s' % e,
                                    harvest_object)
            return False

        identifier = harvest_object.guid


        try:
            # THE FOLLOWING 2 LINES ARE THE ONLY DIFFERENCE BETWEEN THE ORIGINAL fetch_stage AND THIS ONE
            encoded_identifier = urllib.quote_plus(identifier)
            record = self.csw.getrecordbyid([encoded_identifier], outputschema=self.output_schema())
        except Exception as e:
            self._save_object_error('Error getting the CSW record with GUID %s' % identifier, harvest_object)
            return False

        if record is None:
            self._save_object_error('Empty record for GUID %s' % identifier,
                                    harvest_object)
            return False

        try:
            # Save the fetch contents in the HarvestObject
            # Contents come from csw_client already declared and encoded as utf-8
            # Remove original XML declaration
            content = re.sub('<\?xml(.*)\?>', '', record['xml'])

            harvest_object.content = content.strip()
            harvest_object.save()
        except Exception as e:
            self._save_object_error('Error saving the harvest object for GUID %s [%r]' % \
                                    (identifier, e), harvest_object)
            return False

        log.debug('XML content saved (len %s)', len(record['xml']))
        return True

    def get_package_dict(self, iso_values, harvest_object):
        '''
        Constructs a package_dict suitable to be passed to package_create or
        package_update. See documentation on
        ckan.logic.action.create.package_create for more details

        Extensions willing to modify the dict should do so implementing the
        ISpatialHarvester interface

            import ckan.plugins as p
            from ckanext.spatial.interfaces import ISpatialHarvester

            class MyHarvester(p.SingletonPlugin):

                p.implements(ISpatialHarvester, inherit=True)

                def get_package_dict(self, context, data_dict):

                    package_dict = data_dict['package_dict']

                    package_dict['extras'].append(
                        {'key': 'my-custom-extra', 'value': 'my-custom-value'}
                    )

                    return package_dict

        If a dict is not returned by this function, the import stage will be cancelled.

        :param iso_values: Dictionary with parsed values from the ISO 19139
            XML document
        :type iso_values: dict
        :param harvest_object: HarvestObject domain object (with access to
            job and source objects)
        :type harvest_object: HarvestObject

        :returns: A dataset dictionary (package_dict)
        :rtype: dict
        '''

        tags = []

        if 'tags' in iso_values:
            do_clean = self.source_config.get('clean_tags')
            tags_val = [munge_tag(tag) if do_clean else tag[:100] for tag in iso_values['tags']]
            tags = [{'name': tag} for tag in tags_val]

        # Add default_tags from config
        default_tags = self.source_config.get('default_tags', [])
        if default_tags:
            for tag in default_tags:
                tags.append({'name': tag})

        package_dict = {
            'title': iso_values['title'],
            'notes': iso_values['abstract'],
            'tags': tags,
            'resources': [],
        }

        if iso_values.get('topic-category', []):
            # If there are multiple values, pick the first one
            package_dict['theme'] = iso_values.get('topic-category')[0]

        # We need to get the owner organization (if any) from the harvest
        # source dataset
        source_dataset = model.Package.get(harvest_object.source.id)
        if source_dataset.owner_org:
            package_dict['owner_org'] = source_dataset.owner_org

        # Package name
        package = harvest_object.package
        if package is None or package.title != iso_values['title']:
            name = self._gen_new_name(iso_values['title'])
            if not name:
                name = self._gen_new_name(str(iso_values['guid']))
            if not name:
                raise Exception(
                    'Could not generate a unique name from the title or the GUID. Please choose a more unique title.')
            package_dict['name'] = name
        else:
            package_dict['name'] = package.name

        extras = {
            'guid': harvest_object.guid,
            'spatial_harvester': True,
        }

        # Just add some of the metadata as extras, not the whole lot
        for name in [
            # Essentials
            'spatial-reference-system',
            'guid',
            # Usefuls
            'dataset-reference-date',
            'metadata-language',  # Language
            'metadata-date',  # Released
            'coupled-resource',
            'contact-email',
            'frequency-of-update',
            'spatial-data-service-type',
        ]:
            extras[name] = iso_values[name]

        if len(iso_values.get('progress', [])):
            extras['progress'] = iso_values['progress'][0]
        else:
            extras['progress'] = ''

        if len(iso_values.get('resource-type', [])):
            extras['resource-type'] = iso_values['resource-type'][0]
        else:
            extras['resource-type'] = ''

        extras['licence'] = iso_values.get('use-constraints', '')

        def _extract_first_license_url(licences):
            for licence in licences:
                o = urlparse(licence)
                if o.scheme and o.netloc:
                    return licence
            return None

        if 'licence' in extras.keys() and extras['licence'] and len(extras['licence']):
            license_url_extracted = _extract_first_license_url(extras['licence'])
            if license_url_extracted:
                extras['licence_url'] = license_url_extracted

        # Metadata license ID check for package
        use_constraints = iso_values.get('use-constraints')
        if use_constraints:

            context = {'model': model, 'session': model.Session, 'user': self._get_user_name()}
            license_list = p.toolkit.get_action('license_list')(context, {})

            for constraint in use_constraints:
                package_license = None

                for license in license_list:
                    if constraint.lower() == license.get('id') or constraint == license.get('url'):
                        package_license = license.get('id')
                        break

                if package_license:
                    package_dict['license_id'] = package_license
                    break

        extras['access_constraints'] = iso_values.get('limitations-on-public-access', '')

        # Grpahic preview
        browse_graphic = iso_values.get('browse-graphic')
        if browse_graphic:
            browse_graphic = browse_graphic[0]
            extras['graphic-preview-file'] = browse_graphic.get('file')
            if browse_graphic.get('description'):
                extras['graphic-preview-description'] = browse_graphic.get('description')
            if browse_graphic.get('type'):
                extras['graphic-preview-type'] = browse_graphic.get('type')

        for key in ['temporal-extent-begin', 'temporal-extent-end']:
            if len(iso_values[key]) > 0:
                extras[key] = iso_values[key][0]

        # Save responsible organization roles
        if iso_values['responsible-organisation']:
            parties = {}
            for party in iso_values['responsible-organisation']:
                if party['organisation-name'] in parties:
                    if not party['role'] in parties[party['organisation-name']]:
                        parties[party['organisation-name']].append(party['role'])
                else:
                    parties[party['organisation-name']] = [party['role']]
            extras['responsible-party'] = [{'name': k, 'roles': v} for k, v in parties.iteritems()]

        if len(iso_values['bbox']) > 0:
            bbox = iso_values['bbox'][0]
            extras['bbox-east-long'] = bbox['east']
            extras['bbox-north-lat'] = bbox['north']
            extras['bbox-south-lat'] = bbox['south']
            extras['bbox-west-long'] = bbox['west']

            try:
                xmin = float(bbox['west'])
                xmax = float(bbox['east'])
                ymin = float(bbox['south'])
                ymax = float(bbox['north'])
            except ValueError as e:
                self._save_object_error('Error parsing bounding box value: {0}'.format(str(e)),
                                        harvest_object, 'Import')
            else:
                # Construct a GeoJSON extent so ckanext-spatial can register the extent geometry

                # Some publishers define the same two corners for the bbox (ie a point),
                # that causes problems in the search if stored as polygon
                if xmin == xmax or ymin == ymax:
                    extent_string = Template('{"type": "Point", "coordinates": [$x, $y]}').substitute(
                        x=xmin, y=ymin
                    )
                    self._save_object_error('Point extent defined instead of polygon',
                                            harvest_object, 'Import')
                else:
                    extent_string = self.extent_template.substitute(
                        xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax
                    )

                extras['spatial'] = extent_string.strip()
        else:
            log.debug('No spatial extent defined for this object')

        resource_locators = iso_values.get('resource-locator', []) + \
                            iso_values.get('resource-locator-identification', [])
        if len(resource_locators):
            for resource_locator in resource_locators:
                url = resource_locator.get('url', '').strip()
                if url:
                    if not resource_locator.get('name'):
                        '''
                        If URL exists but resource name doesn't, this is a no go. 
                        Resource creation is skipped.
                        '''
                        continue
                    resource = {}
                    resource.update({
                        "url": url,
                        "name": resource_locator.get('name'),
                        "description": resource_locator.get('description') or '',
                        "format": guess_resource_format(url)
                    })

                    # skip generating resources with no format - https://civity.atlassian.net/browse/DEV-3913
                    resource_format = resource.get('format', '')
                    if not resource_format:
                        #TODO merge 2 guess functions 'guess_resource_format' and 'civity_guess_resource_format'(upgrade the original spatial function)
                        match_format_from_url = self.civity_guess_resource_format(url)
                        if match_format_from_url:
                            resource_format = match_format_from_url
                            resource.update({"format": resource_format})
                        else:
                            resource_format = 'URL'
                            resource.update({"format": 'URL'})

                    if resource_format.lower() in ['wms', 'wfs'] and p.plugin_loaded('civity_spatial'):
                        # Construct URL including params: layerName (mandatory), wmsVersion (optional), wfsVersion (optional)
                        stripped_url = url.split('?')[0] if '?' in url else url
                        params_dict = {}
                        params_dict.update({
                            "layerName": resource_locator.get('name')
                        })
                        # Get params from harvester config JSON
                        harvest_config = json.loads(harvest_object.source.config)
                        wms_version = harvest_config.get('wms_version')
                        wfs_version = harvest_config.get('wfs_version')
                        if wms_version:
                            params_dict.update({
                                "wmsVersion": wms_version
                            })
                        if wfs_version:
                            params_dict.update({
                                "wfsVersion": wfs_version
                            })
                        params = urllib.urlencode(params_dict)
                        resource.update({
                            "url": '{url}?{params}'.format(url=stripped_url, params=params)
                        })
                        external_ows_resource = populate_metadata_from_external_ows_resource(resource)
                        resource.update(external_ows_resource)
                        # recover original harvested url
                        resource.update({
                            "url": url
                        })
                    package_dict['resources'].append(resource)
                    
        # Add default_extras from config
        default_extras = self.source_config.get('default_extras', {})
        if default_extras:
            override_extras = self.source_config.get('override_extras', False)
            for key, value in default_extras.iteritems():
                log.debug('Processing extra %s', key)
                if not key in extras or override_extras:
                    # Look for replacement strings
                    if isinstance(value, str):
                        value = value.format(harvest_source_id=harvest_object.job.source.id,
                                             harvest_source_url=harvest_object.job.source.url.strip('/'),
                                             harvest_source_title=harvest_object.job.source.title,
                                             harvest_job_id=harvest_object.job.id,
                                             harvest_object_id=harvest_object.id)
                    extras[key] = value

        extras_as_dict = []
        for key, value in extras.iteritems():
            if isinstance(value, (list, dict)):
                extras_as_dict.append({'key': key, 'value': json.dumps(value)})
            else:
                extras_as_dict.append({'key': key, 'value': value})

        package_dict['extras'] = extras_as_dict

        return package_dict

    def civity_guess_resource_format(self, url):
        resource_format = ''
        for service in ['WMS','WFS']:
            regex = r'(\/(geoserver|geo)\/)([A-Za-z0-9-]+)(\/{service})'.format(service=service.lower())
            if re.findall(regex, url):
                resource_format = service
                break
        return resource_format
