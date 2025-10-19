# 🪑 AI Furniture Recommender  
*An AI-Driven Furniture Product Recommendation & Analytics Web App (2-Day Internship Project)*

---

## 👤 Author & Academic Details  
| Field | Information |
|-------|-------------|
| **Name** | **Hemant** |
| **Roll No.** | **102217141** |
| **Institute** | **Thapar Institute of Engineering & Technology (TIET)** |
| **Project Duration** | **2 Days (Intern Assignment)** |
| **GitHub Repo** | https://github.com/hemant7199/AI-Furniture-Recommender |

---

## 🧠 Project Overview  
The **AI Furniture Recommender** is a full-stack web application that uses **Artificial Intelligence** to recommend furniture products based on natural language queries like:

> _“Show me a modern wooden chair”_  
> _“I need a compact study table for small rooms”_

This system integrates **Machine Learning, NLP, Generative AI, and Analytics** with a modern web interface built using **FastAPI + React**.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **AI Recommendations** | Search via semantic similarity (text embeddings) |
| ✍️ **AI Descriptions (GenAI)** | Auto-generated marketing descriptions |
| 🧾 **Dataset Handling** | Uses 10+ product fields including title, price, brand, image |
| 💬 **Chat-style Interface** | Query-based conversation UI |
| 📊 **Analytics Dashboard** | Price insights, category stats, brand distribution |
| 🧠 **Vector Similarity Search** | Powered by Sentence Transformers + FAISS |
| 🖼 **Image Support** | Displays real product images |
| 🤖 **Future CV Support** | Optional image classification via CNN/ResNet |

---

## 🗂 Dataset Details  
Columns used from the dataset:

```
title  
brand  
description  
price  
categories  
images  
manufacturer  
package dimensions  
country_of_origin  
material  
color  
uniq_id
```

Dataset Link (as per assignment):  
https://drive.google.com/file/d/1uD1UMXT2-13GQkb_H9NmEOyUVI-zKyl6/view

---

## 🏗 Project Structure

```
AI-Furniture-Recommender/
├── backend/       # FastAPI Application
│   ├── app/
│   ├── main.py
│   └── services/
│
├── frontend/      # React + Vite Application
│   ├── src/
│   │   ├── pages/
│   │   └── components/
│   └── index.css
│
├── notebooks/     # Model Training & Analytics (.ipynb)
└── README.md
```

---

## ⚙️ Installation & Run (Local)

### 🖥 Backend – FastAPI
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Runs at → **http://127.0.0.1:8000**

---

### 🌐 Frontend – React (Vite)
```bash
cd frontend
npm install
npm run dev
```
Open Browser → **http://localhost:5173/**

---

## 🔌 Important API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/recommend` | POST | Get AI product recommendations |
| `/analytics/summary` | GET | Dataset insights & stats |
| `/nlp/cluster` | POST | Group similar products |
| `/cv/predict` | GET | (Optional) Image classification |

---

## 🎨 UI & Screenshots


```
### 🖼 Screenshot 1
![Screenshot 1](https://github.com/user-attachments/assets/4ae03696-4208-43d8-9af2-3c05e00a9e8c)

### 🖼 Screenshot 2
![Screenshot 2](https://github.com/user-attachments/assets/e8986f29-d42e-4f5c-bd5d-28540993293c)

### 🖼 Screenshot 3
![Screenshot 3](https://github.com/user-attachments/assets/ca52527b-46d5-40c5-be4f-2d787423f34d)

### 🖼 Screenshot 4
![Screenshot 4](https://github.com/user-attachments/assets/bc320851-1bce-430e-a1ba-d6410f9a4953)

<img width="1536" height="802" alt="Screenshot 2025-10-19 135557" src="https://github.com/user-attachments/assets/4ae03696-4208-43d8-9af2-3c05e00a9e8c" />
<img width="1510" height="325" alt="Screenshot 2025-10-19 135701" src="https://github.com/user-attachments/assets/e8986f29-d42e-4f5c-bd5d-28540993293c" />
<img width="1452" height="761" alt="Screenshot 2025-10-19 135821" src="https://github.com/user-attachments/assets/ca52527b-46d5-40c5-be4f-2d787423f34d" />
<img width="1215" height="638" alt="Screenshot 2025-10-19 135901" src="https://github.com/user-attachments/assets/bc320851-1bce-430e-a1ba-d6410f9a4953" />

```

---

## 📡 Deployment (Optional)

| Platform | Purpose |
|----------|---------|
| **Render** | Backend (FastAPI) |
| **Vercel** | Frontend (React) |
| **Env Var** | `VITE_API_URL = <Backend_URL>` |

---

## 🔮 Future Improvements

- User Login & Personalized Suggestions  
- Pinecone Cloud Integration  
- Advanced CV Model  
- Customer Reviews & Feedback  
- Multi-language Support  

---

## 🙏 Acknowledgements

This project was built as part of an **AI Internship Assignment**, combining ML, NLP, GenAI, Vector DB, and Full Stack development within **2 days**.

---

## 🧑‍💻 Author  
**Hemant** – Roll No. **102217141**  
Thapar Institute of Engineering & Technology (TIET)  
GitHub: https://github.com/hemant7199

---

## 📄 License  
Licensed under the **MIT License**.

