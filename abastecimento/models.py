# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_save, post_delete, pre_save

from django.db import models
from django.utils import timezone
from admin_tools_stats.models import DashboardStatsCriteria
from django.db.models import Q

class Usuario(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	cpf = models.CharField(max_length=20,blank=True, null=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.nome+' - cpf: '+(str(self.cpf) if self.cpf else 'Nao Tem')
	@staticmethod
	def pre_save(sender, instance, **kwargs):
		motoristanome = DashboardStatsCriteria.objects.filter(criteria_name='motoristanome').first()
		responsavelnome = DashboardStatsCriteria.objects.filter(criteria_name='responsavelnome').first()
		if responsavelnome is not None and motoristanome is not None :
			responsavelnome.criteria_dynamic_mapping[instance.nome] = instance.nome
			responsavelnome.criteria_dynamic_mapping[instance.nome] = instance.nome
		else:
			motoristanome = DashboardStatsCriteria.objects.create()
			motoristanome.dynamic_criteria_field_name = 'responsavel__nome'
			motoristanome.criteria_name  = 'responsavelnome'
			motoristanome.criteria_dynamic_mapping = {}
			motoristanome.criteria_dynamic_mapping[instance.nome] = instance.nome

			responsavelnome = DashboardStatsCriteria.objects.create()
			responsavelnome.dynamic_criteria_field_name = 'motorista__nome'
			responsavelnome.criteria_name  = 'motoristanome'
			responsavelnome.criteria_dynamic_mapping = {}
			responsavelnome.criteria_dynamic_mapping[instance.nome] = instance.nome
		motoristanome.save()
		responsavelnome.save()
pre_save.connect(Usuario.pre_save, Usuario, dispatch_uid="sightera.abastecimento.models.Usuario") 

# Create your models here.
class Posto(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	cnpj = models.CharField(max_length=20,blank=True, null=True)
	criado_date = models.DateField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)
	observacao = models.TextField( blank=True, null=True)

	def __str__(self):
		return self.nome+' - cnpj: '+(str(self.cnpj) if self.cnpj else 'Nao Tem')
	@staticmethod
	def pre_save(sender, instance, **kwargs):
		postonome = DashboardStatsCriteria.objects.filter(criteria_name='postonome').first()
		if postonome is not None :
			postonome.criteria_dynamic_mapping[instance.nome] = instance.nome
		else:
			postonome = DashboardStatsCriteria.objects.create()
			postonome.dynamic_criteria_field_name = 'posto__nome'
			postonome.criteria_name  = 'postonome'
			postonome.criteria_dynamic_mapping = {}
			postonome.criteria_dynamic_mapping[instance.nome] = instance.nome
		postonome.save()
pre_save.connect(Posto.pre_save, Posto, dispatch_uid="sightera.abastecimento.models.Posto") 

TIPO_VEICULOS = (
	('PROPRIO', 'Frota própria'),
	('TERCEIRO-SEM', 'Terceirizados sem o desconto de combustível na medição'),
	('TERCEIRO-COM', 'Terceirizados com desconto do combustível na medição'),
)
class Veiculo(models.Model):
	placa = models.CharField(verbose_name="Placa/Codigo Interno",max_length=20,primary_key=True)
	
	tipo = models.CharField(max_length=13, choices=TIPO_VEICULOS,blank=True, null=True)
	observacao = models.TextField( blank=True, null=True)

	criado_date = models.DateField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)
	
	@staticmethod
	def pre_save(sender, instance, **kwargs):
		instance.placa = instance.placa.replace('-','')
		veiculosCriteria = DashboardStatsCriteria.objects.filter(criteria_name='veiculos').first()
		if veiculosCriteria is not None:
			veiculosCriteria.criteria_dynamic_mapping[instance.placa] = instance.placa
		else:
			veiculosCriteria = DashboardStatsCriteria.objects.create()
			veiculosCriteria.dynamic_criteria_field_name = 'veiculo__placa'
			veiculosCriteria.criteria_name  = 'veiculos'
			veiculosCriteria.criteria_dynamic_mapping = {}
			veiculosCriteria.criteria_dynamic_mapping[instance.placa] = instance.placa
		veiculosCriteria.save()

	def __str__(self):
		return unicode(self.placa)+' - TIPO: '+str(self.tipo)
pre_save.connect(Veiculo.pre_save, Veiculo, dispatch_uid="sightera.abastecimento.models.Veiculo") 

class Vale(models.Model):
	codigo = models.CharField('Código', max_length=13,primary_key=True)
	valor = models.FloatField('Valor R$',blank=True, null=True)
	usado = models.BooleanField('Usado',default=False)

	criado_date = models.DateTimeField("Data Criada",
			auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
			blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.codigo+' - R$ '+str(self.valor)

TIPOS_COMBUSTIVEL = (
	('DS5', 'DS5'),
	('ALC', 'Alcool'),
	('DS1', 'DS1'),
	('GSA', 'Gasolina Aditivada'),
	('GSC', 'Gasolina Comum'),
	('ARLA', 'ARLA'),
	('LUB', 'LUB'),
)
class Abastecimento(models.Model):
	vale = models.ForeignKey(Vale,verbose_name="Vale/Cupom",blank=True, null=True)
	veiculo = models.ForeignKey(Veiculo,verbose_name="Veiculo/Equipamento")
	motorista = models.ForeignKey(Usuario,verbose_name="Motorista/Operador",related_name='+')
	posto = models.ForeignKey(Posto,verbose_name="Posto de abastecimento")
	hodometro = models.IntegerField('Hodômetro',default=0)
	quantidade = models.FloatField('Quantidade em Litros')
	valor = models.FloatField('Valor Pago R$')
	combustivel = models.CharField(max_length=10, choices=TIPOS_COMBUSTIVEL)
	responsavel = models.ForeignKey(Usuario,verbose_name="Responsável pelo abastecimento")
	notafiscal = models.CharField(max_length=20,blank=True, null=True)

	criado_date = models.DateTimeField("Data Abastecimento")
	atualizado_date = models.DateTimeField("Data Abastecimento Atualizado",
			blank=True, null=True,auto_now=True)
	observacao = models.TextField( blank=True, null=True)

	def __str__(self):
		return unicode(self.id)
	# This method will be used in the admin display
	def valor_display(self):
		# Normally, you would return this:
		# return '${0:1.2f}'.format(self.budget)
		# but a decimal field will display itself correctly
		# so we can just do this:
		return 'R${0}'.format(self.valor)

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		if instance.vale:
			instance.vale.usado = True
			instance.vale.save()
			#do anything you want
pre_save.connect(Abastecimento.pre_save, Abastecimento, dispatch_uid="sightera.abastecimento.models.Abastecimento") 

try:
	veiculosTiposCriteria = DashboardStatsCriteria.objects.filter(criteria_name='veiculostipos').first()
	if veiculosTiposCriteria is  None:
		
		veiculosTiposCriteria = DashboardStatsCriteria.objects.create()
		veiculosTiposCriteria.dynamic_criteria_field_name = 'veiculo__tipo'
		veiculosTiposCriteria.criteria_name  = 'veiculostipos'
		veiculosTiposCriteria.criteria_dynamic_mapping = {}
		for tipo,descricao in TIPO_VEICULOS:
			veiculosTiposCriteria.criteria_dynamic_mapping[tipo] = descricao
		veiculosTiposCriteria.save()

	combustivelTipoCriteria = DashboardStatsCriteria.objects.filter(criteria_name='combustiveltipos').first()
	if combustivelTipoCriteria is  None:
		
		combustivelTipoCriteria = DashboardStatsCriteria.objects.create()
		combustivelTipoCriteria.dynamic_criteria_field_name = 'combustivel'
		combustivelTipoCriteria.criteria_name  = 'combustiveltipos'
		combustivelTipoCriteria.criteria_dynamic_mapping = {}
		for tipo,descricao in TIPOS_COMBUSTIVEL:
			combustivelTipoCriteria.criteria_dynamic_mapping[tipo] = descricao
		combustivelTipoCriteria.save()
except Exception as inst:
	pass