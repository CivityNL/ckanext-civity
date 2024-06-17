// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

ckan.module('select_child', function ($) {
  return {
    initialize: function () {

        var choices = this.options.choices;
        var parent_field = this.options.parent_field;
        var parent_field_element = $("#field-" + parent_field); //document.getElementById("field-"+parent_field);
        var child_element = this.el;
        var selected_value = this.el.val();

        filterChoices($("select#field-"+parent_field).find(":selected").text());


        function removeOptions(selectbox)
        {
            var i;
            for(i = selectbox.options.length - 1 ; i >= 0 ; i--)
            {
                selectbox.remove(i);
            }
        }

        function filterChoices(parent_text){

            //using the function:
            removeOptions(child_element[0]);

            child_element.append($("<option></option>")
                 .attr("value", "")
                 .text("Niet van toepassing"));

            choices
                .filter(function(choice) { return choice.parent == parent_text; })
                .map(function(choice) {
                     child_element.append($("<option></option>")
                         .attr("value", choice.value)
                         .text(choice.label));
             });

             var b = choices
                .filter(function(choice) { return (choice.parent == parent_text && choice.value == selected_value); }).length;

            if (b == 1) {

                child_element.val(selected_value);
                } else {
                child_element.val("");
               }

        }

//       SET Parent onChange event
        parent_field_element.on('change', function(){

            filterChoices($("select#field-"+parent_field).find(":selected").text());
//          Returns False to avoid the Automatic Reload of the Page
            return false;
        });

    }
  };
});