import os
import cv2
import sys
from esra import rotate_image_with_angle, trim_border, LayoutTrans
from detectors import OCR_model, large_direction_detection, get_document_angle, table_angle_detection
import requests
import numpy as np
import json

def process_image_rotation(image_path):
    """
    Process image rotation based on both large and small angle detections.
    
    Parameters:
    - image_path: Path to the input image file.
    
    Returns:
    - Final rotated image as a numpy array.
    """
    # Detect large rotation angle
    angle_large = large_direction_detection(image_path, api_url="")  
    img_rotated_large = rotate_image_with_angle(image_path, angle_large)
    img_rotated_large = trim_border(img_rotated_large)
    table_angle = table_angle_detection(img_rotated_large, api_url="")
    
    # Detecting and adjusting for small angle rotation
    if table_angle == 361.0:
        # If no table is detected, use document angle detection for small rotation adjustment
        angle_small = get_document_angle(image_path, api_url="")
    else:
        # Use table detection angle for small rotation adjustment if a table is detected
        angle_small = table_angle
        
    final_rotated_image = rotate_image_with_angle(img_rotated_large, angle_small)
    return final_rotated_image


def main(url):
    response = requests.get(url)
    if response.status_code == 200:
        image_data = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        image = process_image_rotation(image)
        result = OCR_model(image, api_url = "")
        output = LayoutTrans(result).space_layout()
    else:
        print(f"Failed to download the image. Status code: {response.status_code}")
        output='Error'
    return output

if __name__ == '__main__':
    img_url=f'http://xxxxx'
    output=main(img_url)

    # process images
    # data_to_write = []
    # for i in range(1,10):
    #     print(i)
    #     img_url=f'http://xxxxx'
    #     try:
    #         output=main(img_url)
    #     except:
    #         output='error'
    #     data_dict = {
    #             "url": img_url,
    #             "img_path": f'{i}.jpg',
    #             "output": output
    #     }
    #     data_to_write.append(data_dict)

    # file_name = ""

    # with open(file_name, 'w') as json_file:
    #     for entry in data_to_write:
    #         json_file.write(json.dumps(entry,ensure_ascii=False) + '\n')

    # print(f"Data written to {file_name} successfully.")


