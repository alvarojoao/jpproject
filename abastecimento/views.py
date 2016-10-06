from django.shortcuts import render
from abastecimento.models import Abastecimento,Posto,Veiculo,Vale,Usuario

# Create your views here.

def home(request):
	"""
	home page
	"""
	kwargs = {'veiculo__placa':'PEW123'}
	for i in kwargs:
		print i,kwargs[i]
	print(Abastecimento.objects.filter(**kwargs))
	return ''
