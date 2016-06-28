
function getRequestRecordInput(){
	name=$("#your_name").val();
	// console.log(name); helpful to debug
	email=$("#your_email").val();

	// do for all id's requestrecord.html

	// Call api to record information to database and send email
	$.get("/api/requestrecord?name=" + name + "&email=" + email, function(response){
		console.log($.parseJSON(response)) //for debugging - will print the returned info
	} );

	// Redirect to thank you page
	window.location = "/thankyou";
}

function getNewTicketInput(){
	// do for all id's in newticket.html
	num = $("#num_multitracks").val();

	// Call api to record information to database
	$.get("/api/newticket?name=" + name + "&email=" + email, function(response){
		console.log($.parseJSON(response)) //for debugging - will print the returned info
	} );

	// Redirect to new multitrack page
	window.location = "/newmultitrack?num=" + num;
}


function getNewMultitrackInput(){
	// same as above

	// Redirect to thank you page
	window.location = "/thankyou";
}


$(document).ready(function() {
	console.log("javascript working");
	// add class="active" to certain url path that is clicked
	var pathname = window.location.pathname;
	$('.nav > li > a[href="'+pathname+'"]').parent().addClass('active');
	$("#submitRequest").click(getRequestRecordInput);
	$("#submitNewTicket").click(getNewTicketInput);
});
