import requests
from bs4 import BeautifulSoup
import json


def get_product_data(url):
    response = requests.get(url)
    if response.status_code == 404:
        return {"deleted": True}

    soup = BeautifulSoup(response.text, 'html.parser')
    get_data = soup.find('script', {'type': 'application/ld+json'}).string
    received_data = json.loads(get_data)

    product_data = {
        "name": received_data["name"],
        "price": received_data["offers"]["price"],
        "stock": received_data["offers"]["availability"].split('/')[-1],
        "description": received_data["description"],
        "image": received_data["image"],
        "native_id": received_data["identifier"],
        "deleted": False,
        "categories": received_data["category"].split(" + "),
        "gtin": received_data["gtin"]
    }

    return product_data


def update_products_data(product_urls, json_file):
    try:
        with open(json_file, 'r') as f:
            existing_products_list = json.load(f)
            existing_products_data = {product['native_id']: product for product in existing_products_list if 'native_id' in product}
    except FileNotFoundError:
        existing_products_data = {}

    new_products_data = []

    for url in product_urls:
        new_data = get_product_data(url)
        if new_data.get('deleted'):
            print(f"Product at URL {url} has been deleted.")
            continue
        existing_data = existing_products_data.get(new_data['native_id']) if new_data.get('native_id') else None
        compare_and_print_changes(existing_data, new_data)
        new_products_data.append(new_data)

    with open(json_file, 'w') as f:
        json.dump(new_products_data, f, indent=4)


def compare_and_print_changes(existing_data, new_data):
    if existing_data is None:
        print(f"New product added: {new_data['name']}")
        return

    if new_data["deleted"]:
        print(f"Product {existing_data['name']} has been deleted.")
        return

    for key in existing_data.keys():
        if existing_data[key] != new_data.get(key):
            print(f"{key.capitalize()} has changed from {existing_data[key]} to {new_data.get(key)} for {new_data['name']}.")

#Test
urls = [
    'https://www.hecht-garten.ch/do-it-garten/reinigungsgeraete/kehrmaschine/hecht-8101-bs-kehrmaschine/a-11908/',
    'https://www.hecht-garten.ch/do-it-garten/arbeitsbekleidung-arbeitsschutz/schutzbrille-gesichtsschutz/hecht-900106y-sicherheitsbrille-gelb_11947_3021/',
    'https://www.hecht-garten.ch/do-it-garten/gartenmaschinen-werkzeuge/zubehoer-gartenmaschinen/hecht-001277bx-ersatzakku-20-v-2-ah_47468_38542/'
]

update_products_data(urls, 'product_data.json')
