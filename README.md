# AIIA :: AI Investment Assistant 💹🤖

**AIIA** (Artificial Intelligence Investment Advisor) is a full-stack web application that lets anyone turn a few sliders into an AI-curated portfolio – then visualise the allocation and performance at a glance.

It’s built with **FastAPI + MongoDB** on the backend and **React (Vite) + TailwindCSS** on the frontend, and taps the OpenAI API plus live market data to keep recommendations fresh.

---

## ✨ Features

| Category | Highlights |
|----------|------------|
| **AI Portfolio Engine** | GPT-4-o prompts + real-time prices (Alpha Vantage ⇢ Yahoo fallback) |
| **Interactive UI** | Budget / horizon / risk sliders, ETFs vs mutual funds vs stocks selector |
| **Visuals** | Pie chart (allocation) & line chart (value over time) with Chart.js |
| **Auth & Storage** | JWT login, MongoDB Atlas for users + history |
| **Docs** | Live Swagger UI at `/docs` |
| **Deploy-ready** | Single-click deploy to Render / Railway / Vercel |

---

## 🏗️ Tech Stack

1. **FastAPI** (Python 3.11)  
2. **MongoDB Atlas**  
3. **OpenAI API**  
4. **Alpha Vantage** (↩︎ Yahoo Finance fallback)  
5. **React 18 + Vite**  
6. **Tailwind CSS 3**  
7. **Chart.js 4**

---

## 📂 Project Structure
```bash
aiia/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routes/              # auth.py, recommend.py, (history, user, …)
│   │   └── utils/               # auth helpers, ai prompt builder, db client
│   ├── requirements.txt
│   └── .env                     # ←- NOT committed
├── frontend/
│   ├── public/                  # AIIA.png, favicon
│   ├── src/
│   │   ├── pages/               # Dashboard.tsx, Login.tsx, Signup.tsx
│   │   ├── components/          # charts, sidebar, …
│   │   ├── services/            # api.ts (axios wrapper)
│   │   ├── AuthContext.tsx
│   │   └── index.css            # Tailwind layers + custom utilities
│   ├── vite.config.ts
│   └── package.json
└── README.md
```
---

## ⚙️ Prerequisites

| Tool | Version |
|-----|----------|
| **Node.js** | ≥ 16 (LTS v20 works) |
| **Python** | 3.10 – 3.13 |
| **MongoDB Atlas** | Free Tier is fine |
| **OpenAI API key** | _sk-…_ |
| (Opt.) **Alpha Vantage key** | free demo works |

---

## 🔐 Environment Variables

### Backend `backend/.env`

```bash
OPENAI_API_KEY=sk-…
OPENAI_MODEL=gpt-4o-mini            # or gpt-4o if you have access

ALPHA_VANTAGE_KEY=YOUR_ALPHA_KEY    # optional – falls back to Yahoo

MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=aiia_db

JWT_SECRET=change_me_super_random
CORS_ORIGINS=http://localhost:5173

```

## 🚀 Local Development
```bash
# 1. Clone
git clone https://github.com/<your-username>/aiia.git
cd aiia
```
### Backend (setup once)

```bash
cd frontend
npm install
npm run dev                              # http://localhost:5173
```

## 🖥️ Using AIIA – Quick Walk-through

1. **Sign Up → Log In**  
   Create an account via the Signup form, then log in. (The JWT is stored in `localStorage`.)

2. **Adjust Parameters**  
   Use the sliders/inputs to set **Budget** (USD), **Time Horizon** (years), **Risk** (1 – 10), and **Fund Type** (Stocks, ETF, Mutual Fund).

3. **Generate Portfolio**  
   Click **Generate Portfolio**. The backend prompts GPT-4-o, fetches live prices, and returns tickers with % allocations plus forecast data.

4. **Visualise**  
   *Pie Chart* shows how capital is split; *Line Chart* plots projected portfolio value over time.

5. **Iterate & Compare**  
   Tweak any slider or fund type and regenerate to explore alternative strategies.

---

## 🛠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| **422 Unprocessable Entity** | Ensure the request body includes `budget`, `horizon`, `risk`, and `fund_type`. |
| **500 Mongo Error** | Verify `MONGO_URI`, credentials, and Atlas IP whitelist. |
| **CORS errors** | Make sure `CORS_ORIGINS` contains `http://localhost:5173`. |
| **Tailwind/PostCSS build errors** | Install `@tailwindcss/postcss` and double-check `postcss.config.js`. |

---

*Happy investing & hacking!*

