import requests
from bs4 import BeautifulSoup
import psycopg2
import re

BASE_URL = "https://www.automobile.tn"

def get_connection():
    return psycopg2.connect(
        dbname="car_api_db",
        user="postgres",
        password="yeahdhia1",
        host="localhost",
        port="8000"
    )

def parse_sitemap(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "xml")
    return [loc.text for loc in soup.find_all("loc")]

def insert_brand(cur, brand):
    cur.execute("""
        INSERT INTO "CarPlace".brands (name)
        VALUES (%s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """, (brand,))
    brand_id = cur.fetchone()
    if not brand_id:
        cur.execute('SELECT id FROM "CarPlace".brands WHERE name=%s;', (brand,))
        brand_id = cur.fetchone()
    return brand_id[0]

def insert_category(cur, category):
    category = category or "Berline"
    cur.execute("""
        INSERT INTO "CarPlace".categories (name)
        VALUES (%s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """, (category,))
    category_id = cur.fetchone()
    if not category_id:
        cur.execute('SELECT id FROM "CarPlace".categories WHERE name=%s;', (category,))
        category_id = cur.fetchone()
    return category_id[0]

def insert_model(cur, model, brand_id):
    cur.execute("""
        INSERT INTO "CarPlace".models (name, brand_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """, (model, brand_id))
    model_id = cur.fetchone()
    if not model_id:
        cur.execute('SELECT id FROM "CarPlace".models WHERE name=%s AND brand_id=%s;', (model, brand_id))
        model_id = cur.fetchone()
    return model_id[0]

def scrape_constants(cur, url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.select_one("h1")
    category = soup.find(string=re.compile("Carrosserie"))

    if not title:
        return

    brand = title.text.strip().split()[0]
    model = " ".join(title.text.strip().split()[1:])

    brand_id = insert_brand(cur, brand)
    category_id = insert_category(cur, category.find_next().text.strip() if category else None)
    insert_model(cur, model, brand_id)

if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()

    sitemap_index = "https://www.automobile.tn/sitemap/sitemap_index.xml"
    sitemap_urls = parse_sitemap(sitemap_index)

    for sm in sitemap_urls:
        car_urls = parse_sitemap(sm)
        for car_url in car_urls[:100]:  # limit for testing
            scrape_constants(cur, car_url)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Brands, models, categories seeded into car_api_db")
