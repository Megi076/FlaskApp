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

    results = []

    for min_age, max_age in age_ranges:
        # Query za da se presmeta prosecnata potrosuvacka za sekoja kategorija
        avg_query = (
            db.session.query(func.avg(UserSpending.money_spent))
            .join(UserInfo, UserInfo.user_id == UserSpending.user_id) #za da se najde istiot korisnik
            .filter(UserInfo.age.between(min_age, max_age)) #da se filtrira spored
        ).scalar()

        results.append({
            "age_range": f"{min_age}-{max_age if max_age < 150 else '+'}",
            "average_spending": avg_query if avg_query else 0
        })

    # da se vrati vo JSON
    return jsonify(results)


#3 end point
# Konekcija do MongoDB

client = MongoClient("mongodb://localhost:27017/")
db = client["users_vouchers"]  # Ime na baza
collection = db["vouchers"]  # Ime na konekcija


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




if __name__ == '__main__':
    app.run(debug=True)






