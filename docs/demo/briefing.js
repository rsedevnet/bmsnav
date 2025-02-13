$(document).ready(function () {
  $('h2').each(function () {
    $(this).text($(this).text().replace(':', ''));
    $(this).text($(this).text().replace('Iff', 'IFF'));
  })

  // $('body').text($('body').text().replace('Iff', 'IFF')); 
});
