HRPT Developer Manual
=====================
This document contains information that hopefully will be useful for a 
developer tasked with extending or maintaining the HRPT system.

General system description
--------------------------
The system has the following capabilities:
  - Display information, facilitated by Django CMS.
  - Registering of users
  - Survey creation
  - Sending invites to the survey to site users
  - The possibility for users to respond to surveys


Usage documentation
-------------------
This document is focused on documenting how the system works with developers as
the target audience. Information on how the system can be used is available in 
the document "111111-Influenzanet_SurveyEditor.pdf" in the docs folder of the 
repo.


Apps:
-----
In the `/apps` folder you will find the following apps:

### Accounts
This app is responsible for user management within the system. It implements 
the user registration workflow which is outlined below.

### Count
This is a very simple app which exposes an endpoint that return the number of
users. It exists for legacy reasons only. Do not remove without approval, since 
other systems depend on this endpoint.

### HRPTinfo
The HRPTInfo app contains resources which is primarily focused on the 
presentation of info on the site, such as forms, template tags and CMS Plugins.

### LoginURL
One important feature of the system is to send newsletters or reminders, 
inviting registered users to answer a Survey. Within these invites a special 
URL can be used that sends the user to the site without having to log in. These 
special URLs are implemented in this app. 

The logic in this app could probably be merged into Reminder, the app 
responsible for sending out newsletters/reminders to reduce the number of apps.

One final note about the LoginURL is that it resides outside of the `apps/` 
folder. It should probably be moved to the same folder as the other apps for 
consistency.

### Partnersites
The HRPT system was initially built in partnership with a number of similar 
sites in different European countries, this app is a reminiscent of that. The
most important part of this app is the model `SiteSetting` which holds the logo
used in the header of the newsletter.

### Pollster
The apps Pollster and Survey have a lot in common. They are both responsible 
for the surveys in the system. The reason why these two apps share the 
responsibility for the surveys is not known, and they could probably be merged.

The Pollster app is primarily responsible for administrating, editing and 
creating surveys. The editing interface for surveys is implemented in 
javascript in this app.


### Reminder
The reminder app is responsible for sending emails with newsletters and 
reminders to the registered users of this site. The app relies on the mail 
sending daemon which must be running. See details on how to run the daemon 
further down in the document.

### Survey
The Survey app is, as mentioned previously, co-responsible for the Surveys 
together with the Pollster app. The Survey app has, among other things, logic 
for displaying Surveys to the end user.


User Registration Flow
----------------------
The first thing to mention regarding user registration is that the site does 
not allow registration for anyone who is interested. The system intends to have
a user base that is statistically representative and for that reason all users
are invited through a process that is outside the scope of this document. To
sign up on the site, the user needs a code that is sent out in the invitation 
as a part of the above mentioned process.

### Step 1: SurveyIdCode
To create a new account the user needs to have a `SurveyIdCode`. This model is 
defined in `/apps/survey/models.py`. The easiest way to create a new 
SurveyIdCode is through the Django admin interface. When creating a new code,
the field `idcode` is the only mandatory field.

Each `SurveyIdCode` is limited to signing up one user. I.e. to sign up ten 
users, ten `SurveyIdCode`s needs to be created.

### Step 2: User Signup
When a new `SurveyIdCode` is created, the user can go to the registration form
to provide details such as username, email address, password, the id code and 
so on. 

When the user submits the form successfully the server will create instances of
two models, Django's built in `User` model (`django.contrib.auth.models.User)`
and the model `UserProfile` (`apps.accounts.models.UserProfile`). Creating the
`UserProfile` instance is done in the `user_registered` signal defined in 
`apps/accounts/signals.py` handler. This handler receives the `user_registered` 
signal. The `UserProfile` model stores user information which is used later in 
the registration process. 

The user will be marked as inactive and as such unable to
login to the account.

The server will also send an email asking the user to activate the account by 
clicking on a link in the mail. The activation procedure is facilitated by the 
`django-registration` module. More information about the library can be found 
here: (https://django-registration.readthedocs.io)

### Step 3: User Activation
When the user opens the activation link from the mail sent from the server 
after successful registration the `User` instance created in the previous step
is marked as active which means that the user is now able to login. This is 
facilitated, as the activation email, by the `django-register` module.

Just after the User is marked as active, an instance of the the supplemental 
user model `SurveyUser` (`apps.survey.models.SurveyUser`) is instantiated. This
is done by `TweakedDefaultActivationView.activate()` defined in 
`apps/accounts/backends.py`. 

This concludes the user registration process.

Question Type Definition
------------------------
The system includes a few different types of question types (Open Answer, 
Single Choice, Multiple Choice etc.). The question types are unfortunately not 
designed to be pluggable, so adding new question types requires adding new code
and markup on different places in the system. This section tries to show those
places in the code base.

### The Question Model
All questions are stored using the `Question` (`apps.pollster.models.Question`)
model which in turn have a foreign key relationship to the `Survey` model. The
type of question is defined through the field `type` on the `Question` model. 
This field is a `CharField` and no validation is applied to the field, which 
allows for creation of new question types without modification.

For each question type there is a defined property on the `Question` model to 
identify whether the Question is of said type, `is_text()`, `
is_single_choice()`, `is_multiple_choice()` etc. A new such property needs to
be added when adding a new question type.

The Question model has a method named `as_fields()` which through an if 
statement determines how the question should be serialized depending on the 
type. When adding a new question type, a new clause needs to be added for the
new type.

### The Tool Box in the Survey Editor
To be able to use the new question type it needs to be added to the drop down
menu of question types available when adding a new question in the survey 
editor. This part of the editor is using the template found in 
`/apps/pollster/templates/properties.html`. Find the select element named 
"tool_question_type" and add a new option for your new question type.

### Templates for the Survey Editor
After adding the new question type to the list of types in the editor, it is 
technically possible to add the question. However, before any sign of the new
question can be displayed in the editor a template for the question must be 
added. A word of caution, you will need to create three templates for each new 
question type, one template for the representation when creating a new question 
in the survey editor, one template used when you load a saved survey still in 
the editor and finally one for the representation in the running survey, facing 
the end user. In this step we will add the templates for the editor.

The template used when creating a new question needs to be placed in the file 
`/apps/pollster/templates/properties.html`. The template of the new question 
type needs to be added in a div with the class name `template-<question-type>`.
This div should be placed inside the div with class `wok-templates`.

All questions share a common template that is used when a stored survey is 
loaded into the editor. This template is located in
`/apps/pollster/templates/question_edit.html`. The template is using if 
statements to separate how different types of questions are rendered. To add 
support for a new type you need to append a new if statement containing the 
markup for the new type.

### Showing and Hiding Provider settings
When you click on questions of different type in the survey editor you can 
notice that different boxes is displayed in the left hand side of the editor
depending on the type of question that is selected. These boxes are called 
providers within the system. Control of which provides should be displayed 
needs to be added for each new question type. This is done in the file 
`/apps/pollster/static/pollster/wok/js/wok.pollster.providers.js`. The file 
defines a class `QuestionPropertyProvider` with a method `attach()`. This 
method contains a if statement showing and hiding the different providers. Add
a new else if clause for the new question type.

Also located in `wok.pollster.providers.js` there is a function 
`getQuestionType()` returning a regex matching all question types. Add the new 
question type to this regex.

### User Facing Template
Finally, we need to add a template rendering the question type when the Survey
is running. This is done similarly to the way that questions loaded from a 
stored survey are rendered but from a different file. All question types share
a template located in `/apps/survey/templates/questions_run.html`. Add a new if
statement for the new question type and add the appropriate markup.

Upgrading a deployed system
---------------------------
Since the system is built on using the Django framework the upgrade procedure 
follows the general upgrade producedure. Outlined below are most of the steps
that could be necessary to run.

The system should be located on `/var/www/hrpt/` on all servers. Begin by 
logging in to the server and go to that folder.

### Stop Apache
Before maintenance activities begin, its recommended to stop Apache to make 
sure that there are no active users on the site.
```bash
sudo service apache2 stop 
```

### Upgrade Ubuntu
It's recommended to keep Ubuntu upgraded to avoid exploits in the operating 
system.
```bash
sudo apt update
sudo apt upgrade
```

### Download the most recent version of the current branch
Before this command is executed, find out which user owns the files then 
perform the git pull as that user (replace <owner> with the username of the 
owner).
```bash
sudo -u <owner> git pull
```

### Update Python Dependencies
This step is only necessary to perform in case there have been changes to the
dependencies of the system, i.e. the file `requirements.txt` has changed.
```bash
sudo pip install -r requirements.txt
```

### Update Translations
This step is only required if there has been changes to the translations file
(`django.po`).
```bash
sudo -u <owner> python manage.py compilemessages
```

### Update Static Content
This step is required if static content (javascript, image, css etc.) is 
updated. It moves the content from the static folders in the system to a 
dedicated folder where it is hosted by the Apache server. Make sure to identify
which users that owns the static content (located in /var/lib/hrpt) and run the 
command as that user.
```bash
sudo -E -u <owner> python manage.py collectstatic
```

### Update Database Schemas
This step is required if changes has been made to the models which are 
reflected in unapplied migration files.
```bash
python manage.py migrate
```

### Restart Apache
```bash
sudo service apache2 start
```
