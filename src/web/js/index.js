window.onload = function () {
    // Query API on page load to return data and display in HTML table with id dataTable
    $(document).ready(function () {
        $.ajax({
            url:  "API_GATEWAY_URL_GOES_HERE/getVanityNumbers",
            type: 'GET',
            contentType: 'application/json',
            success: function (data) {
                // Loop through each result in body object of returned data and create and insert a new row into table id dataTable
                for (var i in data) {
                    var newHtmlRow = 
                    "<tr>" +
                        "<td>" + data[i]["displayTime"] + "</td>" +
                        "<td>" + data[i]["callerNumber"] + "</td>" +
                        "<td>" + data[i]["vanitynumbers"] + "</td>" +
                    "</tr>"

                    $("#dataTable").append(newHtmlRow);
                } 
            },
            error: function (err) {
                alert(err);
            }
        });
    });
}