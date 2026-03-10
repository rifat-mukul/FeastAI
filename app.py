from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import re
import json, os, requests as http_requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import math
import numpy as np
from flask import jsonify


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

OPENROUTER_API_KEY = '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'

locations = {
    'gulshan':     {'food': 'International cuisine, cafes',   'url': "https://www.google.ca/maps/search/Gulshan+resturent/@23.7901972,90.3897927,14z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'badda':       {'food': 'Street food, kebabs',            'url': "https://www.google.ca/maps/search/badda+resturent/@23.7901945,90.3897926,14z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'banani':      {'food': 'Upscale restaurants, coffee',    'url': "https://www.google.ca/maps/search/banani+restaurants/@23.7909997,90.3912129,14.71z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'aftabnagar':  {'food': 'Traditional Bangladeshi dishes', 'url': "https://www.google.ca/maps/search/restaurants+near+Aftab+Nagar,+Dhaka/@23.766433,90.4300181,15z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'framgate':    {'food': 'Street food, curries',           'url': "https://www.google.ca/maps/search/farmgate+restaurant/@23.7562746,90.389278,16z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'mohammadpur': {'food': 'Biryani, mutton curry',          'url': "https://www.google.ca/maps/search/mohammadpur+restaurant+/@23.7658329,90.3356083,15z/data=!3m1!4b1?entry=ttu&hl=en"},
    'shyamoli':    {'food': 'Street food, kebabs',            'url': "https://www.google.ca/maps/search/shyamoli+restaurant/@23.7722406,90.3539775,16z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'dhanmondi':   {'food': 'Bengali sweets, fusion food',    'url': "https://www.google.ca/maps/search/dhanmondi+restaurant/@23.7476824,90.3697812,15.17z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'bashundhara': {'food': 'Fine dining, Bengali cuisine',   'url': "https://www.google.ca/maps/search/bashundhara+restaurant/@23.812303,90.4262597,14.75z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'newmarket':   {'food': 'Street food, snacks',            'url': "https://www.google.ca/maps/search/restaurants+near+New+Market,+Dhaka/@23.7331936,90.3788955,17z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'old_dhaka':   {'food': 'Kacchi biryani, sweets',         'url': "https://www.google.ca/maps/search/old+dhaka+restaurant/@23.7229013,90.3608171,14z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'mirpur':      {'food': 'Biryani, kebabs, snacks',        'url': "https://www.google.ca/maps/search/mirpur+restaurant/@23.8104534,90.321081,13z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'khilgaon':    {'food': 'Kacchi biryani, snacks',         'url': "https://www.google.ca/maps/search/khilgaon+restaurant/@23.7617393,90.4112991,14z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'tejgaon':     {'food': 'Chinese food, kebabs',           'url': "https://www.google.ca/maps/search/tejgaon+restaurant/@23.7636962,90.3687163,15z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'purbachal':   {'food': 'Pithas, traditional dishes',     'url': "https://www.google.ca/maps/search/Purbachal+New+Town+Project+resturent/@23.8526208,90.4877234,14z/data=!4m2!2m1!6e5?entry=ttu&hl=en"},
    'motijheel':   {'food': 'Street food, Bengali sweets',    'url': "https://www.google.ca/maps/search/Motijheel+resturent/@23.7354666,90.4080076,15z/data=!3m1!4b1?entry=ttu&hl=en"},
}

db_config = {
    'host': 'localhost',
    'user': 'mukul',
    'password': 'mukul1572',
    'database': 'feast_ai'
}


# ── DB helpers ────────────────────────────────────────────────────────────────

def get_db_connection():
    return mysql.connector.connect(**db_config)


def get_restaurant_id_from_session():
    return session.get('restaurant_id')


# ── Utility helpers ───────────────────────────────────────────────────────────

def extract_coordinates(map_url):
    """Extract lat/lon from a Google Maps URL."""
    try:
        match = re.search(r'@([-]?\d+\.\d+),([-]?\d+\.\d+)', map_url)
        if match:
            return float(match.group(1)), float(match.group(2))
        print("Coordinates not found in the URL.")
        return None, None
    except Exception as e:
        print(f"Error extracting coordinates: {e}")
        return None, None


def haversine(lat1, lon1, lat2, lon2):
    """Return distance in km between two lat/lon points."""
    R = 6371
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    except (ValueError, TypeError):
        return None
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def compute_tfidf_scores(user_input_text, review_texts):
    """
    Compute cosine similarity scores between user input and a list of review texts
    using TF-IDF vectorization. Returns a numpy array of similarity scores.
    """
    vectorizer   = TfidfVectorizer()
    all_texts    = [user_input_text] + review_texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    scores       = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    return scores


def refine_with_llm(candidate_restaurants, user_input_text):
    """
    Sends the top-15 cosine-similarity candidates + user input to the LLM.
    LLM picks the best max-8 and returns their names as a JSON array.
    Falls back to top-8 candidates if anything goes wrong.
    """
    restaurant_lines = ""
    for i, r in enumerate(candidate_restaurants, 1):
        restaurant_lines += (
            f"{i}. Name: {r['name']}\n"
            f"   Address: {r['address']}\n"
            f"   User Reviews: {r['sample_user_reviews']}\n"
            f"   Rating: {r['rating']}\n"
            f"   Distance: {round(r['distance'], 2)} km\n\n"
        )

    prompt = (
        f'You are a restaurant recommendation expert.\n\n'
        f'A user is looking for: "{user_input_text}"\n\n'
        f'Below are pre-filtered restaurant candidates (already close to the user '
        f'and matched by semantic similarity). Choose a maximum of 8 that best match '
        f"the user's request based on the reviews, rating, and description.\n\n"
        f'Return ONLY a JSON array of the selected restaurant names in order of best '
        f'match, like:\n["Restaurant A", "Restaurant B", "Restaurant C"]\n'
        f'Do not include any explanation or extra text.\n\n'
        f'Candidates:\n{restaurant_lines}'
    )

    try:
        response = http_requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "arcee-ai/trinity-large-preview:free",
                "messages": [{"role": "user", "content": prompt}],
            }),
            timeout=30
        )

        result      = response.json()
        raw_content = result['choices'][0]['message']['content'].strip()

        # Strip markdown code fences if the model wraps its answer
        raw_content = re.sub(r'```json|```', '', raw_content).strip()

        llm_names = json.loads(raw_content)   # should be a list of strings

        # Map names back to full restaurant dicts
        name_to_restaurant = {r['name']: r for r in candidate_restaurants}
        refined = [
            name_to_restaurant[name.strip()]
            for name in llm_names
            if name.strip() in name_to_restaurant
        ]

        return refined[:8] if refined else candidate_restaurants[:8]

    except Exception as e:
        print(f"LLM refinement failed ({e}), falling back to cosine-similarity top-8.")
        return candidate_restaurants[:8]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def home():
    search   = request.args.get('search', '')
    location = request.args.get('location', 'None')
    return render_template('home.html', locations=locations, search=search, location=location)


@app.route('/find_restaurant', methods=['GET', 'POST'])
def find_restaurant():
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, rating, reviews_count, address, contact, price_per_person, map_url FROM restaurants')
    restaurants = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('find_restaurant.html', restaurants=restaurants)


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        email      = request.form.get('email')
        phone      = request.form.get('phone')
        password   = request.form.get('password')
        user_type  = request.form.get('user_type')

        conn   = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            flash("A user with this email already exists. Please choose a different email.")
            cursor.close(); conn.close()
            return render_template('create_account.html')

        cursor.execute('SELECT * FROM users WHERE phone = %s', (phone,))
        if cursor.fetchone():
            flash("A user with this phone number already exists. Please choose a different phone number.")
            cursor.close(); conn.close()
            return render_template('create_account.html')

        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (first_name, last_name, email, phone, password, user_type) VALUES (%s,%s,%s,%s,%s,%s)',
            (first_name, last_name, email, phone, hashed_password, user_type)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Account created successfully!")
        session['user_email'] = email
        session['user_type']  = user_type
        session['user_name']  = first_name
        return redirect(url_for('profile'))

    return render_template('create_account.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if check_password_hash(user[5], password):
                session['user_email']    = email
                session['restaurant_id'] = user[0]
                if user[6] == 'restaurant_owner':
                    return redirect(url_for('restaurant_dashboard'))
                return redirect(url_for('profile'))
            else:
                flash("Invalid email or password. Please try again.")
        else:
            flash("No user found with that email.")

    return render_template('login.html')


# ── Profile / recommendation engine ──────────────────────────────────────────

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_email = session.get('user_email')
    if not user_email:
        flash("You must be logged in to view the profile.")
        return redirect(url_for('login'))

    conn   = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT first_name, last_name, email, phone FROM users WHERE email = %s', (user_email,))
    user = cursor.fetchone()

    cursor.execute('SELECT * FROM preferences')
    available_preferences = cursor.fetchall()

    # ── Always initialise so GET requests never hit UnboundLocalError ─────────
    top_restaurants = []
    food_type_name  = None

    if request.method == 'POST':
        map_url         = request.form.get('map_url')
        submission_mode = request.form.get('submission_mode')
        is_valid        = False
        user_input_text = ''

        if not map_url:
            flash("Please provide a Google Map URL.")

        elif submission_mode == 'selection':
            f_t             = request.form.get('food_type')
            preferable_time = request.form.get('preferable_time')
            if f_t and preferable_time:
                cursor.execute('SELECT name FROM preferences WHERE id = %s', (f_t,))
                pref_row        = cursor.fetchone()
                food_type_name  = pref_row[0] if pref_row else None
                user_input_text = f"{food_type_name}, within {preferable_time} minutes travel time"
                is_valid        = True
            else:
                flash("Please select both a cuisine and a wait time.")

        elif submission_mode == 'writing':
            user_note = request.form.get('user_note', '').strip()
            if user_note:
                user_input_text = user_note
                is_valid        = True
            else:
                flash("Please describe your mood/craving.")

        if is_valid:
            user_lat, user_lon = extract_coordinates(map_url)
            if user_lat is None or user_lon is None:
                flash("Invalid Google Maps URL. Please provide a valid location link.")
            else:
                # Step 1: fetch all restaurants
                cursor.execute('''
                    SELECT name, rating, reviews_count, latitude, longitude,
                           address, contact, price_per_person, map_url, sample_user_reviews
                    FROM restaurants
                ''')
                all_restaurants = cursor.fetchall()

                # Step 2: deduplicate + Haversine sort, keep top 50
                seen   = set()
                ranked = []
                for row in all_restaurants:
                    name = row[0]
                    if name in seen:
                        continue
                    seen.add(name)
                    dist = haversine(user_lat, user_lon, row[3], row[4])
                    if dist is not None:
                        ranked.append({
                            'name':                name,
                            'rating':              row[1],
                            'reviews_count':       row[2],
                            'address':             row[5],
                            'contact':             row[6],
                            'price_per_person':    row[7],
                            'map_url':             row[8],
                            'sample_user_reviews': row[9] or '',
                            'distance':            dist,
                        })

                ranked.sort(key=lambda x: x['distance'])
                top_50 = ranked[:50]

                if not top_50:
                    flash("No restaurants found in our database.")
                else:
                    # Step 3: TF-IDF cosine similarity on sample_user_reviews
                    review_texts = [r['sample_user_reviews'] for r in top_50]
                    scores       = compute_tfidf_scores(user_input_text, review_texts)

                    scored = sorted(zip(top_50, scores), key=lambda x: x[1], reverse=True)

                    # Top 15 candidates passed to LLM
                    top_15_candidates = [
                        {**res, 'similarity': float(score)}
                        for res, score in scored[:15]
                    ]

                    # Step 4: LLM picks best max-8
                    top_restaurants = refine_with_llm(top_15_candidates, user_input_text)

    cursor.close()
    conn.close()

    return render_template(
        'profile.html',
        user=user,
        available_preferences=available_preferences,
        top_restaurants=top_restaurants,
        food_type=food_type_name,
    )


@app.route('/chatbot', methods=['POST'])
def chatbot():
    """
    Receives a JSON body: { "message": "user text" }
    Queries the restaurant DB for relevant context, then calls the LLM.
    Returns: { "reply": "..." }
    """
    data         = request.get_json(force=True, silent=True) or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'reply': "Please type a message so I can help you!"}), 400

    # ── Pull restaurant data for context ──────────────────────────────────────
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, rating, address, price_per_person, sample_user_reviews, location
            FROM restaurants
            ORDER BY rating DESC
            LIMIT 60
        ''')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"DB error in chatbot: {e}")
        rows = []

    # Build a compact restaurant summary for the prompt
    restaurant_context = ""
    for r in rows:
        name, rating, address, price, reviews, location = r
        restaurant_context += (
            f"- {name} | Location: {location} | Rating: {rating} | "
            f"Price/person: {price} BDT | Address: {address} | "
            f"Reviews snippet: {str(reviews)[:120]}\n"
        )

    system_prompt = (
        "You are FeastBot, a friendly AI assistant for Feast AI — a restaurant discovery "
        "platform in Dhaka, Bangladesh. You help users find great restaurants, suggest "
        "cuisines, answer questions about the platform, and give food recommendations.\n\n"
        "Use the restaurant data below to answer accurately. If a specific restaurant is "
        "not in the data, say you don't have info on it yet. Keep replies concise, warm, "
        "and helpful. Format suggestions as a short numbered list when relevant.\n\n"
        f"RESTAURANT DATABASE (top 60 by rating):\n{restaurant_context}"
    )

    try:
        response = http_requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type":  "application/json",
            },
            data=json.dumps({
                "model": "arcee-ai/trinity-large-preview:free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_message},
                ],
            }),
            timeout=30,
        )
        result = response.json()
        reply  = result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"LLM error in chatbot: {e}")
        reply = "Sorry, I'm having trouble connecting right now. Please try again in a moment!"

    return jsonify({'reply': reply})


# ── Other routes ──────────────────────────────────────────────────────────────

@app.route('/restaurants', methods=['GET'])
def restaurants():
    location = request.args.get('location', 'None')
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, rating, reviews_count, latitude, longitude, address,
               contact, price_range, price_per_person, map_url, sample_user_reviews
        FROM restaurants WHERE location = %s
    ''', (location,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        flash("No restaurants found in this area.")
    return render_template('restaurants.html', restaurants=rows, location=location)


@app.route('/restaurant_dashboard')
def restaurant_dashboard():
    restaurant_id = get_restaurant_id_from_session()
    if not restaurant_id:
        flash("Please log in first.")
        return redirect(url_for('login'))
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM menu_items WHERE restaurant_id = %s", (restaurant_id,))
    menu_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('restaurant_dashboard.html', menu_items=menu_items)


@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_name     = request.form.get('item_name')
        item_price    = request.form.get('item_price')
        restaurant_id = get_restaurant_id_from_session()
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO menu_items (name, price, restaurant_id) VALUES (%s, %s, %s)',
            (item_name, item_price, restaurant_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Item '{item_name}' added successfully!")
        return redirect(url_for('restaurant_dashboard'))
    return render_template('add_item.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_email', None)
    session.pop('restaurant_id', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash("Your message has been sent successfully!")
        return redirect(url_for("contact"))
    return render_template("contact.html", message_sent=False)


@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')


@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')


if __name__ == '__main__':
    app.run(debug=True)