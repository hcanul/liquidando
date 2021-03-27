from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(100))
    email = db.Column(db.String(80), unique=True)
    privilegios = db.Column(db.String(20))
    nombre = db.Column(db.String(80))
    psw_recupera = db.Column(db.String(12))
    sol_recupera = db.Column(db.Boolean)
    plan_tarifa = db.Column(db.Integer)
    contador = db.Column(db.Integer)
    enlinea = db.Column(db.Boolean(1))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    update_on = db.Column(db.DateTime, default=db.func.current_timestamp(),
                                       onupdate=db.func.current_timestamp())

    def __init__(self, password, email, privilegios, nombre, psw_recupera, sol_recupera, plan_tarifa, contador, enlinea):
        self.password = self.__crate_password(password)
        self.email = email
        self.privilegios = privilegios
        self.nombre = nombre
        self.psw_recupera = psw_recupera
        self.sol_recupera = sol_recupera
        self.plan_tarifa = plan_tarifa
        self.contador = contador
        self.enlinea = enlinea

    def __crate_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class Tasas(db.Model):
    __tablename__ = 'TazaInteres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False)
    bc_ea = db.Column(db.Float(16,8), nullable=False)
    bc_mensual = db.Column(db.Float(16,8), nullable=False)
    usura_ea = db.Column(db.Float(16,8), nullable=False)
    usura_men = db.Column(db.Float(16,8), nullable=False)
    ipc = db.Column(db.Float, nullable=False)

    def __init__(self, fecha, bc_ea, bc_mensual, usura_ea, usura_men, ipc):
        self.fecha = fecha
        self.bc_ea = bc_ea
        self.bc_mensual = bc_mensual
        self.usura_ea = usura_ea
        self.usura_men = usura_men
        self.ipc = ipc

class Abono(db.Model):
    __tablename__ = 'abonos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_caso = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date)
    monto = db.Column(db.Float(20,2), nullable=False)


class Caso(db.Model):
    __tablename__ = 'casos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    num_proceso = db.Column(db.String(15))
    demandante = db.Column(db.String(150))
    demandado = db.Column(db.String(150))
    juzgado = db.Column(db.String(150))
    c_inicial = db.Column(db.Float(16,2))
    fecha_inicial = db.Column(db.Date)
    fecha_final = db.Column(db.Date)
    otra = db.Column(db.Boolean)
    tasa = db.Column(db.String(15))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    Resul_Calculo = relationship("Resul_Calculo")
    Desglose = relationship("Desglose")

    def __init__(self, user_id, num_proceso, demandante, demandado, juzgado,c_inicial, fecha_inicial, fecha_final, otra, tasa):
        self.user_id = user_id
        self.num_proceso = num_proceso
        self.demandante = demandante
        self.demandado = demandado
        self.juzgado = juzgado
        self.c_inicial = c_inicial
        self.fecha_inicial = fecha_inicial
        self.fecha_final = fecha_final
        self.otra = otra
        self.tasa = tasa


class Resul_Calculo(db.Model):
    __tablename__ = 'ListaCalculos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    casos_id = db.Column(db.Integer, db.ForeignKey('casos.id'))
    fecha = db.Column(db.Date)
    tasa = db.Column(db.Float(10,4))
    interes = db.Column(db.Float(10,4))
    total = db.Column(db.Float(25,4))
    capital = db.Column(db.Float(25,4))

    def __init__(self, casos_id, fecha, tasa, interes, total, capital):
        self.casos_id = casos_id
        self.fecha = fecha
        self.tasa = tasa
        self.interes = interes
        self.total = total
        self.capital = capital


class Desglose(db.Model):
    __tablename__ = 'Desgloses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    casos_id = db.Column(db.Integer, db.ForeignKey('casos.id'))
    periodo = db.Column(db.Integer)
    di = db.Column(db.Integer)
    idi = db.Column(db.Float(25,4))
    df = db.Column(db.Integer)
    idf = db.Column(db.Float(25,4))

    def __init__(self, casos_id, periodo,di,idi,df,idf):
        self.casos_id = casos_id
        self.periodo = periodo
        self.di = di
        self.idi = idi
        self.df = df
        self.idf = idf

