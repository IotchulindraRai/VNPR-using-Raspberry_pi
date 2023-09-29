import numpy as np
import cv2
import imutils
import pytesseract
import mysql.connector
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Chulin@123",
  database="numberplate"
)

mycursor = mydb.cursor()

# Create table if not exists
#mycursor.execute("CREATE TABLE IF NOT EXISTS plates (id INT AUTO_INCREMENT PRIMARY KEY, date_time DATETIME, number_plate VARCHAR(255))")

cap = cv2.VideoCapture(0)  # 0 indicates default camera

while True:
    ret, image = cap.read()
    if not ret:
        break

    image = imutils.resize(image, width=450)

    # preprocessing
    cv2.imshow("Original Capture image", image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):  # press q to quit
        break

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("1 - Grayscale Conversion", gray)

    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    cv2.imshow("2 - Adaptive Thresholding", thresh)

    # Find contours based on thresholded image
    cnts, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Create copy of original image to draw all contours
    img1 = image.copy()
    cv2.drawContours(img1, cnts, -1, (0, 255, 0), 3)
    cv2.imshow("3 - All Contours", img1)

    # Find the largest rectangle contour
    max_rect = None
    max_area = 0
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if area > max_area and 1.5 < w / h < 5:
            max_rect = (x, y, w, h)
            max_area = area
        # time.sleep(2)
    # Crop the number plate from the image
    if max_rect is not None:
        x, y, w, h = max_rect
        plate_img = image[y:y + h, x:x + w]

        # Save the cropped image
        cv2.imwrite('crop image/' + str(time.time()) + '.png', plate_img)

        # Display the cropped image
        cv2.imshow("4 - Cropped Image", plate_img)

        # Use tesseract to convert the cropped image to string
        text = pytesseract.image_to_string(plate_img, lang='eng')
        if text is not None and len(text)>7<13:
            print("Detected Number is :", text)

            # Insert data into MySQL table
            sql = "INSERT INTO plates (date, number_plate) VALUES (%s, %s)"
            val = (time.asctime(time.localtime(time.time())), text)
            mycursor.execute(sql, val)
            mydb.commit()
    else:
            print("Number plate not found or not valid")
else:
        print("Number plate not found or not valid")

cv2.destroyAllWindows()
cap.release()