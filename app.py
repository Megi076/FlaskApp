import requests as requests
from flask import Flask, request, jsonify
from extensions import db

from sqlalchemy import func


import sqlite3

from models import UserSpending
from models import UserInfo
from pymongo import MongoClient

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_vouchers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Create tables at startup
with app.app_context():
    db.create_all()

##
def get_db_connection():
    pass

#vkupna potrosuvacka za korisnik
@app.route('/total_spent/<int:user_id>', methods=['GET'])
def total_spent(user_id): #
    # # SQLAlchemy query za da se dobie vkupniot trosok na korisnikot
    # total_spending = db.session.query(UserSpending.user_id, func.sum(UserSpending.money_spent).label('total_quantity')).group_by(UserSpending.user_id)
    # #total_spending = db.session.query(func.sum(UserSpending.money_spent))\
    #                            #.filter(UserSpending.user_id == user_id).scalar() #funkcija za suma od tabelata user_spending
    #  # i filtriram spored odredeno id

    user_spending = UserSpending.query.filter_by(user_id=user_id).all()
    total_spending = sum([spending.money_spent for spending in user_spending])

    # Ako nema zapisi za toj korisnik da se vrati greska i soodvetna poraka
    if total_spending is None:
        return jsonify({"error": f"No spending data found for user_id {user_id}"}), 404
        #greska 404 so soodvetna poraka

    # Rezultatot se vrakja kako JSON
    return jsonify({"user_id": user_id, "total_spending": total_spending})
             #ako ima odgovor ke go vrati idto i vkupnata potrosuvacka za toj korisnik




#
# #2 end point
# #prosecna potrosuvacka po korisnik
# @app.route('/average_spending_by_age', methods=['GET'])
# def average_spending_by_age():
#     # Definiranje na vozrasni kategorii
#     age_ranges = [
#         (18, 24),
#         (25, 30),
#         (31, 36),
#         (37, 47),
#         (48, 150)  # 150 kako gorna granica za site nad 47 godini
#     ]
#
#     results = []
#
#     for min_age, max_age in age_ranges:
#         # Query za da se presmeta prosecnata potrosuvacka za sekoja kategorija
#         avg_query = (
#             db.session.query(func.avg(UserSpending.money_spent))
#             .join(UserInfo, UserInfo.user_id == UserSpending.user_id) #za da se najde istiot korisnik
#             .filter(UserInfo.age.between(min_age, max_age)) #da se filtrira spored
#         ).scalar()
#
#         results.append({
#             "age_range": f"{min_age}-{max_age if max_age < 150 else '+'}",
#             "average_spending": avg_query if avg_query else 0
#         })
#
#     # da se vrati vo JSON
#     return jsonify(results)
#


#2 end point
#prosecna potrosuvacka po korisnik
@app.route('/average_spending_by_age', methods=['GET'])
def average_spending_by_age():
    # Definiranje na vozrasni kategorii
    age_ranges = [
        (18, 24),
        (25, 30),
        (31, 36),
        (37, 47),
        (48, 150)  # 150 kako gorna granica za site nad 47 godini
    ]

    # da se vrati rezultatot vo forma na recnik, a ne lista bidejki pravi problem so Telegram
    results = {}

    for min_age, max_age in age_ranges:
        # Query za da se presmeta prosecnata potrosuvacka za sekoja kategorija
        avg_query = (
            db.session.query(func.avg(UserSpending.money_spent))
            .join(UserInfo, UserInfo.user_id == UserSpending.user_id) #za da se najde istiot korisnik
            .filter(UserInfo.age.between(min_age, max_age))
        ).scalar()


        age_range_key = f"{min_age}-{max_age if max_age < 150 else '+'}"
        results[age_range_key] = avg_query if avg_query else 0

    # Da se vrati rezultatot vo JSON
    return jsonify(results)

#3 end point
# Konekcija do MongoDB

# client = MongoClient("mongodb://localhost:27017/")
# db = client["users_vouchers"]  # Ime na baza
# collection = db["vouchers"]  # Ime na konekcija

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["users_vouchers"]  # Ime na baza
collection =  mongo_db["vouchers"]  # Ime na konekcija


@app.route('/write_to_mongodb', methods=['POST'])
def write_to_mongodb():
    try:
        # Zemame podatoci od baranjeto
        data = request.get_json()

        # da se zemat vnesenite podatoci, ako ne da se vrati greska so soodvetna poraka
        if not data or "user_id" not in data or "total_spending" not in data:
            return jsonify({"error": "Invalid input. Required fields: user_id, total_spending"}), 400

        user_id = data["user_id"]
        total_spending = data["total_spending"]

        # Da se proveri dali potrosuvackata ja nadminuva granicata, ako ne da se vrati greska so soodvetna poraka
        if total_spending < 1000:
            return jsonify({"error": "Spending does not exceed the required amount"}), 400

        # Vnesuvanje na podatoci vo MongoDB
        document = {"user_id": user_id, "total_spending": total_spending}
        collection.insert_one(document)

        return jsonify({"message": "User data successfully written to MongoDB"}), 201

    except Exception as e:
        # Obrabotka na greski
        return jsonify({"error": str(e)}), 500


# Telegram Bot API token, koj gi dobivame od samata app
TELEGRAM_TOKEN = '7627404850:AAGq__FaH02KchWQK3vCEuhHGFZwmi1XUuI'
# Chat ID kade ke isprakjame poraki
CHAT_ID = '8196067730'

def send_message_to_telegram(message):
    """
    Funkcija za isprakjanje poraka do Telegram koristejki go Bot API
    """
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # Овозможува користење на Markdown за форматирање
    }
    response = requests.post(telegram_url, params=params)

    # Da se proveri dali porakata e uspesno pratena, ako ne da se napise greska so soodvetna poraka
    if response.status_code != 200:
        raise Exception(f"Failed to send message: {response.text}")

@app.route('/send_average_spending_to_telegram', methods=['GET']) #pateka za isprakjanje na poraka do telegram
def send_average_to_telegram():
    try:
        # Se povikuva funkcijata average_spending_by_age
        response = average_spending_by_age()  # treba da se vrati recnik na statistikite sto gi imame implementirano so
        #so funkijata  average_spending_by_age
        average_data = response.get_json()  # da se prezeme JSON objektot

        # Da se proveri dali average_data е dictionay
        if not isinstance(average_data, dict):
            raise ValueError("Invalid data format: Expected a dictionary") #dokolku ne e da se napise poraka so greska

        # Se generira poraka za isprakjanje
        message = "📊 *Average Spending by Age Ranges*:\n"
        for age_range, avg in average_data.items():
            message += f"• Age {age_range}: ${avg:.2f}\n"

        # se isprakja poraka do Telegram
        send_message_to_telegram(message)

        return jsonify({"message": "Message sent successfully to Telegram!"}), 200
        #se isprakja poraka do telegram i se dobiva response 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    #ako toa ne e slucaj se frla exception so greska







if __name__ == '__main__':
    app.run(debug=True)






