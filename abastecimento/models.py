# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_save, post_delete, pre_save

from django.db import models
from django.utils import timezone
from admin_tools_stats.models import DashboardStatsCriteria

class Usuario(models.Model):
	nome = models.CharField(max_length=200)
	cpf = models.CharField(max_length=20,blank=True, null=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
            blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.nome+' - cpf: '+(str(self.cpf) if self.cpf else 'Nao Tem')

# Create your models here.
class Posto(models.Model):
	nome = models.CharField(max_length=200)
	observacao = models.TextField( blank=True, null=True)
	cnpj = models.CharField(max_length=20,blank=True, null=True)
	criado_date = models.DateField("Data Criada",
            auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
            blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.nome+' - cnpj: '+(str(self.cnpj) if self.cnpj else 'Nao Tem')


class Veiculo(models.Model):
	placa = models.CharField(max_length=7,primary_key=True)
	observacao = models.TextField( blank=True, null=True)
	TIPOS = (
		('PROPRIO', 'Frota própria'),
		('TERCEIRO-SEM', 'Terceirizados sem o desconto de combustível na medição'),
		('TERCEIRO-COM', 'Terceirizados com desconto do combustível na medição'),
	)
	tipo = models.CharField(max_length=13, choices=TIPOS)

	criado_date = models.DateField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)
	
	@staticmethod
	def pre_save(sender, instance, **kwargs):
		veiculosCriteria = DashboardStatsCriteria.objects.filter(criteria_name='veiculos').first()
		if veiculosCriteria is not None:
			veiculosCriteria.criteria_dynamic_mapping[instance.placa] = instance.placa
		else:
			veiculosCriteria = DashboardStatsCriteria.objects.create()
			veiculosCriteria.dynamic_criteria_field_name = 'veiculo__placa'
			veiculosCriteria.criteria_name  = 'veiculos'
			veiculosCriteria.criteria_dynamic_mapping[instance.placa] = instance.placa
			veiculosCriteria.save()

	def __str__(self):
		return self.placa+' - TIPO: '+str(self.tipo)
pre_save.connect(Veiculo.pre_save, Veiculo, dispatch_uid="sightera.abastecimento.models.Veiculo") 

class Vale(models.Model):
	valor = models.FloatField('Valor R$')
	codigo = models.CharField('Código', max_length=13,primary_key=True)
	usado = models.BooleanField('Usado',default=False)

	criado_date = models.DateTimeField("Data Criada",
			auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
			blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.codigo+' - R$ '+str(self.valor)

class Abastecimento(models.Model):
	motorista = models.ForeignKey(Usuario,verbose_name="Motorista",related_name='+',blank=True, null=True)
	responsavel = models.ForeignKey(Usuario,verbose_name="Responsável pelo abastecimento")
	veiculo = models.ForeignKey(Veiculo,verbose_name="Veiculo")
	posto = models.ForeignKey(Posto,verbose_name="Posto de abastecimento")
	observacao = models.TextField( blank=True, null=True)
	hodometro = models.IntegerField('Hodômetro',default=0)
	quantidade = models.FloatField('Quantidade em Litros')
	valor = models.FloatField('Valor Pago R$')
	vale = models.OneToOneField(Vale,verbose_name="Vale",limit_choices_to={'usado': False})
	TIPOS_COMBUSTIVEL = (
		('DS5', 'DS5'),
		('ALC', 'ALC'),
		('DS1', 'DS1'),
		('GSA', 'GSA'),
		('GSC', 'GSC'),
		('ARLA', 'ARLA'),
		('LUB', 'LUB'),
		)
	combustivel = models.CharField(max_length=10, choices=TIPOS_COMBUSTIVEL)
	notafiscal = models.CharField(max_length=20,primary_key=True)

	criado_date = models.DateTimeField("Data Abastecimento")
	atualizado_date = models.DateTimeField("Data Abastecimento Atualizado",
			blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.notafiscal
	# This method will be used in the admin display
	def valor_display(self):
		# Normally, you would return this:
		# return '${0:1.2f}'.format(self.budget)
		# but a decimal field will display itself correctly
		# so we can just do this:
		return 'R${0}'.format(self.valor)
	@staticmethod
	def pre_save(sender, instance, **kwargs):
		instance.vale.usado = True
		instance.vale.save()
		#do anything you want
pre_save.connect(Abastecimento.pre_save, Abastecimento, dispatch_uid="sightera.abastecimento.models.Abastecimento") 

