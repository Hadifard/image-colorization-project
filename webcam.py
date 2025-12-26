import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageColorization

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoImageProcessor.from_pretrained("nielsr/vit-based-colorization")
model = AutoModelForImageColorization.from_pretrained(
    "nielsr/vit-based-colorization"
).to(device)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame_rgb)
    inputs = processor(images=image, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)

    colorized = processor.post_process_colorization(
        outputs, target_sizes=[image.size[::-1]]
    )[0]

    colorized = (colorized * 255).astype(np.uint8)
    colorized = cv2.cvtColor(colorized, cv2.COLOR_RGB2BGR)

    cv2.imshow("Real-Time Colorization", colorized)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
