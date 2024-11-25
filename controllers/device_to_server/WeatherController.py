from db_model.MASTER_MODEL import insert_data,custom_select_sql_query,select_one_data
from utils.date_time_format import get_current_datetime,get_current_date,get_current_time
from fastapi import BackgroundTasks
from Library.DecimalEncoder import DecimalEncoder
# from Library import AlertLibrary
import json
from models import device_data_model
# from utils.week_date import weekdays_date
from datetime import datetime




async def get_weather_data(data:device_data_model.WeatherDeviceData,client_id,device):
    try:
        device_data=select_one_data("md_device","device_id",f"client_id={client_id} AND device='{device}'")
        if device_data is None:
            raise ValueError("device not found")
        
        device_id=device_data["device_id"]
        current_datetime = get_current_datetime()
      
        date_obj = datetime.strptime(data.DT, "%d%m%y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        
        time_obj = datetime.strptime(data.TM, "%H%M%S")
        formatted_time = time_obj.strftime("%H:%M:%S")
        
         
        columns = "client_id, device_id, device,tw,temperature, rainfall, rainfall_cumulative, atm_pressure, solar_radiation, humidity, wind_speed, wind_direction, runhr, date, time, created_at"

        # value = f"{client_id}, {device_id}, '{device}',{data.TW}, {data.C1}, {data.C4}, {data.RAIN_CUM}, {data.C3}, {data.C6}, {data.C2}, {data.C4}, {data.C5}, {data.RUNHR}, '{formatted_date}', '{formatted_time}', '{current_datetime}'"
        value = f"{client_id}, {device_id}, '{device}',{data.TW}, {data.C1}, {data.PULSE1}, {data.PULSE2}, {data.C3}, {data.C6}, {data.C2}, {data.C4}, {data.C5}, {0.00}, '{formatted_date}', '{formatted_time}', '{current_datetime}'"
        
        print("value",value)
        weather_data_id = insert_data("td_weather_data", columns, value)
        
        if weather_data_id is None:
            raise ValueError("Weather data was not inserted")
        else:
            await send_last_weather_data(client_id, device_id,device)
            user_data = {"weather_data_id":weather_data_id, "device_id": device_id, "device": device}
        return user_data
    except Exception as e:
        raise ValueError("Could not fetch data",e)
    
    

  
async def send_last_weather_data(client_id, device_id, device):
    try:
        # Lazy import inside the function
        from Library.WsConnectionManagerManyDeviceTypes import WsConnectionManagerManyDeviceTypes
        manager = WsConnectionManagerManyDeviceTypes()
        # background_tasks = BackgroundTasks()
        
        from routes.ws_routes import sennd_ws_message    
                
        custom_sql=f""" SELECT *
                        FROM 
                            td_weather_data td
                        WHERE 
                            td.device_id = {device_id}
                            AND td.device = '{device}'
                            AND td.client_id = {client_id}
                        ORDER BY 
                            td.weather_data_id DESC LIMIT 1"""
        lastdata=custom_select_sql_query(custom_sql,None)
        
        
        custom_sql10=f""" SELECT *
                        FROM 
                            td_weather_data td
                        WHERE 
                            td.device_id = {device_id}
                            AND td.device = '{device}'
                            AND td.client_id = {client_id}
                        ORDER BY 
                            td.weather_data_id DESC LIMIT 10"""
        lastdata10=custom_select_sql_query(custom_sql10,1)
        
        
        

        # background_tasks.add_task(AlertLibrary.send_alert, client_id, device_id, device, json.dumps(lastdata, cls=DecimalEncoder))
        
        # await AlertLibrary.send_alert(client_id, device_id, device, json.dumps(lastdata, cls=DecimalEncoder))
        
        # await manager.send_personal_message("EMS",client_id, device_id, device, json.dumps(lastdata, cls=DecimalEncoder))
        twodata={"lastdata":lastdata,"last10row":lastdata10}
        await sennd_ws_message("WMS",client_id, device_id, device, json.dumps(twodata, cls=DecimalEncoder))
        print("twodata",twodata)
       
        return json.dumps(lastdata, cls=DecimalEncoder)
    except Exception as e:
        raise ValueError("Could not fetch data",e)
    
    
