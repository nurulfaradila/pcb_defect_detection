# 🔍 PCB Defect Detection System
### *Building a Smarter Quality Control Pipeline*

## 📖 Overview

> [!NOTE]  
> This is a **conceptual prototype** and dummy project inspired by real-world industrial challenges in electronics manufacturing. It is designed to demonstrate a full-stack AI integration.

As a **Software Engineer**, I developed this project to explore how complex quality assurance processes can be automated. This system serves as a proof-of-concept for automating the inspection of Printed Circuit Boards (PCBs).

In industrial settings, manual inspection is slow and prone to human error. I built this prototype to demonstrate how **Computer Vision (YOLOv8)** can be used to detect defects like short circuits or missing components in real-time, providing a scalable architectural template for similar real-world applications.

---

## 🚀 Why I Built This

The goal was to create a production-ready AI pipeline that isn't just a script, but a full ecosystem. I focused on:
- **Reliability**: Using asynchronous task queues to ensure ML inference doesn't block the user interface.
- **Scalability**: Decoupling the backend from the workers using RabbitMQ.
- **User Experience**: Providing a clean, interactive dashboard for immediate feedback.

---

## ✨ Key Features I Implemented

- **🧠 Deep Learning Core**: Integrated **YOLOv8** for high-precision object detection.
- **⚡ Asynchronous Workflow**: I used **Celery** and **RabbitMQ** to handle heavy ML tasks in the background, keeping the API responsive.
- **📊 Inspection Tracking**: A **Postgres** database records every scan, allowing users to track quality trends over time.
- **🌐 Interactive UI**: Built with **Streamlit** to allow easy image uploads and visual bounding-box results.
- **🐳 Container Orchestration**: I dockerized the entire stack for consistent deployment across any environment.

---

## 🛠️ Tech Stack I Used

| Layer | Technologies |
| :--- | :--- |
| **Brain** | YOLOv8 (Ultralytics), PyTorch |
| **Backend** | FastAPI, Celery, SQLAlchemy |
| **Infrastructure** | RabbitMQ, PostgreSQL, Docker |
| **Frontend** | Streamlit |

---

## � Getting Started

I've made it easy to get this project running locally.

### 1. Clone & Enter
```bash
git clone <repo-url>
```

### 2. Fast Deployment (Docker)
```bash
docker-compose up --build
```

### 3. Usage
- **The Dashboard**: [http://localhost:8501](http://localhost:8501)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🏗️ Project Architecture

```text
.
├── backend/
│   ├── app/
│   └── tests/
├── frontend/
├── ml/
│   ├── yolov8_model/
│   └── data/
├── docker-compose.yml
└── uploads/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
