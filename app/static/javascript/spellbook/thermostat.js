document.addEventListener("DOMContentLoaded", function () {
    $.ajax({
        url: "/spellbook/thermostat/get_status",
        type: 'GET',
        success: function (output) {
            if (output[0] === 'off') {
                $('#off_btn').addClass('filled');
                $('#on_btn').removeClass('filled');
            } else if (output[0] === 'on') {
                $('#on_btn').addClass('filled');
                $('#off_btn').removeClass('filled');
            } else {
                console.log(output);
                $('#off_btn').addClass('filled');
                $('#on_btn').removeClass('filled');
            }
            let temperature = Number(output[1]).toFixed(2)
            $('#temp').text(temperature)
        },
        error: function (xhr, desc, err) {
            alert("failed");
            console.log(xhr);
            console.log("Details: " + desc + "\nError:" + err);
        }
    });

    let data = [];
    $.ajax({
        url: "spellbook/thermostat/get_temperature_data",
        type: 'GET',
        success: function (output) {
            data = output;

            $.plot($("#temp_plot"),
                [data],
                {
                    axisLabels: {
                        show: true
                    }, xaxis: {
                        mode: "time",
                        timeformat: "%m/%d\n%H:%M",
                        timezone: "browser"
                    }, yaxis: {
                        axisLabel: "Temperature [F]",
                        axisLabelFontSizePixels: 14,
                        axisLabelPadding: 5
                    }
                }
            );
        }
    });
});


$(document).ready(function () {
    setInterval(function () {
        $.ajax({
            url: "/spellbook/thermostat/get_status",
            type: "GET",
            success: function (output) {
                if (output[0] === 'off') {
                    $('#off_btn').addClass('filled');
                    $('#on_btn').removeClass('filled');
                } else if (output[0] === 'on') {
                    $('#on_btn').addClass('filled');
                    $('#off_btn').removeClass('filled');
                } else {
                    console.log(output);
                    $('#off_btn').addClass('filled');
                    $('#on_btn').removeClass('filled');
                }
                let temperature = Number(output[1]).toFixed(2)
                $('#temp').text(temperature)
            }
        });
    }, 10000);


    $('#on_btn').click(function () {
        $('button[type="button"].filled').removeClass('filled');
        $(this).addClass('filled');
        $.ajax({
            url: '/spellbook/thermostat/on_off',
            type: 'POST',
            data: {'status': 'on'},
            success: function (output) {
                console.log(output)
            },
            error: function (xhr, desc, err) {
                alert("failed");
                console.log(xhr);
                console.log("Details: " + desc + "\nError:" + err);
            }
        });
    });

    $('#off_btn').click(function () {
        $('button[type="button"].filled').removeClass('filled');
        $(this).addClass('filled');
        $.ajax({
            url: '/spellbook/thermostat/on_off',
            type: 'POST',
            data: {'status': 'off'},
            success: function (output) {
                console.log(output)
            },
            error: function (xhr, desc, err) {
                alert("failed")
                console.log(xhr);
                console.log("Details: " + desc + "\nError:" + err);
            }
        });
    });
});
