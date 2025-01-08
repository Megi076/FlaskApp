from flask import Flask, request, jsonify
from extensions import db
from models import Book, Author

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Create tables at startup
with app.app_context():
    db.create_all()


@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    # my_list = []
    # for book in books:
    #     my_list.append(book.to_dict())
    # return jsonify(my_list)
    return jsonify([book.to_dict() for book in books])


@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    # book = Book.query.get(id)
    return jsonify(book.to_dict())


@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    print(data)
    new_book = Book(title=data['title'], author_id=data['author_id'])
    # new_book = Book(**data)
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.to_dict()), 201


@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.get_json()
    print(data)
    book = Book.query.get_or_404(id)

    print("title", data.get('title', book.title))
    print("author", data.get('author', book.author))

    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)

    db.session.commit()
    return jsonify(book.to_dict())


@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})


@app.route('/auhtors', methods=['POST'])
def create_author():
    data = request.get_json()
    print(data)
    new_author = Author(name=data['name'], surname=data['surname'], short_bio=data['short_bio'])
    db.session.add(new_author)
    db.session.commit()
    return jsonify(new_author.to_dict()), 201

if __name__ == '__main__':
    app.run(debug=True)