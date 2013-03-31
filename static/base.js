$(function() {
  $("ul.flashes li button.remove").on("click", function(event) {
    $(this).parents("li").fadeOut(500, function () {
      $(this).remove();
    });
  });
});
