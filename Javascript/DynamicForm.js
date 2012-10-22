/* DynamicForm
 *
 * Contains functions to update (via AJAX) certain sections of the page as defined as update-able
 * by the server - and to make basic REST calls.
 */

var RestClient = RestClient || {}

// Returns the XMLHTTPRequest supported by the users browser
RestClient.getXMLHttp = function()
{
  var xmlhttp = false;
  if (window.XMLHttpRequest)
  {
    xmlhttp = new XMLHttpRequest()
  }
  else if (window.ActiveXObject)
  {
    try
    {
      xmlhttp = new ActiveXObject("Msxml2.XMLHTTP")
    }
    catch (e)
    {
      try
      {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP")
      }
      catch (E)
      {
        xmlhttp=false
      }
    }
  }
  if (xmlhttp.overrideMimeType)
  {
      xmlhttp.overrideMimeType('text/xml');
  }
  return xmlhttp;
}

//Makes a raw AJAX call, passing in the response to a callback function - Returns true if the request is made
RestClient.makeRequest = function(url, method, params, callbackFunction)
{
    var xmlhttp = RestClient.getXMLHttp();
    if(!xmlhttp) return false;
    if(!method) method = "POST";

    if(method=="GET")
    {
        xmlhttp.open(method, url + "?" + params, true);
        params = null;
    }
    else
    {
        xmlhttp.open(method, url, true);
        xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xmlhttp.setRequestHeader("Content-length", params.length);
        xmlhttp.setRequestHeader("Connection", "close");
    }

    xmlhttp.onreadystatechange =
            function ()
            {
                if (xmlhttp && xmlhttp.readyState == 4) // something was returned from the server
                {
                    callbackFunction(xmlhttp);
                }
            }
    xmlhttp.send(params);
    return xmlhttp;
}

RestClient.get = function(url, params, callbackFunction)
{
    return RestClient.makeRequest(url, "GET", params, callbackFunction);
}

RestClient.post = function(url, params, callbackFunction)
{
    return RestClient.makeRequest(url, "POST", params, callbackFunction);
}

RestClient.put = function(url, params, callbackFunction)
{
    return RestClient.makeRequest(url, "PUT", params, callbackFunction);
}

RestClient.delete = function(url, params, callbackFunction)
{
    return RestClient.makeRequest(url, "DELETE", params, callbackFunction);
}


var DynamicForm = DynamicForm || {};
DynamicForm.RestClient = RestClient;
DynamicForm.handlers = {};
DynamicForm.loading = {};
DynamicForm.baseURL = '';

DynamicForm.serializeControl = function(pageControl)
{
    return DynamicForm.serializeControls([pageControl])
}

DynamicForm.serializeControls = function(pageControls)
{
    var pageControls = WebElements.map(pageControls, WebElements.get);
    var fields = Array();
    var serializedHandlers = []

    for(currentPageControl = 0; currentPageControl < pageControls.length; currentPageControl++)
    {
        var pageControl = pageControls[currentPageControl];
        var requestHandler = pageControl.attributes.handler.value;
        fields = fields.concat(WebElements.map(DynamicForm.handlers[requestHandler].grabFields, WebElements.get) || []);
        WebElements.map(DynamicForm.handlers[requestHandler].grabForms,
                            function(form)
                            {
                                fields = fields.concat(WebElements.getElementsByTagNames(WebElements.Settings.Serialize,
                                                                                        form, true));
                            });
        fields = fields.concat(WebElements.getElementsByTagNames(WebElements.Settings.Serialize, pageControl, true));
        serializedHandlers.push("requestHandler=" + requestHandler);
    }
    return serializedHandlers.concat([WebElements.serializeElements(WebElements.sortUnique(fields))]).join("&");
}

DynamicForm.abortLoading = function(view)
{
    if(DynamicForm.loading.hasOwnProperty(view) && DynamicForm.loading[view] != null)
    {
        if(DynamicForm.loading[view].abort)
        {
            DynamicForm.loading[view].abort();
        }
    }
}

DynamicForm._requestPageControls = function(pageControls, method, silent, params, timeout)
{
    if(typeof(pageControls) != typeof([]))
    {
        pageControls = [pageControls];
    }
    var pageControls = WebElements.map(pageControls, WebElements.get);
    var pageControlIds = WebElements.map(pageControls, function(control){return '"' + control.id + '"';}).join(",");
    var pageControlName = WebElements.map(pageControls, function(control){return control.id;}).join(",");

    if(!method){method = "GET";}
    if(!params){params = '';}

    DynamicForm.abortLoading(pageControlName);

    if(timeout)
    {
        timeoutMethod = setTimeout("DynamicForm." + method.toLowerCase() + "([" + pageControlIds + "], " + silent +
                                   ", '" + params + "');", timeout);
        DynamicForm.loading[pageControlName] = {'timeout':timeoutMethod,
                                    'abort':function(){clearTimeout(DynamicForm.loading[pageControlName]['timeout']);}};
        return;
    }

    var params = [DynamicForm.serializeControls(pageControls), params].join("&");
    if(!silent)
    {
        for(currentPageControl = 0; currentPageControl < pageControls.length; currentPageControl++)
        {
            var pageControl = pageControls[currentPageControl];
            var loader = WebElements.get(pageControl.id + ":Loading");
            var contentHeight = pageControl.offsetHeight;

            WebElements.hide(pageControl);
            WebElements.show(loader);

            if(contentHeight > loader.offsetHeight)
            {
                var half = String((contentHeight - loader.offsetHeight) / 2) + "px";
                loader.style.marginTop = half;
                loader.style.marginBottom = half;
            }
        }
    }

    DynamicForm.loading[pageControlName] = RestClient.makeRequest(DynamicForm.baseURL, method, params,
                                                function(response){DynamicForm._applyUpdates(response, pageControls)});
}

// DynamicForm._requestPageControls = function(pageControl, method, silent, params, timeout)
// {
//     var pageControl = WebElements.get(pageControl);
//     var requestHandler = pageControl.attributes.handler.value;
//     if(!method){method = "GET";}
//     if(!params){params = '';}
//
//     DynamicForm.abortLoading(pageControl.id);
//
//     if(timeout)
//     {
//         timeoutMethod = setTimeout("DynamicForm." + method.toLowerCase() + "('" + pageControl.id + "', " + silent +
//                                    ", '" + params + "');", timeout);
//         DynamicForm.loading[pageControl.id] = {'timeout':timeoutMethod,
//                                      'abort':function(){clearTimeout(DynamicForm.loading[pageControl.id]['timeout']);}};
//         return;
//     }
//
//     var params = ["requestHandler=" + encodeURIComponent(requestHandler),
//                   DynamicForm.serializeControl(pageControl), params].join("&");
//     if(!silent)
//     {
//         var loader = WebElements.get(pageControl.id + ":Loading");
//         var contentHeight = pageControl.offsetHeight;
//         console.log(contentHeight);
//
//         WebElements.hide(pageControl);
//         WebElements.show(loader);
//
//         if(contentHeight > loader.offsetHeight)
//         {
//             var half = String((contentHeight - loader.offsetHeight) / 2) + "px";
//             loader.style.marginTop = half;
//             loader.style.marginBottom = half;
//         }
//     }
//
//     DynamicForm.loading[pageControl.id] = RestClient.makeRequest(DynamicForm.baseURL, method, params,
//                                                 function(response){DynamicForm._applyUpdate(response, pageControl)});
// }

DynamicForm._applyUpdates = function(xmlhttp, pageControls)
{
    var pageControls = WebElements.map(pageControls, WebElements.get);

    if(document.activeElement && ((document.activeElement.tagName.toLowerCase() == "input"
                                    && document.activeElement.type.toLowerCase() != "button"
                                    && document.activeElement.type.toLowerCase() != "submit") ||
                                    document.activeElement.tagName.toLowerCase() == "textarea" ||
                                    document.activeElement.tagName.toLowerCase() == "select"))
    {
        var lastSelectedId = document.activeElement.id;
        if(lastSelectedId){
            setTimeout("var element = WebElements.get('" + lastSelectedId + "'); element.focus();", 10);
        }
        if(document.activeElement.type == "text"){
            var selectStart = document.activeElement.selectionStart;
            var selectEnd = document.activeElement.selectionEnd;
            if(selectStart != selectEnd){
                setTimeout("WebElements.selectText('" + lastSelectedId + "', " + selectStart + ", " + selectEnd + ");", 11);
            }
        }
    }

    var responses = [];
    if(pageControls.length == 1)
    {
        responses = [xmlhttp];
    }
    else
    {
        responses = eval(xmlhttp.responseText);
    }

    for(currentPageControl = 0; currentPageControl < pageControls.length; currentPageControl++)
    {
        var pageControl = pageControls[currentPageControl];
        var response = responses[currentPageControl];
        pageControl.innerHTML = response.responseText;

        WebElements.show(pageControl);
        DynamicForm.loading[pageControl.id] = null;
        WebElements.hide(pageControl.id + ':Loading');

        WebElements.forEach(pageControl.getElementsByTagName('script'), function(scr){
                if(scr.innerHTML)
                {
                    scriptTag = document.createElement('script');
                    scriptTag.type = "text/javascript"
                    WebElements.replace(scr, scriptTag);
                    scriptTag.text = scr.innerHTML;
                }
            });
    }
}

DynamicForm.get = function(pageControl, silent, params, timeout)
{
    return DynamicForm._requestPageControls(pageControl, "GET", silent, params, timeout);
}

DynamicForm.post = function(pageControl, silent, params, timeout)
{
    return DynamicForm._requestPageControls(pageControl, "POST", silent, params, timeout);
}

DynamicForm.put = function(pageControl, silent, params, timeout)
{
    return DynamicForm._requestPageControls(pageControl, "PUT", silent, params, timeout);
}

DynamicForm.delete = function(pageControl, silent, params, timeout)
{
    return DynamicForm._requestPageControls(pageControl, "DELETE", silent, params, timeout);
}
