import os


class Config(object):
	SECRET_KEY = '7q%3=;8J+X5:f.+pU9e!;6x:E*n_9^Ky0~.R'
	JWT_SECRET_KEY = '7q%3=;8J+X5:f.+pU9e!;6x:E*n_9^Ky0~.R#$&GF(/)RGFHJ*[[[*>!!##$%|@·~·@~¬½~[¬{'


class DevelopmentConfig(Config):
    DEBUG = True
    # Produccion
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@dbase/liquidando"
    # Desarrollo
    # SQLALCHEMY_DATABASE_URI = "mysql://root:ha260182ha@localhost/liquidando" #'mysql://root:ha260182ha@localhost/humanos'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.abspath("static/uploads/")
    IMAGES_FOLDER = os.path.abspath("static/img/")