from django.shortcuts import render
from abastecimento.models import Locacao,Abastecimento,Posto,Veiculo,CustoManutencaoNaoProgramado,CustoManutencaoProgramado

# Create your views here.
from django.core import serializers
import json
from django.http import HttpResponse
import math
from datetime import datetime, date,timedelta
from urlparse import urlparse, parse_qs
import time
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django import template

from datetime import date


register = template.Library()
@login_required
def home(request):
	"""
	home page
	"""
	std = request.GET.get('std', False)
	placas = request.GET.get('placas', None)
	date_months = request.GET.get('monthsago', 12)
	date_range = request.GET.get('date_range', "01/07/2016 - 31/12/2016")
	date_str_start,date_str_end = date_range.replace(" ","").split('-')
	start_date , end_date = datetime.strptime(date_str_start, '%d/%m/%Y'),datetime.strptime(date_str_end, '%d/%m/%Y')
	if date_months:
		date_months = int(date_months)
	# data2 = serializers.serialize('json', some_data_to_dump)
	start = datetime.today()
	end = datetime.today()
	new_start = start + timedelta(days=-1*date_months * 365/12) #day can be negative
	#placas
	if placas:
		placas = placas.split(',')
		placas = Veiculo.objects.filter(placa__in=placas).values_list('placa','isVeiculo').distinct()
	else:
		placas = []
		placas = Abastecimento.objects.filter(hodometro__gt=0,criado_date__range=[start_date, end_date]).values_list('veiculo__placa','veiculo__isVeiculo').distinct()
	finalarray = []
	finalarrayPivot = []
	veiculos_litros = {}
	veiculos_diff = {}
	dates = []
	if len(placas)>0:
		dates =  map(lambda (x,):x.strftime("%Y/%m/%d"),Abastecimento.objects.filter(veiculo__placa__in=map(lambda (x,y):x,placas),criado_date__range=[start_date, end_date]).order_by('criado_date').values_list('criado_date').distinct())
		veiculos_data = {}
		veiculos_consumption = {}
		for pl,isveiculo in placas:
			veiculos_data[pl] =   Abastecimento.objects.filter(veiculo__placa=pl,criado_date__range=[start_date, end_date]).order_by('criado_date').values('hodometro','criado_date','quantidade')
			consumption = {}
			litros = {}
			diffs = {}
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
					diffs[veiculo_data['criado_date'].strftime("%Y/%m/%d")]=str(veiculo_data['hodometro'])+'-'+str(anterior_value['hodometro'])
					anterior_value = veiculo_data
			veiculos_consumption[pl] = consumption
			veiculos_litros[pl] = litros
			veiculos_diff[pl] = diffs
			# if std:
			# 	if len(consumption_datavalues)>1:
			# 		std_value = pstdev(consumption_datavalues)
			# 	else:
			# 		std_value = 0
			# 	with_std_value = False
			# 	if with_std_value:
			# 		consumption_data_data = [[data_criado,[dif,std_value]] for data_criado,dif,litros in consumption]
			# 	else:
			# 		consumption_data_data = [[data_criado,dif] for data_criado,dif,litros in consumption]
		for i,date_val in enumerate(dates):
			finalarray.append([date_val])
			for pl,isveiculo in placas:
				finalarray[i].append(veiculos_consumption[pl].get(date_val,None))

		for i,(pl,isveiculo) in enumerate(placas):
			finalarrayPivotElement = {}
			finalarrayPivotElement['nome'] = pl
			dataformeanhomometro = []
			dataformeanlitros = []
			for i,date_val in enumerate(dates):
				dataformeanhomometro.append(veiculos_consumption[pl].get(date_val,0))
				dataformeanlitros.append(veiculos_litros[pl].get(date_val,0))
				formatedOut = ''
				output = (veiculos_consumption[pl].get(date_val,None),veiculos_litros[pl].get(date_val,None))
				if not (None,None)== output:
					formatedOut =  (str(veiculos_consumption[pl].get(date_val,None))+('km' if isveiculo else 'Hr'),str(veiculos_litros[pl].get(date_val,None))+'litros')
				finalarrayPivotElement[date_val] = formatedOut
			finalarrayPivotElement['media'] = str(mean(dataformeanhomometro))+(' km' if isveiculo else ' Hr')
			finalarrayPivotElement['consumo'] = str(consumo(dataformeanhomometro,dataformeanlitros,isveiculo))+('km/litro' if isveiculo else 'litro/Hr')
			finalarrayPivot.append(finalarrayPivotElement)

	# print query
	consumption_data = {}
	consumption_data['data'] = finalarrayPivot
	consumption_data['dates'] = dates
	consumption_data['datapivot'] = finalarray
	consumption_data['litros'] = veiculos_litros
	consumption_data['diffs'] = veiculos_diff
	consumption_data['labels'] = map(lambda (x,y):x,placas)
	data4 =		json.dumps(consumption_data)
	return HttpResponse(data4, content_type='application/json')

@login_required
def balancotable(request):
	"""
	home page
	"""
	placas = request.GET.get('placas', None)
	date_months = request.GET.get('monthsago', 12)
	if date_months:
		date_months = int(date_months)
	date_range = request.GET.get('date_range', "01/07/2016 - 31/12/2016")
	date_str_start,date_str_end = date_range.replace(" ","").split('-')
	start_date , end_date = datetime.strptime(date_str_start, '%d/%m/%Y'),datetime.strptime(date_str_end, '%d/%m/%Y')
	# data2 = serializers.serialize('json', some_data_to_dump)
	start = datetime.today()
	end = datetime.today()
	new_start = start + timedelta(days=-1*date_months * 365/12) #day can be negative


	#Locacoes
	locacoes = Locacao.objects.filter(data_inicio__range=[start_date, end_date])
	custonaoprogramado = CustoManutencaoNaoProgramado.objects.filter(criado_date__range=[start_date, end_date])
	custoprogramadado = CustoManutencaoProgramado.objects.filter(criado_date__range=[start_date, end_date])

	# #Placas
	if placas:
		placas = placas.split(',')
		placas = Veiculo.objects.filter(placa__in=placas).values_list('placa','valor').distinct()
	else:
		placas = []
		placas_locacao = map(lambda x : placas.append(x),locacoes.values_list('veiculo__placa','veiculo__valor').distinct())
		placas_custo_nao_programado = map(lambda x : placas.append(x),custonaoprogramado.values_list('veiculo__placa','veiculo__valor').distinct())
		placas_custo_programado = map(lambda x : placas.append(x),custoprogramadado.values_list('veiculo__placa','veiculo__valor').distinct())
		placas = set(placas)
	

	finalarrayPivot = []
	dates = []
	veiculo_placas = map(lambda (x,y):x,placas)
	if len(placas)>0:
		dates_locacao = locacoes.filter(veiculo__placa__in=veiculo_placas).order_by('data_inicio').values_list('data_inicio','data_fim')
		dates_custo_nao_programado = custonaoprogramado.filter(veiculo__placa__in=veiculo_placas).order_by('criado_date').values_list('criado_date')
		dates_custo_programado = custoprogramadado.filter(veiculo__placa__in=veiculo_placas).order_by('criado_date').values_list('criado_date')
		for (date_init_,date_fim_) in dates_locacao:
			delta = date_fim_ - date_init_ 
			date_ = date_init_
			dates.append(date_)
			for i in range(delta.days):
				date_ = date_ + timedelta(days=1)
				dates.append(date_)
		for (date_,) in dates_custo_nao_programado:
			dates.append(date_)
		for (date_,) in dates_custo_programado:
			dates.append(date_)
			
		dates =  set(map(lambda x:x.strftime("%Y/%m/%d"),dates))

		veiculos_data = {}
		veiculos_locacao = {}
		veiculos_custo_programado = {}
		veiculos_custo_nao_programado = {}

		print placas
		for pl,valor in placas:
			veiculos_data[pl] =  locacoes.filter(veiculo__placa=pl).order_by('data_inicio').values('data_inicio','data_fim')
			dummy = {}
			for data_ in veiculos_data[pl].values():
				dif = data_['data_fim'] - data_['data_inicio']
				dummy[data_['data_inicio'].strftime("%Y/%m/%d")] = int(valor)
				data_range = data_['data_inicio']

				for d_ in range(dif.days):
					data_range = data_range + timedelta(days=1)
					dummy[data_range.strftime("%Y/%m/%d")] = int(valor)

			veiculos_locacao[pl] = dummy
		 	
			veiculos_data[pl] =  custonaoprogramado.filter(veiculo__placa=pl).order_by('criado_date').values('criado_date','valor')
			dummy = {}
			for data_ in veiculos_data[pl]:
				dummy[data_['criado_date'].strftime("%Y/%m/%d")] = -1*data_['valor']

			veiculos_custo_nao_programado[pl] = dummy

			veiculos_data[pl] =  custoprogramadado.filter(veiculo__placa=pl).order_by('criado_date').values('criado_date','valor')
			dummy = {}
			for data_ in veiculos_data[pl]:
				dummy[data_['criado_date'].strftime("%Y/%m/%d")] = -1*data_['valor']

			veiculos_custo_programado[pl] = dummy
			total_balanco = 0
			finalarrayPivotElement = {}
			finalarrayPivotElement['nome'] = pl
			finalarrayPivotElement['newC'] = {}
			for nome,data_ in [('locacao',veiculos_locacao),('nao_programado',veiculos_custo_nao_programado),('programado',veiculos_custo_programado)]:
				
				finalarrayPivotElement['newC'][nome]={}
				finalarrayPivotElement['newC'][nome]['nome-sub'] = pl+' '+nome
				dataformean = []
				for date_val in dates:
					dataformean.append(data_[pl].get(date_val,0))
					formatedOut = ''
					output = data_[pl].get(date_val,None)
					if output:
						formatedOut =  ('R$')+str(output)
					finalarrayPivotElement['newC'][nome][date_val] = formatedOut
				finalarrayPivotElement['newC'][nome]['media'] = ('R$')+str(mean(dataformean))
				finalarrayPivotElement['newC'][nome]['total'] = ('R$')+str(sum(dataformean))
				total_balanco += sum(dataformean)
			
			finalarrayPivotElement['newC']['balanco']={}
			finalarrayPivotElement['newC']['balanco']['nome-sub'] = pl+' Balanco'
			finalarrayPivotElement['newC']['balanco']['total'] = ('R$')+str(total_balanco)
			finalarrayPivotElement['newC']['balanco']['media'] = ''
			for date_val in dates:
				formatedOut = ''
				finalarrayPivotElement['newC']['balanco'][date_val] = formatedOut
			finalarrayPivot.append(finalarrayPivotElement)


	# # print query
	consumption_data = {}
	consumption_data['data'] = finalarrayPivot
	consumption_data['dates'] = map(lambda x: x,dates)
	consumption_data['labels'] = veiculo_placas
	data4 =	json.dumps(consumption_data)
	return HttpResponse(data4, content_type='application/json')

@login_required
def labels_available(request):

	placas = [ i for (i,) in Abastecimento.objects.filter(hodometro__gte=0).values_list('veiculo__placa').distinct()]
	data4 =		json.dumps(placas)
	return HttpResponse(data4, content_type='application/json')

@login_required
def get_veiculo_km(request,id):
	veiculo = Veiculo.objects.get(pk=id)
	return HttpResponse(json.dumps({'hodometro':veiculo.hodometro}), content_type='application/json')


@login_required
def labels_favorites(request):
	placas = [ i for (i,) in Veiculo.objects.filter(favorito=True).values_list('placa').distinct()]
	data4 =		json.dumps(placas)
	return HttpResponse(data4, content_type='application/json')

@login_required
def update_labels_favorites(request):
	with transaction.atomic():
		placas = request.GET.get('placas', None)
		if placas:
			placas = placas.split(',')
		else:
			placas = []
		for veiculo in Veiculo.objects.all():
			if veiculo.placa in placas:
				veiculo.favorito=True
			else:
				veiculo.favorito=False
			veiculo.save()
	data4 =		json.dumps("ok")

	return HttpResponse(data4, content_type='application/json')


def consumo(data,litros,isveiculo=True):
	if len(data)<=0:
		return 0
	if isveiculo:
		return sum(data)/sum(litros,000.1)
	else:
		return sum(litros)/sum(data,000.1)

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n <= 0:
        return 0
    else:
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