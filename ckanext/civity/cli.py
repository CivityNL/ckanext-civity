import click
import ckan.model as model
from ckan.plugins import toolkit
from ckan.cli import error_shout
from ckanext.civity.helpers import create_group_memberships_from_theme


@click.group(short_help=u"Perform commands in the datapusher.")
def civity():
    """Perform commands in the datapusher.
    """
    pass

@civity.command()
def init():
    """
    Resubmit updated datastore resources.
    """

    pkg_ids = [r[0] for r in model.Session.query(model.Package.id)]
    site_user = toolkit.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})

    for pkg_id in pkg_ids:
        try:
            pkg_dict = toolkit.get_action(u'package_show')({'model': model, 'ignore_auth': True}, {'id': pkg_id})
            create_group_memberships_from_theme(
                {'model': model, 'ignore_auth': True, 'user': site_user['name']},
                pkg_dict
            )
        except Exception as e:
            error_shout(e)
            error_shout(u"Package '{}' was not found".format(pkg_id))
