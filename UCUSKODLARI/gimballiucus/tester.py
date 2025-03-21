import gimballiucus.YKI.image_processing_handler as image_processing_handler
import json
import time
import threading


model_config = json.load(open("./config.json", "r"))["model-config"]
handler = image_processing_handler.Handler()
handler.stop_proccessing()
camera_thread = threading.Thread(target=handler.local_camera, args=(model_config["camera-path"], ), daemon=True)
camera_thread.start()

print("de")
camera_thread.join()