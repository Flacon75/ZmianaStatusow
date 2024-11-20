import shopify
import time
import logging

# Konfiguracja logowania
logging.basicConfig(
    filename="cleanup.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Konfiguracja API
SHOP_URL = "twoj-sklep.myshopify.com"
ACCESS_TOKEN = "twój token"
API_VERSION = "2024-10"

# Rozpoczęcie sesji Shopify
session = shopify.Session(f"https://{SHOP_URL}", API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# Funkcja przetwarzania produktów
def process_products(products):
    for product in products:
        try:
            total_quantity = sum([variant.inventory_quantity for variant in product.variants])
            current_status = product.status

            # Zastosowanie reguły Maćka
            if total_quantity <= 0 and current_status == "draft":
                logging.info(f"Produkt {product.id}: brak zmian (ilość: {total_quantity}, status: draft).")
                continue
            elif total_quantity <= 0 and current_status == "active":
                product.status = "draft"
                product.save()
                logging.info(f"Produkt {product.id}: zmiana statusu na draft (ilość: {total_quantity}).")
            elif total_quantity > 0 and current_status == "draft":
                product.status = "active"
                product.save()
                logging.info(f"Produkt {product.id}: zmiana statusu na active (ilość: {total_quantity}).")
            elif total_quantity > 0 and current_status == "active":
                logging.info(f"Produkt {product.id}: brak zmian (ilość: {total_quantity}, status: active).")
                continue
        except Exception as e:
            logging.error(f"Błąd przetwarzania produktu {product.id}: {e}")

# Funkcja obsługi paginacji za pomocą since_id
def update_all_products():
    logging.info("Rozpoczęto przetwarzanie produktów.")
    since_id = 0
    retry_count = 0

    while True:
        try:
            # Pobranie produktów z API Shopify
            products = shopify.Product.find(limit=250, since_id=since_id)
            if not products:
                logging.info("Brak więcej produktów do przetworzenia.")
                break

            # Przetwarzanie produktów
            process_products(products)

            # Aktualizacja since_id
            since_id = products[-1].id
            retry_count = 0  # Zresetowanie licznika błędów po udanym przetwarzaniu
        except Exception as e:
            logging.error(f"Błąd pobierania produktów: {e}")
            retry_count += 1
            if retry_count >= 5:
                logging.error("Osiągnięto limit błędów. Przerywam działanie.")
                break
            time.sleep(5)  # Poczekaj przed ponowną próbą

# Wykonanie głównej funkcji
if __name__ == "__main__":
    start_time = time.time()
    update_all_products()
    end_time = time.time()
    logging.info(f"Proces zakończony w {end_time - start_time:.2f} sekund.")
    print(f"Proces zakończony w {end_time - start_time:.2f} sekund.")
