$(function () {
  var chatarea = $("#chat");



});


// *******************************************************************
// Chat Application
// *******************************************************************

$(".search-chat").on("keyup", function() {
  var value = $(this).val().toLowerCase();
  $(".chat-users li").filter(function() {
    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
  });
});


$(".app-chat .chat-user ").on("click", function (event) {
  if ($(this).hasClass(".active")) {
    return false;
  } else {
    var findChat = $(this).attr("data-user-id");
    var personName = $(this).find(".chat-title").text();
    var personImage = $(this).find("img").attr("src");
    var hideTheNonSelectedContent = $(this)
      .parents(".chat-application")
      .find(".chat-not-selected")
      .hide()
      .siblings(".chatting-box")
      .show();
    var showChatInnerContent = $(this)
      .parents(".chat-application")
      .find(".chat-container .chat-box-inner-part")
      .show();

    if (window.innerWidth <= 767) {
      $(".chat-container .current-chat-user-name .name").html(
        personName.split(" ")[0]
      );
    } else if (window.innerWidth > 767) {
      $(".chat-container .current-chat-user-name .name").html(personName);
    }
    $(".chat-container .current-chat-user-name img").attr("src", personImage);
    $(".chat").removeClass("active-chat");
    $(".user-chat-box .chat-user").removeClass("bg-light");
    //$('.chat-container .chat-box-inner-part').css('height', '100%');
    $(this).addClass("bg-light");
    $(".chat[data-user-id = " + findChat + "]").addClass("active-chat");
  }
  if ($(this).parents(".user-chat-box").hasClass("user-list-box-show")) {
    $(this).parents(".user-chat-box").removeClass("user-list-box-show");
  }
  $(".chat-meta-user").addClass("chat-active");
  //$('.chat-container').css('height', 'calc(100vh - 158px)');
  $(".chat-send-message-footer").addClass("chat-active");
});

// Send Messages
$(".message-type-box").on("keydown", function (event) {
  if (event.key === "Enter") {
    // Start getting time
    var now = new Date();
    var hh = now.getHours();
    var min = now.getMinutes();

    var ampm = hh >= 12 ? "pm" : "am";
    hh = hh % 12;
    hh = hh ? hh : 12;
    hh = hh < 10 ? "0" + hh : hh;
    min = min < 10 ? "0" + min : min;

    var time = hh + ":" + min + " " + ampm;
    // End

    var chatInput = $(this);
    var chatMessageValue = chatInput.val();
    if (chatMessageValue === "") {
      return;
    }
    $messageHtml =
      '<div class="text-end mb-3"> <div class="p-2 bg-light-info text-dark rounded-1 d-inline-block fs-3">' +
      chatMessageValue +
      '</div> <div class="d-block fs-2">' +
      time +
      "</div>  </div>";
    var appendMessage = $(this)
      .parents(".chat-application")
      .find(".active-chat")
      .append($messageHtml);
    var clearChatInput = chatInput.val("");
  }
});





// *******************************************************************
// Email Application
// *******************************************************************

$(document).ready(function(){
  $(".back-btn").click(function(){
    $(".app-email-chatting-box").hide();
  });
  $(".chat-user").click(function(){
    $(".app-email-chatting-box").show();
  });
});


// *******************************************************************
// chat Offcanvas
// *******************************************************************

$("body").on('click', '.chat-menu', function () {
  $(".app-chat-offcanvas").toggleClass('app-chat-right');
  $(this).toggleClass('app-chat-active');
});