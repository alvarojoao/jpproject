#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin, ImportExportModelAdmin

# Register your models here.
from django.db import transaction

from abastecimento.models import Abastecimento,Posto,Veiculo,Vale,Usuario

class AbastecimentoResource(resources.ModelResource):
	def __str__(self):
		return ""
	class Meta:
		model = Abastecimento
		def __str__(self):
			return self.model.notafiscal

	def before_save_instance(self,instance,using_transactions,dry_run):
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
			row['id'] = unicode(row['id'])
			codigo = unicode(row['vale']).strip()
			obj, created = Vale.objects.update_or_create(codigo=codigo,usado=True)

			placa = unicode(row['veiculo']).strip() 
			obj, created = Veiculo.objects.update_or_create(placa=placa)

			nome = unicode(row['posto']).strip()
			obj, created  = Posto.objects.update_or_create(nome=nome)

			nome = unicode(row['motorista']).strip()
			obj, created = Usuario.objects.update_or_create(nome=nome)

			nome = unicode(row['responsavel']).strip()
			obj, created = Usuario.objects.update_or_create(nome=nome)
		# return self.fields['name'].clean(row) == ''


class UsuarioAdmin(admin.ModelAdmin):

	search_fields = ['nome', 'cpf']


admin.site.register(Usuario, UsuarioAdmin)

class AbastecimentoAdmin(ImportExportMixin, admin.ModelAdmin):
	resource_class = AbastecimentoResource
	
	list_display = ('id','notafiscal','hodometro','quantidade','valor_display','vale', 'responsavel','veiculo')
	search_fields = ['notafiscal', 'responsavel', 'veiculo','posto','observacao']
	list_filter = ('criado_date','veiculo')
	# readonly_fields=('vale','motorista','responsavel','veiculo','posto')
	def get_readonly_fields(self, request, obj=None):
		if obj: # editing an existing object
			return self.readonly_fields + ('motorista','responsavel','veiculo','posto')
		return self.readonly_fields

admin.site.register(Abastecimento, AbastecimentoAdmin)

class PostoAdmin(admin.ModelAdmin):

    search_fields = ['nome', 'cnpj','observacao']
    list_filter = ('criado_date','atualizado_date')


admin.site.register(Posto, PostoAdmin)

class VeiculoAdmin(admin.ModelAdmin):

    search_fields = ['placa','dono']
    list_filter = ('criado_date','atualizado_date','tipo')


admin.site.register(Veiculo, VeiculoAdmin)

class ValeAdmin(admin.ModelAdmin):

    search_fields = ['numero']
    list_filter = ('criado_date','atualizado_date','usado')


admin.site.register(Vale, ValeAdmin)