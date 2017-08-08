# -*- coding: utf-8 -*-

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
from abastecimento.views import home,balancotable,labels_available,labels_favorites,update_labels_favorites,get_veiculo_km
from django.conf.urls import patterns
from django.contrib import admin
from django.http import HttpResponse
from abastecimento.models import Locacao,Veiculo,ManutencaoVeiculo
from django.forms import modelformset_factory
from django.forms import ModelForm
from django import forms
from django.shortcuts import redirect
import datetime
from django.template import Context, Template
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required

admin.autodiscover()
from django import template


class LocacaoForm(ModelForm):
    readonly = ('hodometroInicial',)
    hodometroInicial =  forms.CharField(widget=forms.TextInput(attrs={'readonly':'True'}))
    data_inicio =  forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.DateInput(attrs={'readonly':'True'},format='%d/%m/%Y'))
    data_fim =  forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.DateInput(attrs={'readonly':'True'},format='%d/%m/%Y'))
    class Media:
        js = ['/static/js/action_change.js']
    def __init__(self, *args, **kwargs):
        super(LocacaoForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance',None) and kwargs.get('instance',None).pk:
            self.fields['veiculo'].disabled = True
            self.fields['obra'].disabled = True

    class Meta:
        model = Locacao
        exclude=('criado_date','atualizado_date','hodometro_date')
        readonly = ('hodometroInicial','data_inicio','data_fim')

@login_required
def locacao(request,id):
    # return HttpResponse("Hello!")
    locacao = Locacao()
    # author_form = AuthorModelForm(instance=locacao) # setup a form for the parent
    # LocacaoFormSet = modelformset_factory(Locacao, exclude=('criado_date','atualizado_date'))
    form = LocacaoForm(request.POST or None, instance=locacao)
    # formset = LocacaoFormSet()
    locacaos = Locacao.objects.all()

    return render(request, 'locacao/locacao.html',{u'title':'Locação','site_header':'Ancar Admin','formset': form,'locacaos':locacaos})

@login_required
def balanco(request,id):
    veiculos = Veiculo.objects.all()
    return render(request, 'custos/balanco.html',{u'title':'balanco','site_header':'Ancar Admin'})

@login_required
def abastecimento_grafico(request,id):
    # 
    # context = template.RequestContext(request)
    return render(request, 'abastecimento/graficos.html',{u'title':'balanco','site_header':'Ancar Admin'})

@login_required
def save_locacao(request,id):
    if id is not None:
        locacao = Locacao.objects.get(pk=id)  # if this is an edit form, replace the author instance with the existing one
    else:
        locacao = Locacao()

    if request.POST:
        form = LocacaoForm(request.POST or None, instance=locacao)

        if form.is_valid():
            locacao = form.save(commit=True)
            if locacao.data_fim>=locacao.veiculo.hodometro_date:
                hodometro_diff = locacao.hodometroFinal - locacao.veiculo.hodometro
                locacao.veiculo.hodometro = locacao.hodometroFinal
                locacao.veiculo.hodometro_date = locacao.data_fim
                locacao.veiculo.save()
                manutencaoProgramados = ManutencaoVeiculo.objects.filter(veiculo__placa=locacao.veiculo.placa)
                for item in manutencaoProgramados:
                    item.valorAcumulado = item.valorAcumulado + hodometro_diff
                    item.save()

    return redirect('/admin/locacao/')

@csrf_exempt
def delete_locacao(request,id):
    if id is not None:
        locacao = Locacao.objects.get(pk=id)  # if this is an edit form, replace the author instance with the existing one
        if locacao and request.method=='POST':
            locacao.delete()

    return redirect('/admin/locacao/')

def load_locacao(request,id):
    if id is not None:
        locacao = Locacao.objects.get(pk=id)  # if this is an edit form, replace the author instance with the existing one
    else:
        locacao = Locacao()
    form = LocacaoForm(request.POST or None, instance=locacao)
    form.readonly = form.readonly + ('veiculo',)
    return HttpResponse(form.as_p())

def get_admin_urls(urls):
    def get_urls():
        my_urls = [ 
            url(r'^abastecimento/balanco/(?:(?P<id>[0-9]+))?$', admin.site.admin_view(balanco)),
            url(r'^abastecimento/abastecimento_grafico/(?:(?P<id>[0-9]+))?$', admin.site.admin_view(abastecimento_grafico)),
            url(r'^locacao/(?:(?P<id>[0-9]+))?$', admin.site.admin_view(locacao)),
            url(r'^locacao/save_locacao/(?:(?P<id>[0-9]+))?$', admin.site.admin_view(save_locacao)),
            url(r'^locacao/delete_locacao/(?:(?P<id>[0-9]+))?$', admin.site.admin_view(delete_locacao)),
            url(r'^locacao/load_locacao/(?:(?P<id>[0-9]+))?$', admin.site.admin_view(load_locacao))
        ]
        return my_urls + urls
    return get_urls

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # url(r'^calendar/', include('calendarium.urls')),
    url(r'^customgraph/', home),
    url(r'^balancotable/', balancotable),
    url(r'^get_veiculo_km/(?P<id>.+)', get_veiculo_km),
    url(r'^labels_available/', labels_available),
    url(r'^labels_favorites/', labels_favorites),
    url(r'^update_labels_favorites/', update_labels_favorites)
]

