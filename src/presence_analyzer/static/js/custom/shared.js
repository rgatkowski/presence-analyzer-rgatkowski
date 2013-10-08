/**
 * Created by rgatkowski on 03.10.13.
 */
function parseInterval(value) {
    var result = new Date(1,1,1);
    result.setMilliseconds(value*1000);
    return result;
}

google.load("visualization", "1", {packages:["corechart", "timeline"], 'language': 'pl'});

(function($) {
    $(document).ready(function(){
        var loading = $('#loading');
        $.ajaxSetup({ cache: false });
        $.getJSON("/api/v2/users", function(result) {
            var dropdown = $("#user_id");
            $.each(result, function(item) {
                dropdown.append($("<option />").val(this.user_id).text(this.name).attr("avatar", this.avatar));
            });
            dropdown.show();
            loading.hide();
        });
    })
})(jQuery)