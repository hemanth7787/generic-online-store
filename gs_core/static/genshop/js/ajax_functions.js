
function acknowledge_response(param, json_obj){
  $("#genshop_js_cart_menu").slideToggle();
  $("#genshop_js_cart_menu").slideToggle();
}

function ajax_request(url,method,data,callback,param){
    $.ajax({
        type:method,
        url:url,
        data: data,
        success: function(json_obj){
            if (json_obj['status']=="success"){
              callback(param, json_obj);
            }
            if($('#genshop_js_debug_setting').attr("value")=="True"){
                console.log(json_obj);
            }
        }
    });
}


$( ".genshop_js_basket_add" ).click(function() {
// console.log( this.attributes["productid"].nodeValue );
var url = $('#genshop_js_basket-add-url').html();
var csrf = $('#genshop_js_csrf').html();
var data = {"product_id":this.attributes["productid"].nodeValue, "csrfmiddlewaretoken":csrf}
ajax_request(url,"POST",data, acknowledge_response,"");
});
