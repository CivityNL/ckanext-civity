import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class UseragentPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        plugins.toolkit.add_resource('assets', 'ckanext-useragent')

