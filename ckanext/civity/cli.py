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
    n = len(pkg_ids)

    for idx, pkg_id in enumerate(pkg_ids, start=1):
        counter = "{}/{}".format(idx,n)
        try:
            pkg_dict = toolkit.get_action(u'package_show')({'model': model, 'ignore_auth': True}, {'id': pkg_id})
            member_delete, member_create = create_group_memberships_from_theme(
                {'model': model, 'ignore_auth': True, 'user': site_user['name']},
                pkg_dict
            )
            if member_delete or member_create:
                msg = "{} Updated package [{}]:".format(counter, pkg_id)
                if member_delete:
                    msg += ' removed from {}'.format(member_delete)
                if member_create:
                    msg += ' added to {}'.format(member_delete)
                click.secho(msg, fg="green", bold=True)
            else:
                click.secho("{} Checked package [{}] :: no actions required".format(counter, pkg_id))

        except Exception as e:
            error_shout(e)
            error_shout("{} Package '{}' was not found".format(counter, pkg_id))
