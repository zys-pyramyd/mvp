const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.DEMO_PORT || 3001;

// Serve static files from the demo directory
app.use('/demo', express.static(path.join(__dirname, 'frontend', 'public')));

// Route for demo application
app.get('/demo', (req, res) => {
    res.sendFile(path.join(__dirname, 'frontend', 'public', 'demo.html'));
});

// Health check
app.get('/demo/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'Pyramyd Demo Environment',
        port: PORT,
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(`🎯 Pyramyd Demo Environment running on port ${PORT}`);
    console.log(`📍 Access demo at: http://localhost:${PORT}/demo`);
    console.log(`🔍 Health check: http://localhost:${PORT}/demo/health`);
});

module.exports = app;