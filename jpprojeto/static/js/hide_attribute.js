hide_page=false;
django.jQuery(document).ready(function(){

    var show = function(){
        if (django.jQuery('#id_diretoOrIndireto_1').is(':checked')) {
            django.jQuery(".field-hodometro").hide();
            django.jQuery(".field-veiculo").hide();
            hide_page=true;
        }else
        {
            django.jQuery(".field-hodometro").show();
            django.jQuery(".field-veiculo").show();
            django.jQuery(".page").show();
            hide_page=false;

        }
    }
    django.jQuery("#id_diretoOrIndireto_0").click(show);
    django.jQuery("#id_diretoOrIndireto_1").click(show);
    show();
})