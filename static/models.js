BASE_URL = 'http://127.0.0.1:5000/warbler/api'
DEFAULT_IMG_URL = '/static/images/default-pic.png'



class Message{
    constructor({
        id,
        text,
        timestamp,
        user_id
    })
    {
        this.id = id,
        this.text = text,
        this.timestamp = timestamp,
        this.user_id = user_id
    }
}



class User{
    constructor({
                id,
                username, 
                email, 
                likes=[],
                messages=[]
                }){
        this.id = id,
        this.username = username,
        this.email = email,
        this.likes = likes.map(m => new Message(m));
        this.messages = messages.map(m => new Message(m));
    }

    //user logs in and new instance of User created. User ID is stored in session storage to be referenced for each page load/refresh during session to keep track of logged in user
    static async login(username, password){
        const data = {username, password}
        const res = await axios.post(`${BASE_URL}/users/login`, data)
        const {user, likes, messages} = res.data

        return new User({
            id: user.id,
            username: user.username,
            email: user.email,
            likes: likes,
            messages: messages
        })
    }

    //retrieves data for logged in user to re-generate instance of logged in user each time pages reloaded/refreshed
    static async retreiveLoggedInUser(id){
        const res = await axios.get(`${BASE_URL}/users/${id}`)
        const {user, likes, messages} = res.data
        return new User({
            id: user.id,
            username: user.username,
            email: user.email,
            likes: likes,
            messages: messages
        })
    }


    //user adds or removes message from their likes 
    async addOrRemoveLike(newState, message_id){
        const method = newState === "add" ? 'PATCH' : 'DELETE'
        const res = await axios({
            url:`${BASE_URL}/users/${this.id}/likes/${message_id}`,
            method: method
        })
        const {likes} = res.data
        this.likes = likes

    }

    //check to see if a message is liked by user
    async isLiked(message){
        return this.likes.some(l => (l.id === message.id))
    }
    

    //user creates a new message
    async createMessage(text){
        const data = {text}
        const res = await axios.post(`${BASE_URL}/users/${this.id}/messages`, data)
        const {message} = res.data
        const newMessage = new Message ({
            id: message.id,
            text: message.text,
            timestamp: message.timestamp,
            user_id: message.user_id
        })

        this.messages.push(newMessage)
    }

