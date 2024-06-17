ckan.module('validate_ua', function ($, _) {
  return {
    initialize: function () {
//      console.log('validate_ua loaded')
      var parser = new UAParser();
      var result = parser.getResult();
      var browser = result.browser.name;
      var version = parseInt(result.browser.major);
      var outdated = false;
      var unsupported = false;

	  switch ( browser ) {
	    case 'IE':
            unsupported = true;
            break;
	    case 'Safari':
            unsupported = true;
            break;
	    case 'Edge':
	        if (version < 12){
	            outdated = true;
                }break;

	    case 'Firefox':
	    	if (version < 57){
	            outdated = true;
                }break;

	    case 'Chrome':
	    	if (version < 20){
	            outdated = true;
                }break;

	  	case 'Opera':
	    	if (version < 11){
	            outdated = true;
                }break;

      }
      if (outdated) {
                console.log("This version of "+browser+" is not supported")
	    	    document.getElementById("ua_alert").style.visibility="visible";
                document.getElementById("ua_alert").className="alert alert-error";
	            document.getElementById("ua_alert").innerHTML = "<strong>U gebruikt een verouderde versie ("+version+") van "+browser+".</strong> Wij adviseren u om uw web browser te updaten.<br><strong>You are using an outdated version ("+version+") of "+browser+".</strong> Please update your web browser.";
      }
      if (unsupported) {
                console.log(browser+" is not supported")
	    	    document.getElementById("ua_alert").style.visibility="visible";
                document.getElementById("ua_alert").className="alert alert-error";
                document.getElementById("ua_alert").innerHTML = "<strong>"+browser+" wordt niet ondersteund op deze site.</strong> Wilt u toch gebruik maken van deze site, probeer dan een andere web browser.<br><strong>"+browser+" is not supported for this website.</strong> Consider switching to another web browser.";
      }
    }
  };
});