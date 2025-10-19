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

## 🎨 UI & Screenshots (Add later)

_To be added after frontend improvements:_
```
<img width="1510" height="325" alt="image" src="https://github.com/user-attachments/assets/30525d10-f8d6-421e-b712-d76c47821976" />
<img width="1452" height="761" alt="image" src="https://github.com/user-attachments/assets/7bda9205-a019-4ee6-a1b6-c9f53a0ff496" />
<img width="1215" height="638" alt="image" src="https://github.com/user-attachments/assets/6cba50ee-8951-4523-b220-5900f4bde436" />
<img width="1536" height="802" alt="image" src="https://github.com/user-attachments/assets/6894012b-4863-4b4d-a4b4-503eaa6d7b0f" />

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

