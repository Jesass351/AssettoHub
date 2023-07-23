from flask import Flask, render_template, request, send_from_directory, flash
from sqlalchemy import MetaData, desc
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import math
import markdown
import os

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
from setups import bp as setups_bp
from user import bp as users_bp

app.register_blueprint(auth_bp)
app.register_blueprint(setups_bp)
app.register_blueprint(users_bp)

init_login_manager(app)

from models import Setup, Car, Track
from tools import filtered_setups

def search_params():
    return {
        'car_id': request.args.get('car'),
        'track_id': request.args.get('track'),
    }

@app.route('/')
def index():
    setups = db.session.execute(filtered_setups(search_params())).scalars()

    cars = db.session.execute(db.select(Car)).scalars()
    tracks = db.session.execute(db.select(Track)).scalars()
    
    
    # try:
        # page = request.args.get('page', 1, type=int)
        
        # db_books = db.session.execute(db.select(Book).order_by(desc(Book.year_writing)).limit(app.config['BOOKS_PER_PAGE_INDEX']).offset(app.config['BOOKS_PER_PAGE_INDEX'] * (page - 1))).scalars()
        # books = []
        # for book in db_books:
        #     book.desc = markdown.markdown(book.desc)
        #     books.append(book)
        # book_count = Book.query.count()
        # page_count = math.ceil(book_count / app.config['BOOKS_PER_PAGE_INDEX'])
                
    #     return render_template(
    #         'index.html',
    #         # books = books,
    #         # page = page,
    #         # page_count = page_count
    #     )
    # except:
        # flash("При загрузке данных произошла ошибка",'danger')
    # flash("При загрузке данных произошла ошибка",'danger')
    return render_template(
    'index.html',
    books = [],
    page = 1,
    page_count = 1,
    
    setups=setups,
    cars=cars,
    tracks=tracks,
    search_params = search_params()
    )

# @app.route('/images/<image_id>')
# def image(image_id):
#     img = db.get_or_404(Image, image_id)
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                img.storage_filename)
