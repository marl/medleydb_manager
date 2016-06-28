
function getRequestRecordInput(){
	name=$("#your_name").val();
	// console.log(name); helpful to debug
	email=$("#your_email").val();

	// do for all id's requestrecord.html


	$.get("/thankyou?name=" + name + "&email=" + email, function(response){
		// "hello"
	} );

}

function getNewTicketInpuxt(){
	// do for all id's in newticket.html
	$.get("/multitrack_info?name=" + name + "&email=" + email, function(response){
	// "hello"
	} );
}

$(document).ready(function() { 
	console.log("javascript working");
	// add class="active" to certain url path that is clicked
	var pathname = window.location.pathname;
	$('.nav > li > a[href="'+pathname+'"]').parent().addClass('active');
	$("#submit").click(getforminput);
});
