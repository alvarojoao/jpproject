(function($){   
    $(function(){
        $(document).ready(function() {
            $('body').on('change','#id_veiculo', veiculo_change);           
            $('body').on('keyup input','#id_hodometroFinal', veiculo_hodometroFinal);           
        });
});  
})(jQuery);

// based on the type, action will be loaded

function veiculo_change()
{
    var id_veiculo = $('#id_veiculo').val();
    $.ajax({
            "type"     : "GET",
            "url"      : "/get_veiculo_km/"+id_veiculo,
            "dataType" : "json",
            "cache"    : false,
            "success"  : function(json) {
                $('#id_hodometroInicial').val(json.hodometro)
            }           
    });
}
function veiculo_hodometroFinal(value,valueb)
{
    var inicio = parseInt($('#id_hodometroInicial').val());
    var fim = parseInt($('#id_hodometroFinal').val());
    if(fim< inicio ){
        if($("#warn_hodofinal").length<=0)
            $('#id_hodometroFinal').parent().append('<p id="warn_hodofinal" style="color:red">Tem que ser maior que o Inicial<p>');
    }else{
        $("#warn_hodofinal").remove();
    }
}