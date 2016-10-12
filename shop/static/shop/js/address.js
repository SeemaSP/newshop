/*global $, document, Urls */
/*jslint evil: true */

function searchstates(country_id, ddlname, state_id=0) {
    "use strict";
    $.ajax({
        type: "GET",
        url: Urls['search-states-view'](),
        data: "country=" + country_id,
        success: function (msg) {
            var data = eval("(" + msg + ")"),
                i,
                str;
            $("#" + ddlname).empty();
            str = '<option value= none selected>---------</option>';
            $("#" + ddlname).append(str);
            if (data.length !== 0) {
                for (i = 0; i < data.length; i += 1) {
                    if (state_id == data[i]["id"]){
                        str = '<option selected value="' + data[i]["id"] + '" >' +
                        data[i]["value"] + '</option>';
                    } else {
                        str = '<option value="' + data[i]["id"] + '" >' +
                        data[i]["value"] + '</option>';
                    }
                    $("#" + ddlname).append(str);
                }
            }
        }
    });
}
function searchcities(state_id, ddlname) {
    $.ajax({
        type: "GET",
        url: Urls['search-cities-view'](),
        data: "state=" + state_id,
        success: function (msg) {
            data = eval("(" + msg + ")");
            $("#"+ddlname).empty();
            $("#"+ ddlname).attr("list", "city");
            str = "<datalist id='city'>";
            $(str).insertAfter($("#" + ddlname));
            for (i = 0; i < data.length; i += 1) {
                str = '<option value="' + data[i]["value"] + '">';
                $("#city").append(str);
            }
            str = "</datalist>";
            $(str).insertAfter($("#city"));
        }
    });
}

$(document).ready(function () { 
    "use strict";
    var city1;
    if($("#id_city1").length){
        city1 = $("#id_city1") 
    } else {
        city1 = $("#id_city")
    }
    if ($("#id_country" + " option:selected").val() == '') {
        $("#id_state").attr("disabled", "disabled");
        city1.prop('disabled',true);
        $('.statefancybox').hide();
    } else {
        $("#id_state").removeAttr('disabled');
        searchstates($("#id_country").val(), 'id_state', $("#id_state").val());
        location1.prop('disabled', false);
        $('.statefancybox').show();
    }
    $('#id_country').change(function () {
        $("#id_state").empty();
        var country_id = $(this).val();
        if (country_id === "") {
            $("#id_state").attr("disabled", "disabled");
            city1.val("");
            $('.statefancybox').hide();
        } else {
            searchstates($("#" + this.id).val(), 'id_state');
            $("#id_state").removeAttr('disabled');
            $('.statefancybox').show();
        }
    });
    $('#id_state').change(function () {
        city1.empty();
        var state_id = $(this).val();
        if (state_id === "") {
            city1.prop('disabled',true);
        } else {
            searchcities($("#" + this.id).val(), city1.attr('id'));
            city1.prop('disabled',false);
        }
    });
    $('#id_country').focusout(function (){
        $("#id_state").focus();
    });
});



