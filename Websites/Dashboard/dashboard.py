import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import datetime
import calendar
import os

if not os.path.exists("images"):
    os.mkdir("images")

siteId = '656c954bd3518eb7af0270f3'

def on_message(client, userdata, message):
    global enableAlert
    # msg = json.loads(message.payload.decode())
    # print(msg)
    # # print(f'eA: {enableAlert}, >0: {msg["counter"] > 0}')
    # if(enableAlert and msg['counter'] > 0):
    #     print('ALERTA!')
    #     client.publish(f'/{siteId}/alerts', "ALERTA!") # publish to site alerts topic

client = mqtt.Client()  
# client.on_message = on_message

def mqttConnect(): # mqtt broker connection
    global siteId

    broker_address = "146.235.53.46"
    broker_port = 1883
    username = "nimbus"
    password = "batatafrita"

    client.username_pw_set(username, password)

    client.connect(broker_address, broker_port)

    client.publish(f'/{siteId}/logs', "Client MQTT connected!") # publish to site logs topic

    client.subscribe(f'/{siteId}/cams/')

    # client.loop_start()

# Function to check if MQTT is connected
def is_mqtt_connected():
    return client.is_connected()


# Check MQTT connection and reconnect if necessary
if not is_mqtt_connected():
    print("Connecting to MQTT...")
    mqttConnect()
    print("Connected to MQTT!")

####################################### PAGE #######################################

st.set_page_config(
    page_title="NimbusVision Dashboard",
    page_icon="📊",
    layout="centered",
)

st.title("NimbusVision Dashboard")


# DATE SELECTION
dateNow = datetime.datetime.now()
year = dateNow.year
month = dateNow.month

dateSelect = st.date_input(
    "Selecione o intervalo de tempo para visualizar os dados",
    (datetime.date(year, month, 1), datetime.date(year, month, calendar.monthrange(year, month)[1])),
    format="DD/MM/YYYY",
)

# GET DATA
data_url = f'http://146.235.53.46:8000/contagem/{siteId}'

@st.cache_data(ttl=60)
def get_data() -> pd.DataFrame():
    return pd.read_json(data_url)

data = get_data()
data['created_at'] = data['created_at'].dt.tz_convert('America/Belem')
lastUpdate = data["created_at"][len(data)-1]

dataTemp = pd.DataFrame()
dataTemp['created_at'] = pd.to_datetime(data['created_at']).dt.date
start = dateSelect[0]
finish = dateSelect[1] if len(dateSelect) > 1 else dateSelect[0]
mask = (dataTemp['created_at'] >= start) & (dataTemp['created_at'] <= finish)
data = data.loc[mask]

# ALERTS
st.subheader('Alertas')
enableAlert = st.toggle('Ativar alertas')

if(enableAlert):
    st.write('Alertas ativados!')

# ALL SECTORS GRAPH
st.subheader('Visualização Geral')

data['position'] = data.groupby('setor').cumcount(ascending=False) + 1
meanOf = 10
lastAllSectionsCountMean = data[data['position'] <= meanOf]
lastAllSectionsCount = data[data['position'] == 1]
countMean = np.sum(lastAllSectionsCountMean['contagem'])/meanOf
countLast = np.sum(lastAllSectionsCount['contagem'])

st.metric("Pessoas no estabelecimento", countLast, round(countLast - countMean))

tab1, tab2, tab3 = st.tabs(["Barras", "Linha", "Pizza"])
with tab1:
    place_bar = px.bar(data, x='created_at', y='contagem', labels={'created_at':'Data/Hora', 'contagem':'Pessoas'}, height=500, color='setor')
    st.plotly_chart(place_bar)
with tab2:
    place_bar = px.line(data, x='created_at', y='contagem', labels={'created_at':'Data/Hora', 'contagem':'Pessoas'}, height=500, color='setor')
    st.plotly_chart(place_bar)
with tab3:
    place_bar = px.pie(data, values='contagem', names='setor', height=500)
    st.plotly_chart(place_bar)

# GRAPH BY SECTOR
st.subheader('Visualização Setorial')

# Filter site sections (cams)
section_filter = st.selectbox("Selecione um setor", pd.unique(data["setor"]))
data_setor = data[data["setor"] == section_filter]
# lastUpdateSec = data_setor["created_at"][len(data_setor)-1]

st.metric("Pessoas no setor", data_setor['contagem'].iloc[-1], str(data_setor['contagem'].iloc[-1] - data_setor['contagem'].iloc[-2]))

tab1, tab2 = st.tabs(["Barras", "Linha"])
with tab1:
    sector_bar = px.bar(data_setor, x='created_at', y='contagem', labels={'created_at':'Data/Hora', 'contagem':'Pessoas'}, height=500)
    st.plotly_chart(sector_bar)
with tab2:
    sector_bar = px.line(data_setor, x='created_at', y='contagem', labels={'created_at':'Data/Hora', 'contagem':'Pessoas'}, height=500)
    st.plotly_chart(sector_bar)

st.markdown(f'Ultima atualização dos dados: {lastUpdate.day}/{lastUpdate.month}/{lastUpdate.year} às {lastUpdate.hour}:{lastUpdate.minute}')
# st.markdown(f'Ultima atualização do setor: {lastUpdateSec.day}/{lastUpdateSec.month}/{lastUpdateSec.year} às {lastUpdateSec.hour}:{lastUpdateSec.minute}')


# st.subheader('Raw data')
# st.write(len(data_setor))
# st.write(data_setor)