"""
Smart Crop Advisory System for Small and Marginal Farmers
Root entrypoint to run the Flask application.
"""
import sys
import os

# Add project01 to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project01'))

from app import app, init_db

if __name__ == '__main__':
    # Ensure database is initialized
    init_db()
    print("🌾 Smart Crop Advisory System running at http://127.0.0.1:5000")
    print("📱 Download Android APK at http://127.0.0.1:5000/download")
    app.run(debug=True, host='0.0.0.0', port=5000)
