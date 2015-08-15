$(document).ready(function(){
	$("#about-btn").click( function(event) {
		msgstr = $("#msg").html()
		msgstr = msgstr + "o"
		$("#msg").html(msgstr)
	});
});