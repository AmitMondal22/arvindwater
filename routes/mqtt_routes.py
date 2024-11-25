from fastapi import APIRouter, HTTPException,Response
from controllers.user import UserController

# from Library.MqttLibrary import mqtt_client, MQTT_TOPIC,publish_energy_message
from Library.MqttLibraryClass import MqttLibraryClass

from controllers.device_to_server import WeatherController

from utils.response import errorResponse, successResponse
import json

# from models.mqtt_model import MqttEnergyDeviceData

from hooks.update_event_hooks import update_topics

mqtt_routes = APIRouter()

mqtt_client = MqttLibraryClass("techavoiot.co.in", 1883)
# Connect to the MQTT broker
mqtt_client.connect()


# @mqtt_routes.on_event("startup")
# async def startup_event():
#     mqtt_client.subscribe([("hello", 0),("hello1", 0)])
 
@mqtt_routes.on_event("startup")
async def startup_event():
    await subscribe_topics()

# =========================================================
# MQTT TOPIC

async def subscribe_topics():
    try:
        data = await update_topics()
        print("Subscribing to topics:", data)
        mqtt_client.subscribe(data)
    except Exception as e:
        print("Error in subscribing topics:", e)
        
# =========================================================
# @mqtt_routes.post("/publish/")
# async def publish_message(message_data: MqttEnergyDeviceData):
#     try:
#         # mqtt_client = MqttLibraryClass("test/topic")
#         mqtt_client.publish(f"ems/{message_data.ib_id}/{message_data.device}", message_data.json(), qos=0)
#         return {"message": "Message published successfully"}
#     except Exception as e:
#         return {"error": str(e)}

