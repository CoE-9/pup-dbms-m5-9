(function($) {

    // your code here
	function onFormSubmit(event){

		var data = $(event.target).serializeArray();

		var thesis = {};
		for(var i = 0; i<data.length ; i++){
			thesis[data[i].name] = data[i].value;
		}

		// send data to server
			var thesis_create_api = '/api/thesis';
			$.post(thesis_create_api, thesis, function(response){

			// read response from server
			if (response.status = 'OK') {
				var thesis_info = thesis.year + ' - '  + thesis.thesis_title + ' created by: ' + thesis.app_user + ' <a href=\"/thesis/delete/'+thesis.id+'\"><button id=\"delete\" type=\"submit\">DELETE</button></a><hr> ';
				$('.thesis-list').prepend('<li>' + thesis_info + '</li>')
				$('input[type=text], [type=number]').val('');
				$('select[name=year]').val('year');
				$('select[name=section]').val('section');
			} else {
				// add something 
			}

			});

		return false;
	}

	function loadThesis(){
		var thesis_list_api = '/api/thesis';
		$.get(thesis_list_api, {} , function(response) {
			console.log('.thesis-list', response)
			response.data.forEach(function(thesis){
				var thesis_info = thesis.year + ' - '  + thesis.thesis_title + ' created by: ' + thesis.app_user + ' <a href=\"/thesis/delete/'+thesis.id+'\"><button id=\"delete\" type=\"submit\">DELETE</button></a><hr> ';
				$('.thesis-list').append('<li>' + thesis_info + '</li>')
			});
		});
	}

	$('form#form1').submit(onFormSubmit);
	loadThesis();

	$(document).on('click', 'button#delete', function(){
		$(this).closest('li').remove();
	});


})(jQuery)