// Place JS utils here

var buttonClick = function(elementID) {
    $(elementID).button();
    $(elementID).click(function() {
        $(elementID).button('loading')
    }); 
};