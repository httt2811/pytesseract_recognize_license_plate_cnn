import numpy as np
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import pytesseract 

model = tf.keras.models.load_model('./static/models/object_detection.h5')


def object_detection(path, filename):
    #Read image
    image = load_img(path)
    image = np.array(image, dtype=np.uint8)
    image1 = load_img(path, target_size=(224,224))
    
    #Data preprocessing
    img_arr_224 = img_to_array(image1)/255.0
    h, w, d = image.shape
    test_arr = img_arr_224.reshape(1,224,224,3)
  
    #Make predictions
    coords = model.predict(test_arr)
    
    #Denormalize the values
    denorm = np.array([w,w,h,h])
    coords = coords * denorm
    coords = coords.astype(np.int32)
    
    #Draw bounding on top the image
    xmin, xmax, ymin, ymax = coords[0]
    pt1 = (xmin, ymin)
    pt2 = (xmax, ymax)
    print(pt1, pt2)
    cv2.rectangle(image,pt1,pt2,(0,255,0),3)
    
    #Convert into BGR
    img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite('./static/predict/{}'.format(filename),img_bgr)
    return coords

def OCR(path, filename):
    img = np.array(load_img(path))
    cods = object_detection(path, filename)
    xmin, xmax, ymin, ymax = cods[0]
    roi = img[ymin:ymax, xmin:xmax]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blue = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blue, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    invert = 255 - opening
    cv2.imwrite('./static/roi/{}'.format(filename),invert)
   
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\THAO\AppData\Local\Tesseract-OCR\tesseract.exe'
    data = pytesseract.image_to_string(invert)
    print(data)
    return data
