BASE_URL = 'http://127.0.0.1:5000/warbler/api'
DEFAULT_IMG_URL = '/static/images/default-pic.png'

/*

User
- constructor
- like message (this)

Message
- constructor

Messages
- generate message list (class)
- Add new message (this)

*/


class Message{
    constructor({
        id,
        text,
        timestamp,
        user_id,
        username
    })
    {
        this.id = id,
        this.text = text,
        this.timestamp = timestamp,
        this.user_id = user_id,
        this.username = username
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

    static async signup(username, email, password, image_url=DEFAULT_IMG_URL){
        const data = {username, email, password, image_url}
        const res = await axios.post(`${BASE_URL}/users/signup`, data)
        let {user} = res.data.user
        return new User(id = user.id,
                        username = user.username,
                        email = user.email)
    }

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

    async addLike(message_id){
        const res = await this.addOrRemoveLike("add",message_id)
        const {likes} = res.data
        this.likes = likes
        console.log(likes)

    }

    async removeLike(message_id){
        const res = await this.addOrRemoveLike("delete",message_id)
        const {likes} = res.data
        this.likes = likes
        console.log(likes)

    }

    async addOrRemoveLike(newState, message_id){
        const method = newState === "add" ? 'PATCH' : 'DELETE'
        await axios({
            url:`${BASE_URL}/users/${this.id}/likes/${message_id}`,
            method: method
        })
    }

    async isLiked(message){
        return this.likes.some(l => (l.id === message.id))
    }
        
    async createMessage(text){
        const data = {text}
        const res = await axios.post(`${BASE_URL}/users/${this.id}/messages`, data)
        const {message} = res.data
        const newMessage = new Message ({
            id: message.id,
            text: message.text,
            timestamp: message.timestamp,
            user_id: message.user_id,
            username: message.username
        })

        this.messages.push(newMessage)
    }
    
    
    // async addMessageToLikes(){
    //     const res = await axios.post(
    //         BASE_URL
    //     )
    // }

}
