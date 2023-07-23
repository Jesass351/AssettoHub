from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from app import db, app
from models import User, Setup, SetupStat
from tools import JSONSaver
from sqlalchemy import update, delete
from flask_login import login_required, current_user
import bleach
from sqlalchemy import exc
from auth import check_rights
import markdown
import os
import json

bp = Blueprint('user', __name__, url_prefix='/user')

USER_PARAMS = [
    'time', 'description', 'car_id', 'track_id', 'condition_track', 'condition_air', 'title'
]

def params():
    return { p: request.form.get(p) for p in USER_PARAMS }
    
# @bp.route('/edit/<int:bookID>')
# @login_required
# @check_rights('edit_book')
# def edit(bookID):
#     try:
#         book = db.session.execute(db.select(Book).filter_by(bookID=bookID)).scalar()
#         genres = db.session.execute(db.select(Genre)).scalars()
        
#     except exc.SQLAlchemyError as error:
#         flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    
#     return render_template('books/edit_book.html',book=book, genres=genres)
    
# @bp.route('/edit_post/<int:bookID>', methods=['POST'])
# @login_required
# @check_rights('edit_book')
# def edit_post(bookID):
#     try:
#         params_from_form = params()
#         for param in params_from_form:
#             param = bleach.clean(param)
            
#         book = Book(**params_from_form)
#         db.session.query(Book).filter(Book.bookID == bookID).update({
#             'title': book.title,
#             'desc': book.desc,
#             'year_writing': book.year_writing,
#             'publishing': book.publishing,
#             'author': book.author,
#             'pages': book.pages
#             })
        

#         db.session.query(Books_Genres).filter(Books_Genres.book_id == bookID).delete()
        
#         db.session.commit()
#         genres_form = request.form.getlist("genre")
        
#         for genre in genres_form:
#             db.session.add(Books_Genres(**{'book_id':bookID,'genre_id': genre}))
#         db.session.commit()

        
#         flash('Запись успешно изменена','success')
#     except exc.SQLAlchemyError as error:
#         flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
#         db.session.rollback()
#     return redirect(url_for('books.show', bookID = bookID))

@bp.route('/create')
# @login_required
# @check_rights('create_book')
def create():
    cars = db.session.execute(db.select(Car)).scalars()
    tracks = db.session.execute(db.select(Track)).scalars()
    return render_template('setups/add_setup.html',cars=cars, tracks=tracks)
    
@bp.route('/delete_post/<int:bookID>', methods=['POST'])
@login_required
@check_rights('delete_book')
def delete_post(bookID):
    try:
        book = db.session.execute(db.select(Book).filter(Book.bookID == bookID)).scalar()
        if Book.query.filter_by(cover_id=book.cover_id).count() == 1:
            image = db.session.execute(db.select(Image).filter(Image.id == book.cover_id)).scalar()
            os.remove(
            os.path.join(app.config['UPLOAD_FOLDER'],
                         image.storage_filename))
            db.session.query(Image).filter(Image.id == book.cover_id).delete()
                        
        db.session.query(Book).filter(Book.bookID == bookID).delete()
        db.session.query(Reviews).filter(Reviews.book_id == bookID).delete()
        db.session.query(Books_Genres).filter(Books_Genres.book_id == bookID).delete()
        db.session.query(Books_Compilations).filter(Books_Compilations.book_id == bookID).delete()
    
        db.session.commit()
        flash('Запись успешно удалена', 'success')
    except:
        db.session.rollback()
        flash('Ошибка при удалении', 'danger')
    return redirect(url_for('index'))

@bp.route('/create_post', methods=['POST'])
@login_required
# @check_rights('create_book')
def create_post():
    # try:
        f = request.files.get('setup_file')
    
        if f and f.filename:
            setup_file = JSONSaver(f).save()
        
        params_from_form = params()
        for param in params_from_form:
            param = bleach.clean(param)
            
        params_from_form['author_id'] = current_user.id
            
        setup = Setup(**params_from_form)
        if f:
            setup.file_id = setup_file.id


        db.session.add(setup)
        db.session.commit()
        

        # for genre in genres_form:
        #     db.session.add(Books_Genres(**{'book_id':book.bookID,'genre_id': genre}))
        # db.session.commit()

        flash(f'Настройка была успешно добавлена', 'success')
        return redirect(url_for('index'))
        
    # except exc.SQLAlchemyError as error:
    #     db.session.rollback()
    #     flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    #     return redirect(url_for('index'))
        
@bp.route('like/<int:setupID>')
def like(setupID):
    db.session.add(SetupStat(**{'user_id':current_user.id,'setup_id': setupID, 'action_id':app.config['SETUP_ACTIONS'].get('like', 2)}))
    db.session.commit()
    return redirect(url_for('setups.show', setupID=setupID))

@bp.route('profile')
@login_required
def profile():
    setups = db.session.execute(db.select(Setup).filter_by(author_id=current_user.id)).scalars()
    return render_template('user/profile.html', setups=setups)
        
