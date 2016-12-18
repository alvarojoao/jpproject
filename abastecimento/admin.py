#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from import_export import resources
from django.contrib.auth.admin import UserAdmin

from import_export.admin import ImportExportMixin, ImportExportModelAdmin
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User

# Register your models here.
from django.db import transaction
from abastecimento.models import Grupo,Abastecimento,Posto,Veiculo,Operador,Obra,TIPO_VEICULOS,ItemManutencao,ItemManutencaoVeiculo,Locacao,ItemManutencaoProgramado,ItemManutencaoNaoProgramado
from django import forms
from django.utils.translation import ugettext_lazy as _

from django.conf.urls import patterns
from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.db.models import F


# class ResponsavelAdmin(UserAdmin):

# 	search_fields = ['username']

# admin.site.register(Responsavel, ResponsavelAdmin)
admin.site.site_title = 'Ancar Modulo Administrativo'
admin.site.site_header = 'Ancar Admin'

class GrupoAdmin(admin.ModelAdmin):
	pass

admin.site.register(Grupo, GrupoAdmin)


class ItemManutencaoProgramadoAdmin(admin.ModelAdmin):
	pass


admin.site.register(ItemManutencaoProgramado, ItemManutencaoProgramadoAdmin)


class ItemManutencaoNaoProgramadoAdmin(admin.ModelAdmin):
	pass

admin.site.register(ItemManutencaoNaoProgramado, ItemManutencaoNaoProgramadoAdmin)




class ItemManutencaoAdmin(admin.ModelAdmin):
	class  Meta:
		proxy = True
		app_label = 'equipamento'
	pass

admin.site.register(ItemManutencao, ItemManutencaoAdmin)

class ManutencaoAcionarFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Veiculos precisando manutenção')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'manutencao'
    default_status = ('Precisa', _('manutencao'))

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('Todos', _('Todos')),
            ('Precisa', _('manutencao')),
            ('NaoPrecisa', _('sem manutencao')),
        )

	def choices(self, changelist):

		for lookup, title in self.lookup_choices:
		    yield {
		        'selected': self.value() == lookup,
		        'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
		        'display': title,
		    }

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'Precisa':
            return queryset.filter(valorAcumulado__gte=F('periodoPadrao'))
        if self.value() == 'NaoPrecisa':
            return queryset.filter(valorAcumulado__lte=F('periodoPadrao'))
        if self.value() == 'Todos':
            return queryset.filter()



class ItemManutencaoVeiculoAdmin(admin.ModelAdmin):

	list_display = ('veiculo','periodoPadrao','valorAcumulado','precisaManutencao')
	ordering = ('-valorAcumulado',)
	search_fields = ['material', 'veiculo']
	list_filter = (ManutencaoAcionarFilter,'veiculo','material','unidade')
	# def get_query_set(self):
	#     return super(ItemManutencaoVeiculoAdmin, self).get_query_set().filter(manutencao='Precisa')

	def precisaManutencao(self,obj):
		need = obj.precisaManutencao()
		span = " <span class='need' > Sim <span>" if need =='Sim'else " <span class='' > Não <span>" 
		return span
	precisaManutencao.allow_tags = True
	def changelist_view(self, request, extra_context=None):
	    if not request.GET.has_key('manutencao'):
	        q = request.GET.copy()
	        q['manutencao'] = 'Precisa'  # default value for status
	        request.GET = q
	        request.META['QUERY_STRING'] = request.GET.urlencode()
	    return super(ItemManutencaoVeiculoAdmin, self).changelist_view(
	        request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
		if obj.id is not None and change and form.status is not obj.status :
			a = ItemManutencaoProgramado()
			a.valor = obj.valor
			a.itemManutencaoVeiculo = obj
			a.hodometro = obj.veiculo.hodometro
			a.veiculo = obj.veiculo
			a.save()
		super(ItemManutencaoVeiculoAdmin, self).save_model(request, obj, form, change)

admin.site.register(ItemManutencaoVeiculo, ItemManutencaoVeiculoAdmin)


# from django.db import models

# class SomeAdmin(admin.ModelAdmin):
#     list_display = ('db_field', 'custom_field',)

#     def queryset(self, request):
#         qs = super(SomeAdmin, self).queryset(request)
#         qs = qs.annotate(models.Count('movies'))
#         return qs

#     def custom_field(self, obj):
#         return 'Total movies {0}'.format(obj.movies__count)
#     custom_field.admin_order_field = 'movies__count'
#     custom_field.short_description = 'Movies'

class LocacaoAdmin(admin.ModelAdmin):
	pass

admin.site.register(Locacao, LocacaoAdmin)


class AbastecimentoResource(resources.ModelResource):
	def __str__(self):
		return ""
	class Meta:
		model = Abastecimento
		def __str__(self):
			return self.model.notafiscal

	def before_save_instance(self,instance,using_transactions,dry_run):
		print instance
		pass

	def before_import_row(self,row, **kwargs):
		with transaction.atomic():
			try:
				val = float(row['hodometro'])
			except Exception as err:
				row['hodometro'] = 0

			try:
				val = float(row['quantidade'])
			except Exception as err:
				row['quantidade'] = 0

			try:
				val = float(row['valor'])
			except Exception as err:
				row['valor'] = 0
			print row
			row['id'] = unicode(row['id'])
			vale = row['vale']

			placa = unicode(row['veiculo']).strip() 
			obj, created = Veiculo.objects.update_or_create(placa=placa)

			nome = unicode(row['posto']).strip()
			obj, created  = Posto.objects.update_or_create(nome=nome)

			nome = unicode(row['motorista']).strip()
			obj, created = Operador.objects.update_or_create(nome=nome)

			nome = row['responsavel']
			permissions = []
			permissions.append(Permission.objects.get(name='Can delete abastecimento'))
			permissions.append(Permission.objects.get(name='Can change abastecimento'))
			permissions.append(Permission.objects.get(name='Can add abastecimento'))
			permissions.append(Permission.objects.get(name='Can delete operador'))
			permissions.append(Permission.objects.get(name='Can change operador'))
			permissions.append(Permission.objects.get(name='Can add operador'))
			permissions.append(Permission.objects.get(name='Can delete veiculo'))
			permissions.append(Permission.objects.get(name='Can change veiculo'))
			permissions.append(Permission.objects.get(name='Can add veiculo'))
			permissions.append(Permission.objects.get(name='Can delete posto'))
			permissions.append(Permission.objects.get(name='Can change posto'))
			permissions.append(Permission.objects.get(name='Can add posto'))

			permissions.append(Permission.objects.get(name='Can delete obra'))
			permissions.append(Permission.objects.get(name='Can change obra'))
			permissions.append(Permission.objects.get(name='Can add obra'))
			# listobj = Responsavel.objects.filter(username=nome)
			# obj,created = Responsavel.objects.update_or_create(username=nome,is_staff=True) 
			# obj.user_permissions.set(permissions)
			# obj.set_password('usuario123')

			obj,created = User.objects.update_or_create(username=nome,password='usuario123',is_staff=True) 
			obj.user_permissions.set(permissions)
			row['responsavel'] = obj.id

		# return self.fields['name'].clean(row) == ''


class OperadorAdmin(admin.ModelAdmin):

	search_fields = ['nome', 'cpf']


admin.site.register(Operador, OperadorAdmin)

class ObraAdmin(admin.ModelAdmin):
	radio_fields = {"status": admin.VERTICAL,"sairnaagenda": admin.VERTICAL}



admin.site.register(Obra, ObraAdmin)


class Abastecimentoform(forms.ModelForm):
	class Meta:
		model = Abastecimento
		fields = '__all__'

	def clean(self):
		cleaned_data = self.cleaned_data

		veiculo = self.cleaned_data.get('veiculo',None)
		hodometro = self.cleaned_data.get('hodometro',None)
		if veiculo is not None and hodometro is not None and veiculo.tipo == TIPO_VEICULOS[0][0] and hodometro<=0:
			msg = _('Valor %s Invalido de Hodometro/Horimetro   para veiculos do tipo %s'%(hodometro,veiculo.tipo))
			self._errors["hodometro"] = self.error_class([msg])
			del cleaned_data["hodometro"]
			# raise forms.ValidationError(
			# 			_('Valor %(value)s Invalido de Hodometro/Horimetro   para veiculos do tipo %(tipo)s'),
			# 			params={'value': hodometro,'tipo':veiculo.tipo},
			# 		)
		return cleaned_data

class AbastecimentoAdmin(ImportExportMixin, admin.ModelAdmin):
	resource_class = AbastecimentoResource
	
	form = Abastecimentoform

	list_display = ('id','criado_date','notafiscal','hodometro','quantidade','valor_display','vale', 'responsavel_display','veiculo')
	search_fields = ['notafiscal', 'veiculo__placa','responsavel__username','posto__nome','observacao']
	list_filter = ('criado_date','responsavel','veiculo')
	# readonly_fields=('vale','motorista','responsavel','veiculo','posto')
	def save_model(self, request, obj, form, change):
		if not request.user.is_superuser:
			if obj.id is None:
				obj.responsavel = request.user
			obj.notafiscal =  obj.notafiscal

		obj.save()

	# def get_fields(self,request,obj=None):
	# 	if request.user.is_superuser:
	# 		return self.readonly_fields
	# 	else:	
	# 		if obj and not obj.responsavel==resquest.user: # editing an existing object
	# 			return self.readonly_fields+list_display
	# 		return self.readonly_fields

	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			return self.readonly_fields
		else:	
			if obj and not obj.responsavel==request.user: # editing an existing object
				return self.readonly_fields+tuple(obj._meta.get_all_field_names())
			return self.readonly_fields+('responsavel','notafiscal')


	# def get_search_results(self, request,queryset,search_term):
	# 	print 'lkkkkkkkkkk',request.user.is_superuser
	# 	if request.user.is_superuser:
	# 		return Abastecimento.objects.all()
	# 	else:
	# 		return Abastecimento.objects.filter(responsavel=request.user)

admin.site.register(Abastecimento, AbastecimentoAdmin)

class PostoAdmin(admin.ModelAdmin):

    search_fields = ['nome', 'cnpj','observacao']
    list_filter = ('criado_date','atualizado_date')


admin.site.register(Posto, PostoAdmin)

class Veiculoform(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(Veiculoform, self).__init__(*args, **kwargs)
		self.fields['isVeiculo'].choices = self.fields['isVeiculo'].choices[1:]

	class Meta:
		model = Veiculo
		fields = '__all__'
		app_label = 'equipamento'

		def clean(self):
			start_date = self.cleaned_data.get('veiculo')
			if start_date > end_date:
				raise forms.ValidationError("Dates are fucked up")
			return self.cleaned_data

class VeiculoAdmin(admin.ModelAdmin):

	form = Veiculoform
	search_fields = ['placa','tipo','observacao']
	list_filter = ('criado_date','atualizado_date','tipo')
	radio_fields = {"isVeiculo": admin.VERTICAL}
	# filter_horizontal = ('itensManutencao',)

admin.site.register(Veiculo, VeiculoAdmin)

