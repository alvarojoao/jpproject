hide_page=false;
django.jQuery(document).ready(function(){

    $('form').submit(function(e) {
        var currentForm = this;
        e.preventDefault();
        if($('#id_manutencaoRealizada_1').is(':checked')){
            if (confirm("Tem certeza em realizar essa baixa?")) {
                currentForm.submit();
            }
        }else{
                currentForm.submit();
            
        }
    });
})