# -*- coding: utf-8 -*-

from django.views.generic.edit import CreateView, UpdateView, FormMixin
from django.views.generic.list import ListView
from django.contrib import messages
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import paginator as django_paginator

from lumina.models import Image
from lumina.forms import ImageCreateForm, ImageUpdateForm, ImageSearchForm
from lumina import models


# ===============================================================================
# Image
# ===============================================================================

class ImageListView(ListView, FormMixin):
    model = Image
    PAGE_RESULT_SIZE = settings.LUMINA_DEFAULT_PAGINATION_SIZE

    def get_queryset(self):
        return Image.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_search'] = True
        context['form'] = self.form
        # overwrites 'object_list' from `get_queryset()`
        context['object_list'] = self.search_result_qs
        context['hide_search_result'] = self.search_result_qs is None
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        self.form = self.get_form(form_class=ImageSearchForm)
        self.search_result_qs = None

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = self.get_form(form_class=ImageSearchForm)
        self.search_result_qs = self._do_search(request, self.form)

        return super().get(request, *args, **kwargs)

    def _do_search(self, request, form):
        # Validate form
        if not form.is_valid():
            messages.error(request,
                           "Los parámetros de la búsqueda son inválidos")
            return Image.objects.none()

        # Do the search
        qs = Image.objects.visible_images(self.request.user)
        if form.cleaned_data['customer']:
            qs = qs.filter(session__customer=form.cleaned_data['customer'])

        if form.cleaned_data['session_type']:
            qs = qs.filter(session__session_type=form.cleaned_data['session_type'])

        if form.cleaned_data['fecha_creacion_desde']:
            qs = qs.filter(created__gte=form.cleaned_data['fecha_creacion_desde'])

        if form.cleaned_data['fecha_creacion_hasta']:
            qs = qs.filter(created__lte=form.cleaned_data['fecha_creacion_hasta'])

        # ----- <OrderBy> -----
        qs = qs.order_by('session__customer__name',
                         'session__customer__id',
                         'session__name',
                         'session__id',
                         'created')
        # ----- </OrderBy> -----

        # ----- <Paginate> -----
        result_paginator = django_paginator.Paginator(qs, self.PAGE_RESULT_SIZE)
        try:
            qs = result_paginator.page(self.form.cleaned_data['page'])
        except django_paginator.PageNotAnInteger:  # If page is not an integer, deliver first page.
            qs = result_paginator.page(1)
        except django_paginator.EmptyPage:  # If page is out of range (e.g. 9999), deliver last page of results.
            qs = result_paginator.page(result_paginator.num_pages)
        # ----- </Paginate> -----

        return qs


class ImageCreateView(CreateView):
    model = Image
    form_class = ImageCreateForm
    template_name = 'lumina/image_add.html'
    pk_url_kwarg = 'session_id'

    def _get_queryset(self):
        return models.Session.objects.visible_sessions(self.request.user)

    def get_success_url(self):
        return reverse('session_detail', args=[self.object.session.pk])

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio

        #    *** before super().form_valid()
        #    (Pdb) form.instance.image.name
        #    u'estado-del-arte.odt'
        #    *** after super().form_valid()
        #    (Pdb) form.instance.image.name
        #    u'images/2013/06/02/estado-del-arte_2.odt'
        form.instance.set_original_filename(form.instance.image.name)

        #    *** befor and after super().form_valid() this works
        #    (Pdb) form.instance.image.size
        #    77052
        form.instance.size = form.instance.image.size

        # TODO: is NOT safe to trust the content type reported by the user
        #    *** befor super().form_valid() this works
        #    (Pdb) form.files['image'].content_type
        #    u'application/vnd.oasis.opendocument.text'
        form.instance.set_content_type(form.files['image'].content_type)

        ret = super().form_valid(form)
        messages.success(self.request, 'La imagen fue creada correctamente')

        #    *** after super().form_valid() `form.instance.image.name` has the
        #        filename from the filesystem, which WILL BE DIFFERENT from the
        #        original filename on the user's computer
        #    (Pdb) form.instance.image.name
        #    u'images/2013/06/02/estado-del-arte_2.odt'

        return ret

    def get_initial(self):
        session_id = self.kwargs[self.pk_url_kwarg]
        initial = super().get_initial()
        initial.update({
            'session': self._get_queryset().get(pk=session_id),
        })
        return initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        session_id = self.kwargs[self.pk_url_kwarg]
        form_kwargs['session'] = self._get_queryset().get(pk=session_id)
        return form_kwargs

    def get_context_data(self, **kwargs):
        session_id = self.kwargs[self.pk_url_kwarg]
        return super().get_context_data(
            session=self._get_queryset().get(pk=session_id),
            **kwargs
        )


class ImageUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = Image
    form_class = ImageUpdateForm
    template_name = 'lumina/image_update_form.html'

    #    def get_context_data(self, **kwargs):
    #        context = super(ImageUpdateView, self).get_context_data(**kwargs)
    #        context.update({'menu_image_update_flag': 'active'})
    #        return context

    def get_queryset(self):
        return self.request.user.studio.image_set.all()

    def form_valid(self, form):
        ret = super(ImageUpdateView, self).form_valid(form)
        messages.success(self.request, 'La imagen fue actualizada correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(ImageUpdateView, self).get_context_data(**kwargs)
        context['form'].fields['session'].queryset = self.request.user.studio.session_set.all()
        return context
