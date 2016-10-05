from django.contrib import admin

# Register your models here.

from abastecimento.models import Abastecimento,Posto,Veiculo,Vale



class AbastecimentoAdmin(admin.ModelAdmin):

    search_fields = ['responsavel', 'veiculo', 'posto','observacao']
    list_filter = ('criado_date','atualizado_date')


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