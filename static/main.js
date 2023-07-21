let currentUser = ""


/*************************************************** */
//log-in function
$('#user_form').on('submit',handleLogin)

async function handleLogin(evt){
    evt.preventDefault()
    const username = $('#username').val() 
    const password = $('#password').val()   


    currentUser = await User.login(username, password)
    sessionStorage.setItem('currentUserId',currentUser.id)
    window.location.href='/';

}


/*************************************************** */
//Retrieve user data each time page reloads/new page to store in currentUser 

async function retrieveLoggedInUserDetails (){
    userId = sessionStorage.getItem('currentUserId')
    currentUser = await User.retreiveLoggedInUser(userId)
}

/*************************************************** */
//Put messages on page

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


/*************************************************** */
//Like/unlike a message

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


/*************************************************** */
//Creating a new message (modal popup)

$(document).ready(function() {
    // Event listener for opening the pop-up
    $('#openPopup').on('click', function() {
      // Show the Bootstrap modal
      $('#messageModal').modal('show');
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
  