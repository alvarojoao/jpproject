from django.contrib import admin

# Register your models here.

from abastecimento.models import Abastecimento,Posto,Veiculo,Vale,Usuario



class UsuarioAdmin(admin.ModelAdmin):

    search_fields = ['nome', 'cpf']


admin.site.register(Usuario, UsuarioAdmin)

class AbastecimentoAdmin(admin.ModelAdmin):
	
	list_display = ('notafiscal','hodometro','quantidade','valor_display','vale', 'responsavel','veiculo')
	search_fields = ['notafiscal', 'responsavel', 'veiculo','posto','observacao']
	list_filter = ('criado_date','veiculo')
	# readonly_fields=('vale','motorista','responsavel','veiculo','posto')
	def get_readonly_fields(self, request, obj=None):
		if obj: # editing an existing object
			return self.readonly_fields + ('vale','motorista','responsavel','veiculo','posto')
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