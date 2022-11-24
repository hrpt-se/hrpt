from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from cms.models import Page
from cms.menu_bases import CMSAttachMenu
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool

from . import views
from apps.accounts import views as accounts_views
from django.contrib.auth import views as auth_views

class SurveyMenu(CMSAttachMenu):
    name = "Survey menu"

    def get_nodes(self, request):
        """
        This method is used to build the menu tree.
        """
        # nodes = [
        #     NavigationNode(
        #         _("Symptoms survey"),
        #         reverse(views.index),
        #         "views.index",
        #     ),
        #     NavigationNode(
        #         _("Manage household"),
        #         reverse(views.people),
        #         "views.people",
        #     ),
        #     NavigationNode(
        #         _("My settings"),
        #         reverse(accounts_views.my_settings),
        #         "accounts_views.my_settings",
        #     ),
        #     NavigationNode(
        #         _("Change password"),
        #         reverse(auth_views.password_change),
        #         "auth_views.password_change",
        #     ),
        # ]

        nodes = []

        return nodes

menu_pool.register_menu(SurveyMenu)
