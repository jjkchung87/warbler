let currentUser = ""

$('#user_form').on('submit',handleLogin)

async function handleLogin(evt){
    evt.preventDefault()
    const username = $('#username').val() 
    const password = $('#password').val()   


    currentUser = await User.login(username, password)
    sessionStorage.setItem('currentUserId',currentUser.id)
    window.location.href='/';

}


async function retrieveLoggedInUserDetails (){
    userId = sessionStorage.getItem('currentUserId')
    currentUser = await User.retreiveLoggedInUser(userId)
}

async function putMessagesOnPage(){
    $('#messages').empty()
    await retrieveLoggedInUserDetails()    
    for(let message of currentUser.messages){
        const messageHTML = generateMessageHtml(message)
        $('#messages').append(messageHTML)
    }
}


function generateMessageHtml(message){
    let buttonType = currentUser.isLiked(message) ? "btn-primary" : "btn-secondary";

    return `
    <li class="list-group-item">
        <a href="/messages/${message.id}" class="message-link"/>
        <a href="/users/${message.user_id}">
            <img src="#" alt="" class="timeline-image">
        </a>
        <div class="message-area">
            <a href="/users/${message.id}">@USER NAME GOES HERE</a>
            <span class="text-muted">${message.timestamp}</span>
            <p>${message.text}</p>
        </div>

      <div>
      <a class=" btn btn-sm like-button
      ${buttonType}"
      id="${message.id}"
    >
      <i class="fa fa-thumbs-up"></i> 
  </a>`

}




$('#messages').on('click','.like-button',handleLike)

async function handleLike(evt){
    console.log("CLICK")
    evt.preventDefault()
    let message_id = $(this).attr('id')
   


    if($(this).hasClass('btn-primary')){
        await currentUser.addOrRemoveLike("delete", message_id)
    } else {
        await currentUser.addOrRemoveLike("add",message_id)
    }

    $(this).toggleClass("btn-primary btn-secondary")
    
}

$(document).ready(function() {
    // Event listener for opening the pop-up
    $('#openPopup').on('click', function() {
      // Show the Bootstrap modal
      $('#messageModal').modal('show');
  
    //   // Load AJAX content when the pop-up is triggered
    //   $.ajax({
    //     url: '/get_new_message_content', // Replace with your backend URL to fetch the content
    //     method: 'GET',
    //     success: function(data) {
    //       // Display the fetched content inside the modal body
    //       $('.modal-body').html(data);
    //     },
    //     error: function(error) {
    //       console.error('Error loading content:', error);
    //     }
    //   });
    });
  
    // Event listener for submitting the form inside the pop-up
    $('#messageForm').on('submit', async function(event) {
        event.preventDefault();
        let $input = $('#message')
        let $text = $input.val()
        console.log($input, $text)
        await currentUser.createMessage($text)
  
        $(document).ready(async function(){putMessagesOnPage()})
        $input.val("")
        $('#messageModal').modal('hide');
    });
    


  });
  