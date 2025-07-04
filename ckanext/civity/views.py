from flask import Blueprint
from ckan.plugins import toolkit
from ckanext.civity.helpers import get_accessibility_info_enabled

civity_blueprint = Blueprint(u'civity', __name__)


def accessibility():
    return toolkit.render('accessibility/index.html')


def get_blueprints():
    if get_accessibility_info_enabled():
        civity_blueprint.add_url_rule(
            rule='/accessibility',
            view_func=accessibility,
            methods=['GET']
        )

    return [civity_blueprint]
