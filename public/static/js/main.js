(function() {
    document.addEventListener("DOMContentLoaded", function() {
        restoreForm();
        var submitButton = document.querySelector("#submit-form");
        submitButton.addEventListener("click", submitForm);
    });

    function submitForm(e) {
        data = serialize(document.forms[0]);
        saveForm(data);
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
            context.has_bonus = function() {
                return Number(this.bonus) != 0;
            }
            resultsContainer.innerHTML = Mustache.render(resultsTemplate, context, { route_template: routeTemplate });
        } else if (request.status = 400) {
            resultsContainer.innerHTML = Mustache.render(validationErrorTemplate, context);
        } else {
            resultsContainer.innerHTML = Mustache.render(errorTemplate, context)
        }

        // add event listeners to newly rendered buttons
        document.querySelector("#best-routes-tab").addEventListener("click", function(e) { showBestRoutes() });
        document.querySelector("#most-direct-tab").addEventListener("click", function(e) { showMostDirectRoutes() });
    }

    function showBestRoutes() {
        // toggle tab styles
        var bestRoutesTab = document.querySelector("#best-routes-tab");
        var mostDirectTab = document.querySelector("#most-direct-tab");
        addClass(bestRoutesTab, "results-tab-selected");
        removeClass(bestRoutesTab, "results-tab-unselected");
        addClass(mostDirectTab, "results-tab-unselected");
        removeClass(mostDirectTab, "results-tab-selected");

        // toggle result list
        document.querySelector("#best-routes").style.display = "";
        document.querySelector("#most-direct-route").style.display = "none";
    }

    function showMostDirectRoutes() {
        // toggle tab styles
        var bestRoutesTab = document.querySelector("#best-routes-tab");
        var mostDirectTab = document.querySelector("#most-direct-tab");
        addClass(bestRoutesTab, "results-tab-unselected");
        removeClass(bestRoutesTab, "results-tab-selected");
        addClass(mostDirectTab, "results-tab-selected");
        removeClass(mostDirectTab, "results-tab-unselected");

        // toggle result list
        document.querySelector("#best-routes").style.display = "none";
        document.querySelector("#most-direct-route").style.display = "";
    }

    function addClass(el, className) {
        if (el.classList) {
            el.classList.add(className);
        } else {
            el.className += " " + className;
        }
    }

    function removeClass(el, className) {
        if (el.classList) {
            el.classList.remove(className);
        } else {
            el.className = el.className.replace(new RegExp('(^|\\b)' + className.split(' ').join('|') + '(\\b|$)', 'gi'), ' ');
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

    function saveForm(data) {
    }

    function restoreForm() {
    }

    var resultsTemplate = "\
<span class='results-tabs'><span class='results-tab results-tab-selected' id='best-routes-tab'>Best routes</span><span class='results-tab results-tab-unselected' id='most-direct-tab'>Most direct route</span></span>\
<div id='best-routes'>\
  <ol>\
    {{#routes}}\
      <div class='row'>\
        <div class='col-xs-12'>\
          <li>\
            {{> route_template}}\
          </li>\
        </div>\
      </div>\
    {{/routes}}\
  </ol>\
</div>\
<div id='most-direct-route' style='display:none'>\
  {{#most_direct}}\
    <div class='row'>\
      <div class='col-xs-12'>\
        {{> route_template }}\
      </div>\
    </div>\
  {{/most_direct}}\
</div>\
";
    var routeTemplate = "\
<div class='results-route'>\
  <dl class='dl-horizontal'>\
    <dt>Cost</dt><dd>{{ cost }} hours</dd>\
    <dt>Distance</dt><dd>{{ distance }} miles</dd>\
    <dt>Actual time</dt><dd>{{ cost_without_bonuses }} hours</dd>\
    <dt>Route</dt>\
    <dd>\
      <div class='results-directions'>\
        {{#nodes}}\
          <span class='results-node{{#is_target}} results-node-target{{/is_target}}{{#has_bonus}} results-node-bonus{{/has_bonus}}'>{{ id }}{{#has_bonus}} (-{{ bonus }}){{/has_bonus}}</span>,\
        {{/nodes}}\
      </div>\
    </dd>\
  </dl>\
</div>\
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