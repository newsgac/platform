const redis = require("redis");

const WebSocket = require('ws');
 
const wss = new WebSocket.Server({ port: 5051 });

wss.on('connection', function connection(ws) {
  const subscriptions = [];
  ws.on('message', function incoming(message) {
    const msg = JSON.parse(message);
    if (msg.type === 'watch_new') {
      const sub = redis.createClient(6379, 'redis');
      sub.subscribe("celery_task_new");
      sub.on("message", function (channel, message) {
        ws.send(message);
        // console.log("sub channel " + channel + ": " + JSON.stringify(JSON.parse(message), null, 4));
      });
      subscriptions.push(sub);
    }
    else if (msg.type === 'watch_task') {
      const sub = redis.createClient(6379, 'redis');
      sub.subscribe("celery_task_" + msg.task_id);
      sub.on("message", function (channel, message) {
        ws.send(message);
        // console.log("sub channel " + channel + ": " + JSON.stringify(JSON.parse(message), null, 4));
      });
      subscriptions.push(sub);
    } else {
      console.warn('receiving unknown message');
    }
    // console.log('received: %s', message);
  });
  ws.on('close', () => {
    // console.log('closing');
    subscriptions.forEach(sub => sub.quit());
  });
});

