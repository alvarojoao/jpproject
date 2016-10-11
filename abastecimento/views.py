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
		placas = [ i[0] for i in Abastecimento.objects.filter(hodometro__gte=0,criado_date__range=[start, new_end]).values_list('veiculo__placa').distinct()]

	if len(placas)>0:
		dates =  Abastecimento.objects.filter(veiculo__placa__in=placas,criado_date__range=[start, new_end]).order_by('criado_date').values_list('criado_date').distinct()
		veiculos_data = {}
		veiculos_consumption = {}
		for pl in placas:
			veiculos_data[pl] =   Abastecimento.objects.filter(veiculo__placa__in=placas,criado_date__range=[start, new_end]).order_by('criado_date').values('hodometro','criado_date','quantidade')
			consumption = {}
			for i,veiculo_data in enumerate(veiculos_data[pl]):
				if i== 0:
					# consumption.append(None)
					pass
				else:
					consumption[veiculo_data.criado_date.strftime("%Y/%m/%d")]=(abs(veiculo_data.hodometro-query[i-1].hodometro),veiculo_data.quantidade)
			veiculos_consumption[pl] = consumption
			
			if len(consumption)>0:
				std_value = pstdev(map(lambda (x,y,z):y,consumption))
			else:
				std_value = 0
				
			with_std_value = False
			if with_std_value:
				consumption_data_data = [[data_criado,[dif,std_value]] for data_criado,dif,litros in consumption]
			else:
				consumption_data_data = [[data_criado,dif] for data_criado,dif,litros in consumption]

		litros = [ litros_val for data_criado,dif,litros_val in consumption]


	# print query
	consumption_data = {}
	consumption_data['data'] = consumption_data_data
	consumption_data['labels'] = placas
	consumption_data['litros'] = litros

	data4 =		json.dumps(consumption_data)

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