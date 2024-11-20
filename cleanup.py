import requests

# Dane autoryzacyjne
SHOP_URL = "https://changeme-1234.myshopify.com"  # <- Zmień na swój URL sklepu
API_VERSION = "2024-10"
ACCESS_TOKEN = "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"

# Endpoint i nagłówki
base_url = f"{SHOP_URL}/admin/api/{API_VERSION}/products.json"
headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

# Funkcja pobierająca produkty z paginacją
def fetch_all_products():
    page = 1
    products = []
    while True:
        params = {"limit": 250, "page": page}
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Błąd pobierania produktów (strona {page}): {response.status_code}")
            print(response.text)
            break

        page_products = response.json().get("products", [])
        if not page_products:
            break  # Koniec danych

        products.extend(page_products)
        page += 1

    return products

# Funkcja aktualizująca status produktu
def update_product_status(product_id, new_status):
    url = f"{SHOP_URL}/admin/api/{API_VERSION}/products/{product_id}.json"
    data = {
        "product": {
            "id": product_id,
            "status": new_status
        }
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Zaktualizowano produkt {product_id} na status '{new_status}'")
    else:
        print(f"Błąd aktualizacji produktu {product_id}: {response.status_code}")
        print(response.text)

# Główna funkcja przetwarzająca produkty
def process_products():
    products = fetch_all_products()
    if not products:
        print("Brak produktów do przetworzenia.")
        return

    for product in products:
        # Oblicz całkowitą ilość dla produktu
        total_quantity = sum(int(variant["inventory_quantity"]) for variant in product["variants"])
        current_status = product.get("status")

        # Reguły przetwarzania
        if total_quantity <= 0 and current_status == "draft":
            print(f"Produkt {product['id']} już w statusie 'draft'. NIC NIE ROBIĆ.")
        elif total_quantity <= 0 and current_status == "active":
            print(f"Produkt {product['id']} w statusie 'active'. Zmiana na 'draft'.")
            update_product_status(product["id"], "draft")
        elif total_quantity > 0 and current_status == "draft":
            print(f"Produkt {product['id']} w statusie 'draft'. Zmiana na 'active'.")
            update_product_status(product["id"], "active")
        elif total_quantity > 0 and current_status == "active":
            print(f"Produkt {product['id']} już w statusie 'active'. NIC NIE ROBIĆ.")

# Uruchomienie
if __name__ == "__main__":
    process_products()
