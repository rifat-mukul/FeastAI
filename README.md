# 🍽️ Feast AI — Smart Restaurant Discovery Platform

Feast AI is an AI-powered restaurant discovery web application built for **Dhaka, Bangladesh**. It helps users find the best nearby restaurants based on their mood, food preferences, and real-time location — using a smart recommendation engine backed by NLP and LLM refinement.

---

## 🚀 Features

- 🔍 **AI Restaurant Recommendations** — Describe your craving in plain text or select a cuisine type, and the system finds the best matches
- 📍 **Location-Aware Search** — Paste your Google Maps link and get restaurants ranked by distance using Haversine formula
- 🤖 **LLM Refinement** — Top candidates are passed to an LLM (via OpenRouter) for intelligent re-ranking
- 💬 **FeastBot Chatbot** — Built-in AI chatbot to help users explore restaurants and get suggestions
- 🗺️ **Browse by Area** — Explore restaurants across 16+ Dhaka neighborhoods (Gulshan, Banani, Dhanmondi, Mirpur, etc.)
- 👤 **User Authentication** — Secure registration and login with hashed passwords
- 🍴 **Restaurant Owner Dashboard** — Restaurant owners can log in and manage their menu items
- 📋 **TF-IDF Semantic Matching** — Matches user intent with restaurant reviews using cosine similarity

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MySQL |
| NLP / Similarity | scikit-learn (TF-IDF + Cosine Similarity) |
| LLM | OpenRouter API (arcee-ai/trinity-large-preview) |
| Frontend | HTML, CSS, JavaScript (Jinja2 templates) |
| Auth | Werkzeug password hashing |
| Distance | Haversine formula |

---

## 📁 Project Structure

```
feastAI/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                    # API keys (never commit this!)
├── .gitignore
├── README.md
├── static/                 # CSS, JS, images
├── templates/              # HTML templates
│   ├── home.html
│   ├── profile.html
│   ├── restaurants.html
│   ├── find_restaurant.html
│   ├── login.html
│   ├── create_account.html
│   ├── restaurant_dashboard.html
│   └── ...
├── test.py
├── test2.py
├── dataEDA.ipynb           # Exploratory data analysis
└── updated_eda_data.csv    # Restaurant dataset
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/rifat-mukul/feastAI.git
cd feastAI
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 5. Set up MySQL database
```sql
CREATE DATABASE feast_ai;
```
Then import your schema and data into the `feast_ai` database.

Update `db_config` in `app.py` with your MySQL credentials.

### 6. Run the application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key for LLM access |

---

## 🧠 How the Recommendation Engine Works

1. User provides their **Google Maps location link** + food preference or free-text mood
2. All restaurants are fetched from the database and sorted by **distance** (Haversine)
3. Top 50 nearest restaurants are scored using **TF-IDF cosine similarity** against user reviews
4. Top 15 candidates are sent to the **LLM** (via OpenRouter) for intelligent final ranking
5. Best 8 restaurants are returned to the user

---

## 📍 Supported Areas in Dhaka

Gulshan, Badda, Banani, Aftabnagar, Farmgate, Mohammadpur, Shyamoli, Dhanmondi, Bashundhara, New Market, Old Dhaka, Mirpur, Khilgaon, Tejgaon, Purbachal, Motijheel

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Rifat Mukul**  
Built with ❤️ for food lovers in Dhaka 🇧🇩