BASE_URL = 'http://127.0.0.1:5000/api/warbler'

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


class User(
    constructor({
                username, 
                email, 
                likes=[]
                }){
        this.username = username,
        this.email = email,
        this.likes = likes.map(m => new Message(m));
    }

    async addMessageToLikes(){
        const res = await axios.post(
            BASE_URL
        )
    }

)
