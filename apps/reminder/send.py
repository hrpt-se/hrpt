import datetime
from traceback import format_exc

from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader, Template
from django.urls import reverse
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils.translation import activate

import loginurl.utils #This is a third party app. Just letting you know...

from apps.partnersites.context_processors import site_context

from .models import get_reminders_for_users, UserReminderInfo, ReminderError


def create_message(user, message, language):
    if language:
        activate(language)

    site_url = '%s://%s' % (settings.URL_SCHEME, Site.objects.get_current().domain)

    inner_template = Template(message.message)

    survey_list_url = '%s://%s%s' % (settings.URL_SCHEME, Site.objects.get_current(), "/sv/valkommen/")
    profile_url = '%s://%s%s' % (settings.URL_SCHEME, Site.objects.get_current(), "/accounts/settings/")

    context_dict = {
        'url': get_self_authenticating_url(user, survey_list_url),
        'profile_url': get_self_authenticating_url(user, profile_url),
        # 'unsubscribe_url': get_self_authenticating_url(user, reverse('unsubscribe')),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
    }
    context_dict.update(site_context())
    context_dict['site_logo'] = site_url + context_dict['site_logo']

    inner = inner_template.render(Context(context_dict))

    context_dict['inner'] = inner
    context_dict['MEDIA_URL'] = '%s%s' % (site_url, settings.MEDIA_URL)
    context_dict['message'] = message

    templ = loader.get_template('message.html')

    return inner, templ.render(context_dict)


def send_reminders(fake=False):
    active_users = User.objects.filter(is_active=True)

    # returns user, message, language
    reminders = get_reminders_for_users(active_users)
    i = 0
    for (user, message, language) in reminders:
        if not fake:
            send_message_and_update_reminder_info(user, message, language)
        else:
            print('Fake sending', user.email, message.subject)
        i = i + 1
    return i


def get_self_authenticating_url(user, target_url):
    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    usage_left = 5
    key = loginurl.utils.create(user, usage_left, expires, target_url)
    domain = Site.objects.get_current()
    path = reverse('loginurl-index').strip('/')
    loginurl_base = '%s://%s/%s' % (settings.URL_SCHEME, domain, path)
    return '%s/%s' % (loginurl_base, key.key)


def send_message_and_update_reminder_info(user, message, language, is_test_message=False):
    now = datetime.datetime.now()
    text_base, html_content = create_message(user, message, language)
    text_content = strip_tags(text_base)
    msg = EmailMultiAlternatives(
        message.subject,
        text_content,
        "%s <%s>" % (message.sender_name, message.sender_email),
        [user.email],
    )

    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except Exception as e:
        ReminderError.objects.create(
            user=user,
            message=str(e),
            traceback=format_exc(),
        )

    if not is_test_message:
        info = UserReminderInfo.objects.get(user=user)
        info.last_reminder = now
        info.save()
