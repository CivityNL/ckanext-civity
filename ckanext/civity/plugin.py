import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.civity.helpers as h


class CivityPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
                             'civity')

    def get_helpers(self):
        return {
            'civity_donl_theme_list_choices': h.donl_theme_list_choices,
            'civity_donl_authority_list_choices': h.donl_authority_list_choices,
            'civity_donl_language_list_choices': h.donl_language_list_choices,
            'civity_donl_spatial_scheme_list_choices': h.donl_spatial_scheme_list_choices,
            'civity_donl_spatial_value_list_choices': h.donl_spatial_value_list_choices
        }
