import os

SECRET_KEY = 'os.urandom(12).hex()'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_2033_assetto:NANO@std-mysql.ist.mospolytech.ru/std_2033_assetto'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

ADMIN_ROLE_ID = 1
MODER_ROLE_ID = 2
USER_ROLE_ID = 3

SETUP_ACTIONS = {
    'download': 1,
    'like': 2
}

MAX_CONTENT_LENGTH = 0.5 * 1024 * 1024

SETUPS_PER_PAGE_INDEX = 10
SETUPS_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'files')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')

CAR_IMAGES = {
    'BMW M4':'m4_default.jpg',
    'Aston Martin V8': 'aston_martin_v8_default.jpg'
}
