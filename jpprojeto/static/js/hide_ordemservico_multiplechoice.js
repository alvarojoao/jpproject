var need_reload = false;
django.jQuery(document).ready(function(){


    $('body').on('change','#id_veiculo', veiculo_change);                   
    $('body').on('change','#id_manutencaoRealizadas_to,#id_manutencaoCorretivaRealizadas_to', manutencao_change);           
    $('body').on('click','#id_manutencaoRealizadas_add_link,#id_manutencaoRealizadas_add_all_link,#id_manutencaoCorretivaRealizadas_add_link,#id_manutencaoCorretivaRealizadas_add_all_link', function() {
      $( '#id_manutencaoRealizadas_to,#id_manutencaoCorretivaRealizadas_to' ).change();
    });    
    $('body').on('click','#id_manutencaoRealizadas_remove_all_link,#id_manutencaoRealizadas_remove_link,#id_manutencaoCorretivaRealizadas_remove_all_link,#id_manutencaoCorretivaRealizadas_remove_link', function() {
      need_reload = false;
      $( '#id_manutencaoRealizadas_to,#id_manutencaoCorretivaRealizadas_to' ).change();
      $('#id_veiculo').change();
    });  

    function veiculo_change(b,c,d){
        var selected = $('#id_veiculo').find(":selected").text();
        if(need_reload){
            location.reload();
        }

        var a = $("#id_manutencaoRealizadas_from option");
        for(var i=0;i<a.length;i++){
            if(a[i].text.indexOf(selected)<0){
                $(a[i]).remove()
            }else{  
                $(a[i]).show()
            }
        }
        var a = $("#id_manutencaoCorretivaRealizadas_from option");
        for(var i=0;i<a.length;i++){
            if(a[i].text.indexOf(selected)<0){
                $(a[i]).remove()
            }else{
                $(a[i]).show()
            }
        }
        need_reload = true;
        manutencao_change();
    } 

    function manutencao_change(b,c,d){
        var a = $("#id_manutencaoRealizadas_to option");
        var b = $("#id_manutencaoCorretivaRealizadas_to option");
        $('#id_materials_select option').hide();
        for(var i=0;i<a.length;i++){
            $('#id_materials_select option[value="manutencaoRealizadas-'+a[i].value+'"]').show();
        }
        for(var i=0;i<b.length;i++){
            $('#id_materials_select option[value="manutencaoCorretivaRealizadas-'+b[i].value+'"]').show();
        }
                
    } 


});

