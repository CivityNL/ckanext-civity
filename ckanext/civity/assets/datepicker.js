"use strict";


this.ckan.module('datepicker', function($) {
    return {
        initialize: function () {
            var ua = window.navigator.userAgent;
            var msie = ua.indexOf("MSIE ");


//              IF Internet Explorer !!!! ALARM!!!
            if (msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./))
            {
                this.el.datepicker({
                    dateFormat: "dd-mm-yy",
                    showOn: "button",
                    buttonImage: "/images/calendar_icon.png",
                    buttonImageOnly: true,
                    buttonText: this.ngettext('Select date')
                });
                this.el.val(
                    this.el.val().split("-").reverse().join("-")
                )
            }
        }
    };
});

