import boto3
import os
from dotenv import load_dotenv, find_dotenv
from src.extract_text import extract_text_from_image
from datetime import datetime
import time
from io import BytesIO
import psycopg2
load_dotenv(find_dotenv('app.env'),override=True)

#establishing the connection
conn = psycopg2.connect(
   database=os.getenv('DB_NAME'), 
   user=os.getenv('DB_USER'), 
   password=os.getenv('DB_PASSWORD'), 
   host=os.getenv('DB_HOST'), 
   port= os.getenv('DB_PORT')
)
#Creating a cursor object using the cursor() method
cursor = conn.cursor()

def upload_image_to_s3(image):
    
    # Create an S3 client
    s3_client = boto3.client('s3', region_name='ap-south-2')
    bucket_name = os.getenv('S3_BUCKET_NAME')

    try:
        date = time.strftime("%Y:%m:%d").split(":")

        prefix = f"images/{date[0]}/{date[1]}/{date[2]}/"

        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        file_suffix = 1
        if 'Contents' in response:
            file_suffix = len(response['Contents']) + 1


        object_name = prefix + str(file_suffix) + ".jpg"

        in_mem_file = BytesIO()
        image.save(in_mem_file, format="JPEG")  # Save image to in-memory file in JPEG format
        image_bytes = in_mem_file.getvalue()
        in_mem_file.seek(0)

        text = extract_text_from_image(image_bytes)

        if text is None:
            return None, None, None, False
        
        data, entry_time, time_now = check_if_number_plate_exists(text)

        if data:
            return [text,data,entry_time,time_now], None, None, True     
            

        # Upload the file
        s3_client.upload_fileobj(in_mem_file, bucket_name, object_name)

        time_now = datetime.now()
        add_to_db(file_suffix, text, time_now)
        
        return text, file_suffix, time_now, False
    except Exception as e:
        print(e)
        return None, None, None, False
    
def add_to_db(SrNo, vehicle_number, entry_time):
    # Add the data to the database
    cursor.execute("INSERT INTO vehicleentries (\"Sr No\", \"Vehicle Number\", \"Entry Time\") VALUES (%s, %s, %s)", (SrNo, vehicle_number, entry_time))
    conn.commit()

def check_if_number_plate_exists(vehicle_number):
    cursor.execute("SELECT * FROM vehicleentries WHERE \"Vehicle Number\" = %s", (vehicle_number,))
    data = cursor.fetchone()
    if data is None:
        return None, None, None
    
    # Compute parking charges
    entry_time = data[2]
    time_now = datetime.now()
    time_difference = time_now - entry_time

    # Calculate the parking charges
    parking_charges = 0
    if (time_difference.total_seconds() / 3600) > 0:
        parking_charges = 10 * (time_difference.total_seconds() / 3600)

    # Delete the entry from the database
    cursor.execute("DELETE FROM vehicleentries WHERE \"Vehicle Number\" = %s", (vehicle_number,))
    conn.commit()

    entry_time = entry_time.strftime("%Y-%m-%d %H:%M:%S")
    time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")

    return parking_charges, entry_time, time_now
