// Javascript event acknowledge/response -----------------------------------------------------------
function basket_line_update(param, json_obj){
 var qty_input = $(param).parents(".cart_quantity_button").find(".cart_quantity_input");
 //debugger;
 var price = $(param).parents(".genshop_js_basket_row").find(".cart_price").find("P");
 var line_total = $(param).parents(".genshop_js_basket_row").find(".cart_total").find("P");
 qty_input.val(parseInt(json_obj["payload"]["qty"]));
 price.html(json_obj["payload"]["price"]);
 line_total.html(json_obj["payload"]["total"]);
 $(param).parents(".genshop_js_basket_row").effect('highlight', 500 );
}

function basket_line_delete(param, json_obj){
 var row = $(param).parents(".genshop_js_basket_row");
 $(row).effect('fade', 300 );
}

function acknowledge_response(param, json_obj){
  var cart = $('#genshop_js_cart_menu');
  var imgtodrag = $(param).parents('.product-image-wrapper').find("img").eq(0);
  //var imgtodrag = $(this).parent('.item').find("img").eq(0);
  if (imgtodrag) {
      var imgclone = imgtodrag.clone()
          .offset({
          top: imgtodrag.offset().top,
          left: imgtodrag.offset().left
      }).css({
          'opacity': '0.5',
              'position': 'absolute',
              'height': '191px',
              'width': '185px',
              'z-index': '100'
      }).appendTo($('body'))
          .animate({
          'top': cart.offset().top + 10,
              'left': cart.offset().left + 10,
              'width': 75,
              'height': 75
      }, 1000, 'easeInOutExpo');

      setTimeout(function () {
          cart.effect("shake", {
              times: 2
          }, 200);
      }, 1500);

      imgclone.animate({
          'width': 0,
              'height': 0
      }, function () {
          $(param).detach();
      });
  }
}

// Common Jquery helper functions -----------------------------------------------------------------
function ajax_request(url,method,data,callback,param){
    $.ajaxSetup({
        data: {"csrfmiddlewaretoken": $('#genshop_js_csrf').html() },
    });
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


// Javascript event registeration -----------------------------------------------------------------
// Basket add
$( ".genshop_js_basket_add" ).click(function() {
// console.log( this.attributes["productid"].nodeValue );
var url = $('#genshop_js_basket-add-url').html();

var data = {"product_id":this.attributes["productid"].nodeValue}
ajax_request(url,"POST",data, acknowledge_response,this);
});

// Basket item increment (+)
$( ".genshop_js_cart_inc" ).click(function() {
var url = $('#genshop_js_basket-modify-url').html();
var data = { "basket_id":$(this).parents(".genshop_js_basket_row").attr("genshop_js_basket_id"),
             "action" :  "increment" }
ajax_request(url,"POST",data, basket_line_update,this);
});

// Basket item decrement (-)
$( ".genshop_js_cart_dec" ).click(function() {
var url = $('#genshop_js_basket-modify-url').html();
var data = { "basket_id":$(this).parents(".genshop_js_basket_row").attr("genshop_js_basket_id"),
             "action" :  "decrement" }
ajax_request(url,"POST",data, basket_line_update,this);
});

// Basket item remove
$( ".genshop_js_cart_del" ).click(function() {
var url = $('#genshop_js_basket-modify-url').html();
var data = { "basket_id":$(this).parents(".genshop_js_basket_row").attr("genshop_js_basket_id"),
             "action" :  "remove" }
ajax_request(url,"POST",data, basket_line_delete,this);
});
