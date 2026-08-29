# KrishiMitra Market Estimator ("Mandi Compare")
### Smart India Hackathon 2026 — Problem Statement SIH26132
**Theme:** Agriculture, Foodtech & Rural Development  
**Team:** InnoVate  
**Product:** KrishiMitra Market Estimator  

---

## 🌾 Overview & Objective

Agricultural producers frequently sell their harvest at local village markets or the nearest APMC Mandi, unaware that a market 50–100 km away might offer significantly higher listing prices. However, higher listing prices do not automatically guarantee higher profits once logistics, loading/unloading, and market cess are deducted.

**KrishiMitra** solves this by evaluating candidate markets, automatically calculating **Transport Costs** and **Mandi Handling Charges**, and recommending the market that delivers the **highest net profit return per quintal** to the farmer.

---

## 🧮 Core Mathematical Formulas

Every calculation is implemented in dedicated, unit-testable service modules:

```text
1. Transport Cost (₹) = Distance (km) × Rate (₹/km/quintal) × Quantity (quintal)
2. Transport Cost per qtl = Distance (km) × Rate (₹/km/quintal)
3. Total Other Costs per qtl = Loading + Unloading + Market Cess
4. Total Cost per qtl = Transport Cost per qtl + Total Other Costs per qtl
5. Net Price per qtl (₹/qtl) = Mandi Listing Price − Total Cost per qtl
6. Total Net Farmer Earnings (₹) = Net Price per qtl × Quantity (quintal)
```

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.8+
- pip

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Launch Application
```bash
python backend/app.py
```

On first launch, SQLite database `backend/database/krishimitra.db` will automatically initialize tables and seed realistic sample data matching the SIH pitch deck scenario.

Open your browser to:
- **Farmer Interface (Screen 1 & 2):** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Admin Configuration Panel (Screen 3):** [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

---

## 📂 Modular File Architecture

```
KrishiMitra/
├── backend/
│   ├── app.py                          # Flask entrypoint & API routing
│   ├── config.py                       # Constants, DB paths, mock API toggle
│   ├── database/
│   │   ├── db_connection.py            # Thread-safe SQLite connection context manager
│   │   ├── db_init.py                  # DDL table creation scripts
│   │   └── seed_data.py                # Initial seed data matching SIH pitch deck
│   ├── models/
│   │   ├── crop_model.py               # Crop data access methods
│   │   ├── mandi_model.py              # Mandi coordinates & entity methods
│   │   ├── price_model.py              # Mandi crop prices & historical points
│   │   ├── distance_model.py           # Geographical distance matrix
│   │   └── cost_model.py               # Loading, unloading, cess & freight rates
│   ├── services/
│   │   ├── transport_cost_calculator.py# Distance x Rate x Quantity pure calculator
│   │   ├── net_price_calculator.py     # Mandi Price - Total Cost pure calculator
│   │   ├── cost_estimation_service.py  # Loading, unloading, and market fees lookup
│   │   ├── maps_distance_service.py    # Distance Matrix lookup with GPS Haversine fallback
│   │   ├── data_fetcher_service.py     # Agmarknet / e-NAM data fetcher & scheduler
│   │   ├── price_comparison_engine.py  # Mandi price alignment across markets
│   │   ├── ranking_recommendation_engine.py # Descending net price ranking engine
│   │   ├── tts_engine.py               # Text-to-speech engine (Marathi/Hindi/English)
│   │   ├── analytics_reports_service.py# 7-Day historical price trends & spread
│   │   └── notification_service.py     # Price surge alerts & market advisories
│   ├── admin/
│   │   └── admin_panel.py              # CRUD controller for administrative tools
│   └── requirements.txt                # Python package dependencies
├── frontend/
│   ├── index.html                      # Screen 1: Farmer Crop, Mandi & Quantity Form
│   ├── dashboard.html                  # Screen 2: Mandi Compare & Effective Price Breakdown
│   ├── admin.html                      # Screen 3: Master Data & Admin Management Panel
│   ├── css/style.css                   # Mobile-first, high contrast, farmer-friendly styling
│   └── js/
│       ├── app.js                      # Farmer input handling & localization
│       ├── dashboard.js                # Comparison table, summary card, TTS, Google Maps
│       └── admin.js                    # Admin panel CRUD operations
└── README.md                           # Documentation & Phase 2 Integration Guide
```

---

## 🎯 Demo Values (Matching SIH Pitch Deck)

When selecting **Cotton (कपास)** and **Home Mandi: Nagpur**:

| Rank | Mandi | Distance | Listing Price | Transport Cost (₹0.80/km) | Other Costs | **Net Farmer Return** | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **🏆 #1** | **Amravati** | 145 km | ₹7,250 / qtl | -₹116 / qtl | ₹0 / qtl | **₹7,134 / qtl** | **Recommended** |
| #2 | **Nagpur** | 0 km | ₹7,216 / qtl | ₹0 / qtl | -₹116 / qtl | **₹7,100 / qtl** | Home Mandi |
| #3 | **Pune** | 600 km | ₹7,348 / qtl | -₹480 / qtl | ₹0 / qtl | **₹6,868 / qtl** | Alternative |
| #4 | **Akola** | 312.5 km | ₹7,013 / qtl | -₹250 / qtl | ₹0 / qtl | **₹6,763 / qtl** | Alternative |
| #5 | **Nashik** | 875 km | ₹7,090 / qtl | -₹700 / qtl | -₹100 / qtl | **₹6,290 / qtl** | Alternative |

---

## 🔌 Active Live API Integrations

1. **Agmarknet Mandi Price Feed (data.gov.in XML API):**
   - **Resource ID:** `9ef84268-d588-465a-a308-a864a43d0070`
   - **API Key:** `579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b`
   - **Format:** `xml` (Parsed with `xml.etree.ElementTree` in [`data_fetcher_service.py`](file:///c:/Users/HP-PC/Documents/KrishiMitra/backend/services/data_fetcher_service.py))
   - **Endpoint:** `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`
   - Automatically parses `<modal_price>` / `<max_price>` filtered by commodity and market, with graceful fallback.

2. **Google Maps Platform (JavaScript & Distance Matrix API):**
   - **API Key:** `AIzaSyDOkEUdOO0Lnb_7HpOZ41mBxc1RSO4QDeU`
   - **Backend Routing:** [`maps_distance_service.py`](file:///c:/Users/HP-PC/Documents/KrishiMitra/backend/services/maps_distance_service.py) queries Google Maps Distance Matrix API.
   - **Frontend Visualization:** [`dashboard.html`](file:///c:/Users/HP-PC/Documents/KrishiMitra/frontend/dashboard.html) renders an interactive Google Map with custom markers for Home Mandi (🏠), Champion recommended market (🏆), candidate mandis (📍), and driving polyline.

---

## 🌐 Free Cloud Deployment Guide

### Option 1: Deploy on Vercel (100% Free Serverless)
Pre-configured with `vercel.json` and `api/index.py`:
1. Push this folder to a GitHub repository.
2. Sign up / Log in to [Vercel.com](https://vercel.com).
3. Click **"Add New Project"** $\rightarrow$ Import your GitHub repository.
4. Keep the default settings and click **"Deploy"**.
5. Your live prototype URL will be generated (e.g. `https://krishimitra.vercel.app`).

### Option 2: Deploy on Render.com (100% Free Web Service — Recommended)
Pre-configured with `render.yaml` and `Procfile`:
1. Push this repository to GitHub.
2. Log in to [Render.com](https://render.com).
3. Click **"New Web Service"** $\rightarrow$ Connect your GitHub repo.
4. Settings:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --chdir backend app:app`
5. Click **"Deploy Web Service"** to get a free live URL (e.g. `https://krishimitra.onrender.com`).

### Option 3: Deploy on Railway.app / Koyeb
1. Connect repository on [Railway.app](https://railway.app) or [Koyeb.com](https://koyeb.com).
2. It will automatically detect `Procfile` and deploy your Flask app.
