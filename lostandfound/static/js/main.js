// Enable pusher logging - don't include this in production
    Pusher.logToConsole = true;

    var pusher = new Pusher('1774431e5feb87294873', {
      cluster: 'us2',
      forceTLS: true
    });

    var channel = pusher.subscribe('notification');
    channel.bind('found-item', function(data) {
    	iziToast.info({
		    title: '',
		    message: JSON.stringify(data.message),
		    timeout:10000,
		    position:"topRight",
		});
    });