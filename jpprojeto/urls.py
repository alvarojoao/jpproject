"""{{ project_name }} URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/{{ docs_version }}/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.shortcuts import render

from django.conf.urls import url
from django.contrib import admin
from abastecimento.views import home,labels_available,labels_favorites,update_labels_favorites
from django.conf.urls import patterns
from django.contrib import admin
from django.http import HttpResponse
from abastecimento.models import Locacao
from django.forms import modelformset_factory
from django.forms import ModelForm

admin.autodiscover()

class LocacaoForm(ModelForm):
     class Meta:
         model = Locacao
         exclude=('criado_date','atualizado_date')


def my_view(request,id):
    # return HttpResponse("Hello!")
    if id:
        locacao = Locacao.objects.get(pk=id)  # if this is an edit form, replace the author instance with the existing one
    else: 
        locacao = Locacao()
    if request.POST:
        form = LocacaoForm(request.POST or None, instance=locacao)

        if form.is_valid():
            locacao = form.save(commit=True)
            if locacao.is_valid():
                locacao.save()
    # author_form = AuthorModelForm(instance=locacao) # setup a form for the parent

    # LocacaoFormSet = modelformset_factory(Locacao, exclude=('criado_date','atualizado_date'))
    form = LocacaoForm(request.POST or None, instance=locacao)

    # formset = LocacaoFormSet()
    return render(request, 'calendar/as.html',{'formset': form})

def get_admin_urls(urls):
    def get_urls():
        my_urls = patterns('',
            (r'^my_view/(?P<id>[0-9]*)$', admin.site.admin_view(my_view))
        )
        return my_urls + urls
    return get_urls

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^calendar/', include('calendarium.urls')),
    url(r'^customgraph/', home),
    url(r'^labels_available/', labels_available),
    url(r'^labels_favorites/', labels_favorites),
    url(r'^update_labels_favorites/', update_labels_favorites)
]

