# ✅ SEO Checker Backend (Python Flask API)

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

def get_html_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return None

def analyze_seo(url):
    html = get_html_content(url)
    if html is None:
        return {"error": "Failed to fetch the website."}

    soup = BeautifulSoup(html, 'html.parser')
    
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_desc = ""
    if soup.find("meta", attrs={"name": "description"}):
        meta_desc = soup.find("meta", attrs={"name": "description"}).get("content", "")

    h1 = soup.find("h1")
    images = soup.find_all("img")
    img_total = len(images)
    img_missing_alt = sum(1 for img in images if not img.get("alt"))

    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    try:
        robots_check = requests.get(base_url + "/robots.txt").status_code == 200
    except:
        robots_check = False

    return {
        "title": title,
        "meta_description": meta_desc,
        "h1_present": bool(h1),
        "total_images": img_total,
        "images_missing_alt": img_missing_alt,
        "robots_txt_found": robots_check
    }

@app.route('/api/seo-check', methods=['POST'])
def seo_check():
    data = request.get_json()
    url = data.get("url", "")
    if not url.startswith("http"):
        return jsonify({"error": "Invalid URL."}), 400

    result = analyze_seo(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
