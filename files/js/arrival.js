
$(function() {
/* AJAX SETUP FOR CSRF */

//Getting the cookie from the html because the csrfcookie has security flaws when used 
//with client side js
function getToken(){
    var csrftoken = $('#token').val();
    return csrftoken;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", getToken());
        }
    }
});
/* END AJAX SETUP */


function toggle(username, type, previousValue, label)
{
    $.ajax({
        method: 'POST',
        url: 'toggle/',
        data: {'username': username, 'type': type, 'prev': previousValue},
        success: function() {
            $(label).toggleClass("label-success label-danger");
            if(previousValue == "True")
            {
                $(label).attr('value', "False");
            }
            else if(previousValue == "False")
            {
                $(label).attr('value', "True");
            }
        },
        error: function(res) {
                alert(res['responseText']);
        },
        crossDomain: false
    });
}

$(document).ready(function()
{
     $('tr').each(function(i, row)
    {
        $(row).find('.paid').click(function()
        {
            var username = $(row).find('.username').text();
            var prev = $(this).attr('value');
            toggle(username, 0, prev, this);
        });
        $(row).find('.arrived').click(function()
        {
            var username = $(row).find('.username').text();
            var prev = $(this).attr('value');
            toggle(username, 1, prev, this);
        });
    });     
});

$(document).ready(function(){
             //add index column with all content.
             $(".filterable tr:has(td)").each(function(){
               var t = $(this).text().toLowerCase(); //all row text
               $("<td class='indexColumn'></td>")
                .hide().text(t).appendTo(this);
             });//each tr
             $("#FilterTextBox").keyup(function(){
               var s = $(this).val().toLowerCase().split(" ");
               //show all rows.
               $(".filterable tr:hidden").show();
               $.each(s, function(){
                   $(".filterable tr:visible .indexColumn:not(:contains('"
                      + this + "'))").parent().hide();
               });//each
             });//key up.
             $("input:text:visible:first").focus();
            });//document.ready

});
