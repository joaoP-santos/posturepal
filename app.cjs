const express = require('express');
const { sendSerialData } = require('./serialPort');

const app = express();
const port = 3000;

// Middleware to handle JSON requests
app.use(express.json());

// API endpoint to update posture quality
app.post('/posture', (req, res) => {
  const { postureQuality } = req.body;

  // Send data to serial port
  const message = postureQuality === 'Good' ? 'off' : 'on';
  sendSerialData(message);  // Send "off" for good posture, "on" for bad posture

  res.send({ status: 'Posture updated', message });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
