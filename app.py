from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'

# Data storage files
FEATURES_FILE = 'data/features.json'
NEARBY_FILE = 'data/nearby.json'
FEEDBACK_FILE = 'data/feedback.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize data files if they don't exist
def initialize_data():
    if not os.path.exists(FEATURES_FILE):
        default_features = [
            {
                "id": 1,
                "icon": "fas fa-concierge-bell",
                "title": "Exceptional Service",
                "description": "Experience world-class hospitality with our dedicated team",
                "image": "lobby.jpg"
            },
            {
                "id": 2,
                "icon": "fas fa-bed",
                "title": "Luxurious Rooms",
                "description": "Elegantly designed spaces for ultimate comfort",
                "image": "deluxe a1.jpg"
            },
            {
                "id": 3,
                "icon": "fas fa-utensils",
                "title": "Fine Dining",
                "description": "Savor exquisite cuisine at our restaurant",
                "image": "resto.jpg"
            },
            {
                "id": 4,
                "icon": "fas fa-swimming-pool",
                "title": "Recreation",
                "description": "Relax and unwind in our premium facilities",
                "image": "pool.jpg"
            }
        ]
        with open(FEATURES_FILE, 'w') as f:
            json.dump(default_features, f, indent=2)

    if not os.path.exists(NEARBY_FILE):
        default_nearby = [
            {
                "id": 1,
                "title": "City of Dreams",
                "description": "Premier entertainment and gaming destination",
                "image": "cod.jpg",
                "distance": "2.1 km • 8 min walk"
            },
            {
                "id": 2,
                "title": "Landers",
                "description": "Supermarket and shopping center for daily needs",
                "image": "Landers.jpg",
                "distance": "1.2 km • 5 min walk"
            },
            {
                "id": 3,
                "title": "MOA Arena",
                "description": "World-class concert and sports events venue",
                "image": "MOA ARENA.jpg",
                "distance": "3.5 km • 12 min walk"
            },
            {
                "id": 4,
                "title": "MOA Globe",
                "description": "Iconic observation wheel with spectacular city views",
                "image": "MOA GLOBE.jpg",
                "distance": "3.2 km • 10 min walk"
            },
            {
                "id": 5,
                "title": "NAIA Terminal 3",
                "description": "International airport terminal for convenient travel",
                "image": "naiaterm3.jpg",
                "distance": "8.7 km • 15 min drive"
            },
            {
                "id": 6,
                "title": "NAIA Terminal 1",
                "description": "International airport terminal for global connections",
                "image": "naiaterm1.jpg",
                "distance": "9.2 km • 20 min drive"
            },
            {
                "id": 7,
                "title": "National University-MOA",
                "description": "Premier educational institution near mall area",
                "image": "National University-MOA.jpg",
                "distance": "4.1 km • 14 min walk"
            },
            {
                "id": 8,
                "title": "Parqal",
                "description": "Modern shopping and dining complex",
                "image": "parqal.jpg",
                "distance": "2.8 km • 9 min walk"
            },
            {
                "id": 9,
                "title": "SNR",
                "description": "Shopping center with various retail options",
                "image": "snr.jpg",
                "distance": "1.8 km • 6 min walk"
            },
            {
                "id": 10,
                "title": "Solaire",
                "description": "Luxury resort and casino with premium amenities",
                "image": "solaire.jpg",
                "distance": "2.5 km • 8 min walk"
            }
        ]
        with open(NEARBY_FILE, 'w') as f:
            json.dump(default_nearby, f, indent=2)

    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump([], f)

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Main routes
@app.route('/')
def index():
    features = load_data(FEATURES_FILE)
    nearby = load_data(NEARBY_FILE)
    testimonials = load_data(FEEDBACK_FILE)
    return render_template('index.html', features=features, nearby=nearby, testimonials=testimonials)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    elif request.method == 'POST':
        return submit_feedback()

# Admin routes
@app.route('/admin')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/dashboard.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Simple authentication (you should use proper password hashing in production)
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/features')
def admin_features():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    features = load_data(FEATURES_FILE)
    return render_template('admin/features.html', features=features)

@app.route('/admin/features/add', methods=['GET', 'POST'])
def admin_add_feature():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        features = load_data(FEATURES_FILE)
        new_id = max([f['id'] for f in features], default=0) + 1
        
        new_feature = {
            "id": new_id,
            "icon": request.form.get('icon'),
            "title": request.form.get('title'),
            "description": request.form.get('description'),
            "image": request.form.get('image')
        }
        
        features.append(new_feature)
        save_data(FEATURES_FILE, features)
        flash('Feature added successfully!', 'success')
        return redirect(url_for('admin_features'))
    
    return render_template('admin/add_feature.html')

@app.route('/admin/features/edit/<int:feature_id>', methods=['GET', 'POST'])
def admin_edit_feature(feature_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    features = load_data(FEATURES_FILE)
    feature = next((f for f in features if f['id'] == feature_id), None)
    
    if not feature:
        flash('Feature not found!', 'error')
        return redirect(url_for('admin_features'))
    
    if request.method == 'POST':
        feature['icon'] = request.form.get('icon')
        feature['title'] = request.form.get('title')
        feature['description'] = request.form.get('description')
        feature['image'] = request.form.get('image')
        
        save_data(FEATURES_FILE, features)
        flash('Feature updated successfully!', 'success')
        return redirect(url_for('admin_features'))
    
    return render_template('admin/edit_feature.html', feature=feature)

@app.route('/admin/features/delete/<int:feature_id>')
def admin_delete_feature(feature_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    features = load_data(FEATURES_FILE)
    features = [f for f in features if f['id'] != feature_id]
    save_data(FEATURES_FILE, features)
    flash('Feature deleted successfully!', 'success')
    return redirect(url_for('admin_features'))

@app.route('/admin/nearby')
def admin_nearby():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    nearby = load_data(NEARBY_FILE)
    return render_template('admin/nearby.html', nearby=nearby)

@app.route('/admin/nearby/add', methods=['GET', 'POST'])
def admin_add_nearby():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        nearby = load_data(NEARBY_FILE)
        new_id = max([n['id'] for n in nearby], default=0) + 1
        
        new_place = {
            "id": new_id,
            "title": request.form.get('title'),
            "description": request.form.get('description'),
            "image": request.form.get('image'),
            "distance": request.form.get('distance')
        }
        
        nearby.append(new_place)
        save_data(NEARBY_FILE, nearby)
        flash('Nearby place added successfully!', 'success')
        return redirect(url_for('admin_nearby'))
    
    return render_template('admin/add_nearby.html')

@app.route('/admin/nearby/edit/<int:place_id>', methods=['GET', 'POST'])
def admin_edit_nearby(place_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    nearby = load_data(NEARBY_FILE)
    place = next((n for n in nearby if n['id'] == place_id), None)
    
    if not place:
        flash('Place not found!', 'error')
        return redirect(url_for('admin_nearby'))
    
    if request.method == 'POST':
        place['title'] = request.form.get('title')
        place['description'] = request.form.get('description')
        place['image'] = request.form.get('image')
        place['distance'] = request.form.get('distance')
        
        save_data(NEARBY_FILE, nearby)
        flash('Place updated successfully!', 'success')
        return redirect(url_for('admin_nearby'))
    
    return render_template('admin/edit_nearby.html', place=place)

@app.route('/admin/nearby/delete/<int:place_id>')
def admin_delete_nearby(place_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    nearby = load_data(NEARBY_FILE)
    nearby = [n for n in nearby if n['id'] != place_id]
    save_data(NEARBY_FILE, nearby)
    flash('Place deleted successfully!', 'success')
    return redirect(url_for('admin_nearby'))

# Feedback submission
def submit_feedback():
    if request.method == 'POST':
        feedback_list = load_data(FEEDBACK_FILE)
        new_id = max([f.get('id', 0) for f in feedback_list], default=0) + 1
        
        feedback = {
            "id": new_id,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "message": request.form.get('message'),
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "read": False
        }
        
        feedback_list.append(feedback)
        save_data(FEEDBACK_FILE, feedback_list)
        flash('Thank you for your feedback! We will get back to you soon.', 'success')
        
    return redirect(url_for('contact'))

@app.route('/admin/feedback')
def admin_feedback():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    feedback = load_data(FEEDBACK_FILE)
    return render_template('admin/feedback.html', feedback=feedback)

@app.route('/admin/feedback/mark_read/<int:feedback_id>')
def admin_mark_read(feedback_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    feedback_list = load_data(FEEDBACK_FILE)
    for item in feedback_list:
        if item['id'] == feedback_id:
            item['read'] = True
            break
    save_data(FEEDBACK_FILE, feedback_list)
    return redirect(url_for('admin_feedback'))

@app.route('/admin/feedback/delete/<int:feedback_id>')
def admin_delete_feedback(feedback_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    feedback_list = load_data(FEEDBACK_FILE)
    feedback_list = [f for f in feedback_list if f['id'] != feedback_id]
    save_data(FEEDBACK_FILE, feedback_list)
    flash('Feedback deleted successfully!', 'success')
    return redirect(url_for('admin_feedback'))

# Static file serving
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    initialize_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
