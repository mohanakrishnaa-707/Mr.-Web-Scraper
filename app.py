from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import pandas as pd
import requests
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


blocked_domains = ["facebook.com", "linkedin.com", "twitter.com", "bank", "login", "admin"]


unwanted_phrases = [
    "home", "about", "contact", "services", "login", "register", "privacy", "terms",
    "disclaimer", "language", "search", "next", "previous", "menu", "footer", "copyright",
    "social", "policy", "all rights reserved", "subscribe", "cookies", "advertise", "donate"
]

def is_collusive(text, all_seen):
   
    if all_seen.count(text) > 1:
        return True
    return False

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get('url')
        scrape_type = data.get('type')

        # Domain check
        if any(domain in url.lower() for domain in blocked_domains):
            return jsonify({"error": "Blocked or sensitive domain"}), 403

  
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

       
        if soup.find("input", {"type": "password"}):
            return jsonify({"error": "Sensitive page detected"}), 403

     
        if scrape_type == "table":
            tables = soup.find_all("table")
            if not tables:
                return jsonify({"error": "No tables found"}), 404

            csv_files = []
            for i, table in enumerate(tables):
                try:
                    df = pd.read_html(str(table))[0]
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_files.append(csv_buffer.getvalue())
                except Exception:
                    continue  # Skip tables that can't be parsed

            if not csv_files:
                return jsonify({"error": "No parseable tables"}), 404

            return jsonify({"result": "\n\n".join(csv_files)})

      
        elif scrape_type == "text":
            elements = soup.find_all(["p", "h1", "h2", "h3", "li", "article", "span"])
            all_texts = [el.get_text(strip=True) for el in elements]

            seen = []
            cleaned = []
            for text in all_texts:
                if len(text) < 5:
                    continue

                lower = text.lower()
                if any(word in lower for word in unwanted_phrases):
                    continue

                if "•" in lower and len(lower) < 100:
                    continue  # likely language/menu items

                if is_collusive(text, all_texts):
                    continue

                cleaned.append(text)

            if not cleaned:
                return jsonify({"error": "No useful text found"}), 404

            return jsonify({"result": "\n\n".join(cleaned)})

        else:
            return jsonify({"error": "Invalid scrape type"}), 400

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5000)
