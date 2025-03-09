const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    username: { type: String, unique: true, required: true },
    email: { type: String, unique: true, required: true },
    password: { type: String, required: true },  // Password will be hashed
    friends: [{
        userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User'},
        lastChatTime: { type: Date, default: Date.now }
    }] // References to other users they are chatting with
});

const User = mongoose.model('User', userSchema);

module.exports = User;
