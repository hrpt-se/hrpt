from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from registration.backends.model_activation.views import RegistrationView


from .backend import TweakedDefaultActivationView
from . import views
from .forms import CaptchaUnicodeRegistrationForm, CaptchaPasswordResetForm

urlpatterns = [
    # From registration.backends.default.urls
    url(r'^activate/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ),
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        TweakedDefaultActivationView.as_view(
            template_name='registration/activate.html'

        ),
        name='registration_activate'),
    url(r'^register/$',
        RegistrationView.as_view(
            template_name='registration/registration_form.html',
            form_class=CaptchaUnicodeRegistrationForm
        ),
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(
            template_name='registration/registration_complete.html'
        ),
        name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'
        ),
        name='registration_disallowed'),
    # From registration.auth_urls
    url(r'^login/$', auth_views.LoginView.as_view(), name='auth_login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='auth_logout'),
    url(r'^password/change/$', auth_views.PasswordChangeView.as_view(), name='password_change'),
    url(r'^password/change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^password/reset/$',
        auth_views.PasswordResetView.as_view(form_class=CaptchaPasswordResetForm),
        name='password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),

    url(r'^settings/email/$', views.my_settings, {'form': 'email'}),
    url(r'^settings/password/$', views.my_settings, {'form': 'password'}),
    url(r'^settings/username/$', views.my_settings, {'form': 'username'}),
    url(r'^settings/deactivate/$', views.my_settings, {'form': 'deactivate'}),
    url(r'^settings/$', views.my_settings, name='settings')
]
