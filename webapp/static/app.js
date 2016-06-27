

$(document).ready(function() { 
	console.log("javascript working");
	// add class="active" to certain url path that is clicked
	var pathname = window.location.pathname;
	$('.nav > li > a[href="'+pathname+'"]').parent().addClass('active');
});

