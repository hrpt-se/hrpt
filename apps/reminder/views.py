from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

from .models import (
    UserReminderInfo, get_upcoming_dates, get_prev_reminder,
    NewsLetterTemplate, QueuedEmail, ManualNewsLetter
)

from .send import create_message, send_message_and_update_reminder_info


import apps.pollster.models as pollster_models


@login_required
def unsubscribe(request):
    if request.method == "POST":
        info, _ = UserReminderInfo.objects.get_or_create(user=request.user, defaults={'active': True, 'last_reminder': request.user.date_joined})
        info.active = False
        info.save()
        return render_to_response('unsubscribe_successful.html', locals(), context_instance=RequestContext(request))
    return render_to_response('unsubscribe.html', locals(), context_instance=RequestContext(request))


@staff_member_required
def overview(request):
    dates_and_descriptions = get_upcoming_dates(datetime.now())
    upcoming = [{'date': d, 'description': description} for d, description in dates_and_descriptions]
    return render(request, 'overview.html', locals())


@staff_member_required
def manage(request, year, month, day, hour, minute):
    timenow = datetime(*map(int, [year, month, day, hour, minute, 59]))

    reminder_dict = get_prev_reminder(timenow, published=False)
    reminder = _user_reminder_translated(reminder_dict, request.user)

    if request.method == "POST":
        sent = True
        #eeerrr.... is_test_message is not a kwarg... is this just an error
        send_message_and_update_reminder_info(datetime.now(), request.user, reminder, None, is_test_message=True)

    return render(request, 'manage.html', locals())


@staff_member_required
def preview(request, year, month, day, hour, minute):

    int_params = map(int, [year, month, day, hour, minute, 59])
    date_and_time = datetime(*int_params)

    reminder_dict = get_prev_reminder(date_and_time, published=False)
    reminder = _user_reminder_translated(reminder_dict, request.user)

    text_base, html_content = create_message(request.user, reminder, settings.LANGUAGE_CODE)
    return HttpResponse(html_content)


def _user_reminder_translated(reminder_dict, user):
    info, _ = UserReminderInfo.objects.get_or_create(user=user, defaults={'active': True, 'last_reminder': user.date_joined})
    language = info.get_language()

    #TODO: just hardcode to swedish, then later remove internacionalization all together!!!!

    if not language in reminder_dict:
        language = settings.LANGUAGE_CODE
    if not language in reminder_dict:
        return None

    reminder = reminder_dict[language]

    return reminder


################################################################################
### New Newsletter System
################################################################################
# This is new code that implements the new manual newsletter reminder

@staff_member_required
def list_newsletter_templates(request):
    newsletterTemplates = NewsLetterTemplate.objects.all()
    return render(request, 'list_templates.html', locals())


@staff_member_required
def show_newsletter_template(request, id):
    # All this really does is passing the id to the url of an iframe...
    # then the iframe is rendered by show_newsletter_template_in_iframe

    surveys = pollster_models.Survey.objects.filter(status="PUBLISHED")

    template = NewsLetterTemplate.objects.language("sv").get(id=id)
    text_base, _ = create_message(request.user, template, 'sv')

    return render(request, 'show_template.html', {
        'id': id,
        'surveys': surveys,
        'plain_text_message': strip_tags(text_base)
    })


@staff_member_required
def show_newsletter_template_in_iframe(request,id):
    template = NewsLetterTemplate.objects.language("sv").get(id=id)
    reminder_contents_text, reminder_contents_html = create_message(request.user, template, "sv")
    # in this case we render as user admin. Maybe we want the ability to rend as another user???
    # or maybe have a test user as a fixture or something as a test

    data = {}
    if request.GET.get('plaintext'):
        data['reminder_contents'] = strip_tags(reminder_contents_text)
    else:
        data['reminder_contents'] = reminder_contents_html

    return render(request, 'show_newsletter_template_in_iframe.html', data)


@staff_member_required
def send_test_email_to_myself(request,newsletter_template_id):
    if request.method == "POST":

        template = NewsLetterTemplate.objects.language("sv").get(id=newsletter_template_id)
        text_base, html_content = create_message(request.user, template, "sv")
        text_content = strip_tags(text_base)

        msg = EmailMultiAlternatives(
            template.subject,
            text_content,
            "%s <%s>" % (template.sender_name, template.sender_email),
            [request.user.email],
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()

    return HttpResponse("Nothing to see here!!")


@staff_member_required
def send_manual_newsletter(request, newsletter_template_id):
    if request.method == "POST":
        template = NewsLetterTemplate.objects.language("sv").get(id=newsletter_template_id)
        newsletter = ManualNewsLetter.objects.create(
            sender_email=template.sender_email,
            sender_name=template.sender_name,
            subject=template.subject,
            message=template.message,
            template=template,
        )
        reminder = True if request.POST.get("reminder") else False
        users = _newsletter_recipients(shortname=request.POST.get("reminder_to_this_survey", None), reminder=reminder)
        for user in users:
            QueuedEmail.objects.create(user=user, manual_newsletter=newsletter)

    return HttpResponse("Nothing to see here!!")


def _newsletter_recipients(shortname=None, reminder=False):
    if not shortname:
        return User.objects.filter(is_active=True)

    survey = pollster_models.Survey.objects.get(shortname=shortname, status="PUBLISHED")
    if not reminder:
        return survey.members
    responses = survey.as_model().objects.all()
    return survey.members.exclude(pk__in=responses.values_list("user", flat=True))
