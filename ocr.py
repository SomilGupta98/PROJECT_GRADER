import os
import easyocr
import sys

# Set the environment variable to use utf-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set the default encoding for stdout to utf-8
sys.stdout.reconfigure(encoding='utf-8')

reader = easyocr.Reader(["en"], verbose=False)
test = []

for i in range(1,8):
    # Read the image file
    image_path = f't{i}.jpg'
    result = reader.readtext(image_path)

    # Extract and print only the detected string and the confidence score
    for detection in result:
        text = detection[1]
        confidence = detection[2]
        test.append((text, confidence))

print(test)
