$(function() {
  // "remove" buttons on flashed messages
  $("ul.flashes li button.remove").on("click", function removeMsg(event) {
    $(this).parents("li").fadeOut(500, function () {
      $(this).remove();
    });
  });
  // alert user before deleting account
  $("form#delete_user").submit(function warnUser(event) {
    var confirmation = confirm("Are you sure? This will permanently delete your account and all information associated with it.");
    if (confirmation) {
      return true;
    } else {
      return false;
    }
  });
});
