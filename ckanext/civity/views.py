from flask import Blueprint
from ckan.plugins import toolkit

civity_blueprint = Blueprint(u'civity', __name__)


def accessibility():
    return toolkit.render('accessibility/index.html')


civity_blueprint.add_url_rule(
    rule='/accessibility',
    view_func=accessibility,
    methods=['GET']
)


def get_blueprints():
    return [civity_blueprint]
