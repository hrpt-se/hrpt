import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.conf import settings

from parler.models import TranslatableModel, TranslatedFields

from apps.survey.models import SurveyUser


"""
IMPORTANT:
When reading this file, it is necessairy  to take into account that quite a 
lot of stuff is actually duplicated functionality!
Scroll down to the part marked with "NEW CODE" to read more.
"""


# A short word on terminology:
# "Reminder" may refer to a NewsLetter object, or simply a placeholder
# that's based on the is_default_reminder NewsLetterTemplate

NO_INTERVAL = -1
WEEKLY_WITH_BATCHES = -2


class UserReminderInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_reminder = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField()
    language = models.CharField(max_length=5, blank=True, null=True)

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.__unicode__()

    def get_language(self):
        if not self.language:
            return settings.LANGUAGE_CODE
        return self.language


class ReminderSettings(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    send_reminders = models.BooleanField(
        _("Send reminders"),
        help_text=_("Check this box to send reminders")
    )

    interval = models.IntegerField(
        _("Interval"),
        choices=(
            (7, _("Weekly")),
            (14, _("Bi-weekly")),
            (NO_INTERVAL, _("Don't send reminders at a fixed interval")),
            (WEEKLY_WITH_BATCHES, "Send exactly 7 days after the last action "
                                  "was taken.")),
        null=True,
        blank=True
    )

    begin_date = models.DateTimeField(
        _("Begin date"),
        help_text="Date & time of the first reminder and point of reference "
                  "for subsequent reminders; "
                  "(Time zone: %s)" % settings.TIME_ZONE,
        null=True,
        blank=True
    )

    batch_size = models.IntegerField(
        "Batch size",
        null=True,
        blank=True,
        help_text="Batch size determines the max. sent emails per call to "
                  "'reminder_send'; choose in coordinance with your crontab "
                  "interval and total users; Leave empty to not have "
                  "any maximum"
    )
    currently_sending = models.BooleanField(
        "Currently sending",
        help_text="This indicates if the reminders are being sent right now. "
                  "Don't tick this box unless you absolutely know what "
                  "you're doing",
        default=False
    )

    last_process_started_date = models.DateTimeField(
        "Last process started at",
        help_text="This indicates if the reminders are being sent right now. "
                  "Don't change this value unless you absolutely know what "
                  "you're doing"
    )

    def __unicode__(self):
        return _("Reminder settings")

    def __str__(self):
        return self.__unicode__()

    def get_interval(self):
        if self.interval == WEEKLY_WITH_BATCHES:
            return 7
        return self.interval


class NewsLetterTemplate(TranslatableModel):
    is_default_reminder = models.BooleanField(
        _("Is default reminder"),
        help_text=_("If this option is checked this template is the standard "
                    "template for reminder emails.")
    )

    is_default_newsitem = models.BooleanField(
        _("Is default newsitem"),
        help_text=_("If this option is checked this template is the standard "
                    "template for new news items.")
    )

    sender_email = models.EmailField(
        _("Sender email"),
        help_text="Only use email addresses for your main domain to ensure "
                  "deliverability"
    )

    sender_name = models.CharField(_("Sender name"), max_length=255)

    translations = TranslatedFields(
        subject=models.CharField(max_length=255),
        message=models.TextField(
            help_text="The strings {{ url }} and {{ unsubscribe_url }} may be "
                      "used to refer to the profile url and unsubscribe url."
        )
    )

    def __unicode__(self):
        return self.subject

    def __str__(self):
        return self.__unicode__()


class NewsLetter(TranslatableModel):
    date = models.DateTimeField(_("Date"), unique=True, choices=[])

    sender_email = models.EmailField(
        _("Sender email"),
        help_text="Only use email addresses for your main domain to ensure "
                  "deliverability"
    )

    sender_name = models.CharField(_("Sender name"), max_length=255)

    published = models.BooleanField(
        "Is published",
        help_text="Uncheck this box to postpone sending of this newsletter "
                  "until the box is checked.",
        default=True
    )

    translations = TranslatedFields(
        subject=models.CharField(max_length=255),
        message=models.TextField(
            help_text="The strings {{ url }} and {{ unsubscribe_url }} "
                      "may be used to refer to the profile url and "
                      "unsubscribe url."
        )
    )

    def __unicode__(self):
        return self.subject

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ("-date",)


class MockNewsLetter(object):
    def __init__(self):
        self.date = None
        self.sender_email = None
        self.sender_name = None
        self.subject = None
        self.message = None


class ReminderError(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    traceback = models.TextField()

    def __unicode__(self):
        return self.message

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ("-timestamp",)

    def email(self):
        return self.user.email


def get_settings():
    try:
        return ReminderSettings.objects.first()
    except ReminderSettings.DoesNotExist:
        return None


def get_upcoming_dates(now):
    settings = get_settings()
    if not settings or not settings.send_reminders or not settings.begin_date:
        raise StopIteration()

    if settings.get_interval() < 0:
        yield now, "Current newsletter"
        raise StopIteration()

    to_yield = 7
    current = settings.begin_date

    while to_yield > 0:
        if current >= now - datetime.timedelta(2 * settings.get_interval()):
            diff = current - now
            days = abs(diff.days) % 7
            weeks = abs(diff.days) / 7
            if diff.days > 0:
                if weeks == 0:
                    yield current, \
                          _("%(current)s (in %(days)s days)") % locals()
                else:
                    yield current, \
                          _("%(current)s (in %(weeks)s weeks)") % locals()
            else:
                if weeks == 0:
                    yield current, \
                          _("%(current)s (%(days)s days ago)") % locals()
                else:
                    yield current, \
                          _("%(current)s (%(weeks)s weeks ago)") % locals()
            to_yield -= 1
        current += datetime.timedelta(settings.get_interval())


def get_default_for_reminder(language):
    if not NewsLetterTemplate.objects.language(language)\
                                     .filter(is_default_reminder=True)\
                                     .exists():
        return None

    return NewsLetterTemplate.objects.language(language)\
                                     .filter(is_default_reminder=True)\
                                     .first()


def get_default_for_newsitem(language):
    if not NewsLetterTemplate.objects.language(language)\
                                 .filter(is_default_newsitem=True)\
                                 .exists():
        return None
    return NewsLetterTemplate.objects.language(language)\
                                     .filter(is_default_newsitem=True)\
                                     .first()


def get_prev_reminder_date(now, published=True):
    """Returns the date of the previous reminder or None if there's no
    such date"""

    settings = get_settings()

    if not settings or not settings.send_reminders or not settings.begin_date \
            or now < settings.begin_date:
        return None

    if settings.interval == NO_INTERVAL:
        qs = NewsLetter.objects.filter(date__lte=now)\
                               .exclude(date__gt=now)\
                               .order_by("-date")
        if published:
            qs = qs.filter(published=published)
        qs = list(qs)
        if len(qs) == 0:
            return None
        return qs[0].date

    current = settings.begin_date
    prev = settings.begin_date

    while True:
        if current >= now:
            return prev
        prev = current
        current += datetime.timedelta(settings.get_interval())


def get_prev_reminder(now, published=True):
    """Returns the reminder (newsletter/tempate) to send at a given moment
    as a dict with languages as keys, or None if there is no such reminder

    TODO: while we don't remove i18n alltogether, this should actually fail on
    the absense of the desired translation instead of returning None. There is
    no reason not to fail if indeed we are in a situation where an error has
    occurred.

    TODO: seriously refactor this..., this p() stuff rinks. Break this up in
    two functions, what is the point of calleing p() a zillion times on the
    same argument?
    """

    def p(qs):
        if published:
            return qs.filter(published=published)
        return qs

    prev_date = get_prev_reminder_date(now, published)
    if prev_date is None:
        return None

    if p(NewsLetter.objects.filter(date=prev_date)).count():
        result = {}
        for language, name in settings.LANGUAGES:
            if p(NewsLetter.objects.language(language).filter(date=prev_date)):
                result[language] = p(
                    NewsLetter.objects.language(language)).get(date=prev_date)
        return result

    result = {}
    for language, name in settings.LANGUAGES:
        template = get_default_for_reminder(language)
        if template is None:
            continue

        newsletter = MockNewsLetter()
        newsletter.date = prev_date
        newsletter.sender_email = template.sender_email
        newsletter.sender_name = template.sender_name
        newsletter.subject = template.subject
        newsletter.message = template.message
        result[language] = newsletter

    return result


def get_reminders_for_users(users):
    """
    returns: user, reminder, language
    """

    now = datetime.datetime.now()
    reminder_dict = get_prev_reminder(now)

    # this reminder dics is a template
    if not reminder_dict:
        raise StopIteration()

    batch_size = get_settings().batch_size if get_settings() else None

    yielded = 0
    for user in users:
        if batch_size and yielded >= batch_size:
            raise StopIteration

        info, _ = UserReminderInfo.objects.get_or_create(
            user=user,
            defaults={
                'active': True,
                'last_reminder': user.date_joined
            }
        )

        if not info.active:
            continue

        language = info.get_language()
        if language not in reminder_dict:
            language = settings.LANGUAGE_CODE

        reminder = reminder_dict[language]

        if info.last_reminder is None:
            yield user, reminder, language
            yielded += 1
            continue

        if get_settings() and get_settings().interval == WEEKLY_WITH_BATCHES:
            survey_users = SurveyUser.objects.filter(user=user, deleted=False)
            if not survey_users.count():
                SurveyUser.objects.create(
                    user=user,
                    name=user.username
                )
                survey_users = SurveyUser.objects.filter(user=user)

            last_action_date = max(su.get_last_weekly_survey_date()
                                   for su in survey_users)

            if info.last_reminder and info.last_reminder > last_action_date:
                last_action_date = info.last_reminder

            last_action = (now - last_action_date).days
            last_action_long_ago_enough = last_action >= 7

            if not last_action_long_ago_enough:
                continue

        if info.last_reminder < reminder.date:
            yield user, reminder, language
            yielded += 1


"""
The email sending was too intricate and most of its functionality depends on 
database registers that are used as state storages rather than actual data.
For example, decisions of weather to send or not an email, are based on colums 
like "last active" or is_active.
This makes it impossible to track what happened once in the future.

We leave the current system as is, and create a new one by side, but we do use 
the ExistingModel and the UserReminderInfo model. Although we specifically 
avoid writing to the latest.

"""


class ManualNewsLetter(models.Model):
    """
    This is to hold a log of all the instances where we sent a mass email.
    We had the NewsLetter model in the previous implementation, but it was a
    bag of lethal snakes. Let's create a new table only for manual email sends
    and keep it to the point.

    This should contain everything that ihat is necessairy to create an email
    message (except from the the recipient of course)Most fields are copied
    from the origin template.
    A reference to the template where the contents originated from is kept
    anyway for reference
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    template = models.ForeignKey(NewsLetterTemplate, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.subject

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ("-timestamp",)


class FailedEmail(models.Model):
    """
    We already had ReminderError but let's leave it alone
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manual_newsletter = models.ForeignKey(ManualNewsLetter, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    traceback = models.TextField()

    def __unicode__(self):
        return self.message

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ("-timestamp",)


class QueuedEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manual_newsletter = models.ForeignKey(ManualNewsLetter, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class SentEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manual_newsletter = models.ForeignKey(ManualNewsLetter, on_delete=models.CASCADE)
    queued = models.DateTimeField()  # TODO: remove the field
    sent = models.DateTimeField(auto_now_add=True)
