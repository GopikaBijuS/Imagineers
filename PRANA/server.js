const { spawn } = require('child_process');

// Start Python script
const pythonProcess = spawn('python', ['main.py']);

pythonProcess.stdout.on('data', (data) => {
    console.log(`Python Output: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
});

pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
});

const express = require('express');
const bcrypt = require('bcrypt');
const mongoose = require('mongoose');
const path = require('path');
const session = require('express-session');
const User = require('./models/User');

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'static')));
app.use(session({
    secret: 'your_secret_key',
    resave: false,
    saveUninitialized: true
}));

mongoose.connect('mongodb://localhost:27017/PRANA', {
}).then(() => {
    console.log('MongoDB connected...');
}).catch(err => console.log('MongoDB connection error:', err));

// Signup Route
app.post('/signup', async (req, res) => {
    const { username, email, password } = req.body;
    try {
        const existingUser = await User.findOne({ $or: [{ email }, { username }] });
        if (existingUser) {
            return res.status(400).json({ message: 'User already exists!' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({ username, email, password: hashedPassword });
        await newUser.save();
        res.redirect('/index.html');
    } catch (error) {
        console.log('Signup error:', error);
        res.status(500).json({ message: 'Error during signup!' });
    }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'static', 'index.html'));  // Default page
});
// Signin Route
app.post('/signin', async (req, res) => {
    const { username, password } = req.body;
    try {
        const user = await User.findOne({ username });
        if (!user) {
            return res.status(400).json({ message: 'Invalid username or password!' });
        }

        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(400).json({ message: 'Invalid username or password!' });
        }

        req.session.user = user;
        res.redirect('/home');
    } catch (error) {
        console.log('Signin error:', error);
        res.status(500).json({ message: 'Error during login!' });
    }
});

// Home Route (Protected)
app.get('/home', (req, res) => {
    if (!req.session.user) {
        return res.redirect('/index.html');
    }
    res.sendFile(path.join(__dirname, 'static', 'home.html'));
});

// Logout Route
app.get('/logout', (req, res) => {
    req.session.destroy(() => {
        res.redirect('/index.html');
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

