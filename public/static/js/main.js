(function() {
    document.addEventListener("DOMContentLoaded", function() {
        var submitButton = document.querySelector("#submit-form");
        submitButton.addEventListener("click", submitForm);
    });

    function submitForm(e) {
        data = serialize(document.forms[0]);
        var request = new XMLHttpRequest();
        request.onload = function() {
            resultsHandler(request);
        }

        request.open('POST', '/route/', true);
        request.send(data);

        document.querySelector("#results-container").innerHTML = "";
        showSpinner();
    }

    function resultsHandler(request) {
        hideSpinner();
        var resultsContainer = document.querySelector("#results-container");
        var context = JSON.parse(request.responseText);
        if (request.status == 200) {
            context.multipleRoutes = function() {
                return context.routes.length > 1;
            }
            resultsContainer.innerHTML = Mustache.render(resultsTemplate, context);
        } else if (request.status = 400) {
            resultsContainer.innerHTML = Mustache.render(validationErrorTemplate, context);
        } else {
            resultsContainer.innerHTML = Mustache.render(errorTemplate, context)
        }
    }

    function showSpinner() {
        var spinner = document.querySelector("#spinner");
        spinner.style.display = "";
    }

    function hideSpinner() {
        var spinner = document.querySelector("#spinner");
        spinner.style.display = "none";
    }

    var resultsTemplate = "\
     {{#multipleRoutes}}Multiple equivalent routes found{{/multipleRoutes}}\
     {{#routes}}\
       <div class='results-route bg-success'>\
         <div class='results-score'>Cost: {{ cost }} hours</div>\
         <div class='results-directions'>\
           {{#nodes}}\
             <span class='results-node{{#is_target}} results-node-target{{/is_target}}'>{{ id }}</span>,\
           {{/nodes}}\
         </div>\
       </div>\
     {{/routes}}\
    ";

    var validationErrorTemplate = "\
      <div class='bg-danger text-danger'>\
        Errors:\
        <ul>\
          {{#errors}}\
            <li class='text-danger'>{{ . }}</li>\
          {{/errors}}\
         </ul>\
      </div>\
    ";

    var errorTemplate = "\
      <div class='bg-danger'>{{ message }}</div>\
    ";
})();