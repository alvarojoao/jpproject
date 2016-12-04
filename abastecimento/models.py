# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_save, post_delete, pre_save

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.core.validators import MinValueValidator, MaxValueValidator

def validate_hodometro_and_veiculo_type(value):
	if value <0 :
		raise ValidationError(
			_('Esse campo não pode ter valor %(value)s, o campo deve ter valor maior ou igual a zero'),
			params={'value': value},
		)


# class Responsavel(User):

# 	def __str__(self):              # __unicode__ on Python 2
# 		return self.username

class Tipo(models.Model):
	codigo = models.CharField(max_length=200,primary_key=True)
	descricao = models.CharField(max_length=200)
	unidade = models.CharField(max_length=200)
	def __str__(self):
		return self.codigo+'-'+self.unidade

class Familia(models.Model):
	codigo = models.CharField(max_length=200,primary_key=True)
	tipo = models.CharField(max_length=200)
	nome = models.CharField(max_length=200)
	descricao = models.CharField(max_length=200)
	quantidadeDiaria = models.CharField(max_length=200)
	def __str__(self):
		return self.codigo

class Marca(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	descricao = models.CharField(max_length=200)
	def __str__(self):
		return self.nome

UNIDADE_VEICULO = (
	('Km', 'Hodometro'),
	('Hr', 'Horimetro')
)

class Modelo(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	marca = models.ForeignKey(Marca,null=True)
	descricao = models.CharField(max_length=200)
	unidade = models.CharField(max_length=3, choices=UNIDADE_VEICULO,blank=True, null=True)
	def __str__(self):
		return self.nome

class Cor(models.Model):
	cor = models.CharField(max_length=200)
	def __str__(self):
		return self.cor

class Eixo(models.Model):
	descricao = models.CharField(max_length=200)
	numeroPneus = models.IntegerField('Número de Pneus',default=0)
	def __str__(self):
		return self.numeroPneus

class Grupo(models.Model):
	nome = models.CharField(max_length=100)
	def __str__(self):
		return nome

class ItemManutencao(models.Model):
	grupo = models.ForeignKey(Grupo)
	descricao = models.CharField(max_length=200)
	material = models.CharField(max_length=200)
	tempoServico = models.IntegerField('Tempo em Horas',default=0)
	criado_date = models.DateField("Data Criada", auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado", blank=True, null=True,auto_now=True)
	def __str__(self):
		return self.material

class ItemManutencaoVeiculo(models.Model):
	ItemManutencao = models.ForeignKey(ItemManutencao)
	descricao = models.CharField(max_length=200)
	material = models.CharField(max_length=200)
	periodoPadrao = models.IntegerField('Horas ou Kilometros para cada troca',default=0)
	quantidade = models.IntegerField('Quantidade necessaria para troca',default=0)
	unidade = models.CharField(max_length=3, choices=UNIDADE_VEICULO,blank=True, null=True)
	tempoServico = models.IntegerField('Tempo de servico total',default=0)
	criado_date = models.DateField("Data Criada", auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado", blank=True, null=True,auto_now=True)
	def __str__(self):
		return str(self.periodoPadrao)



# class componente(models.Model):
# 	codigo = models.CharField(max_length=200,primary_key=True)
# 	nome = models.CharField(max_length=200,primary_key=True)



# #orcamento
# class custo(models.Model):
# 	veiculo = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)
# 	notafiscal = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)
# 	data_emissao = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)
# 	componente = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)
# 	valor = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)
# 	fornecedor = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)
	
# 	criado_date = models.DateField("Data Criada",
# 	        auto_now_add=True)
# 	atualizado_date = models.DateTimeField("Data Atualizado",
# 	        blank=True, null=True,auto_now=True)



class Operador(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	cpf = models.CharField(max_length=20,blank=True, null=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.nome+' - cpf: '+(str(self.cpf) if self.cpf else 'Nao Tem')

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

TIPO_VEICULOS = (
	('PROPRIO', 'Frota própria'),
	('TERCEIRO-SEM', 'Terceirizados sem o desconto de combustível na medição'),
	('TERCEIRO-COM', 'Terceirizados com desconto do combustível na medição')
)

MAQUINA_VEICULO = (
	(False, 'Maquina'),
	(True, 'Veiculo')
)

SIM_NAO = (
	(False, 'Não'),
	(True, 'Sim')
)

class Obra(models.Model):
	nome = models.CharField(max_length=200,primary_key=True)
	status = models.BooleanField('Status',choices=SIM_NAO,default=False,blank=False, null=False)
	sairnaagenda = models.BooleanField('Sair na Agenda',choices=SIM_NAO,default=False,blank=False, null=False)

	criado_date = models.DateField("Data Criada", auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado", blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.nome


class Fornecedor(models.Model):
	codigo = models.CharField(max_length=200,primary_key=True)
	razaoSocial = models.CharField(max_length=200)
	nomeFantasia = models.CharField(max_length=200)
	cnpj = models.CharField(max_length=20,blank=True, null=True)
	endereco = models.CharField(max_length=20,blank=True, null=True)
	conceito = models.CharField(max_length=20,blank=True, null=True)
	observacao = models.TextField( blank=True, null=True)
	
	criado_date = models.DateField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)

	def __str__(self):
		return self.nome+' - cnpj: '+(str(self.cnpj) if self.cnpj else 'Nao Tem')

class Veiculo(models.Model):
	placa = models.CharField(verbose_name="Placa/Codigo Interno",max_length=30,primary_key=True)
	
	tipo = models.CharField(max_length=13, choices=TIPO_VEICULOS,blank=True, null=True)
	isVeiculo = models.BooleanField(choices=MAQUINA_VEICULO,default=True,blank=False, null=False,verbose_name="Veiculo/Maquina ")
	observacao = models.TextField( blank=True, null=True)
	favorito = models.BooleanField(verbose_name="Favorito no grafico",default=False)
	itensManutencao = models.ManyToManyField(ItemManutencaoVeiculo,null=True,blank=True)
	hodometro = models.IntegerField('Hodômetro/Horimetro',default=0,validators= [])

	criado_date = models.DateField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)

	def __str__(self):
		return unicode(self.placa)+' - TIPO: '+str(self.tipo)

class ItemManutencaoProgramado(models.Model):
	ItemManutencaoVeiculo = models.ForeignKey(ItemManutencaoVeiculo)
	hodometro = models.IntegerField('Hodômetro/Horimetro',default=0,validators= [])
	veiculo = models.ForeignKey(Veiculo,verbose_name="Veiculo/Equipamento")
	criado_date = models.DateField("Data Criada", auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado", blank=True, null=True,auto_now=True)
	def __str__(self):
		return str(self.veiculo)

class ItemManutencaoNaoProgramado(models.Model):
	ItemManutencao = models.ForeignKey(ItemManutencao)
	hodometro = models.IntegerField('Hodômetro/Horimetro',default=0,validators= [])
	veiculo = models.ForeignKey(Veiculo,verbose_name="Veiculo/Equipamento")
	criado_date = models.DateField("Data Criada", auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado", blank=True, null=True,auto_now=True)
	def __str__(self):
		return str(self.veiculo)

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
	vale = models.CharField(max_length=50,verbose_name="Vale/Cupom",blank=True, null=True)
	veiculo = models.ForeignKey(Veiculo,verbose_name="Veiculo/Equipamento")
	motorista = models.ForeignKey(Operador,verbose_name="Motorista/Operador",related_name='+')
	posto = models.ForeignKey(Posto,verbose_name="Posto de abastecimento")
	hodometro = models.IntegerField('Hodômetro/Horimetro',default=0,validators= [validate_hodometro_and_veiculo_type])
	quantidade = models.FloatField('Quantidade em Litros')
	valor = models.FloatField('Valor Pago R$')
	combustivel = models.CharField(max_length=10, choices=TIPOS_COMBUSTIVEL)
	responsavel = models.ForeignKey(User,verbose_name="Responsável pelo abastecimento")
	obra = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)

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

	def responsavel_display(self):
		# Normally, you would return this:
		# return '${0:1.2f}'.format(self.budget)
		# but a decimal field will display itself correctly
		# so we can just do this:
		return self.responsavel.username





class Locacao(models.Model):

	obra = models.ForeignKey(Obra,verbose_name="Obra envolvida no abastecimento",null=True)
	veiculo = models.ForeignKey(Veiculo,verbose_name="Veiculo/Equipamento")
	hodometroInicial = models.IntegerField('Hodômetro/Horimetro Inicial',default=0,validators= [validate_hodometro_and_veiculo_type])
	hodometroFinal = models.IntegerField('Hodômetro/Horimetro Final',default=0,validators= [validate_hodometro_and_veiculo_type])
	horasprodutivo = models.IntegerField('Horas produtivas',default=8,validators=[MinValueValidator(0),
                                       MaxValueValidator(8)])
	horasmanutencaoPreventiva = models.IntegerField('Horas Manutenção preventiva',default=0,validators=[MinValueValidator(0),
                                       MaxValueValidator(8)])
	horasmanutencaoCorretiva = models.IntegerField('Horas Manutenção corretiva',default=0,validators=[MinValueValidator(0),
                                       MaxValueValidator(8)])
	observacao = models.TextField( blank=True, null=True)
	data_inicio = models.DateField("Data Inicio"
	        )
	data_fim = models.DateField("Data Fim"
	        )

	criado_date = models.DateField("Data Criada",
	        auto_now_add=True)
	atualizado_date = models.DateTimeField("Data Atualizado",
	        blank=True, null=True,auto_now=True)
	def title(self):
		return str(self.veiculo)+' '+str(self.obra)+' HorasProdutivas:'+str(self.horasprodutivo-self.horasmanutencaoPreventiva-self.horasmanutencaoCorretiva)

