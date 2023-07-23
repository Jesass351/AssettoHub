from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from app import db, app
from models import Setup, Car, Track, SetupStat, SetupFile
from tools import JSONSaver
from sqlalchemy import update, delete
from flask_login import login_required, current_user
import bleach
from sqlalchemy import exc
from auth import check_rights
import markdown
import os
import json

bp = Blueprint('setups', __name__, url_prefix='/setups')

PER_PAGE = 10

BMW_M4_DATA = {
    'wheel_rate':[90000, 120000, 144000],
    'bump_stop_up':[],
    'bump_stop_down':[],
    'max_bb':56,
    'max_toe':1,
    'max_camber':5,
    'preload':[20,40],
    'toe_min_front':-0.2,
    'toe_min_rear':0,
    'camber_min_front':-4,
    'camber_min_rear':-4,
    'caster_min':8,
    'min_bp':80,
    'min_bb':53,
    
    
}

ASTON_MARTIN_V8_DATA = {
    'wheel_rate':[90000, 120000, 144000],
    'bump_stop_up':[],
    'bump_stop_down':[],
    'max_bb':56,
    'max_toe':1,
    'max_camber':5,
    'preload':[20,40],
    'toe_min_front':-0.2,
    'toe_min_rear':0,
    'camber_min_front':-4,
    'camber_min_rear':-4,
    'caster_min':8,
    'min_bp':80,
    'min_bb':53,
}

CARS_DATA = {
    'BMW M4': BMW_M4_DATA,
    'Aston Martin V8': ASTON_MARTIN_V8_DATA
}
    

SETUP_PARAMS = [
    'time', 'description', 'car_id', 'track_id', 'condition_track', 'condition_air', 'title'
]

def params():
    return { p: request.form.get(p) for p in SETUP_PARAMS }
    
@bp.route('/edit/<int:setupID>')
@login_required
# @check_rights('edit_book')
def edit(setupID):
    try:
        setup = db.session.execute(db.select(Setup).filter_by(id=setupID)).scalar()
        cars = db.session.execute(db.select(Car)).scalars()
        tracks = db.session.execute(db.select(Track)).scalars()
    except exc.SQLAlchemyError as error:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    
    return render_template('setups/edit_setup.html',setup=setup, cars=cars, tracks=tracks)
    
@bp.route('/edit_post/<int:setupID>', methods=['POST'])
@login_required
# @check_rights('setupID')
def edit_post(setupID):
    try:
        params_from_form = params()
        for param in params_from_form:
            param = bleach.clean(param)
            
        book = Book(**params_from_form)
        db.session.query(Book).filter(Book.bookID == bookID).update({
            'title': book.title,
            'desc': book.desc,
            'year_writing': book.year_writing,
            'publishing': book.publishing,
            'author': book.author,
            'pages': book.pages
            })
        db.session.query(Books_Genres).filter(Books_Genres.book_id == bookID).delete()
        
        db.session.commit()
        genres_form = request.form.getlist("genre")
        
        for genre in genres_form:
            db.session.add(Books_Genres(**{'book_id':bookID,'genre_id': genre}))
        db.session.commit()

        
        flash('Запись успешно изменена','success')
    except exc.SQLAlchemyError as error:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        db.session.rollback()
    return redirect(url_for('books.show', bookID = bookID))

@bp.route('/create')
# @login_required
# @check_rights('create_book')
def create():
    cars = db.session.execute(db.select(Car)).scalars()
    tracks = db.session.execute(db.select(Track)).scalars()
    return render_template('setups/add_setup.html',cars=cars, tracks=tracks)
    
@bp.route('/delete/<int:setupID>', methods=['POST'])
@login_required
# @check_rights('delete_book')
def delete_post(setupID):
    # try:
        setup = db.session.execute(db.select(Setup).filter_by(id = setupID)).scalar()
        if Setup.query.filter_by(file_id=setup.file_id).count() == 1:
            file = db.session.execute(db.select(SetupFile).filter_by(id = setup.file_id)).scalar()
            os.remove(f'media/files/{setup.file_id}.json')
            db.session.query(SetupFile).filter_by(id = setup.file_id).delete()

        db.session.query(Setup).filter_by(id = setupID).delete()
        db.session.query(SetupStat).filter_by(setup_id = setupID).delete()
    
        db.session.commit()
        flash('Запись успешно удалена', 'success')
        return redirect(url_for('user.profile'))
    # except:
    #     db.session.rollback()
    #     flash('Ошибка при удалении', 'danger')
    # return redirect(url_for('index'))

@bp.route('/create_post', methods=['POST'])
@login_required
# @check_rights('create_book')
def create_post():
    # try:
        f = request.files.get('setup_file')
    
        if f and f.filename:
            setup_file = JSONSaver(f).save()
        if setup_file is None:
            flash('Проверьте файл (загружен не .json)')
            return redirect(url_for('index'))

        
        params_from_form = params()
        for param in params_from_form:
            param = bleach.clean(param)
            
        params_from_form['author_id'] = current_user.id
            
        setup = Setup(**params_from_form)
        if f:
            setup.file_id = setup_file.id
        db.session.add(setup)
        db.session.commit()
        flash(f'Настройка была успешно добавлена', 'success')
        return redirect(url_for('index'))
        
@bp.route('like/<int:setupID>')
def like(setupID):
    db.session.add(SetupStat(**{'user_id':current_user.id,'setup_id': setupID, 'action_id':app.config['SETUP_ACTIONS'].get('like', 2)}))
    db.session.commit()
    return redirect(url_for('setups.show', setupID=setupID))

@bp.route('/<int:setupID>')
def show(setupID):
    setup = db.session.execute(db.select(Setup).filter_by(id=setupID)).scalar()
    with open(f'media/files/{setup.file_id}.json', 'r', encoding='utf-8') as f: #открыли файл
        file = json.load(f)
    download_status = False
    if request.args.get('download_json'):
        download_status = True
    if download_status:
        path = f'media/files/{setup.file_id}.json'
        if current_user.is_authenticated:
            if current_user.check_already_action(setupID, app.config['SETUP_ACTIONS'].get('download', 1)):
                db.session.add(SetupStat(**{'user_id':current_user.id,'setup_id': setup.id, 'action_id':app.config['SETUP_ACTIONS'].get('download', 1)}))
                db.session.commit()
        return send_file(path, as_attachment=True, download_name=f'{setup.get_car()}_{setup.get_track()}_{setup.time}_{setup.condition_track}_{setup.condition_air}.json', mimetype="application/json")
    car_data = CARS_DATA.get(setup.get_car(), '')
    return render_template('setups/show_setup.html', setup=setup, file=file, car_data=car_data)
        