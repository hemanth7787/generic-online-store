
function acknowledge_response(param, json_obj){
  // $("#genshop_js_cart_menu").slideToggle();
  // $("#genshop_js_cart_menu").slideToggle();
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


$( ".genshop_js_basket_add" ).click(function() {
// console.log( this.attributes["productid"].nodeValue );
var url = $('#genshop_js_basket-add-url').html();

var data = {"product_id":this.attributes["productid"].nodeValue}
ajax_request(url,"POST",data, acknowledge_response,this);
});
