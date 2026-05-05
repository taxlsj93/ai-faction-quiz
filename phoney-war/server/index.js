const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const { joinSession, handleAction, handleAbility, handleSkill, handleDisconnect } = require('./session.js');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: '*' },
  transports: ['websocket', 'polling'],
});

app.use(express.static(path.join(__dirname, '../client')));

// Rate limiter: 5 actions/sec per socket
const rateLimitMap = new Map();
function isRateLimited(socketId) {
  const now = Date.now();
  const entry = rateLimitMap.get(socketId) || { count: 0, reset: now + 1000 };
  if (now > entry.reset) { entry.count = 0; entry.reset = now + 1000; }
  entry.count++;
  rateLimitMap.set(socketId, entry);
  return entry.count > 5;
}

io.on('connection', (socket) => {
  console.log(`[connect] ${socket.id}`);

  socket.on('joinSession', (data) => {
    joinSession(io, socket, data);
  });

  socket.on('action', (data) => {
    if (isRateLimited(socket.id)) {
      socket.emit('actionResult', { success: false, error: 'rate-limit' });
      return;
    }
    handleAction(io, socket, data);
  });

  socket.on('useAbility', (data) => {
    if (isRateLimited(socket.id)) return;
    handleAbility(io, socket, data);
  });

  socket.on('useSkill', (data) => {
    handleSkill(io, socket, data);
  });

  socket.on('disconnect', () => {
    console.log(`[disconnect] ${socket.id}`);
    rateLimitMap.delete(socket.id);
    handleDisconnect(socket);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Phoney War server running on http://localhost:${PORT}`);
});
