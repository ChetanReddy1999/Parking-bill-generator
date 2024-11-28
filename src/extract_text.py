import logging
import boto3

from src.constants import IND_NUM_PREFIX
from botocore.exceptions import ClientError
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('app.env'), override=True)

# Get the boto3 client.
textract_client = boto3.client('textract', region_name='ap-south-1')


def extract_text_from_image(image):
    try:
        # Call Amazon Textract to detect text in the image.
        response = textract_client.detect_document_text(Document={'Bytes': image})

        # Print detected text.
        detected_text = ""
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                detected_text += item["Text"] + "\n"

        if detected_text=="":
            return None
        return extract_number_plate(detected_text)
    except ClientError as e:
        logging.error(e)
        return None

def extract_number_plate(text):
    for line in text.split("\n"):
        if line.startswith(tuple(IND_NUM_PREFIX)):
            # eg - AP36AZ1234
            if line[0:2].isalpha() and line[2:4].isdigit() and line[-4:].isdigit():
                return line
    
    return None