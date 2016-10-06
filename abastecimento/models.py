# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_save, post_delete, pre_save

from django.db import models
from django.utils import timezone

class Usuario(models.Model):
	nome = models.CharField(max_length=200)
	cpf = models.CharField(max_length=20,blank=True, null=True)
	def __str__(self):
		return self.nome

# Create your models here.
class Posto(models.Model):
    nome = models.CharField(max_length=200)
    observacao = models.TextField()
    cnpj = models.CharField(max_length=20)

    criado_date = models.DateTimeField("Data Criada",
            auto_now_add=True)
    atualizado_date = models.DateTimeField("Data Atualizado",
            blank=True, null=True,auto_now=True)

    def __str__(self):
        return self.nome


class Veiculo(models.Model):
	dono = models.ForeignKey(Usuario,blank=True, null=True)
	placa = models.CharField(max_length=7)
	observacao = models.TextField()
	TIPOS = (
		('PROPRIO', 'Frota própria'),
		('TERCEIRO-SEM', 'Terceirizados sem o desconto de combustível na medição'),
		('TERCEIRO-COM', 'Terceirizados com desconto do combustível na medição'),
	)
	tipo = models.CharField(max_length=13, choices=TIPOS)

	criado_date = models.DateTimeField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.placa

class Vale(models.Model):
	valor = models.DecimalField('Valor', max_digits=5, decimal_places=2)
	numero = models.DecimalField('Número', max_digits=15, decimal_places=0)
	usado = models.BooleanField('Usado',default=False)

	criado_date = models.DateTimeField("Data Criada",
			auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
			blank=True, null=True,auto_now=True)

	def __str__(self):
		return str(self.numero)

class Abastecimento(models.Model):
	responsavel = models.ForeignKey(Usuario)
	veiculo = models.ForeignKey(Veiculo)
	posto = models.ForeignKey(Posto)
	observacao = models.TextField()
	ODOM = models.CharField(max_length=13)
	quantidade = models.FloatField('Quantidade')
	valor = models.FloatField('Valor')
	vale = models.OneToOneField(Vale)
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
	notafiscal = models.CharField(max_length=13)

	criado_date = models.DateTimeField("Data Abastecimento")
	atualizado_date = models.DateTimeField("Data Abastecimento Atualizado",
			blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.notafiscal

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		instance.vale.usado = True
		instance.vale.save()
		#do anything you want
pre_save.connect(Abastecimento.pre_save, Abastecimento, dispatch_uid="sightera.abastecimento.models.Abastecimento") 

