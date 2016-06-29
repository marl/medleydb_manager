
function getRequestRecordInput(){
	your_name=$("#your_name").val();
	// console.log(name); helpful to debug
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
	piano=$("#piano").val();
	guitar=$("#guitar").val();
	drums=$("#drums").val();
	bass=$("#bass").val();
	vocals=$("#vocals").val();
	violin=$("#violin").val();
	viola=$("#viola").val();
	cello=$("#cello").val();
	// do for all id's requestrecord.html

	// Call api to record information to database and send email
	$.get("/api/requestrecord?your_name=" + your_name +
		"&your_email=" + your_email
		"&you=" + you +
		"&contact_name=" + contact_name +
		"&contact_email=" + contact_email +
		"&record_date1=" + record_date1 +
		"&record_date2=" + record_date2 +
		"&record_date3=" + record_date3 +
		"&hours_needed=" + hours_needed +
		"&expected_num=" + expected_num +
		"&genre=" + genre +
		"&piano=" + piano +
		"&guitar=" + guitar +
		"&drums=" + drums +
		"&bass=" + bass +
		"&vocals=" + vocals +
		"&violin=" + violin +
		"&viola=" + viola +
		"&cello=" + cello, 
		function(response){
		console.log($.parseJSON(response)) //for debugging - will print the returned info
	} );

	// Redirect to thank you page
	window.location = "/thankyou";
}

function getNewTicketInput(){
	// do for all id's in newticket.html
	session_date = $("#session_date").val();
	engineer_name = $("#engineer_name").val();
	engineer_email = $("#engineer_email").val();
	creator_name 00= $("#creator_name").val();
	creator_email = $("#creator_email").val();
	assignee_name = $("#assignee_name").val();
	assignee_email = $("#assignee_email").val();
	mixer_name = $("#mixer_name").val();
	mixer_email = $("#mixer_email").val();
	mixed_date = $("#mixed_date").val();
	location_mixed = $("#location_mixed").val();
	looation_exported = $("#location_exported").val();
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
		"&num=" + num_multitracks, 
		function(response){
		console.log($.parseJSON(response)) //for debugging - will print the returned info
	} );

	// Redirect to new multitrack page
	window.location = "/newticket_multitracks?numks=" + num_multitracks;
}


function getNewMultitrackInput(){
	// same as above
	multitrack_name = $("#multitrack_name").val();
	multitrack_id = $("#multitrack_id").val();
	artist_name = $("#artist_name").val();
	start_time = $("#start_time").val();
	end_time = $("#end_time").val();

	$.get("/api/newmultitrack?multitrack_name=" + multitrack_name + 
		"&multitrack_id=" + multitrack_id +
		"&artist_name=" + artist_name +
		"&start_time=" + start_time +
		"&end_time=" + end_time,
		function(response){
		console.log($.parseJSON(response))
} );


	// Redirect to thank you page
	window.location = "/thankyou";
}

function validateRequestRecordForm() {
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;
    var x = document.forms["requestrecord"]["your_name"].value;
    if (x == null || x == "") {
        alert("Name must be filled out");
        return false;



    }
    


$(document).ready(function() {
	console.log("javascript working");
	// add class="active" to certain url path that is clicked
	var pathname = window.location.pathname;
	$('.nav > li > a[href="'+pathname+'"]').parent().addClass('active');
	$("#submitRequest").click(getRequestRecordInput);
	$("#submitNewTicket").click(getNewTicketInput);
});
