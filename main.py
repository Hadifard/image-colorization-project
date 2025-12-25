import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageColorization

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = AutoImageProcessor.from_pretrained("nielsr/vit-based-colorization")
model = AutoModelForImageColorization.from_pretrained(
    "nielsr/vit-based-colorization"
).to(device)

def colorize_image(image_path: str):
    # Load image (grayscale or RGB)
    image = Image.open(image_path).convert("RGB")

    # Preprocess
    inputs = processor(images=image, return_tensors="pt").to(device)

    # Inference
    with torch.no_grad():
        outputs = model(**inputs)

    # Post-process
    colorized = processor.post_process_colorization(
        outputs, target_sizes=[image.size[::-1]]
    )[0]

    # Convert to OpenCV format
    colorized = (colorized * 255).astype(np.uint8)
    colorized = cv2.cvtColor(colorized, cv2.COLOR_RGB2BGR)

    return colorized


if __name__ == "__main__":
    img_path = "input.jpg"
    result = colorize_image(img_path)

    cv2.imshow("Colorized Image", result)
    cv2.imwrite("output_colorized.jpg", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
