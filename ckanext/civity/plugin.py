import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.civity.helpers as h
import ckanext.civity.logic.auth.get as auth_get
import ckanext.civity.logic.auth.create as auth_create
import ckanext.civity.validators as validators
import ckanext.civity.views as views
from ckanext.civity.interfaces import IFacetLabelFunction
import ckanext.civity.logic.action.get as action_get
from ckanext.civity.uploader import CivityResourceUpload
from ckan.lib.plugins import DefaultTranslation
import ckanext.civity.cli as cli


class CivityPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IBlueprint)


    users_assign_all_groups = toolkit.config.get('civity.users_assign_all_groups', False)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'ckanext-civity')

        # Monkey-patch legacy Bootstrap pagination
        if 'ckan.base_templates_folder' in config_ and config_['ckan.base_templates_folder'] == 'templates-bs2':
            from ckan.lib.helpers import Page
            Page.pager = h.legacy_pager
        return config_

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        unicode_safe = toolkit.get_validator('unicode_safe')
        schema.update({
            'ckanext.civity.portal_intro_text': [ignore_missing, unicode_safe]
        })
        return schema

    # IAuthFunctions
    def get_auth_functions(self):
        auth_functions = {
            'config_option_show': auth_get.config_option_show
        }
        if self.users_assign_all_groups:
            auth_functions.update({
                'member_create': auth_create.member_create
            })
        return auth_functions

    # IValidators
    def get_validators(self):
        return {
            'url_checker': validators.url_checker,
            'custom_url_resource_validator': validators.custom_url_resource_validator,
            'non_empty_org_validator': validators.non_empty_org_validator,
            'ignore_missing_but_keep_value': validators.ignore_missing_but_allow_empty
        }

    # IPackageController
    def after_create(self, context, pkg_dict):
        if self.users_assign_all_groups:
            return h.create_group_memberships_from_theme(context, pkg_dict)

    def after_update(self, context, pkg_dict):
        if self.users_assign_all_groups:
            return h.create_group_memberships_from_theme(context, pkg_dict)

    def after_search(self, search_results, search_params):
        label_functions = dict()
        search_facets = search_results.get('search_facets', {})

        for plugin in plugins.PluginImplementations(IFacetLabelFunction):
            label_functions = plugin.get_label_functions(label_functions)

        for field_name, search_facet in search_facets.items():
            search_facet_items = search_facet.get('items', [])
            if field_name in label_functions and search_facet_items:
                for search_facet_item in search_facet_items:
                    search_facet_item['display_name'] = label_functions[field_name](search_facet_item)
                search_facet['items'] = search_facet_items
 
        return search_results

    # ITemplateHelpers
    def get_helpers(self):
        return {'civity_group_list': h.group_list,
                'civity_choices_to_json': h.choices_to_json,
                'civity_donl_theme_list_choices': h.donl_theme_list_choices,
                'civity_donl_authority_list_choices': h.donl_authority_list_choices,
                'civity_donl_language_list_choices': h.donl_language_list_choices,
                'civity_donl_spatial_scheme_list_choices': h.donl_spatial_scheme_list_choices,
                'civity_donl_spatial_value_list_choices': h.donl_spatial_value_list_choices,
                'sweden_theme_list_choices': h.sweden_theme_list_choices,
                'civity_get_matomo_id': h.get_matomo_id,
                'civity_get_matomo_url': h.get_matomo_url,
                'civity_get_matomo_custom_url': h.get_matomo_custom_url,
                'civity_get_siteimprove_src': h.get_siteimprove_src,
                'civity_get_scheming_package_types_list': h.get_scheming_package_types_list,
                'civity_get_now_date': h.get_now_date,
                'civity_get_package_title': h.get_package_title,
                'civity_get_package_notes': h.get_package_notes,
                'civity_i18n_error_document': h.i18n_error_document,
                'sanitize_id': h.sanitize_id
                }

    # IActions

    def get_actions(self):
        return {
            'config_option_list': action_get.config_option_list
        }

    # IUploader

    def get_resource_uploader(self, data_dict):
        return CivityResourceUpload(data_dict)

    # IClick
    def get_commands(self):
        return [cli.civity]

    # IBlueprint
    def get_blueprint(self):
        u'''Return a Flask Blueprint object to be registered by the app.'''
        return views.get_blueprints()
