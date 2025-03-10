const { spawn } = require('child_process');
const express = require('express');
const bcrypt = require('bcrypt');
const mongoose = require('mongoose');
const path = require('path');
const session = require('express-session');
const User = require('./models/User');
const { GoogleGenerativeAI } = require("@google/generative-ai");

const app = express();

// Start Python script for AI processing (if needed)
const pythonProcess = spawn('python', ['main.py']);
pythonProcess.stdout.on('data', (data) => console.log(`Python Output: ${data}`));
pythonProcess.stderr.on('data', (data) => console.error(`Python Error: ${data}`));
pythonProcess.on('close', (code) => console.log(`Python process exited with code ${code}`));

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'static')));
app.use(session({
    secret: 'your_secret_key',
    resave: false,
    saveUninitialized: true
}));

// MongoDB Connection
mongoose.connect('mongodb://localhost:27017/PRANA', {})
    .then(() => console.log('✅ MongoDB connected...'))
    .catch(err => console.log('❌ MongoDB connection error:', err));

// Initialize Generative AI
const genAI = new GoogleGenerativeAI("AIzaSyBJSlieYtJVvlC_WwCfAl1WUaOmiaCAOpk");
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

// Routes

// Home Route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'index.html'));
});

// Signup Route
app.post('/signup', async (req, res) => {
    const { username, email, password } = req.body;
    try {
        const existingUser = await User.findOne({ $or: [{ email }, { username }] });
        if (existingUser) return res.status(400).json({ message: 'User already exists!' });
        
        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({ username, email, password: hashedPassword });
        await newUser.save();
        res.redirect('/index.html');
    } catch (error) {
        console.error('Signup error:', error);
        res.status(500).json({ message: 'Error during signup!' });
    }
});

// Signin Route
app.post('/signin', async (req, res) => {
    const { username, password } = req.body;
    try {
        const user = await User.findOne({ username });
        if (!user) return res.status(400).json({ message: 'Invalid username or password!' });

        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) return res.status(400).json({ message: 'Invalid username or password!' });

        req.session.user = user;
        res.redirect('/home');
    } catch (error) {
        console.error('Signin error:', error);
        res.status(500).json({ message: 'Error during login!' });
    }
});

// Chatbot Route (Using Gemini AI)
app.post("/chat", async (req, res) => {
    const userMessage = req.body.message;
    console.log(`User: ${userMessage}`);

    if (!userMessage || userMessage.trim() === "") {
        return res.status(400).json({ error: "Message is required" });
    }

    try {
        const result = await model.generateContent(userMessage);
        const botResponse = result.response.text();
        console.log(`Gemini AI: ${botResponse}`);
        res.json({ response: botResponse });
    } catch (error) {
        console.error("Gemini API Error:", error);
        res.status(500).json({ error: "Failed to get response from Gemini AI" });
    }
});

// Protected Home Route
app.get('/home', (req, res) => {
    if (!req.session.user) return res.redirect('/index.html');
    res.sendFile(path.join(__dirname, 'static', 'home.html'));
});

// Logout Route
app.get('/logout', (req, res) => {
    req.session.destroy(() => res.redirect('/index.html'));
});

// Start Server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));

