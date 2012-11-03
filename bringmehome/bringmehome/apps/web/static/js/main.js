$(document).ready(function () {
	$('#address-form').submit(function (e) {
		e.preventDefault();
		var address = $(this).find('#address-input').val(),
		user_id = $('#user-id').val();
		data = {
			'url': ('/rest/address/' + user_id + '/'  + address),
			'type': 'GET',
			'success': function (response) {
				if (!response.length) {
					console.log('Did you forget your keys?')
				} else {
					$('#variable-content').empty().append($('<h3>Select your address:</h3><ol id="address-select" style="list-style-type:none;"></ol>'));
					$.each(response, function (idx, itm) {
						var tag = '<li style="margin: 15px 0px 15px 0px;"><a class="btn btn-primary address-select">' + itm + '</a></li>';
						$('#variable-content').find('ol').append($(tag));
					});
				}
			},
			'error': function (response) {
				console.log('error')
			}
		}
		$.ajax(data);
		return false;
	});

	$('.address-select').live('click', function (e) {
		console.log(1)
		e.preventDefault();
		var address = $(this).text(),
		user_id = $('#user-id').val();
		data = {
			'url': ('/rest/register/' + user_id + '/'  + address),
			'type': 'GET',
			'success': function (response) {
				if (!response.length) {
					console.log('Did you forget your keys?')
				} else {
					$('#variable-content').empty().append($('<h3>Thanks!</h3><p>Your address has been saved!</p>'));
				}
			},
			'error': function (response) {
				console.log('error')
			}
		}
		$.ajax(data);
		return false;
	});
});