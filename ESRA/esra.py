import logging
import json
import copy
import base64
import requests
import math
import cv2
import numpy as np
from PIL import Image, ImageChops
logging.basicConfig(level=logging.DEBUG)


def is_same_line(box1, box2, epsilon=0.15):
    """
    Determines if two bounding boxes belong to the same line.
    
    Args:
        box1 (List[float]): [x1, y1, x2, y2].
        box2 (List[float]): [x1, y1, x2, y2].
        
    Returns:
        bool: True if boxes are on the same line, False otherwise.
    """
    mid_y1 = (box1[1] + box1[3]) / 2
    mid_y2 = (box2[1] + box2[3]) / 2
    height1 = box1[3] - box1[1]
    height2 = box2[3] - box2[1]
    
    tolerance1 = height1 * epsilon
    tolerance2 = height2 * epsilon
    
    return (box2[1] + tolerance2 < mid_y1 < box2[3] - tolerance2) and \
           (box1[1] + tolerance1 < mid_y2 < box1[3] - tolerance1)


def union_box(box1, box2):
    """
    Computes the union of two bounding boxes.
    
    Args:
        box1 (List[float]): [x1, y1, x2, y2].
        box2 (List[float]): [x1, y1, x2, y2].
        
    Returns:
        List[float]: [x1, y1, x2, y2] of the union box.
    """
    x1 = min(box1[0], box2[0])
    y1 = min(box1[1], box2[1])
    x2 = max(box1[2], box2[2])
    y2 = max(box1[3], box2[3])
    return [x1, y1, x2, y2]


def boxes_sort(boxes):
    """
    Sorts bounding boxes from top-left to bottom-right.

    Args:
        boxes (List[List[float]]): List of [x1, y1, x2, y2] boxes.
        
    Returns:
        List[int]: Sorted indices based on y-coordinate then x-coordinate.
    """
    sorted_id = sorted(range(len(boxes)), key=lambda x: (boxes[x][1], boxes[x][0]))

    return sorted_id


# Main class for layout transformation
class LayoutTrans:
    def __init__(self, raw_ocr_data):
        self.parse_raw_ocr(raw_ocr_data)
        self.logger = logging.getLogger(__name__)
    
    def parse_raw_ocr(self, raw_ocr_data):
        # Get OCR results
        maplist = json.loads(
                        json.loads(raw_ocr_data.text)['resultMap']['result']
                    )['result']['final_result_log']['regions']
        
        # Parsing the bounding boxes and texts from the OCR data
        self.boxes = [[item['points'][0][0], item['points'][0][1],
                       item['points'][2][0], item['points'][2][1]]
                      for item in maplist]
        self.texts = [item['content_list'][0] for item in maplist]
        
    def space_layout(self):
        line_boxes = []
        line_texts = []
        max_line_char_count = 0
        line_width = 0
        
        # Process the bounding boxes to group them by line      
        while self.boxes:
            current_line_boxes = [self.boxes.pop(0)]
            current_line_texts = [self.texts.pop(0)]
            line_char_count = len(current_line_texts[-1])
            line_union_box = current_line_boxes[-1]

            # Group bounding boxes that are in the same line
            while self.boxes and is_same_line(current_line_boxes[-1], self.boxes[0]):
                current_line_boxes.append(self.boxes.pop(0))
                current_line_texts.append(self.texts.pop(0))
                line_char_count += len(current_line_texts[-1])
                line_union_box = union_box(line_union_box, current_line_boxes[-1])

            # Sort boxes and texts by their horizontal starting point (x1)
            sorted_indices = sorted(range(len(current_line_boxes)),
                                    key=lambda i: current_line_boxes[i][0])
            current_line_boxes = [current_line_boxes[i] for i in sorted_indices]
            current_line_texts = [current_line_texts[i] for i in sorted_indices]

            # Keep track of the lines
            line_boxes.append(current_line_boxes)
            line_texts.append(current_line_texts)

            # Update the maximum number of characters for a single line
            if line_char_count > max_line_char_count:
                max_line_char_count = line_char_count
                line_width = line_union_box[2] - line_union_box[0]

        # Estimate character width on the line with the max number of characters
        char_width = (line_width / max_line_char_count) * 0.7 if max_line_char_count else 1

        spaced_texts = []

        # Apply spacing logic to each line
        for line_number, line_box in enumerate(line_boxes):
            spaced_line = ""
            for box_index, box in enumerate(line_box):
                left_padding = int(box[0] / char_width) - len(spaced_line)
                spaced_line += " " * left_padding + line_texts[line_number][box_index]
            spaced_texts.append(spaced_line)
        
        # Combine all lines into a single string output, replacing the ☠ character with a space
        output_text = "\n".join(spaced_texts).replace("☠", " ")
        return output_text

def trim_border(img_array):
    """
    Trim the border of the image based on the color of the top-left pixel.
    
    Parameters:
    - img_array: Input image as a numpy array.
    
    Returns:
    - Trimmed image as a numpy array.
    """
    image = Image.fromarray(img_array)
    background = Image.new(image.mode, image.size, image.getpixel((0,0)))
    diff = ImageChops.difference(image, background)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    
    if bbox:
        return np.asarray(image.crop(bbox))
    else:
        return img_array
        
def rotate_image_with_angle(image, angle, scale=0.8):
    """
    Rotate the given image by a specified angle with scaling.
    
    Parameters:
    - image: Input image as a numpy array.
    - angle: Rotation angle in degrees.
    - scale: Scale factor. Default is 0.8 (80% of the original size).
    
    Returns:
    - Rotated image as a numpy array.
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # Getting rotation matrix
    M = cv2.getRotationMatrix2D(center=center, angle=angle, scale=scale)
    
    # Calculating new image boundaries
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    
    # Adjusting rotation matrix to include translation
    M[0, 2] += (nW / 2) - center[0]
    M[1, 2] += (nH / 2) - center[1]
    
    # Performing the affine transformation with black border
    rotated_image = cv2.warpAffine(src=image, M=M, dsize=(nW, nH), borderValue=(0, 0, 0))
    return rotated_image
    
