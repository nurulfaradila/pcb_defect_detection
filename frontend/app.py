import streamlit as st
import requests
import time
from PIL import Image, ImageDraw
import io

BACKEND_URL = "http://backend:8000"

import os
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="PCB Defect Detection", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Typography */
            html, body, [class*="css"] {
                font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                color: #1e293b;
            }
            
            /* Modern Card Style */
            .css-1r6slb0, .css-12oz5g7 {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            
            /* Button Styling */
            .stButton>button {
                color: white;
                background-color: #0f172a; /* Slate 900 */
                border-radius: 8px;
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                border: none;
                transition: all 0.2s ease-in-out;
                letter-spacing: 0.025em;
            }
            .stButton>button:hover {
                background-color: #334155; /* Slate 700 */
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
            }
            .stButton>button:active {
                transform: translateY(0);
            }

            /* Custom Sidebar */
            [data-testid="stSidebar"] {
                background-color: #f8fafc; /* Slate 50 */
                border-right: 1px solid #e2e8f0;
            }
            
            /* Headings */
            h1 {
                color: #0f172a;
                font-weight: 800;
                letter-spacing: -0.025em;
                margin-bottom: 1.5rem;
            }
            h2, h3 {
                color: #334155;
                font-weight: 600;
                letter-spacing: -0.015em;
            }
            
            /* Metrics */
            [data-testid="stMetricValue"] {
                font-size: 1.8rem !important;
                font-weight: 700 !important;
                color: #0f172a !important;
            }
            [data-testid="stMetricLabel"] {
                font-size: 0.875rem !important;
                font-weight: 500 !important;
                color: #64748b !important;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("PCB Defect Detection System")

# Function to fetch stats
def get_stats():
    try:
        res = requests.get(f"{API_URL}/history")
        if res.status_code == 200:
            history = res.json()
            total_scans = len(history)
            defects_found = sum(1 for item in history if item.get("result") and item["result"].get("defects"))
            defect_rate = (defects_found / total_scans * 100) if total_scans > 0 else 0
            return total_scans, defects_found, defect_rate
    except:
        pass
    return 0, 0, 0

# Dashboard Metrics
total, defects, rate = get_stats()
col1, col2, col3 = st.columns(3)
col1.metric("Total PCBs Scanned", total)
col2.metric("Defects Detected", defects)
col3.metric("Defect Rate", f"{rate:.1f}%")

st.markdown("---")

st.sidebar.header("Control Panel")
page = st.sidebar.radio("Navigation", ["Live Inspection", "Historical Data"])

if page == "Live Inspection":
    st.header("Live Inspection")
    uploaded_file = st.file_uploader("Upload PCB Image (Standard Protocol)", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col_img, col_data = st.columns([2, 1])
        
        image = Image.open(uploaded_file)
        with col_img:
            st.image(image, caption='Source Image', use_column_width=True)
        
        with col_data:
            st.subheader("Analysis Control")
            if st.button("Run Inspection Analysis", type="primary"):
                with st.spinner('Processing...'):
                    try:
                        files = {"file": uploaded_file.getvalue()}
                        response = requests.post(f"{API_URL}/predict", files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)})
                        
                        if response.status_code == 200:
                            data = response.json()
                            task_id = data["task_id"]
                            st.info(f"Task ID: {task_id}")
                            
                            progress_bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.01)
                                progress_bar.progress(i + 1)
                            
                            while True:
                                res = requests.get(f"{API_URL}/status/{task_id}")
                                if res.status_code == 200:
                                    status_data = res.json()
                                    if status_data["status"] == "SUCCESS":
                                        result = status_data.get("result", {})
                                        defects = result.get("defects", [])
                                        
                                        if defects:
                                            st.error(f"{len(defects)} Defects Found")
                                        else:
                                            st.success("No Defects Detected")
                                        
                                        # Draw bounding boxes
                                        draw = ImageDraw.Draw(image)
                                        for d in defects:
                                            bbox = d["bbox"]
                                            label = f"{d['type'].upper()} ({d['confidence']:.2f})"
                                            draw.rectangle(bbox, outline="red", width=4)
                                            draw.text((bbox[0], bbox[1]-10), label, fill="red")
                                            
                                        with col_img:
                                            st.image(image, caption='Analyzed Result', use_column_width=True)
                                        
                                        st.subheader("Defect Report")
                                        for d in defects:
                                            st.markdown(f"**Type:** `{d['type']}` | **Conf:** `{d['confidence']:.2f}`")
                                        break
                                    elif status_data["status"] == "FAILURE":
                                        st.error("System Error: Analysis Failed")
                                        break
                                time.sleep(1)
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")

elif page == "Historical Data":
    st.header("Analysis History")
    if st.button("Refresh Data"):
        try:
            res = requests.get(f"{API_URL}/history")
            if res.status_code == 200:
                history = res.json()
                processed_data = []
                for item in history:
                    defect_types = []
                    result = item.get("result")
                    if result and "defects" in result:
                        for defect in result["defects"]:
                            defect_types.append(defect.get("type", "unknown"))
                    
                    try:
                        from datetime import datetime
                        dt_obj = datetime.fromisoformat(item["created_at"].replace("Z", ""))
                        formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        formatted_date = item["created_at"]

                    processed_data.append({
                        "Filename": item.get("original_filename", item["filename"]),
                        "Defect Types": ", ".join(defect_types) if defect_types else "None",
                        "Status": item["status"],
                        "Created At": formatted_date
                    })
                
                st.dataframe(processed_data, use_container_width=True)
            else:
                st.error("Failed to retrieve history logs")
        except Exception as e:
            st.error(f"Error: {e}")
