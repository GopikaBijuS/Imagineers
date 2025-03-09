const mongoose = require('mongoose');
const messageSchema = new mongoose.Schema({
  from: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },  // Sender
  to: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },    // Receiver
  text: { type: String, required: true },                                       // Message content
  timestamp: { type: Date, default: Date.now },                                 // Time when the message was sent
});

const Message = mongoose.model('Message', messageSchema);

module.exports = Message;
