import ckan.plugins as plugins
from ckanext.spatial.interfaces import ISpatialHarvester
import ckanext.civityscheming.logic.harmonization as harm
import json
import os
import logging

log = logging.getLogger(__name__)

CONFIG_DEFAULT_OPTIONS = [
    "schema_preset",
    "dataplatform_link_enabled",
    "geoserver_link_enabled",
    "geonetwork_link_enabled",
    "donl_link_enabled",
    'wms_version',
    'wfs_version'
]

def get_schema_preset(schema_preset_name):
    return load_schema('harvest_schema_presets/{schema_preset_name}.json'
                       .format(schema_preset_name=schema_preset_name))


def load_schema(json_schema):
        filepath = os.path.join(os.path.dirname(__file__), json_schema)
        with open(filepath, 'r') as file_contents:
            schema_dict = json.loads(file_contents.read())
        return schema_dict

class CivityHarvestPlugin(plugins.SingletonPlugin):
    plugins.implements(ISpatialHarvester, inherit=True)


     # ISpatialHarvester
    def get_package_dict(self, context, data_dict):

        # Get Package converted from default ISpatialHarvester
        package_dict = data_dict['package_dict']
        harvest_object = data_dict['harvest_object']
        harvest_config = self.get_harvest_config_dict(harvest_object.source.config)
        harvest_schema_preset = harvest_config.get('schema_preset', "noord_holland") #TODO create a default schema_preset to replace current default
        # Populate dataset metadata values from harvest_config
        package_dict = self.populate_from_harvest_config(harvest_config, package_dict.copy())
        # Bring nested 'extras' dict keys to parent dict
        package_dict = self.normalize_extras(package_dict.copy())

        # Harmonize data
        package_dict = self.harmonize_with_schema_preset(package_dict.copy(), harvest_schema_preset)

        return package_dict

    def normalize_extras(self, package_dict):
        extras_to_dict = {x['key']: x['value'] for x in package_dict['extras']}
        package_dict = dict(extras_to_dict.items() + package_dict.items())
        package_dict.pop('extras')
        return package_dict


    def harmonize_with_schema_preset(self, pkg_dict, schema_preset_name):

        schema_preset = get_schema_preset(schema_preset_name)
        harmonized_pkg_dict = harm.harmonize_package_fields(schema_preset, pkg_dict)
        return harmonized_pkg_dict

    def get_harvest_config_dict(self, harvest_config_str):
        harvest_config_raw = json.loads(harvest_config_str)
        harvest_config = dict()
        for attribute in harvest_config_raw:
            if attribute in CONFIG_DEFAULT_OPTIONS:
                harvest_config[attribute] = harvest_config_raw[attribute]
        return harvest_config

    def populate_from_harvest_config(self, harvest_config, package_dict):
        for attribute in harvest_config:
            if bool(harvest_config.get(attribute, "false").lower() == "true"):
                package_dict[attribute] = 'True'
            elif bool(harvest_config.get(attribute, "false").lower() == "false"):
                package_dict[attribute] = 'False'
        return package_dict