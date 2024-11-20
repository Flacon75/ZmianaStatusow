import shopify
from concurrent.futures import ThreadPoolExecutor
import time

# 1. Konfiguracja API
SHOP_URL = "changeme-1234.myshopify.com"
ACCESS_TOKEN = "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"  # Używamy Admin API Access Token

# Poprawna konfiguracja sesji
session = shopify.Session(f"https://{SHOP_URL}", "2024-01", ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# 2. Funkcja do pobierania jednej strony produktów
def fetch_products_page(page):
    try:
        return shopify.Product.find(limit=250, page=page)
    except Exception as e:
        print(f"Błąd pobierania strony {page}: {e}")
        return []

# 3. Funkcja do przetwarzania produktów
def process_products(products):
    for product in products:
        total_quantity = sum(
            [int(variant.inventory_quantity) for variant in product.variants]
        )
        current_status = product.status

        # Zastosuj reguły
        if total_quantity <= 0 and current_status == "draft":
            continue  # NIC NIE ROBIĆ
        elif total_quantity <= 0 and current_status == "active":
            product.status = "draft"
        elif total_quantity > 0 and current_status == "draft":
            product.status = "active"
        elif total_quantity > 0 and current_status == "active":
            continue  # NIC NIE ROBIĆ

        # Zapisz zmiany
        try:
            product.save()
        except Exception as e:
            print(f"Błąd zapisu produktu {product.id}: {e}")

# 4. Główna funkcja obsługująca paginację i równoległe pobieranie
def update_all_products():
    page = 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            # Uruchamiamy równoległe pobieranie stron
            future_pages = {executor.submit(fetch_products_page, page): page for page in range(page, page + 10)}
            all_products = []
            
            for future in future_pages:
                try:
                    products = future.result()
                    if not products:  # Jeśli strona jest pusta, kończymy
                        break
                    all_products.extend(products)
                except Exception as e:
                    print(f"Błąd pobierania strony: {e}")

            if not all_products:
                break

            # Równoległe przetwarzanie pobranych produktów
            executor.map(process_products, [all_products])
            page += 10  # Przejdź do następnych stron

# 5. Wykonanie procesu
start_time = time.time()
update_all_products()
end_time = time.time()

print(f"Proces zakończony w {end_time - start_time} sekund.")

# 6. Zakończenie sesji
shopify.ShopifyResource.clear_session()
