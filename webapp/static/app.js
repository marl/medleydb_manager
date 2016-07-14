
function getParameterByName(name, url) {
	console.log("called getParamterByName");
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}


function getRequestRecordInput(){
	console.log("called getRequestRecordInput");
	your_name=$("#your_name").val();
	your_email=$("#your_email").val();
	you=$("#you").val();
	contact_name=$("#contact_name").val();
	contact_email=$("#contact_email").val();
	record_date1=$("#record_date1").val();
	record_date2=$("#record_date2").val();
	record_date3=$("#record_date3").val();
	hours_needed=$("#hours_needed").val();
	num_multitracks=$("#num_multitracks").val();
	genre=$("#genre").val();
	comments=$("#comments").val();

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
		"&num_multitracks=" + num_multitracks +
		"&genre=" + genre +
		"&comments=" + comments,
		function(response){
			console.log("called requestrecord api");
			window.location = "/uploadform?ticket_number=" + response;
		} 
	);

}


function getNewTicketInput(){
	console.log("called getNewTicketInput");
	ticket_name = $("#ticket_name").val();
	status = $("#status").val();
	your_name=$("#your_name").val();
	your_email=$("#your_email").val();
	you=$("#you").val();
	contact_name=$("#contact_name").val();
	contact_email=$("#contact_email").val();
	session_date = $("#session_date").val();
	engineer_name = $("#engineer_name").val();
	engineer_email = $("#engineer_email").val();
	creator_name = $("#creator_name").val();
	creator_email = $("#creator_email").val();
	assignee_name = $("#assignee_name").val();
	assignee_email = $("#assignee_email").val();
	mixer_name = $("#mixer_name").val();
	mixer_email = $("#mixer_email").val();
    bouncer_name = $("#bouncer_name").val();
    bouncer_email = $("#bouncer_email").val();
	mixed_date = $("#mixed_date").val();
	location_mixed = $("#location_mixed").val();
	location_exported = $("#location_exported").val();
	running_name = $("#running_name").val();
	genre = $("#genre").val();
	comments = $("#comments").val();
	num_multitracks = $("#num_multitracks").val();

	// Call api to record information to database
	$.get("/api/newticket?ticket_name=" + ticket_name +
		"&status=" + status + 
		"&your_name=" + your_name + 
		"&your_email=" + your_email + 
		"&you=" + you +
		"&contact_name=" + contact_name +
		"&contact_email=" + contact_email +
		"&session_date=" + session_date + 
		"&engineer_name=" + engineer_name +
		"&engineer_email=" + engineer_email +
		"&creator_name=" + creator_name +
		"&creator_email=" + creator_email +
		"&assignee_name=" + assignee_name +
		"&assignee_email=" + assignee_email +
		"&mixer_name=" + mixer_name +
		"&mixer_email=" + mixer_email +
		"&bouncer_name=" + bouncer_name +
		"&bouncer_email=" + bouncer_email +
		"&mixed_date=" + mixed_date +
		"&location_mixed=" + location_mixed +
		"&location_exported=" + location_exported +
		"&running_name=" + running_name +
		"&genre=" + genre +
		"&comments=" + comments +
		"&num_multitracks=" + num_multitracks, 
		function(response){
			console.log("called newticket api");
			window.location = "/newticket_multitracks?multitrack_number="+1+
			"&num_multitracks="+response.num_multitracks+
			"&ticket_number="+response.ticket_number;
		} 
	);
	
}


function getNewMultitrackInput(){
	console.log("called getNewMultitrackInput");
	var multitrack_number = getParameterByName('multitrack_number');
	var num_multitracks = getParameterByName('num_multitracks');
	var ticket_number = getParameterByName('ticket_number');
	title = $("#title").val();
	artist_name = $("#artist_name").val();
	start_time = $("#start_time").val();
	end_time = $("#end_time").val();
	genre = $("#genre").val();
	num_instruments = $("#num_instruments").val();
	update_ticket_history = false;

	$.get("/api/newmultitrack?ticket_number=" + ticket_number +
		"&multitrack_number=" + multitrack_number +
		"&num_multitracks=" + num_multitracks +
		"&title=" + title + 
		"&artist_name=" + artist_name +
		"&start_time=" + start_time +
		"&end_time=" + end_time +
		"&genre=" + genre +
		"&num_instruments=" + num_instruments +
		"&update_ticket_history=" + update_ticket_history,
		function(response){
			console.log("called newmultitrack api");
			console.log(response);

		} 
	);

	if (multitrack_number != num_multitracks) {
		multitrack_number = (parseInt(multitrack_number)+1).toString();
		window.location = "/newticket_multitracks?multitrack_number="+multitrack_number+
			"&num_multitracks="+num_multitracks+
			"&ticket_number="+ticket_number;		
	}
	else {
		window.location = "/thankyou";
	}

}


function getUpdatedTicketInput(){
	console.log("called getUpdatedTicketInput");
	var ticket_number = getParameterByName('ticket_number');
	var ticket_revision_id = getParameterByName('ticket_revision_id');
	status = $("#status").val();
	ticket_name = $("#ticket_name").val();
	session_date = $("#session_date").val();
	engineer_name = $("#engineer_name").val();
	engineer_email = $("#engineer_email").val();
	assignee_name = $("#assignee_name").val();
	assignee_email = $("#assignee_email").val();
	mixer_name = $("#mixer_name").val();
	mixer_email = $("#mixer_email").val();
    bouncer_name = $("#bouncer_name").val();
    bouncer_email = $("#bouncer_email").val();
	comments = $("#comments").val();
	

	// Call api to record information to database
	$.get("/api/updateticket?ticket_number=" + ticket_number +
		"&ticket_revision_id=" + ticket_revision_id +
		"&status=" + status + 
		"&ticket_name=" + ticket_name +
		"&session_date=" + session_date + 
		"&engineer_name=" + engineer_name +
		"&engineer_email=" + engineer_email +
		"&assignee_name=" + assignee_name +
		"&assignee_email=" + assignee_email +
		"&mixer_name=" + mixer_name +
		"&mixer_email=" + mixer_email +
		"&bouncer_name=" + bouncer_name +
		"&bouncer_email=" + bouncer_email +
		"&comments=" + comments,
		function(response){
			console.log("called updatetickt api");
			window.location = "/ticket?ticket_number="+ticket_number;
		} 
	);

}

function getAddMultitrackInput(){
	var ticket_number = getParameterByName('ticket_number');
	var ticket_revision_id = getParameterByName('ticket_revision_id')
	var num_multitracks = getParameterByName('num_multitracks');
	var multitrack_id = getParameterByName('multitrack_id');
	title = $("#title").val();
	artist_name = $("#artist_name").val();
	start_time = $("#start_time").val();
	end_time = $("#end_time").val();
	genre = $("#genre").val();
	num_instruments = $("#num_instruments").val();
	update_ticket_history = true;

	$.get("/api/newmultitrack?ticket_number=" + ticket_number +
		"&ticket_revision_id=" + ticket_revision_id +
		"&multitrack_id=" + multitrack_id +
		"&num_multitracks=" + num_multitracks +
		"&title=" + title + 
		"&artist_name=" + artist_name +
		"&start_time=" + start_time +
		"&end_time=" + end_time +
		"&genre=" + genre +
		"&num_instruments=" + num_instruments +
		"&update_ticket_history=" + update_ticket_history,
		function(response){
			window.location = "/ticket?ticket_number="+ticket_number;
		} 
	);

}


$(document).ready(function() {
	// add class="active" to certain url path that is clicked
	var pathname = window.location.pathname;
	$('.nav > li > a[href="'+pathname+'"]').parent().addClass('active');
	// $("#submitRequest").click(getRequestRecordInput);
	// $("#submitNewTicket").click(getNewTicketInput);
	// $("#nextMultitrack").click(getNewMultitrackInput);
	// $("#submitNewMultitrack").click(getNewMultitrackInput);
	$("#updateTicketSubmit").click(getUpdatedTicketInput);


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

	$('#addMultitrack').validator().on('submit', function (e) {
	  if (e.isDefaultPrevented()) {
	    return false;
	  } else {
	    e.preventDefault();
	    $("#addMultitrack").click(getAddMultitrackInput);
	  }
	});

});





