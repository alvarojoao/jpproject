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
from abastecimento.models import Abastecimento,Posto,Veiculo,Operador

# class ResponsavelAdmin(UserAdmin):

# 	search_fields = ['username']


# admin.site.register(Responsavel, ResponsavelAdmin)

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

class AbastecimentoAdmin(ImportExportMixin, admin.ModelAdmin):
	resource_class = AbastecimentoResource
	
	list_display = ('id','notafiscal','hodometro','quantidade','valor_display','vale', 'responsavel_display','veiculo')
	search_fields = ['notafiscal', 'veiculo__placa','responsavel__username','posto__nome','observacao']
	list_filter = ('criado_date','responsavel','veiculo')
	# readonly_fields=('vale','motorista','responsavel','veiculo','posto')
	def save_model(self, request, obj, form, change):
		if not request.user.is_superuser:
			if not change:
				obj.responsavel = request.user
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
			return self.readonly_fields+('responsavel',)


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

class VeiculoAdmin(admin.ModelAdmin):

    search_fields = ['placa','tipo','observacao']
    list_filter = ('criado_date','atualizado_date','tipo')


admin.site.register(Veiculo, VeiculoAdmin)

