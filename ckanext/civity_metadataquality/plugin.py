import ckan.plugins as plugins
import ckanext.civity_metadataquality.helpers as helpers


class MetaDataQualityPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer
    def update_config(self, config):
        plugins.toolkit.add_template_directory(config, 'templates')
        plugins.toolkit.add_resource('assets', 'ckanext-civity_metadataquality')

    # IPackageController
    def after_show(self, context, pkg_dict):
        metadataquality = helpers.validate_metadata_quality(context, pkg_dict)
        if metadataquality is not None:
            pkg_dict['civity_metadataquality'] = metadataquality
        return pkg_dict
