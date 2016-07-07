
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
		"&genre=" + genre,
		function(response){
			window.location = "/uploadform?ticket_number=" + response;
		} 
	);

}


function getNewTicketInput(){
	// do for all id's in newticket.html
	ticket_name = $("#ticket_name").val();
	status = $("#status").val();
	your_name=$("#your_name").val();
	your_email=$("#your_email").val();
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
	$.get("/api/newticket?ticket_name=" + ticket_name +
		"&status=" + status + 
		"&your_name=" + your_name + 
		"&your_email=" + your_email + 
		"&session_date=" + session_date + 
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
		"&genre=" + genre +
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
	// same as above
	ticket_number = $("#ticket_number").val();
	your_name = $("#your_name").val();
    your_email = $("#your_email").val();
    status = $("#status").val();
    engineer_name = $("#engineer_name").val();
    engineer_email = $("#engineer_email").val();
    mixer_name = $("#mixer_name").val();
    mixer_email = $("#mixer_email").val();
    bouncer_name = $("#bouncer_name").val();
    bouncer_email = $("#bouncer_email").val();
    comments = $("#comments").val();
	multitrack_name = $("#multitrack_name").val();
	artist_name = $("#artist_name").val();
	start_time = $("#start_time").val();
	end_time = $("#end_time").val();
	genre = $("#genre").val();
	num_instruments = $("#genre").val();

	$.get("/api/newmultitrack?ticket_number=" + ticket_number +
		"&multitrack_name=" + multitrack_name + 
		"&your_name=" + your_name +
	    "&your_email=" + your_email +
	    "&status=" + status +
	    "&engineer_name=" + engineer_name +
	    "&engineer_email=" + engineer_email +
	    "&mixer_name=" + mixer_name +
	    "&mixer_email=" + mixer_email +
	    "&bouncer_name=" + bouncer_name +
	    "&bouncer_email=" + bouncer_email +
		"&artist_name=" + artist_name +
		"&start_time=" + start_time +
		"&end_time=" + end_time +
		"&genre=" + genre +
		"&comments=" + comments,
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
		window.location = "/thankyou";
	}

}


function getUpdatedTicketInput(){
	var ticket_number = getParameterByName('ticket_number');
	status = $("#status").val();
	ticket_name = $("#ticket_name").val();
	session_date = $("#session_date").val();
	engineer_name = $("#engineer_name").val();
	engineer_email = $("#engineer_email").val();
	assignee_name = $("#assignee_name").val();
	assignee_email = $("#assignee_email").val();
	comments = $("#comments").val();

	// Call api to record information to database
	$.get("/api/updateticket?status=" + status + 
		"&ticket_name=" + ticket_name +
		"&ticket_number=" + ticket_number +
		"&session_date=" + session_date + 
		"&engineer_name=" + engineer_name +
		"&engineer_email=" + engineer_email +
		"&assignee_name=" + assignee_name +
		"&assignee_email=" + assignee_email +
		"&comments=" + comments,
		function(response){
			console.log($.parseJSON(response)); //for debugging - will print the returned info
		} 
	);

	window.location = "/viewtickets";
}


$(document).ready(function() {
	// add class="active" to certain url path that is clicked
	var pathname = window.location.pathname;
	$('.nav > li > a[href="'+pathname+'"]').parent().addClass('active');
	// $("#submitRequest").click(getRequestRecordInput);
	// $("#submitNewTicket").click(getNewTicketInput);
	// $("#nextMultitrack").click(getNewMultitrackInput);
	// $("#submitNewMultitrack").click(getNewMultitrackInput);
	$("#updateTicket").click(getUpdatedTicketInput);

	$('#requestrecord').validator().on('submit', function (e) {
	  if (e.isDefaultPrevented()) {
	    return false;
	  } else {
	    e.preventDefault();
	    $("#submitRequest").click(getRequestRecordInput);
	  }
	});

	$('#newTicket').validator().on('submit', function (e) {
	  if (e.isDefaultPrevented()) {
	  	console.log("hi")
	    return false;
	  } else {
	    e.preventDefault();
	    $("#submitNewTicket").click(getNewTicketInput);
	  }
	});

	$('#nextMultitrack').validator().on('submit', function (e) {
	  if (e.isDefaultPrevented()) {
	    return false;
	  } else {
	    e.preventDefault();
	    $("#nextMultitrack").click(getNewMultitrackInput);
	    $("#submitNewMultitrack").click(getNewMultitrackInput);
	  }
	});

});





