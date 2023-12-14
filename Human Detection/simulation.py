import json
import random
import paho.mqtt.client as mqtt
import schedule

def mqttConnection(): # mqtt broker connection
    global siteTopic

    broker_address = "146.235.53.46"
    broker_port = 1883
    username = "nimbus"
    password = "batatafrita"

    client = mqtt.Client()
    client.username_pw_set(username, password)

    client.connect(broker_address, broker_port)

    client.publish(f'{siteTopic}/logs', "Client MQTT connected!") # publish to site logs topic

    return client

# Dictionary to store the last generated values for each sector
sectors = ["entrada", "praça de alimentação", "acougue", "padaria", "hortifruti"]
last_values = {sector: 0 for sector in sectors}

def generate_json(sector):
    # Generate a new value within maxDifference of the last value for the sector
    value = random.randint(max(0, last_values[sector] - maxDifference), min(20, last_values[sector] + maxDifference))
    
    # Update the last value for the sector
    last_values[sector] = value
    
    data = {"counter": value}
    json_str = json.dumps(data)
    return json_str

def callback_function(sector):
    publishContent = generate_json(sector)
    topic = f'/{siteTopic}/cams/{sector}'
    # print(f'{topic} -> {publishContent}')
    mqttClient.publish(topic, publishContent) # send people counting simulation to topic /siteTopic/cams/camTopic

# Start callback functions for each sector
def simulateData():
    for sector in sectors:
        callback_function(sector)


siteTopic = '656c954bd3518eb7af0270f3'
publishInterval = 60*5 # interval in seconds to publish human detection simulation
maxDifference = 5
mqttClient = mqttConnection()


schedule.every(publishInterval).seconds.do(simulateData)

while True:
    schedule.run_pending()
