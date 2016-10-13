from django.shortcuts import render
from abastecimento.models import Abastecimento,Posto,Veiculo
# Create your views here.
from django.core import serializers
import json
from django.http import HttpResponse
import math
from datetime import datetime, date,timedelta
from urlparse import urlparse, parse_qs
import time

def home(request):
	"""
	home page
	"""

	# data = simplejson.dumps(some_data_to_dump)
	placas = request.GET.get('placas', None)
	if placas:
		placas = placas.split(',')
	else:
		placas = []
		
	# data2 = serializers.serialize('json', some_data_to_dump)
	start = date(2016, 01, 01)
	end = datetime.today()
	new_end = end + timedelta(days=1) #day can be negative

	#placas
	if len(placas)==0:
		placas = [ i for (i,) in Abastecimento.objects.filter(hodometro__gte=0,criado_date__range=[start, new_end]).values_list('veiculo__placa').distinct()]

	if len(placas)>0:
		dates =  map(lambda (x,):x.strftime("%Y/%m/%d"),Abastecimento.objects.filter(veiculo__placa__in=placas,criado_date__range=[start, new_end]).order_by('criado_date').values_list('criado_date').distinct())
		veiculos_data = {}
		veiculos_consumption = {}
		veiculos_litros = {}

		for pl in placas:
			veiculos_data[pl] =   Abastecimento.objects.filter(veiculo__placa=pl,criado_date__range=[start, new_end]).order_by('criado_date').values('hodometro','criado_date','quantidade')
			consumption = {}
			litros = {}
			consumption_datavalues = []
			anterior_value = {}
			for i,veiculo_data in enumerate(veiculos_data[pl]):
				if i== 0:
					anterior_value = veiculo_data
				else:
					consumo_value = abs(veiculo_data['hodometro']-anterior_value['hodometro'])
					consumption[veiculo_data['criado_date'].strftime("%Y/%m/%d")]=consumo_value
					consumption_datavalues.append(consumo_value)
					litros[veiculo_data['criado_date'].strftime("%Y/%m/%d")]=anterior_value['quantidade']
					anterior_value = veiculo_data
			veiculos_consumption[pl] = consumption
			veiculos_litros[pl] = litros
			

			# if len(consumption_datavalues)>0:
			# 	std_value = pstdev(consumption_datavalues)
			# else:
			# 	std_value = 0
			# with_std_value = False
			# if with_std_value:
			# 	consumption_data_data = [[data_criado,[dif,std_value]] for data_criado,dif,litros in consumption]
			# else:
			# 	consumption_data_data = [[data_criado,dif] for data_criado,dif,litros in consumption]

		finalarray = []
		for i,date_val in enumerate(dates):
			finalarray.append([date_val])
			for pl in placas:
				finalarray[i].append(veiculos_consumption[pl].get(date_val,None))


	# print query
	consumption_data = {}
	consumption_data['data'] = finalarray
	consumption_data['litros'] = veiculos_litros
	consumption_data['labels'] = placas

	data4 =		json.dumps(consumption_data)

	return HttpResponse(data4, content_type='application/json')
def labels_available(request):

	placas = [ i for (i,) in Abastecimento.objects.filter(hodometro__gte=0).values_list('veiculo__placa').distinct()]
	data4 =		json.dumps(placas)
	return HttpResponse(data4, content_type='application/json')

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n # the population variance
    return pvar**0.5