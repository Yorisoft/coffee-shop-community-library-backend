from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

from .models import Book
from flask.json import jsonify

@app.route('/')
def root_view():
    #book = Book.query.filter_by(isbn='0525947647').all()
    #result = [d.to_dict() for d in book] #book.to_dict()
    return jsonify({"msg": "Welcome to Coffee shop"}), 200


#/book/<isbn>
#HTTP Method: GET
@app.route('/book/<string:isbn>', methods=['GET'])
def show_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    return book.to_dict()

#/book/<isbn>
#HTTP Method: GET
@app.route('/book', methods=['GET'])
def index_book():
    # to do
    c = 10
    p = 1
    try:
        c = int(request.args.get('c'))
        p = int(request.args.get('p'))
    except Exception:
        return jsonify({"msg": "Invalid page params"}), 400
    try:
        book_list = Book.query.order_by(Book.title.asc()).paginate(p, per_page=c).items
        result = [d.to_dict() for d in book_list]
        return jsonify(result=result)      
    except Exception:
        return jsonify({"msg": "Pagination error"}), 400


#/book/<isbn>
#HTTP Method: PUT
#Should mainly be able to update book count but missing field
@app.route('/book', methods=['POST'])
def store_book():
    book = Book(None,None, None,None,None,None,None,None)
    content = request.json
    if 'title' in content and 'year_of_publication' in content and 'isbn' in content and 'author' in content and 'publisher' in content:
        ifExist = Book.query.filter_by(isbn=content['isbn']).all()
        if len(ifExist) != 0:
            return jsonify({"msg": "Isbn already exists"}), 400
        book.title = content['title']
        book.year_of_publication = content['year_of_publication']
        book.isbn = content['isbn']
        book.author = content['author']
        book.publisher = content['publisher']
        if 'image_url_s' in  content:
            book.image_url_s = content['image_url_s']
        if 'image_url_m' in  content:
            book.image_url_m = content['image_url_m']
        if 'image_url_l' in  content:
            book.image_url_l = content['image_url_l']  
        if 'number_of_copies' in  content:
            book.number_of_copies = content['number_of_copies']   
        else:
            book.number_of_copies = 1                   
        db.session.add(book)
        db.session.commit()
        return book.to_dict(), 201
    else:
        return jsonify({"msg": "client error illegal request"}), 400

#/book/<isbn>
#HTTP Method: PUT
#Should mainly be able to update book count but missing field
@app.route('/book/<string:isbn>', methods=['PUT'])
def update_book(isbn):
    update_flag = False
    book = Book.query.filter_by(isbn=isbn).first()
    content = request.json
    if 'title' in content:
        book.title = content['title']
        update_flag = True
    if 'year_of_publication' in content:
        book.year_of_publication = content['year_of_publication']
        update_flag = True
    if update_flag:    
        db.session.commit()
    return book.to_dict()


#/book/<isbn>
#HTTP Method: PUT
#Should mainly be able to update book count but missing field
@app.route('/inventory/loan/book/<string:isbn>', methods=['PUT'])
def inventory_loan_book(isbn):
    update_flag = False
    book = Book.query.filter_by(isbn=isbn).first()
    content = request.json
    
    if 'loans' in content:
        if book.number_of_copies == 0 and book.number_of_copies >= content['loans']:
            return jsonify({"msg": "No books available"}), 400
        if book.number_of_copies < content['loans']:
            return jsonify({"msg": "You cant borrow more books than we have"}), 400    
        
        update_copies_count = book.number_of_copies - content['loans']
        book.number_of_copies = update_copies_count
        update_flag = True
    if update_flag:    
        db.session.commit()
    return book.to_dict()

#/book/<isbn>
#HTTP Method: PUT
#Should mainly be able to update book count but missing field
@app.route('/inventory/return/book/<string:isbn>', methods=['PUT'])
def inventory_return_book(isbn):
    update_flag = False
    book = Book.query.filter_by(isbn=isbn).first()
    content = request.json
    if 'returns' in content:
        update_copies_count = book.number_of_copies + content['returns']
        book.number_of_copies = update_copies_count
        update_flag = True
    if update_flag:    
        db.session.commit()
    return book.to_dict()    



 #/book/<isbn>
#HTTP Method: PUT
#Should mainly be able to update book count but missing field
@app.route('/book/<string:isbn>', methods=['DELETE'])
def delete_book(isbn):
    book = Book.query.filter_by(isbn=isbn).all()
    if len(book) > 0:
        for obj in book:
            db.session.delete(obj)
            db.session.commit()
        return jsonify({"msg": "Book deleted"}), 200
    else:
        return jsonify({"msg": "Book does not exist"}), 404     