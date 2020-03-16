// get current year for copyright. acces with <span id="year"></span>
$('#year').text(new Date().getFullYear());

// fade messages
setTimeout(() => {
    $('#message').fadeOut('slow');
  }, 2000);
