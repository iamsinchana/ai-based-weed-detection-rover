import cv2
import time
import numpy as np
import streamlit as st
from ultralytics import YOLO
import requests

# -----------------------
# LOAD MODEL
# -----------------------

model = YOLO("weed.pt")   # YOUR MODEL PATH
ESP_IP = "192.168.14.217"  # YOUR ESP32 IP

# -----------------------
# ESP32 COMMUNICATION
# -----------------------

def send_esp_command(cmd):
    try:
        if cmd == "weed":
            requests.get(f"http://{ESP_IP}/cut", timeout=0.2)
        else:
            requests.get(f"http://{ESP_IP}/move", timeout=0.2)
    except:
        pass

# -----------------------
# STREAMLIT CONFIG
# -----------------------

st.set_page_config(
    page_title="Smart Weed Detection Rover",
    layout="wide"
)

# -----------------------
# DARK UI
# -----------------------

st.markdown("""
<style>
.stApp {background-color:#121212; color:white;}
h1,h2,h3{
color:#00ff9c;
text-align:center;
}

.paragraph{
color:#cccccc;
font-size:1.05rem;
line-height:1.6;
}

.light-green{
font-size:4rem;
text-align:center;
animation: glowG 1s infinite alternate;
}

.light-red{
font-size:4rem;
text-align:center;
animation: glowR 1s infinite alternate;
}

@keyframes glowG {
from {text-shadow:0 0 5px #00ff00;}
to {text-shadow:0 0 25px #00ff00;}
}

@keyframes glowR {
from {text-shadow:0 0 5px #ff0000;}
to {text-shadow:0 0 25px #ff0000;}
}

</style>
""", unsafe_allow_html=True)


st.title("🌱 Smart Weed Detection Rover Dashboard")
left,right = st.columns([2,1])


# -----------------------
# RIGHT PANEL
# -----------------------

with right:
    st.subheader("📘 Project Overview")
    st.markdown("""
    <div class='paragraph'>
    AI based weed detection using YOLO.

    System behavior:

    • Detects weeds in crop field  
    • Rover moves normally when no weed  
    • Rover stops and activates cutter when weed detected  

    Supports:

    • Live camera  
    • Uploaded image  
    • Uploaded video  
    </div>
    """, unsafe_allow_html=True)

    st.subheader("⚙ Input Source")

    source = st.radio(
        "Choose input type:",
        ["Live Camera","Upload Image","Upload Video"]
    )


# -----------------------
# LEFT PANEL
# -----------------------

with left:

    st.subheader("📡 Detection Feed")

    frame_box = st.empty()
    light_box = st.empty()
    fps_box = st.empty()
    confidence_box = st.empty()


# -----------------------
# DETECTION FUNCTION
# -----------------------

def process_image(frame):
    results = model(frame, imgsz=512, conf=0.45)
    weed_detected = False
    conf_value = 0
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = box.conf[0].item()
            # WEED ONLY
            if cls == 1:
                weed_detected = True
                conf_value = max(conf_value, round(conf*100,1))
                x1,y1,x2,y2 = map(int,box.xyxy[0])
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),3)
                cv2.putText(
                    frame,
                    f"Weed {conf_value}%",
                    (x1,y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0,0,255),
                    2
                )
    return frame, weed_detected, conf_value


# -----------------------
# LIVE CAMERA
# -----------------------

if source == "Live Camera":
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Camera not found")
        st.stop()
    while True:
        ret,frame = cap.read()
        if not ret:
            break
        start = time.time()
        frame,weed,conf = process_image(frame)
        end = time.time()
        fps = round(1/(end-start),1)
        frame_box.image(
            cv2.cvtColor(frame,cv2.COLOR_BGR2RGB),
            width=640
        )
        fps_box.markdown(f"### ⚡ FPS: **{fps}**")
        confidence_box.markdown(f"### 📊 Confidence: **{conf}%**")

        if weed:

            light_box.markdown(
                "<div class='light-green'>🟢</div>",
                unsafe_allow_html=True
            )
            send_esp_command("weed")
        else:
            light_box.markdown(
                "<div class='light-red'>🔴</div>",
                unsafe_allow_html=True
            )
            send_esp_command("move")

# -----------------------
# IMAGE
# -----------------------

elif source == "Upload Image":
    uploaded = st.file_uploader(
        "Upload image",
        type=["jpg","jpeg","png"]
    )
    if uploaded:
        file_bytes = np.frombuffer(uploaded.read(),np.uint8)
        img = cv2.imdecode(file_bytes,1)
        frame,weed,conf = process_image(img)
        frame_box.image(
            cv2.cvtColor(frame,cv2.COLOR_BGR2RGB),
            width=640
        )
        confidence_box.markdown(f"### 📊 Confidence: **{conf}%**")
        if weed:
            light_box.markdown(
                "<div class='light-green'>🟢</div>",
                unsafe_allow_html=True
            )
            send_esp_command("weed")
        else:
            light_box.markdown(
                "<div class='light-red'>🔴</div>",
                unsafe_allow_html=True
            )
            send_esp_command("move")


# -----------------------
# VIDEO
# -----------------------

elif source == "Upload Video":
    uploaded = st.file_uploader(
        "Upload video",
        type=["mp4","avi","mov"]
    )
    if uploaded:
        tfile = "temp_video.mp4"
        with open(tfile,"wb") as f:
            f.write(uploaded.read())
        cap = cv2.VideoCapture(tfile)
        while cap.isOpened():
            ret,frame = cap.read()
            if not ret:
                break
            start = time.time()
            frame,weed,conf = process_image(frame)
            end = time.time()
            fps = round(1/(end-start),1)
            frame_box.image(
                cv2.cvtColor(frame,cv2.COLOR_BGR2RGB),
                width=640
            )
            fps_box.markdown(f"### ⚡ FPS: **{fps}**")
            confidence_box.markdown(f"### 📊 Confidence: **{conf}%**")

            if weed:
                light_box.markdown(
                    "<div class='light-green'>🟢</div>",
                    unsafe_allow_html=True
                )
                send_esp_command("weed")

            else:
                light_box.markdown(
                    "<div class='light-red'>🔴</div>",
                    unsafe_allow_html=True
                )
                send_esp_command("move")
        cap.release()