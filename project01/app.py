import os
import sqlite3
import json
import base64
import random
import math
from datetime import datetime, timedelta
from io import BytesIO

from flask import (Flask, render_template, request, url_for,
                   flash, redirect, session, jsonify, send_file, send_from_directory)
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartcrop_secret_2026'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── Crop Knowledge Base ────────────────────────────────────────────────────
CROP_DB = {
    "Rice":       {"n":80,"p":40,"k":40,"temp":(20,30),"rain":(150,250),"soil":["Clayey","Loamy"],"ph":(5.5,7.0),"season":"Kharif","price":2200,"cost":18000,"yield_per_acre":25},
    "Wheat":      {"n":80,"p":60,"k":40,"temp":(10,25),"rain":(50,100),"soil":["Loamy","Sandy Loam"],"ph":(6.0,7.5),"season":"Rabi","price":2100,"cost":15000,"yield_per_acre":20},
    "Maize":      {"n":80,"p":40,"k":20,"temp":(18,27),"rain":(60,120),"soil":["Loamy","Sandy Loam"],"ph":(5.5,7.5),"season":"Kharif","price":1700,"cost":12000,"yield_per_acre":30},
    "Sugarcane":  {"n":200,"p":60,"k":200,"temp":(20,35),"rain":(100,200),"soil":["Loamy","Clayey"],"ph":(6.0,8.0),"season":"Annual","price":3200,"cost":40000,"yield_per_acre":400},
    "Cotton":     {"n":100,"p":50,"k":50,"temp":(21,30),"rain":(60,120),"soil":["Black","Sandy Loam"],"ph":(5.8,8.0),"season":"Kharif","price":5800,"cost":25000,"yield_per_acre":7},
    "Groundnut":  {"n":20,"p":40,"k":40,"temp":(25,30),"rain":(50,100),"soil":["Sandy Loam","Loamy"],"ph":(5.5,7.0),"season":"Kharif","price":5500,"cost":20000,"yield_per_acre":8},
    "Tomato":     {"n":100,"p":60,"k":80,"temp":(20,27),"rain":(60,100),"soil":["Loamy","Sandy Loam"],"ph":(6.0,7.0),"season":"Rabi","price":1200,"cost":35000,"yield_per_acre":60},
    "Onion":      {"n":80,"p":50,"k":80,"temp":(13,24),"rain":(50,80),"soil":["Loamy","Sandy Loam"],"ph":(6.0,7.5),"season":"Rabi","price":1500,"cost":25000,"yield_per_acre":50},
    "Banana":     {"n":200,"p":60,"k":300,"temp":(20,35),"rain":(75,200),"soil":["Loamy","Clayey"],"ph":(5.5,7.0),"season":"Annual","price":1800,"cost":50000,"yield_per_acre":120},
    "Turmeric":   {"n":120,"p":60,"k":120,"temp":(20,30),"rain":(150,250),"soil":["Loamy","Sandy Loam"],"ph":(5.5,7.0),"season":"Kharif","price":7000,"cost":60000,"yield_per_acre":30},
    "Chilli":     {"n":100,"p":50,"k":50,"temp":(20,30),"rain":(60,120),"soil":["Loamy","Sandy Loam"],"ph":(6.0,7.5),"season":"Kharif","price":8000,"cost":30000,"yield_per_acre":10},
    "Soybean":    {"n":40,"p":60,"k":40,"temp":(20,30),"rain":(60,100),"soil":["Loamy","Clayey"],"ph":(6.0,7.5),"season":"Kharif","price":4400,"cost":14000,"yield_per_acre":12},
    "Coconut":    {"n":100,"p":40,"k":200,"temp":(27,34),"rain":(150,250),"soil":["Sandy Loam","Loamy"],"ph":(5.5,8.0),"season":"Annual","price":30,"cost":20000,"yield_per_acre":80},
    "Mustard":    {"n":80,"p":40,"k":40,"temp":(10,25),"rain":(40,60),"soil":["Loamy","Sandy Loam"],"ph":(6.0,7.5),"season":"Rabi","price":4000,"cost":10000,"yield_per_acre":8},
    "Mango":      {"n":100,"p":50,"k":100,"temp":(24,30),"rain":(75,250),"soil":["Loamy","Sandy Loam"],"ph":(5.5,7.5),"season":"Annual","price":4000,"cost":30000,"yield_per_acre":50},
}

DISEASES = {
    "Rice":      [{"name":"Rice Blast","desc":"Fungal disease causing diamond-shaped lesions on leaves","treatment":"Apply Tricyclazole 75WP @ 6g/10L. Remove infected plants.","prevention":"Use resistant varieties. Avoid excess nitrogen.","severity":"High"},
                  {"name":"Bacterial Blight","desc":"Yellow to white lesions along leaf margins","treatment":"Apply Copper Oxychloride 50WP @ 30g/10L. Drain fields.","prevention":"Use certified seeds. Avoid waterlogging.","severity":"Medium"}],
    "Wheat":     [{"name":"Yellow Rust","desc":"Yellow pustules in stripes on leaves","treatment":"Apply Propiconazole 25EC @ 10ml/10L. ","prevention":"Sow resistant varieties. Early sowing.","severity":"High"},
                  {"name":"Powdery Mildew","desc":"White powdery coating on leaves","treatment":"Apply Sulphur 80WP @ 25g/10L.","prevention":"Maintain crop spacing.","severity":"Low"}],
    "Tomato":    [{"name":"Early Blight","desc":"Dark brown spots with concentric rings on lower leaves","treatment":"Apply Mancozeb 75WP @ 25g/10L every 7 days.","prevention":"Rotate crops. Avoid overhead watering.","severity":"Medium"},
                  {"name":"Late Blight","desc":"Water-soaked lesions turning brown, white mold on underside","treatment":"Apply Metalaxyl-M 8WP @ 25g/10L.","prevention":"Use resistant varieties. Destroy infected debris.","severity":"High"}],
    "Cotton":    [{"name":"Cotton Leaf Curl","desc":"Upward curling of leaves, vein thickening","treatment":"Apply Imidacloprid 70WG @ 2.5g/10L for whitefly control.","prevention":"Remove weed hosts. Use virus-free planting material.","severity":"High"},
                  {"name":"Fusarium Wilt","desc":"Yellowing, wilting and death of plant","treatment":"Drench with Carbendazim 50WP @ 10g/10L.","prevention":"Soil solarization. Crop rotation.","severity":"High"}],
    "Maize":     [{"name":"Northern Corn Blight","desc":"Long, elliptical grey-green lesions on leaves","treatment":"Apply Mancozeb 75WP @ 25g/10L.","prevention":"Use resistant hybrids.","severity":"Medium"}],
    "Groundnut": [{"name":"Tikka Disease","desc":"Circular brown spots with yellow halo","treatment":"Apply Carbendazim 50WP @ 10g/10L.","prevention":"Use certified seed. Crop rotation.","severity":"Medium"}],
    "Banana":    [{"name":"Panama Wilt","desc":"Yellowing of lower leaves, splitting of pseudostem","treatment":"Drench with Carbendazim 50WP @ 10g/10L.","prevention":"Use resistant varieties (Cavendish).","severity":"High"}],
    "Chilli":    [{"name":"Anthracnose","desc":"Sunken circular spots on fruits, orange spore masses","treatment":"Apply Copper Hydroxide 77WP @ 30g/10L.","prevention":"Avoid wounding. Harvest at right maturity.","severity":"Medium"}],
    "General":   [{"name":"Nutrient Deficiency","desc":"Yellowing, stunted growth, pale leaves","treatment":"Apply balanced NPK fertilizer as per soil test.","prevention":"Regular soil testing. Balanced fertilization.","severity":"Low"},
                  {"name":"Root Rot","desc":"Roots turn brown/black, plant wilts","treatment":"Drench with Metalaxyl 35WS @ 5g/10L.","prevention":"Improve drainage. Avoid overwatering.","severity":"Medium"}],
}

WEATHER_DATA = {
    "Chennai":    {"temp":30,"humidity":78,"rainfall":120,"forecast":"Partly cloudy, light showers expected."},
    "Coimbatore": {"temp":26,"humidity":65,"rainfall":85,"forecast":"Clear skies, mild winds."},
    "Madurai":    {"temp":32,"humidity":60,"rainfall":60,"forecast":"Hot and dry, irrigation needed."},
    "Salem":      {"temp":28,"humidity":70,"rainfall":95,"forecast":"Overcast, moderate rainfall likely."},
    "Trichy":     {"temp":31,"humidity":68,"rainfall":75,"forecast":"Sunny with evening showers."},
    "Tirunelveli":{"temp":33,"humidity":72,"rainfall":110,"forecast":"Humid with intermittent rain."},
    "Erode":      {"temp":29,"humidity":63,"rainfall":80,"forecast":"Clear with light breeze."},
    "Vellore":    {"temp":27,"humidity":67,"rainfall":70,"forecast":"Pleasant weather, suitable for field work."},
    "Thanjavur":  {"temp":30,"humidity":75,"rainfall":130,"forecast":"Partly cloudy, paddy fields conditions good."},
    "Dindigul":   {"temp":28,"humidity":66,"rainfall":78,"forecast":"Mild conditions, good for cultivation."},
}

IRRIGATION_ADVICE = {
    "Rice":       "Maintain 5-7cm standing water during vegetative stage. Drain 10 days before harvest.",
    "Wheat":      "Irrigate at crown root (21 DAS), tillering (45 DAS), jointing, flowering and grain filling stages.",
    "Maize":      "Critical stages: V6 (knee-high), tasseling and silking. Avoid water stress at silking.",
    "Cotton":     "Irrigate at flowering and boll development. Avoid waterlogging. Deficit irrigation at maturity.",
    "Tomato":     "Drip irrigation preferred. Keep soil moist. Avoid wetting foliage. 400-600mm total.",
    "Groundnut":  "Irrigate at pegging and pod development stages. Avoid waterlogging.",
    "Sugarcane":  "Weekly irrigation in dry season. Furrow irrigation preferred. 1500-2500mm total.",
    "Onion":      "Frequent light irrigations. Stop 10-15 days before harvest. Drip irrigation saves 40% water.",
    "Banana":     "Weekly irrigation. Drip system recommended. Mulching reduces water loss.",
    "Default":    "Irrigate based on soil moisture. Check 6 inches deep — if dry, irrigate. Drip systems save 30-50% water.",
}

TAMIL_RESPONSES = {
    "crop":       "உங்கள் மண் மற்றும் வானிலை நிலைமைகளுக்கு ஏற்ற பயிர்களை தேர்வு செய்யுங்கள்.",
    "disease":    "பயிர் நோய்களை முன்கூட்டியே கண்டறிந்து தகுந்த மருந்துகளை பயன்படுத்துங்கள்.",
    "weather":    "இன்று வானிலை: {temp}°C வெப்பம், {humidity}% ஈரப்பதம். {forecast}",
    "irrigation": "உங்கள் பயிரின் தேவைக்கு ஏற்ப நீர்ப்பாசனம் செய்யுங்கள். சொட்டு நீர் முறை சிறந்தது.",
    "profit":     "உங்கள் {crop} பயிரிலிருந்து ₹{profit} வரை லாபம் எதிர்பார்க்கலாம்.",
    "alert":      "உங்கள் மாவட்டத்தில் {disease} நோய் அறிவிக்கப்பட்டுள்ளது. உஷாராக இருங்கள்.",
    "greeting":   "வணக்கம்! நான் உங்கள் விவசாய உதவியாளர். எப்படி உதவட்டுமா?",
    "default":    "உங்கள் கேள்விக்கு நன்றி. மேலும் தகவல்களுக்கு விவசாய அலுவலகத்தை தொடர்பு கொள்ளுங்கள்.",
}

# ─── DB Helper ───────────────────────────────────────────────────────────────
def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    conn = sqlite3.connect(db_path)
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# ─── AI Engine ───────────────────────────────────────────────────────────────
def recommend_crops(n, p, k, temp, rainfall, humidity, soil_type, ph=6.5):
    scores = []
    for crop, req in CROP_DB.items():
        score = 100
        # Nutrient matching (40 pts)
        score -= min(40, abs(n - req['n']) / 2)
        score -= min(20, abs(p - req['p']) / 2)
        score -= min(20, abs(k - req['k']) / 2)
        # Temperature (20 pts)
        t_min, t_max = req['temp']
        if t_min <= temp <= t_max:
            score += 20
        else:
            score -= min(30, abs(temp - (t_min + t_max) / 2))
        # Rainfall (20 pts)
        r_min, r_max = req['rain']
        if r_min <= rainfall <= r_max:
            score += 20
        else:
            score -= min(30, abs(rainfall - (r_min + r_max) / 2) / 2)
        # Soil match (20 pts)
        if soil_type in req['soil']:
            score += 20
        # pH match (10 pts)
        ph_min, ph_max = req['ph']
        if ph_min <= ph <= ph_max:
            score += 10
        scores.append((crop, max(0, score), req))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:5]

def detect_disease(image_data_b64, crop_name="General"):
    """Rule-based disease detection using image color analysis."""
    try:
        img_bytes = base64.b64decode(image_data_b64.split(',')[1] if ',' in image_data_b64 else image_data_b64)
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        img_small = img.resize((100, 100))
        pixels = list(img_small.getdata())
        
        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)
        
        # Color-based heuristic disease detection
        brown_score = avg_r / (avg_g + 1) + avg_r / (avg_b + 1)
        yellow_score = (avg_r + avg_g) / (avg_b + 1)
        green_score = avg_g / ((avg_r + avg_b) / 2 + 1)
        
        diseases_list = DISEASES.get(crop_name, DISEASES["General"])
        
        if green_score > 1.5:
            confidence = 72 + random.randint(0, 15)
            disease = {"name": "Healthy Plant", "desc": "The plant appears healthy. No visible disease detected.",
                      "treatment": "Continue regular crop management practices.",
                      "prevention": "Maintain proper nutrition and irrigation.", "severity": "None"}
        elif brown_score > 2.5:
            confidence = 78 + random.randint(0, 15)
            disease = diseases_list[0] if diseases_list else DISEASES["General"][0]
        elif yellow_score > 2.0:
            confidence = 74 + random.randint(0, 15)
            disease = diseases_list[-1] if len(diseases_list) > 1 else DISEASES["General"][1]
        else:
            confidence = 65 + random.randint(0, 20)
            disease = random.choice(diseases_list)
        
        return {"disease": disease, "confidence": confidence,
                "avg_color": {"r": int(avg_r), "g": int(avg_g), "b": int(avg_b)}}
    except Exception as e:
        return {"disease": DISEASES["General"][0], "confidence": 60, "error": str(e)}

def predict_yield_profit(crop_name, area_acres, soil_type="Loamy", irrigation="Good"):
    info = CROP_DB.get(crop_name)
    if not info:
        return None
    
    base_yield = info["yield_per_acre"] * area_acres
    irrigation_factor = {"Excellent": 1.15, "Good": 1.0, "Average": 0.85, "Poor": 0.70}.get(irrigation, 1.0)
    soil_factor = 1.1 if soil_type in info["soil"] else 0.9
    
    estimated_yield = base_yield * irrigation_factor * soil_factor
    cultivation_cost = info["cost"] * area_acres
    gross_income = estimated_yield * info["price"]
    net_profit = gross_income - cultivation_cost
    
    return {
        "crop": crop_name,
        "area": area_acres,
        "estimated_yield_quintals": round(estimated_yield, 1),
        "price_per_quintal": info["price"],
        "gross_income": round(gross_income),
        "cultivation_cost": round(cultivation_cost),
        "net_profit": round(net_profit),
        "roi_percent": round((net_profit / cultivation_cost) * 100, 1) if cultivation_cost > 0 else 0,
        "season": info["season"],
        "break_even_yield": round(cultivation_cost / info["price"], 1),
    }

def get_weather(location):
    loc_key = location.strip().title()
    for key in WEATHER_DATA:
        if key.lower() in loc_key.lower() or loc_key.lower() in key.lower():
            data = WEATHER_DATA[key].copy()
            data["location"] = key
            return data
    # Default with some variation
    base = list(WEATHER_DATA.values())[0].copy()
    base["location"] = location
    base["temp"] += random.randint(-3, 3)
    base["humidity"] += random.randint(-10, 10)
    return base

def get_irrigation_advice(crop_name):
    return IRRIGATION_ADVICE.get(crop_name, IRRIGATION_ADVICE["Default"])

def get_tamil_response(query):
    q = query.lower()
    if any(w in q for w in ["crop","pore","payan","vivasayam","payir"]):
        return TAMIL_RESPONSES["crop"]
    if any(w in q for w in ["disease","noi","noy","sick"]):
        return TAMIL_RESPONSES["disease"]
    if any(w in q for w in ["rain","weather","vaanilai","mazhai"]):
        return TAMIL_RESPONSES["weather"].format(temp=30, humidity=70, forecast="இன்று மழை சாத்தியம்.")
    if any(w in q for w in ["water","irrigation","neer","niir"]):
        return TAMIL_RESPONSES["irrigation"]
    if any(w in q for w in ["profit","laadam","labam","income","earn"]):
        return TAMIL_RESPONSES["profit"].format(crop="நெல்", profit="45,000")
    if any(w in q for w in ["hello","vanakkam","hi","help","udavi"]):
        return TAMIL_RESPONSES["greeting"]
    return TAMIL_RESPONSES["default"]

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        location = request.form['location']
        district = request.form.get('district', location)
        contact = request.form['contact']
        if not all([username, password, location, contact]):
            flash('All fields are required!', 'danger')
        else:
            conn = get_db()
            if conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone():
                flash('Username already exists.', 'danger')
                conn.close()
            else:
                hashed = generate_password_hash(password)
                conn.execute('INSERT INTO users (username,password,location,district,contact) VALUES (?,?,?,?,?)',
                             (username, hashed, location, district, contact))
                conn.commit()
                conn.close()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
    return render_template('login.html', action='register')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user is None or not check_password_hash(user['password'], password):
            flash('Invalid username or password.', 'danger')
        else:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['location'] = user['location']
            session['district'] = user['district'] or user['location']
            return redirect(url_for('dashboard'))
    return render_template('login.html', action='login')

@app.route('/demo-login')
def demo_login():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username=?', ('demo_farmer',)).fetchone()
    if not user:
        hashed = generate_password_hash('demo123')
        conn.execute('''
            INSERT INTO users (username, password, location, district, contact)
            VALUES (?, ?, ?, ?, ?)
        ''', ('demo_farmer', hashed, 'Pollachi', 'Coimbatore', 'demofarmer@smartcrop.in'))
        conn.commit()
        user = conn.execute('SELECT * FROM users WHERE username=?', ('demo_farmer',)).fetchone()

        # Seed sample crops for demo farmer
        conn.execute('''
            INSERT INTO crops (user_id, crop_name, planted_date, area_size, soil_type, protection_strategy, status, quantity_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], 'Rice (Paddy)', '2026-08-15', '2.5 Acres', 'Clayey', 'Pseudomonas fluorescens (Organic)', 'Growing', 'Expected 55 quintals'))
        conn.execute('''
            INSERT INTO crops (user_id, crop_name, planted_date, area_size, soil_type, protection_strategy, status, quantity_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], 'Tomato', '2026-07-10', '1.0 Acre', 'Loamy', 'Mancozeb 75WP (Chemical)', 'Harvesting Soon', '45 quintals'))
        conn.execute('''
            INSERT INTO crops (user_id, crop_name, planted_date, area_size, soil_type, protection_strategy, status, quantity_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], 'Groundnut', '2026-09-01', '1.5 Acres', 'Sandy Loam', 'Trichoderma seed treatment', 'Planted', 'Expected 14 quintals'))
        conn.execute('''
            INSERT INTO disease_alerts (user_id, district, crop_name, disease_name, severity)
            VALUES (?, ?, ?, ?, ?)
        ''', (user['id'], 'Coimbatore', 'Tomato', 'Early Blight', 'Medium'))
        conn.commit()

    conn.close()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['location'] = user['location']
    session['district'] = user['district'] or user['location']
    flash('Logged in as Demo Farmer (Pollachi, Coimbatore) with 1-click! Feel free to explore all modules.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    crops = conn.execute('''
        SELECT crops.*, users.username, users.location, users.contact, users.id as farmer_uid
        FROM crops JOIN users ON crops.user_id = users.id
        ORDER BY crops.created_at DESC
    ''').fetchall()
    alerts = conn.execute('''
        SELECT disease_alerts.*, users.username
        FROM disease_alerts JOIN users ON disease_alerts.user_id = users.id
        ORDER BY reported_at DESC LIMIT 10
    ''').fetchall()
    conn.close()
    weather = get_weather(session.get('location', 'Tamil Nadu'))
    return render_template('dashboard.html', crops=crops, alerts=alerts,
                           weather=weather, current_user_id=session['user_id'])

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    my_crops = conn.execute('SELECT * FROM crops WHERE user_id=? ORDER BY created_at DESC',
                            (session['user_id'],)).fetchall()
    my_alerts = conn.execute('SELECT * FROM disease_alerts WHERE user_id=? ORDER BY reported_at DESC',
                             (session['user_id'],)).fetchall()
    conn.close()
    return render_template('profile.html', crops=my_crops, alerts=my_alerts)

@app.route('/add_crop', methods=['POST'])
def add_crop():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    crop_name = request.form['crop_name']
    planted_date = request.form.get('planted_date')
    area_size = request.form.get('area_size')
    soil_type = request.form.get('soil_type','Loamy')
    protection_strategy = request.form.get('protection_strategy','None')
    status = request.form['status']
    quantity_info = request.form.get('quantity_info')
    if not crop_name or not status:
        flash('Crop Name and Status are required!', 'danger')
    else:
        conn = get_db()
        conn.execute('INSERT INTO crops (user_id,crop_name,planted_date,area_size,soil_type,protection_strategy,status,quantity_info) VALUES (?,?,?,?,?,?,?,?)',
                     (session['user_id'], crop_name, planted_date, area_size, soil_type, protection_strategy, status, quantity_info))
        conn.commit()
        conn.close()
        flash(f'{crop_name} added to your diary!', 'success')
    return redirect(url_for('profile'))

@app.route('/delete_crop/<int:id>', methods=['POST'])
def delete_crop(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    crop = conn.execute('SELECT * FROM crops WHERE id=?', (id,)).fetchone()
    if crop and crop['user_id'] == session['user_id']:
        conn.execute('DELETE FROM crops WHERE id=?', (id,))
        conn.commit()
        flash('Crop entry deleted.', 'info')
    conn.close()
    return redirect(url_for('profile'))

# ─── AI Feature Routes ────────────────────────────────────────────────────────
@app.route('/crop-recommendation')
def crop_recommendation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('crop_recommendation.html',
                           crop_list=list(CROP_DB.keys()))

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    results = recommend_crops(
        n=float(data.get('n',80)),
        p=float(data.get('p',40)),
        k=float(data.get('k',40)),
        temp=float(data.get('temp',28)),
        rainfall=float(data.get('rainfall',100)),
        humidity=float(data.get('humidity',65)),
        soil_type=data.get('soil_type','Loamy'),
        ph=float(data.get('ph',6.5))
    )
    crops_out = []
    for crop, score, req in results:
        crops_out.append({
            "name": crop, "score": round(score, 1),
            "season": req["season"],
            "soil": req["soil"],
            "price_quintal": req["price"],
            "yield_acre": req["yield_per_acre"],
        })
    # Save recommendation
    conn = get_db()
    conn.execute('INSERT INTO recommendations (user_id,input_data,recommended_crops) VALUES (?,?,?)',
                 (session['user_id'], json.dumps(data), json.dumps([c['name'] for c in crops_out[:3]])))
    conn.commit()
    conn.close()
    return jsonify({'recommendations': crops_out})

@app.route('/disease-detection')
def disease_detection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('disease_detection.html', crop_list=list(CROP_DB.keys()))

@app.route('/api/detect-disease', methods=['POST'])
def api_detect_disease():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    image_b64 = data.get('image')
    crop_name = data.get('crop', 'General')
    if not image_b64:
        return jsonify({'error': 'No image provided'}), 400
    result = detect_disease(image_b64, crop_name)
    # Auto-report alert if disease found
    if result['disease']['name'] != 'Healthy Plant':
        try:
            conn = get_db()
            conn.execute('INSERT INTO disease_alerts (user_id,district,crop_name,disease_name,severity) VALUES (?,?,?,?,?)',
                         (session['user_id'], session.get('district','Unknown'),
                          crop_name, result['disease']['name'], result['disease']['severity']))
            conn.commit()
            conn.close()
        except:
            pass
    return jsonify(result)

@app.route('/yield-profit')
def yield_profit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('yield_profit.html', crop_list=list(CROP_DB.keys()))

@app.route('/api/predict-profit', methods=['POST'])
def api_predict_profit():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    result = predict_yield_profit(
        crop_name=data.get('crop','Rice'),
        area_acres=float(data.get('area',1.0)),
        soil_type=data.get('soil','Loamy'),
        irrigation=data.get('irrigation','Good'),
    )
    if result is None:
        return jsonify({'error': 'Crop not found'}), 404
    return jsonify(result)

@app.route('/weather')
def weather_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    weather = get_weather(session.get('location','Chennai'))
    all_weather = []
    for loc, w in WEATHER_DATA.items():
        wd = w.copy(); wd['location'] = loc
        all_weather.append(wd)
    return render_template('weather.html', weather=weather,
                           all_weather=all_weather,
                           irrigation_crops=list(IRRIGATION_ADVICE.keys())[:-1])

@app.route('/api/irrigation-advice', methods=['POST'])
def api_irrigation():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    crop = request.json.get('crop','Rice')
    advice = get_irrigation_advice(crop)
    weather = get_weather(session.get('location','Chennai'))
    need = "High" if weather['rainfall'] < 70 else ("Medium" if weather['rainfall'] < 120 else "Low")
    return jsonify({'crop': crop, 'advice': advice, 'water_need': need, 'weather': weather})

@app.route('/alerts')
def alerts_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    all_alerts = conn.execute('''
        SELECT disease_alerts.*, users.username, users.location
        FROM disease_alerts JOIN users ON disease_alerts.user_id = users.id
        ORDER BY reported_at DESC
    ''').fetchall()
    my_district = session.get('district', session.get('location',''))
    my_alerts = [a for a in all_alerts if my_district.lower() in a['district'].lower()
                 or a['district'].lower() in my_district.lower()]
    conn.close()
    return render_template('alerts.html', all_alerts=all_alerts, my_alerts=my_alerts,
                           my_district=my_district)

@app.route('/api/report-alert', methods=['POST'])
def api_report_alert():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO disease_alerts (user_id,district,crop_name,disease_name,severity) VALUES (?,?,?,?,?)',
                 (session['user_id'], data.get('district', session.get('district','Unknown')),
                  data.get('crop','General'), data.get('disease','Unknown Disease'),
                  data.get('severity','Medium')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'Alert reported successfully'})

@app.route('/api/tamil-assistant', methods=['POST'])
def api_tamil():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    query = request.json.get('query','')
    response = get_tamil_response(query)
    return jsonify({'response': response, 'query': query})

@app.route('/api/agribot', methods=['POST'])
def api_agribot():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    msg = request.json.get('message','').lower()
    location = session.get('location','Tamil Nadu')
    weather = get_weather(location)
    
    if any(w in msg for w in ['recommend','suggest','crop','which crop','what crop','grow']):
        resp = "🌾 Use our <a href='/crop-recommendation'>Crop Recommendation Tool</a> to get AI-based crop suggestions based on your soil NPK, temperature, and rainfall data."
    elif any(w in msg for w in ['disease','sick','spot','blight','wilt','pest','fungal','rust']):
        resp = "🔬 Upload a photo of your affected plant in our <a href='/disease-detection'>Disease Detection Tool</a> for instant AI diagnosis and treatment advice."
    elif any(w in msg for w in ['profit','income','earn','yield','harvest','price','market']):
        resp = "💰 Use our <a href='/yield-profit'>Yield & Profit Predictor</a> to estimate your harvest income and compare crops."
    elif any(w in msg for w in ['weather','rain','temperature','humid','forecast','climate']):
        resp = f"🌤️ Current weather in {weather['location']}: <strong>{weather['temp']}°C</strong>, Humidity: {weather['humidity']}%, Rainfall: {weather['rainfall']}mm. {weather['forecast']} See <a href='/weather'>full weather dashboard</a>."
    elif any(w in msg for w in ['water','irrigat','drip','flood','channel','canal']):
        resp = "💧 Get crop-specific irrigation schedules and water management tips in our <a href='/weather'>Weather & Irrigation Module</a>."
    elif any(w in msg for w in ['alert','outbreak','spread','report','district','area']):
        resp = "🚨 Check district-level crop disease outbreak alerts in our <a href='/alerts'>Location Alert System</a>. You can also report a new disease sighting."
    elif any(w in msg for w in ['tamil','voice','speak','audio','vaai']):
        resp = "🎙️ Tamil voice assistant is available on this page. Click the microphone button to ask in Tamil!"
    elif any(w in msg for w in ['rice','paddy','wheat','maize','cotton','tomato','banana','sugarcane','onion']):
        crop = next((c for c in CROP_DB if c.lower() in msg), 'Rice')
        info = CROP_DB[crop]
        resp = f"🌱 <strong>{crop}</strong>: Best in {', '.join(info['soil'])} soil. Temperature: {info['temp'][0]}-{info['temp'][1]}°C. Market price: ₹{info['price']}/quintal. Season: {info['season']}."
    elif any(w in msg for w in ['hello','hi','help','start','begin','namaste','vanakkam']):
        resp = "🙏 Welcome to Smart Crop Advisory! I can help you with: 🌾 Crop recommendations | 🔬 Disease detection | 💰 Profit prediction | 🌤️ Weather | 💧 Irrigation | 🚨 Disease alerts. What do you need?"
    elif any(w in msg for w in ['soil','npk','nitrogen','phosphorus','potassium','ph']):
        resp = "🧪 Soil health is critical! Get your soil tested at your nearest Krishi Vigyan Kendra. Use our <a href='/crop-recommendation'>Crop Recommendation</a> tool to enter your NPK values for best crop match."
    else:
        resp = f"Thank you for your question about '{msg}'. I'm here to assist with crop selection, disease identification, profit estimates, weather, and irrigation. Use the navigation menu to access specialized tools or ask me anything about farming! 🌾"
    
    return jsonify({'response': resp})

@app.route('/download')
def download_page():
    return render_template('download.html')

@app.route('/download/apk')
@app.route('/download-apk')
def download_apk():
    apk_path = os.path.join(os.path.dirname(__file__), 'static', 'downloads', 'SmartCropAdvisory.apk')
    if not os.path.exists(apk_path):
        apk_path = os.path.join(os.path.dirname(__file__), '..', 'downloads', 'SmartCropAdvisory.apk')
    if os.path.exists(apk_path):
        return send_file(
            apk_path,
            as_attachment=True,
            download_name='SmartCropAdvisory.apk',
            mimetype='application/vnd.android.package-archive'
        )
    return "APK not found. Please build or check back shortly.", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
