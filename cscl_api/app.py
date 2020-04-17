from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
CORS(app, resources={r"/*": {"origins": "*"}})
swagger = Swagger(app)
db = SQLAlchemy(app)

from .models import Book
from flask.json import jsonify

@app.route('/')
def root_view():
    """Endpoint to check api health
    This is using docstrings for specifications.
    ---
    definitions:
      Status:
        type: object
        properties:
          msg:
            type: string             
    responses:
      200:
        description: Api health status
        schema:
          $ref: '#/definitions/Status'
    """
    return jsonify({"msg": "Welcome to Coffee shop"}), 200


#/book/<isbn>
#HTTP Method: GET
@app.route('/book/<string:isbn>', methods=['GET'])
def show_book(isbn):
    """Endpoint for retrieving a book by using its isbn
    This is using docstrings for specifications.
    ---
    parameters:
      - name: isbn
        in: path
        type: string
        required: true
    definitions:
      Book:
        type: object
        properties:
          author:
            type: string
          image_url_l:
            type: string  
          image_url_m:
            type: string
          image_url_s:
            type: string
          isbn:
            type: string
          number_of_copies:
            type: string
          publisher:
            type: string 
          title:
            type: string 
          year_of_publication:
            type: integer             
    responses:
      200:
        description: A book
        schema:
          $ref: '#/definitions/Book'
    """
    book = Book.query.filter_by(isbn=isbn).first()
    return book.to_dict()


#/book?c=10&p=1
#HTTP Method: GET
@app.route('/book', methods=['GET'])
def index_book():
    """Endpoint used for pagianting a list of books
    This is using docstrings for specifications.
    ---
    parameters:
      - name: c
        in: query
        type: integer
        required: true
        description: Number of books returned
      - name: p
        in: query
        type: integer
        required: true 
        description: The offset used to traverse the list of books 
    definitions:
      Status:
        type: object
        properties:
          msg:
            type: string
      Book:
        type: object
        properties:
          author:
            type: string
          image_url_l:
            type: string  
          image_url_m:
            type: string
          image_url_s:
            type: string
          isbn:
            type: string
          number_of_copies:
            type: string
          publisher:
            type: string 
          title:
            type: string 
          year_of_publication:
            type: integer 
      Page:
        type: object
        properties:
          next:
            type: string 
          prev:
            type: string
          result:
            type: array 
            items:
               $ref: '#/definitions/Book'                           
    responses:
      200:
        description: A book
        schema:
          $ref: '#/definitions/Page'  
      400:
        description: Pagination error
        schema:
          $ref: '#/definitions/Status'    
    """
    # to do
    book_count = Book.query.count()
    print(book_count)
    next = None
    prev = None
    c = 10
    p = 1
    try:
        c = int(request.args.get('c'))
        p = int(request.args.get('p'))
    except Exception:
        return jsonify({"msg": "Invalid page params"}), 400
    if p > 1:
        check_prev = p - 1
        if book_count >= c * check_prev:
            prev = request.base_url + "?c=" + str(c) + "&p=" + str(check_prev)
    check_next = p + 1  
    if book_count >= c * check_next:
        next = request.base_url + "?c=" + str(c) + "&p=" + str(check_next)
    try:
        book_list = Book.query.order_by(Book.title.asc()).paginate(p, per_page=c).items
        result = [d.to_dict() for d in book_list]
        return jsonify(result=result, next = next, prev = prev)      
    except Exception:
        return jsonify({"msg": "Pagination error"}), 400  


#/book/<isbn>
#HTTP Method: PUT
#Should mainly be able to update book count but missing field
@app.route('/book', methods=['POST'])
def store_book():
    """Endpoint for creating a book entry
    This is using docstrings for specifications.
    ---
    parameters:
      - name: isbn
        in: body
        type: string
        required: true
      - name: author
        in: body
        type: string
        required: true
      - name: title
        in: body
        type: string
        required: true
      - name: publisher
        in: body
        type: string
        required: true
      - name: image_url_s
        in: body
        type: string
        required: false
      - name: image_url_m
        in: body
        type: string
        required: false
      - name: image_url_l
        in: body
        type: string
        required: false
      - name: number_of_copies
        in: body
        type: integer
        required: true
      - name: year_of_publication
        in: body
        type: integer
        required: true              
    definitions:
      Status:
        type: object
        properties:
          msg:
            type: string
      Book:
        type: object
        properties:
          author:
            type: string
          image_url_l:
            type: string  
          image_url_m:
            type: string
          image_url_s:
            type: string
          isbn:
            type: string
          number_of_copies:
            type: string
          publisher:
            type: string 
          title:
            type: string 
          year_of_publication:
            type: integer             
    responses:
      201:
        description: A book
        schema:
          $ref: '#/definitions/Book'
      400:
        description: Request error
        schema:
          $ref: '#/definitions/Book'    
    """
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
    """Endpoint for updating a book entry
    This is using docstrings for specifications.
    ---
    parameters:
      - name: isbn
        in: path
        type: string
        required: true
      - name: author
        in: body
        type: string
        required: false
      - name: title
        in: body
        type: string
        required: false
      - name: publisher
        in: body
        type: string
        required: false
      - name: image_url_s
        in: body
        type: string
        required: false
      - name: image_url_m
        in: body
        type: string
        required: false
      - name: image_url_l
        in: body
        type: string
        required: false
      - name: number_of_copies
        in: body
        type: integer
        required: false
      - name: year_of_publication
        in: body
        type: integer
        required: false              
    definitions:
      Book:
        type: object
        properties:
          author:
            type: string
          image_url_l:
            type: string  
          image_url_m:
            type: string
          image_url_s:
            type: string
          isbn:
            type: string
          number_of_copies:
            type: string
          publisher:
            type: string 
          title:
            type: string 
          year_of_publication:
            type: integer             
    responses:
      201:
        description: A book
        schema:
          $ref: '#/definitions/Book'
    """
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
    """Endpoint for borrowing a book entry
    This is using docstrings for specifications.
    ---
    parameters:
      - name: isbn
        in: path
        type: string
        required: true
      - name: loans
        in: body
        type: integer
        required: false             
    definitions:
      Status:
        type: object
        properties:
          msg:
            type: string
      Book:
        type: object
        properties:
          author:
            type: string
          image_url_l:
            type: string  
          image_url_m:
            type: string
          image_url_s:
            type: string
          isbn:
            type: string
          number_of_copies:
            type: string
          publisher:
            type: string 
          title:
            type: string 
          year_of_publication:
            type: integer             
    responses:
      201:
        description: A book
        schema:
          $ref: '#/definitions/Book'
      400:
        description: Request error
        schema:
          $ref: '#/definitions/Status'    
    """
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
    """Endpoint for returning a book entry
    This is using docstrings for specifications.
    ---
    parameters:
      - name: isbn
        in: path
        type: string
        required: true
      - name: returns
        in: body
        type: integer
        required: false             
    definitions:
      Book:
        type: object
        properties:
          author:
            type: string
          image_url_l:
            type: string  
          image_url_m:
            type: string
          image_url_s:
            type: string
          isbn:
            type: string
          number_of_copies:
            type: string
          publisher:
            type: string 
          title:
            type: string 
          year_of_publication:
            type: integer             
    responses:
      201:
        description: A book
        schema:
          $ref: '#/definitions/Book'
    """
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
    """Endpoint for deleting a book entry
    This is using docstrings for specifications.
    ---
    parameters:
      - name: isbn
        in: path
        type: string
        required: true            
    definitions:
      Status:
        type: object
        properties:
          msg:
            type: string             
    responses:
      200:
        description: Success msg
        schema:
          $ref: '#/definitions/Status'
      404:
        description: No book found
        schema:
          $ref: '#/definitions/Status'    
    """
    book = Book.query.filter_by(isbn=isbn).all()
    if len(book) > 0:
        for obj in book:
            db.session.delete(obj)
            db.session.commit()
        return jsonify({"msg": "Book deleted"}), 200
    else:
        return jsonify({"msg": "Book does not exist"}), 404    