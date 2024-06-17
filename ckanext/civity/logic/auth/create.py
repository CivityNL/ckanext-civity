import ckan.plugins.toolkit as toolkit
import ckan.logic.auth as logic_auth
import ckan.authz as authz

import logging

log = logging.getLogger(__name__)


@toolkit.auth_allow_anonymous_access
def member_create(context, data_dict):
    group = logic_auth.get_group_object(context, data_dict)
    user = context['user']

    # User must be able to update the group to add a member to it
    permission = 'update'
    # However if the user is member of group then they can add/remove datasets

    if not group.is_organization and data_dict.get('object_type') == 'package':
        permission = 'manage_group'

    authorized = authz.has_user_permission_for_group_or_org(group.id,
                                                            user,
                                                            permission)
    if not authorized:

        # Civity workaround to assign group to a dataset/package
        if data_dict.get('object_type') == 'package' and data_dict.get('capacity') == 'member':
            return {'success': True}

        return {'success': False,
                'msg': _('User %s not authorized to edit group %s') %
                       (str(user), group.id)}
    else:
        return {'success': True}
