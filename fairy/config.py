# файл конфигурации проекта
import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)


class Config:
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = config.get('SECRET_KEY')
    SECRET_KEY_FOR_TOKEN = config.get('SECRET_KEY_FOR_TOKEN')

    MAIL_SERVER = 'smtp.mail.ru'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    MAIL_USERNAME = config.get('MAIL_USERNAME')
    MAIL_PASSWORD = config.get('MAIL_PASSWORD')
    FLASKY_ADMIN = config.get('FLASKY_ADMIN')
    FLASKY_MAIL_SENDER = config.get('FLASKY_MAIL_SENDER')
    FLASKY_MAIL_SUBJECT_PREFIX = 'Проект ФЕЯ: '

    ######################################
    # папка загрузки файлов открыток
    UPLOAD_FOLDER = 'static/uploads/'
    MAX_CONTENT_LENGTH = 1024 * 1024  # максимальный размер файла 1МБ
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

    RECAPTCHA_PUBLIC_KEY = config.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = config.get('RECAPTCHA_PRIVATE_KEY')
