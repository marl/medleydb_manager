
function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}


function getRequestRecordInput(){
	your_name=$("#your_name").val();
	your_email=$("#your_email").val();
	you=$("#you").val();
	contact_name=$("#contact_name").val();
	contact_email=$("#contact_email").val();
	record_date1=$("#record_date1").val();
	record_date2=$("#record_date2").val();
	record_date3=$("#record_date3").val();
	hours_needed=$("#hours_needed").val();
	expected_num=$("#expected_num").val();
	genre=$("#genre").val();
	
	// Call api to record information to database
	$.get("/api/requestrecord?your_name=" + your_name +
		"&your_email=" + your_email +
		"&you=" + you +
		"&contact_name=" + contact_name +
		"&contact_email=" + contact_email +
		"&record_date1=" + record_date1 +
		"&record_date2=" + record_date2 +
		"&record_date3=" + record_date3 +
		"&hours_needed=" + hours_needed +
		"&expected_num=" + expected_num +
		"&genre=" + genre +
		
		function(response){
			console.log($.parseJSON(response)); //for debugging - will print the returned info
		} 
	);

	// Send email to your_email, MedleyD.taea5mqvehv6g5ij@u.box.com , and studio manager

	// Redirect to thank you page
	window.location = "/thankyou";
}


function getNewTicketInput(){
	// do for all id's in newticket.html
	ticket_name = $("#ticket_name").val();
	status = $("#status").val();
	session_date = $("#session_date").val();
	engineer_name = $("#engineer_name").val();
	engineer_email = $("#engineer_email").val();
	creator_name = $("#creator_name").val();
	creator_email = $("#creator_email").val();
	assignee_name = $("#assignee_name").val();
	assignee_email = $("#assignee_email").val();
	mixer_name = $("#mixer_name").val();
	mixer_email = $("#mixer_email").val();
	mixed_date = $("#mixed_date").val();
	location_mixed = $("#location_mixed").val();
	location_exported = $("#location_exported").val();
	genre = $("#genre").val();
	comments = $("#comments").val();
	num_multitracks = $("#num_multitracks").val();

	// Call api to record information to database
	$.get("/api/newticket?session_date=" + session_date + 
		"&engineer_name=" + engineer_name +
		"&engineer_email=" + engineer_email +
		"&creator_name=" + creator_name +
		"&creator_email=" + creator_email +
		"&assignee_name=" + assignee_name +
		"&assignee_email=" + assignee_email +
		"&mixer_name=" + mixer_name +
		"&mixer_email=" + mixer_email +
		"&mixed_date=" + mixed_date +
		"&location_mixed=" + location_mixed +
		"&location_exported=" + location_exported +
		"&comments=" + comments +
		"&num_multitracks=" + num_multitracks, 
		function(response){
			console.log($.parseJSON(response)); //for debugging - will print the returned info
		} 
	);

	// Redirect to new multitrack page
	window.location = "/newticket_multitracks?multitrack_number=1&total_multitracks=" + num_multitracks;
}



function getNewMultitrackInput(){
	console.log('hi')
	// same as above
	multitrack_name = $("#multitrack_name").val();
	multitrack_id = $("#multitrack_id").val();
	artist_name = $("#artist_name").val();
	start_time = $("#start_time").val();
	end_time = $("#end_time").val();
	genre = $("#genre").val();
	num_instruments = $("#genre").val();

	$.get("/api/newmultitrack?multitrack_name=" + multitrack_name + 
		"&multitrack_id=" + multitrack_id +
		"&artist_name=" + artist_name +
		"&start_time=" + start_time +
		"&end_time=" + end_time +
		"&genre=",
		function(response){
			console.log($.parseJSON(response));
		} 
	);

	var multitrack_number = getParameterByName('multitrack_number');
	var total_multitracks = getParameterByName('total_multitracks');

	if (multitrack_number != total_multitracks) {
		multitrack_number = (parseInt(multitrack_number)+1).toString();
		window.location = "/newticket_multitracks?multitrack_number="+multitrack_number+"&total_multitracks="+total_multitracks;
	}
	else {

		// Send email to your_email, MedleyD.taea5mqvehv6g5ij@u.box.com , and studio manager

		window.location = "/thankyou";
	}

}



function validateRequestRecordForm() {
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    }
}


$(document).ready(function() {
	console.log("javascript working");
	// add class="active" to certain url path that is clicked
	var pathname = window.location.pathname;
	$('.nav > li > a[href="'+pathname+'"]').parent().addClass('active');
	$("#submitRequest").click(getRequestRecordInput);
	$("#submitNewTicket").click(getNewTicketInput);
	$("#nextMultitrack").click(getNewMultitrackInput);
	$("#submitNewMultitrack").click(getNewMultitrackInput);

});
