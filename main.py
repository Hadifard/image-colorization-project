# coloriziation B&W photos using Zhang et al. Algorithm
# author by HADI SARHANGI FARD

import numpy as np
import cv2
import os
import sys

# you need these files:
# colorization_deploy_v2.prototxt
# colorization_release_v2.caffemodel
# pts_in_hull.npy
# get them from: https://github.com/richzhang/colorization/tree/caffe/colorization/models

def load_model():
    print("loading the model...")
    
    # checking files existence
    if not os.path.exists("model/colorization_deploy_v2.prototxt"):
        print("ERROR: Model files are not found!")
        print("Download from: https://github.com/richzhang/colorization/tree/caffe/colorization/models")
        return None
    
    net = cv2.dnn.readNetFromCaffe("model/colorization_deploy_v2.prototxt", 
                                    "model/colorization_release_v2.caffemodel")
    
    pts = np.load("model/pts_in_hull.npy")
    
    # add the cluster centers
    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]
    
    print("the model loaded!")
    return net

def colorize_image(net, img_path):
    print("colorizing:", img_path)
    
    # reading image
    img = cv2.imread(img_path)
    if img is None:
        print("cant read image!")
        return None
    
    h = img.shape[0]
    w = img.shape[1]
    
    # convert to lab
    img = img.astype("float32") / 255.0
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    
    # resizeing image
    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50
    
    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    
    #resizing back
    ab = cv2.resize(ab, (w, h))
    
    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
    
    #convert BACK to bgr
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")
    
    print("done!")
    return colorized

def show_images(original, colorized):
    #making a grayscale version
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    #making images side by side
    result = np.hstack([gray, colorized])
    
    cv2.imshow("Before and After", result)
    print("press any key to close")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
if __name__ == "__main__":
    # create model folder
    if not os.path.exists("model"):
        os.mkdir("model")
    
    # loading the model
    net = load_model()
    if net is None:
        sys.exit(1)
        
    # colorization the single image
    print("\n--- Processing single image ---")
    input_img = "horse.jpg"  #change input image location <----------
    output_img = "output_colorized.jpg"
    
    if os.path.exists(input_img):
        original = cv2.imread(input_img)
        result = colorize_image(net, input_img)
        if result is not None:
            cv2.imwrite(output_img, result)
            print("saved to:", output_img)
            show_images(original, result)
    else:
        print("image not found:", input_img)
    
    print("\n--- Batch processing ---")
    input_folder = "input_images"
    output_folder = "output_images"
    
    if os.path.exists(input_folder):
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        
        files = os.listdir(input_folder)
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                in_path = os.path.join(input_folder, file)
                out_path = os.path.join(output_folder, "colorized_" + file)
                
                result = colorize_image(net, in_path)
                if result is not None:
                    cv2.imwrite(out_path, result)
    else:
        print("no input_images folder found")
    print("\nall done!")
