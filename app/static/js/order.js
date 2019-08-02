function order() {
var div = document.getElementById("sortable")
var children = div.childNodes;
var elements = [];
for (var i=0; i<div.childNodes.length; i++) {
    var child = div.childNodes[i];
    if (child.nodeType == 1) {
        elements.push(child)      
    }
}
string=""
for (var i=0; i<elements.length; i++) {
    string+=elements[i].id.toString();
    }

document.getElementById("order").value = string;}

setInterval(order, 5);

$( function() {
    $( "#sortable" ).sortable();
    $( "#sortable" ).disableSelection();
} );
