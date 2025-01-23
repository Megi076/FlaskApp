import requests

# Osnovna URL adresa na Flask aplikacijata
BASE_URL = "http://127.0.0.1:5000"

## 1. Prezemanje na vkupnata potrosuvacka na korisnik
def fetch_total_spent(user_id):
    # Kreiranje na endpoint za prezemanje na vkupnata potrosuvacka
    endpoint = f"{BASE_URL}/total_spent/{user_id}"
    try:
        # Izvrasuvanje na  HTTP GET baranje do API-to
        response = requests.get(endpoint)
        if response.status_code == 200:
            # Uspesno odgovoreno, podatocite se citaat vo JSON format
            data = response.json()
            print(f"Total spending for user {user_id}: {data['total_spending']}")
            return data #se vrakja soodveten odgovor
        else:
            # Ako ne uspee baranjeto se prikazuva poraka za greska
            print(f"Failed to fetch total spending: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        # Prifatena greska pri obid za baranje
        print(f"Error occurred while fetching total spending: {e}")

# 2. Prezemanje na prosecna potrosuvacka po vozrasni grupi
def fetch_average_spending_by_age():
    # Kreiranje na endpoint za prezemanje na prosecna potrosuvacka
    endpoint = f"{BASE_URL}/average_spending_by_age"
    try:
        #Izvrasuvanje na  HTTP GET baranje do API-to
        response = requests.get(endpoint)
        if response.status_code == 200:
            # Uspesno odgovoreno, podatocite se citaat vo JSON format
            data = response.json()
            print("Average spending by age ranges:")
            # Prikazuvanje na podatocite po vozrasni grupi
            for age_range, avg_spending in data.items():
                print(f"  Age {age_range}: {avg_spending:.2f}")
            return data
        else:
            # Ako ne uspee baranjeto se prikazuva poraka za greska
            print(f"Failed to fetch average spending: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        # Prifatena greska pri obid za baranje
        print(f"Error occurred while fetching average spending: {e}")

# 3. Zapisuvanje na korisnici vo MongoDB
def write_to_mongodb(user_id, total_spending):
    # Kreiranje na endpoint za zapisuvanje vo MongoDB
    endpoint = f"{BASE_URL}/write_to_mongodb"
    # Podatoci koi sto ke se ispratat vo JSON
    payload = {
        "user_id": user_id,
        "total_spending": total_spending
    }
    try:
        # Izvrsuvanje na HTTP POST baranje do API-to
        response = requests.post(endpoint, json=payload)
        if response.status_code == 201:
            # Upsesno zapisuvanje
            print("User data successfully written to MongoDB.")
        else:
            # Ako ne uspee baranjeto, se prikazuva poraka za greska
            print(f"Failed to write data to MongoDB: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        # Prifatena greska pri obid za baranje
        print(f"Error occurred while writing to MongoDB: {e}")

if __name__ == "__main__":
    print("=== Flask API Client Script ===")

    # Primer 1: Prezemanje na vkupnata potrosuvacka za odreden korisnik
    user_id = 791  # Treba da se zameni so validen user_id
    total_data = fetch_total_spent(user_id)

    if total_data:
        total_spending = total_data['total_spending']

        # Primer 2: Zapisuvanje vo MongoDB ako potrosuvackata nadminuva 1000
        if total_spending > 1000:
            write_to_mongodb(user_id, total_spending)
        else:
            print(f"User {user_id} is not eligible for a voucher (spending: {total_spending}).")

    # Primer 3: Prezemanje na prosecnata potrosuvacka po vozrasni grupi
    fetch_average_spending_by_age()
