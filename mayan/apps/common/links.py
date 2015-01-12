from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _


def has_usable_password(context):
    return context['request'].user.has_usable_password


link_password_change = {'text': _(u'Change password'), 'view': 'common:password_change_view', 'famfam': 'computer_key', 'condition': has_usable_password}
link_current_user_details = {'text': _(u'User details'), 'view': 'common:current_user_details', 'famfam': 'vcard'}
link_current_user_edit = {'text': _(u'Edit details'), 'view': 'common:current_user_edit', 'famfam': 'vcard_edit'}

link_about = {'text': _(u'About'), 'view': 'common:about_view', 'famfam': 'information'}
link_license = {'text': _(u'License'), 'view': 'common:license_view', 'famfam': 'script'}

link_current_user_locale_profile_details = {'text': _(u'Locale profile'), 'view': 'common:current_user_locale_profile_details', 'famfam': 'world'}
link_current_user_locale_profile_edit = {'text': _(u'Edit locale profile'), 'view': 'common:current_user_locale_profile_edit', 'famfam': 'world_edit'}

link_logout = {'text': _(u'Logout'), 'view': 'common:logout_view', 'famfam': 'door_out'}
