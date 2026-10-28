# 🌾 SMART CROP ADVISORY SYSTEM FOR SMALL AND MARGINAL FARMERS
### குறு மற்றும் சிறு விவசாயிகளுக்கான நுண்ணறிவு பயிர் ஆலோசனைக் கட்டமைப்பு

[![Android APK Download](https://img.shields.io/badge/Download-Android%20APK-00e676?style=for-the-badge&logo=android&logoColor=white)](https://raw.githubusercontent.com/devendran6/SMART-CROP-ADVISORY-SYSTEM-/main/project01/static/downloads/SmartCropAdvisory.apk)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=for-the-badge&logo=flask&logoColor=black)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 📱 Direct Online APK Download

Small and marginal farmers can download the Android Application directly to their mobile devices:

- 📥 **[Direct Online APK Download Link](https://raw.githubusercontent.com/devendran6/SMART-CROP-ADVISORY-SYSTEM-/main/project01/static/downloads/SmartCropAdvisory.apk)**
- 🌐 **Web App Download Page:** `/download` (via running server or deployed website)
- 📦 **File Name:** `SmartCropAdvisory.apk` (v1.0.0, Signed & Verified with Android v1/v2/v3 signatures)

### 📲 How to Install on Android:
1. Tap the **[Download APK](https://raw.githubusercontent.com/devendran6/SMART-CROP-ADVISORY-SYSTEM-/main/project01/static/downloads/SmartCropAdvisory.apk)** link above on your phone browser.
2. When downloaded, tap the notification or open your **Downloads** folder.
3. If prompted, allow **"Install from unknown sources"** in your phone settings.
4. Tap **Install** and open **Smart Crop Advisory**!

---

## ⚡ One-Click Demo Access
Anyone can test the entire platform with a single click without registering:
- 🚀 **One-Click Demo Login:** Navigate to `/demo-login` (or click the yellow **"Demo Login"** button on the navbar/login card).
- Automatically logs in as `demo_farmer` from **Pollachi, Coimbatore** with pre-configured crops (Paddy, Tomato, Groundnut) and localized disease alerts.

---

## 🌟 System Overview

The **Smart Crop Advisory System for Small and Marginal Farmers** is an intelligent AI-based agricultural software platform designed to democratize modern farming guidance. Small and marginal farmers often face severe financial risks due to lack of timely agronomic advice, market unpredictability, unpredictable rainfall, and devastating pest attacks. This platform unifies all critical advisory functions into a single mobile-friendly platform.

---

## 🚀 Core Modules

### 1. 🌾 AI-Based Crop Recommendation Module
- Analyzes soil nutrient levels: **Nitrogen (N)**, **Phosphorus (P)**, **Potassium (K)**, and **pH**.
- Incorporates climatic factors: **Temperature**, **Rainfall**, **Humidity**, and **Soil Type** (Loamy, Clayey, Black, Red, Sandy Loam, Alluvial).
- Suggests optimal crops ranked by suitability percentage (Rice, Wheat, Maize, Cotton, Sugarcane, Tomato, Banana, Turmeric, Groundnut, etc.) along with sowing season and expected market realization.

### 2. 🔬 AI-Based Crop Disease Detection Module
- Farmers upload or capture leaf photos through their mobile camera.
- Computer vision analysis inspects visual symptoms (chlorosis, necrosis, lesion patterns) to detect diseases like:
  - *Rice Blast & Bacterial Blight*
  - *Tomato Early Blight & Late Blight*
  - *Wheat Yellow Rust & Powdery Mildew*
  - *Cotton Leaf Curl & Fusarium Wilt*
  - *Healthy Foliage Validation*
- Delivers dual treatment strategies:
  - **Chemical Treatments** (dosage & active ingredients)
  - **Organic & Eco-friendly Remedies** (Neem seed kernel extract, Trichoderma, Panchagavya)
  - **Preventive Measures** for the next cycle.

### 3. 🌤️ Weather Monitoring & Smart Irrigation Guidance
- Real-time weather monitoring (temperature, humidity, precipitation, wind).
- District-level weather forecast for Tamil Nadu and South Indian agro-climatic zones.
- **Crop-Specific Irrigation Scheduling**: Tailored water guidance (critical stages, drip irrigation recommendations, flood drainage warnings before monsoon).

### 4. 🚨 Location-Based Disease Outbreak Alerts
- District-wise early warning bulletin for active crop diseases and agricultural risks.
- **Farmer Community Reporting**: Allows any farmer to report a disease sighting in their village, instantly alerting neighboring farms to take preventative spray measures.

### 5. 💰 Yield and Profit Prediction Module
- Calculates expected yield (quintals/acre) based on crop, acreage, soil, and irrigation quality.
- Breaks down cultivation expenses (seeds, fertilizers, crop protection, labor, irrigation).
- Compares gross income, net profit, and **Return on Investment (ROI %)**.
- **Side-by-Side Crop Comparison Table**: Compare profitability across 15+ crops on a 1-acre plot before investing capital.

### 6. 🎙️ தமிழ் Voice Assistant (Tamil Agri Voice Assistant)
- Fully bilingual voice and text assistant tailored for rural and elderly farmers.
- Accepts voice input in Tamil (`ta-IN`) and English (`en-IN`).
- Speaks back answers using Web Speech Synthesis.
- Responds to spoken queries like *"பயிர் பரிந்துரை செய்"*, *"நெல் நோய் மருந்து என்ன?"*, *"வானிலை எப்படி இருக்கிறது?"*, and *"எவ்வளவு லாபம் கிடைக்கும்?"*.

### 7. 🚜 Farmer Diary & Regional Cultivation Dashboard
- Personal digital diary to track planted crops, sowing dates, acreages, and protection measures.
- Community regional dashboard aggregating local crop distribution to prevent local oversupply and price crashes.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask, SQLite3, Pillow (PIL), NumPy
- **Frontend:** Responsive HTML5, Modern CSS Glassmorphism Neon Theme, Vanilla JavaScript, FontAwesome
- **Speech & Audio:** Web SpeechRecognition API (`ta-IN`), Web SpeechSynthesis API
- **Mobile APK:** Android Native WebView, Android SDK 35/36, `javac`, `d8`, `aapt`, `zipalign`, `apksigner`

---

## 💻 Running the Web Application Locally

### Prerequisites
- Python 3.8 or higher installed on your computer.

### Step 1: Clone the Repository
```bash
git clone https://github.com/devendran6/SMART-CROP-ADVISORY-SYSTEM-.git
cd SMART-CROP-ADVISORY-SYSTEM-
```

### Step 2: Install Dependencies
```bash
pip install flask pillow
```

### Step 3: Initialize Database & Run Server
```bash
python run.py
```
Or directly from `project01`:
```bash
cd project01
python init_db.py
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📱 Building the Android APK from Source

The repository includes a ready-to-install signed APK in `downloads/SmartCropAdvisory.apk` and `project01/static/downloads/SmartCropAdvisory.apk`.

To recompile the APK from the `android/` source:
```powershell
# Using Android SDK build-tools (35.0.0)
$aapt = "$env:LOCALAPPDATA\Android\Sdk\build-tools\35.0.0\aapt.exe"
$d8 = "$env:LOCALAPPDATA\Android\Sdk\build-tools\35.0.0\d8.bat"
$zipalign = "$env:LOCALAPPDATA\Android\Sdk\build-tools\35.0.0\zipalign.exe"
$apksigner = "$env:LOCALAPPDATA\Android\Sdk\build-tools\35.0.0\apksigner.bat"
$androidJar = "$env:LOCALAPPDATA\Android\Sdk\platforms\android-36\android.jar"

# 1. Generate R.java
& $aapt package -m -J "android\src" -M "android\AndroidManifest.xml" -S "android\res" -I $androidJar

# 2. Compile Java
& javac -encoding utf-8 -source 8 -target 8 -cp $androidJar -d "android\bin" android\src\com\smartcrop\advisory\*.java

# 3. Compile DEX
& $d8 --lib $androidJar --output "android\bin" (Get-ChildItem "android\bin\com\smartcrop\advisory\*.class").FullName

# 4. Package, Align and Sign
& $aapt package -f -M "android\AndroidManifest.xml" -S "android\res" -I $androidJar -F "android\bin\unaligned.apk"
Push-Location "android\bin"; & $aapt add unaligned.apk classes.dex; Pop-Location
& $zipalign -f -p 4 "android\bin\unaligned.apk" "android\bin\aligned.apk"
& $apksigner sign --ks "android\smartcrop.keystore" --ks-pass pass:smartcrop123 --out "downloads\SmartCropAdvisory.apk" "android\bin\aligned.apk"
```

---

## 👥 Contributors & Acknowledgements
- Developed for small and marginal farmers across Tamil Nadu and India.
- Integrates agronomic guidelines from ICAR and Tamil Nadu Agricultural University (TNAU).

---
© 2026 Smart Crop Advisory System. Open source under MIT License.
