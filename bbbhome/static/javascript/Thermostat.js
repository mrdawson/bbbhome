document.addEventListener("DOMContentLoaded", function() {
  $.ajax({
    url: "/get_status",
    type: 'GET',
    success: function(output) {
      if (output[0] == '0'){
        $('#off_btn').addClass('filled');
      } else if (output[0] == '1') {
        $('#on_btn').addClass('filled');
      } else{
        console.log(output)
        $('#off_btn').addClass('filled');
      }
      var temperature = Number(output[1]).toFixed(2)
      $('#temp').text(temperature)
    },
    error: function(xhr, desc, err) {
      alert("failed")
      console.log(xhr);
      console.log("Details: " + desc + "\nError:" + err);
    }
  });
  var times = [];
  var temps = [];
  var data = [];
  $.ajax({
    url: "/get_t_data",
    type: 'GET',
    success: function(output) {
      data = output

      $.plot($("#temp_plot"),
        [data],
        {axisLabels: {
          show: true
        },xaxis: {
          mode: "time",
          timeformat: "%m/%d\n%H:%M",
          timezone: "browser"
        },yaxis: {
          axisLabel: "Temperature [F]",
          axisLabelFontSizePixels: 14,
          axisLabelPadding: 5
        }}
      );
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
	  var temperature = Number(output[1]).toFixed(2)
          $('#temp').text(temperature)
        }
    });
  }, 10000);



  $('#on_btn').click(function() {
    $('button[type="button"].filled').removeClass('filled');
    $(this).addClass('filled');
    $.ajax({
      url: '/on_off',
      type: 'POST',
      data: {'status' : 1},
      success: function(output) {
        console.log(output)
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
