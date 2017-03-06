document.addEventListener("DOMContentLoaded", function() {
  $.ajax({
    url: "/get_status",
    type: 'GET',
    success: function(output) {
      if (output == '0'){
        $('#off_btn').addClass('filled');
      } else if (output == '1') {
        $('#on_btn').addClass('filled');
      } else{
        console.log(output)
        $('#off_btn').addClass('filled');
      }
    },
    error: function(xhr, desc, err) {
      alert("failed")
      console.log(xhr);
      console.log("Details: " + desc + "\nError:" + err);
    }
  });
});

$(document).ready(function(){
  setInterval(function() {
    $.ajax({
        url: "/get_status",
        type: "GET",
        success: function(output) {
          if (output[0] == '0'){
            $('#off_btn').addClass('filled');
            $('#on_btn').removeClass('filled');
          } else if (output[0] == '1') {
            $('#on_btn').addClass('filled');
            $('#off_btn').removeClass('filled');
          } else{
            console.log(output)
            $('#off_btn').addClass('filled');
          }
          $('#temp').text(output[1])
        }
    });
  }, 1000);


  $('#on_btn').click(function() {
    $('button[type="button"].filled').removeClass('filled');
    $(this).addClass('filled');
    $.ajax({
      url: '/on_off',
      type: 'POST',
      data: {'status' : 1},
      success: function(output) {
        console.log(output)
        //if(data == "ok") {}
      },
      error: function(xhr, desc, err) {
        alert("failed")
        console.log(xhr);
        console.log("Details: " + desc + "\nError:" + err);
      }
    });
  });

  $('#off_btn').click(function(){
    $('button[type="button"].filled').removeClass('filled');
    $(this).addClass('filled');
    $.ajax({
      url: '/on_off',
      type: 'POST',
      data: {'status' : 0},
      success: function(output) {
        console.log(output)
        //if(data == "ok") {}
      },
      error: function(xhr, desc, err) {
        alert("failed")
        console.log(xhr);
        console.log("Details: " + desc + "\nError:" + err);
      }
    });
  });

  $('#timed').click(function(){
    if ($(this).hasClass('filled')){
      $(this).removeClass('filled');
    } else{
      $(this).addClass('filled');
    }
  });
});
