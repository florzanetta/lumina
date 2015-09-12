# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views import generic

from lumina import models
from lumina import forms

logger = logging.getLogger(__name__)


class StudioUserListView(generic.ListView):
    model = models.LuminaUser
    template_name = 'lumina/user_list_studio.html'

    def get_queryset(self):
        return self.request.user.get_all_photographers()
