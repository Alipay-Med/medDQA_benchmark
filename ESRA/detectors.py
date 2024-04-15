import logging
import json
import copy
import base64
import requests
import math
import cv2
import numpy as np
from PIL import Image, ImageChops

def convert_img_array_to_bytes(img_array):
    # Encode the image array into a JPEG format using OpenCV
    success, encoded_image = cv2.imencode(".jpg", img_array)

    if success:
        byte_data = encoded_image.tostring()
        return byte_data
    else:
        raise ValueError("Image encoding failed.")


# Four-Direction Detection - Small Angle
def get_document_angle(image_path: str, api_host: str) -> float:
    """
    Calculates the angle of a document in an image by sending the image to a specified API endpoint.

    Parameters:
    - image_path: Path to the image file.
    - api_host: Hostname and path of the API excluding protocol.

    Returns:
    A floating-point angle of the detected document or zero if no document is detected.
    """
    try:
        # Convert the image to a bytes array and encode it in base64
        image_bytes = str(base64.b64encode(convert_img_array_to_bytes(image_path)), encoding="utf-8")

        # Prepare the request body
        body = {
            "appId": "",
            "appName": "",
            "attributes": {
                "_ROUTE_": "",
            },
            "params": {
                "imageRaw": image_b64_string
            },
            "serviceCode": "",
            "uri": ""
        }
        headers = {"Content-Type": "application/json"}

        # Send the request to the API
        response = requests.post(f"{api_host}", json=body, headers=headers)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

        # Parse the response
        result = response.json()

        if result["resultMap"]['areas']:
            points = result["resultMap"]['areas'][0]['points']
            angle_rad = math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0])
            angle_deg = math.degrees(angle_rad)
            return angle_deg
        else:
            return 0 
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Four-Direction Detection - Large Angle
def large_direction_detection(image_path, api_host):
    image_bytes_base64 = str(base64.b64encode(convert_img_array_to_bytes(image_path)), encoding="utf-8")
    
    body = {
        "appId": "",
        "appName": "",
        "attributes": {
            "_ROUTE_": "",
        },
        "params": {
            "imageRaw": image_bytes_base64
        },
        "serviceCode": "",
        "uri": ""
    }
    
    headers = {"Content-Type": "application/json"}

    try:      
        response = requests.post(api_host, json=body, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        labels = result.get('resultMap', {}).get('labels', [])
        scores = [label.get('score') for label in labels]
        directions = [-90.0, 0, 90.0, 180.0]
        
        for score, direction in zip(scores, directions):
            if score == 1.0:
                return direction
        return None

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def table_angle_detection(image_path, api_host):
    """
    Detects the main body of a table in an image file and computes its orientation angle.

    Parameters:
    - file_path: A string representing the path to the image file.
    - api_endpoint: A string representing the API endpoint to send the request to.

    Returns:
    - A float representing the minimum angle of the table main body, if detected.
    - Returns 361.0 to signify redirection to document detection if no table main body is detected.
    """
    try:
        # Encode the image file to base64
        image_bytes = str(base64.b64encode(convert_img_array_to_bytes(image_path)), encoding="utf-8")
        
        # Prepare the API request payload
        body = {
            "appId": "",
            "appName": "",
            "attributes": {"_ROUTE_": ""},
            "params": {"imageRaw": image_bytes},
            "serviceCode": "",
            "uri": ""
        }
        headers = {"Content-Type": "application/json"}
        
        # Make the API request
        response = requests.post(api_host, json=body, headers=headers)
        response.raise_for_status()  # Check for HTTP request errors
        
        result = response.json()

        # Check if any table areas are detected
        if result["resultMap"]['areas']:
            # Extract the bounding box points of the first detected area
            bbox = result["resultMap"]['areas'][0]['points']
            # Calculate the angle based on the points
            angle = math.degrees(math.atan2(bbox[1][1] - bbox[0][1], bbox[1][0] - bbox[0][0]))
            return float(angle)
        else:
            # Return 361.0 to indicate the necessity of redirection to document detection
            return 361.0
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def OCR_model(image_path, api_host):
    im_data = base64.b64encode(convert_img_array_to_bytes(image_path)).decode('utf8')
    ext = {
        "keep_in_landmark_regions": "",
        "highlight": "",
    }
    
    body = {
            "objectFeatures": {
                "image": {
                    "objectValue": [im_data]
                },
                "ext":{
                    "objectValue": [json.dumps(ext)]
                }
            }
        }
    headers = {
            "Content-Type": "application/json",
            "MPS-app-name": "",
            "MPS-http-version": "",
            "MPS-trace-id": ""
    }
    
    response_ocr = requests.post(
        api_host, data = json.dumps(body), headers = headers, timeout=30)
    return response_ocr