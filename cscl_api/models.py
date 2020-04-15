from .app import db
from sqlalchemy_serializer import SerializerMixin

class Book(db.Model, SerializerMixin):

    __tablename__ = 'books'
    
    isbn = db.Column(db.String(13), primary_key=True, nullable=False)
    title = db.Column(db.String(255), unique=False, nullable=True)
    author = db.Column(db.String(255), unique=False, nullable=True)
    year_of_publication = db.Column(db.Integer, nullable=True)
    publisher = db.Column(db.String(255), unique=False, nullable=True)
    image_url_s = db.Column(db.String(255), unique=False, nullable=True)
    image_url_m = db.Column(db.String(255), unique=False, nullable=True)
    image_url_l = db.Column(db.String(255), unique=False, nullable=True)
    number_of_copies = db.Column(db.Integer, nullable=True, default=1)

    def __init__(self, isbn, title, author, year_of_publication, publisher, 
                    image_url_s, image_url_m, image_url_l, number_of_copies):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year_of_publication = year_of_publication
        self.publisher = publisher
        self.image_url_s = image_url_s
        self.image_url_m = image_url_m
        self.image_url_l = image_url_l
        self.number_of_copies = number_of_copies

    def __repr__(self):
        return '<Book %r>' % self.isbn