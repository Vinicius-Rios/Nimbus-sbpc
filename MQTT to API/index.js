const mqtt = require("mqtt");

const client = mqtt.connect({
  host: '146.235.53.46',
  port: 1883,
  username: 'nimbus',
  password: 'batatafrita'
});

client.on("connect", () => {
  client.subscribe("/#", (err) => {
    if (!err) {
      client.publish("/log", "MQTT connected to API");
    }
  });
});

client.on("message", (topic, message) => {
  // message is Buffer
	try{
    estabelecimentoId = topic.split('/')[1]
    setor = topic.split('/')[3]
		const msg = JSON.parse(message);

    console.log(topic + ' has ' + msg.counter + ' persons.')
		
    fetch("http://146.235.53.46:8000/api/contagem", {
      method: "POST",
      body: JSON.stringify({
        estabelecimendoId: estabelecimentoId,
        setor: setor,
        contagem: msg.counter
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8"
      }
    })
    .then(response => response.json())
    .then(response => console.log(JSON.stringify(response)))

	} catch (err) {
		console.log("Error: " + err);
	}
});
