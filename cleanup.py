import shopify
import time

# Konfiguracja API
SHOP_URL = "nazwa-sklepu.myshopify.com"
ACCESS_TOKEN = "wpisz token"
API_VERSION = "2024-10"

# Rozpoczęcie sesji Shopify
session = shopify.Session(f"https://{SHOP_URL}", API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# Funkcja przetwarzania produktów
def process_products(products):
    for product in products:
        total_quantity = sum(
            [variant.inventory_quantity for variant in product.variants]
        )
        current_status = product.status

        # Zastosowanie reguły Maćka
        if total_quantity <= 0 and current_status == "draft":
            continue
        elif total_quantity <= 0 and current_status == "active":
            product.status = "draft"
        elif total_quantity > 0 and current_status == "draft":
            product.status = "active"
        elif total_quantity > 0 and current_status == "active":
            continue

        # Zapisanie zmian
        product.save()

# Funkcja obsługi paginacji za pomocą since_id
def update_all_products():
    since_id = 0  # since_id zaczynamy od zera
    while True:
        try:
            # Pobranie produktów z API Shopify
            products = shopify.Product.find(limit=250, since_id=since_id)
            if not products:
                break

            # Przetwarzanie produktów
            process_products(products)

            # Aktualizacja since_id
            since_id = products[-1].id  # Ustawienie ID ostatniego produktu jako nowy since_id
        except Exception as e:
            print(f"Błąd pobierania strony: {e}")
            break

# Wykonanie głównej funkcji
start_time = time.time()
update_all_products()
end_time = time.time()

print(f"Proces zakończony w {end_time - start_time:.2f} sekund.")

# Zakończenie sesji Shopify uwaga trochę potrwa
shopify.ShopifyResource.clear_session()
