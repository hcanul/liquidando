####################################################
################## Liquidando ######################
####################################################
from flask import Flask, request,  jsonify, session, render_template, make_response, send_file, send_from_directory
from config import DevelopmentConfig
import datetime
from datetime import date, timedelta
import sys

from pandas import ExcelFile
from xlsxwriter.workbook import Workbook
from xlsxwriter.utility import xl_range
from xlsxwriter.utility import xl_rowcol_to_cell
from numpy.random import randint


import json
from functools import lru_cache
from sqlalchemy.sql import func, desc
####### importaciones locales#####
from models import db, User, Tasas, Abono
from tools.envioCorreo import correo
from tools.recuperame import otroProceso
from tools.fechaMY import fechaMA
from tools.calculo import Amortiza
###########################################
############ nuevo intento ################
import base64
from io import BytesIO
import io
import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.writer.excel import save_virtual_workbook
###########################################
import pymysql
pymysql.install_as_MySQLdb()
###########################################
######## Libreria para el API ############
from flask_cors import CORS
import json
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)
cors = CORS(app, resources={ r"/api/*":{"origins":"*"}})
app.config.from_object(DevelopmentConfig)
jwt = JWTManager(app)



@app.route("/api/login", methods=['POST'])
def login():
	usr = request.get_json()['user']
	psw = request.get_json()['psw']
	print(usr)
	result=""
	user = User.query.filter_by(email=usr).first()
	if user is not None:
		if user.sol_recupera == 0:
			if user is not None and user.verify_password(psw):
				access_token = create_access_token(identity = {'nombre':user.nombre, 'privilegios':user.privilegios, 'plan':user.plan_tarifa, 'id': user.id, }, expires_delta=datetime.timedelta(minutes=480))
				result = access_token, 200
				print(result)
			else:
				result = jsonify({'error':"Datos Invalidos"})
		else:
			if user is not None and user.password==psw:
				access_token = create_access_token(identity = {'nombre':user.nombre, 'privilegios':user.privilegios, 'plan':user.plan_tarifa, 'id': user.id, }, expires_delta=datetime.timedelta(minutes=480))
				result = access_token
			else:
				result = jsonify({'error':"cambio"})
	else:
		result = jsonify({'error':"Datos Invalidos"})
	return result


@app.route("/api/usuarios/registro", methods=['POST'])
def registro():
	data = request.json
	print(data['dataUser'], data['dataPago'])
	user = User.query.filter_by(email=data['dataUser'][3]).first()
	if user :
		if user.email == data['dataUser'][3]:
			return jsonify({'data':1}) # El Correo existe en la base de datos
		else:
			return jsonify({'data':2}) # El usuario esta ocupado por otro usuario
	else:
		tarifa = 0
		conta = 0
		if data['dataUser'][4] == "PRUEBA":
			tarifa = 0
			contador = 1
			priv="0.0.0.0.1"
		elif data['dataUser'][4] == 'BASICO':
			tarifa = 1
			contador = 10
			priv = "0.0.0.1.1"
		else:
			tarifa = 2
			contador = 30
			priv = "0.0.1.1.1"
		x = correo(data['dataUser'][3], data['dataUser'][1], fechaMA(), data['dataUser'][3], tarifa)
		if x == "Exito":
			registr_usuario = User(
				password = data['dataUser'][1],
				email = data['dataUser'][3],
				privilegios = priv,
				nombre = data['dataUser'][2],
				psw_recupera = "",
				sol_recupera = 0,
				plan_tarifa = tarifa,
				contador = contador,
				enlinea = 0,
			)
			db.session.add(registr_usuario)
			db.session.commit()
			return {'data':0}, 200
		else:
			return {'data':5}, 500


#########################
### debo convertirlo a una funcion y llamarla con los parametros requeridos
@app.route("/api/amortizacion/calculo", methods=['POST'])
@jwt_required
def amortiza():
	### si es liquidacion convencional
	if request.json[1] == 0:
		if len(request.json[0]) == 9:
			data = [request.json[0][0],request.json[0][4],request.json[0][5],request.json[0][6],request.json[0][7],request.json[0][8]]
			return jsonify(Amortiza.amortiza(data)),200
		elif len(request.json[0]) == 8:
			data = [request.json[0][0],request.json[0][4],request.json[0][5],request.json[0][6],request.json[0][7]]
			return jsonify(Amortiza.amortiza(data)),200
	### si es liquidacion rapida
	elif request.json[1] == 1:
		return jsonify(Amortiza.amortiza(request.json[0])),200


@app.route("/api/amortizacion/calculo", methods=['PUT'])
@jwt_required
def saveAmortiza():
	return Amortiza.saveAmortiza(request.json)

@app.route("/api/amortizacion/abonos", methods=['POST'])
@jwt_required
def abonos():
	data = request.json
	if data[2]=="0":
		for item in data[1]:
			abonos = Abono(
					num_caso=data[0],
					fecha=item['fecha'],
					monto=float(item['monto'])
				)
			db.session.add(abonos)
			db.session.commit()
		return jsonify({'data':"exito"})
	elif data[2]=="1":
		for item in data[1]:
			abonos = Abono(
					num_caso=data[0],
					fecha=item['fecha'],
					monto=float(item['monto'])*(-1)
				)
			db.session.add(abonos)
			db.session.commit()
		return jsonify({'data':"exito"})

@app.route("/api/lista/tasas", methods=['GET'])
@jwt_required
def tasas():
	result = db.session.query(Tasas).order_by(desc(Tasas.id)).first()
	lista=[]
	lista2=[]
	today = date.today()
	mes = today.month if (len(str(today.month)) == 2) else "0"+str(today.month)
	anio = today.year # le reste uno pra poder obtener los datos del año 2019
	resulFechasIPC = db.session.query(Tasas.bc_ea).filter(Tasas.fecha.between(str(anio)+'-01-01', str(anio)+'-12-01')).all()
	resulFechasBC = db.session.query(Tasas.bc_mensual).filter(Tasas.fecha.between(str(anio)+'-01-01', str(anio)+'-12-01')).all()
	print(result.fecha,mes)
	if str(result.fecha)[5:7] == str(mes):
		print(result.fecha,mes) 
		if str(result.fecha)[:4] == str(anio):
			lista = [str(result.fecha),
				str((result.bc_ea)*100)[:7],
				str((result.bc_mensual)*100)[:7],
				str((result.usura_ea)*100)[:7],
				str((result.usura_men)*100)[:7],
				str((result.ipc)*100)[:7]]
			lista2 = [(float(x[0])*100) for x in resulFechasIPC] # lleno las listas para la grafica1
			lista3 = [(float(x[0])*100) for x in resulFechasBC] # lleno las listas para la grafica2
	else:
		lista = ["Sin Datos",
			"Sin Datos",
			"Sin Datos",
			"Sin Datos",
			"Sin Datos",
			"Sin Datos",]
		lista2 = [(float(x[0])*100) for x in resulFechasIPC]
		lista3 = [(float(x[0])*100) for x in resulFechasBC]

	lista3=[]
	return jsonify({'data':[lista, lista2,lista3]})


@app.route("/api/recupera", methods=['POST'])
@jwt_required
def recupera():
	result = User.query.filter_by(email = data['email']).first()
	if result == None:
		return jsonify({'data':False})
	else:
		x = otroProceso(passw=data['psw'], fecha=fechaMA(), correo=data['email'])
		if x=="Exito":
			result.psw_recupera = data['psw']
			result.sol_recupera = True
			db.session.commit()
			return jsonify({'data':True})
		else:
			return jsonify({'data':False})


@app.route("/api/recibe/archivo/excel", methods=['POST'])
@jwt_required
def uploadExcel():
	if request.method == 'POST':
		try:
			archivo = request.files['file'].stream.read()
			toread = io.BytesIO(archivo)
		except ValueError as e:
			return jsonify({'data':e}),500
		try:
			df = pd.read_excel(toread, 'Hoja1', skiprows=[0,1,2,3,4,5])
			df2 = pd.read_excel(toread, 'Hoja2', skiprows=[0,1,2,3,4,5])
		except ValueError as e:
			return jsonify({'data':e}),500
		datos = request.form['id']
		plan = User.query.filter_by(id = int(datos)).first()
		
		df1_columnas = ['Radicado del Proceso', 'Demandante', 'Demandado', 'Juzgado', 'Capital o Monto Inicial', 'Fecha inicial (AAAA-MM-DD)', 'Fecha final  (AAAA-MM-DD)', 'tasa convenida']
		
		######### Comparar dos listas #############
		comparacio = [item for item in df.columns if item in df1_columnas]
		if len(comparacio) < 8:
			return jsonify({'data':'Lo Sentimos Su archivo tiene un formato distinto, intente de nuevo descargando la plantilla, Gracias'}), 200
		##########################################
		
		#df2_columnas = df2.columns #['Radicado del Proceso', 'Fecha (AAAA-MM-DD)', 'Abono', 'Capitalizaciones']
		## listo para implentar el codigo de ivan
		df1_seleccionados = df[df.columns] # seleccionamos las columnas por nombre de cabeceras
		df2_seleccionados = df2[df2.columns]
		if plan.plan_tarifa == 2 and plan.contador>0:    
			df1_seleccionados = df[df.columns] # seleccionamos las columnas por nombre de cabeceras
			df2_seleccionados = df2[df2.columns]
			print(df1_seleccionados)
			# iloc selecciona un numero de filas o columnas sintaxis df.iloc[0:10,0:5] df.iloc[<inicio:fin> filas, <inicio:fin> columnas]
			###### falta la funcionalidad con la funcion que enviara ivan #######
			return jsonify({'data':"Exito"})
		elif plan.plan_tarifa == 1 and plan.contador>0:
			print(df1_seleccionados.iloc[:plan.contador])
			print(df2_seleccionados.describe())
			return jsonify({'data':"Exito"})
		elif plan.plan_tarifa == 0 and plan.contador==1:
			print(df1_seleccionados.iloc[:plan.contador])
			print(df2_seleccionados.describe())
			return jsonify({'data':"Exito"})
		else:
			return jsonify({'data':'Lo Sentimos Creditos insuficientes, contrata de nuevo!, Gracias'}), 200


@app.route("/api/historia/listado/<data>", methods=['GET'])
@jwt_required
def listHistorial(data):
	return Amortiza.historial(data)

@app.route("/api/historia/listado/impresion/<data>", methods=['GET'])
@jwt_required
def printPDF(data):
	return Amortiza.imprimirPDF(data)


@app.route('/api/amortizacion/lotes/plantilla', methods=['GET'])
@jwt_required
def envioExcel():
	excel = os.path.join(app.config["UPLOAD_FOLDER"] + '/excel', 'plantilla.xlsx')
	return send_file(excel, attachment_filename="plantilla.xlsx", as_attachment=True),200


@app.route('/api/reportes/historia/excel/<data>', methods=['GET'])
@jwt_required
def printExcel(data):
	ruta_image = os.path.join(app.config["IMAGES_FOLDER"], 'image92.png')
	file_excel = Amortiza.exportExcel(data, ruta_image)
	return send_file(file_excel, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',attachment_filename='xxl.xlsx', as_attachment=True), 200


@app.route('/api/admin/captura/tazas', methods=['POST'])
@jwt_required
def capturaTazas():
	data = request.json
	hacer = Amortiza()
	result = hacer.AdminTazas(data)
	return result

if __name__ == '__main__':
	db.init_app(app)
	with app.app_context():
		db.create_all()
	app.run( port=7550, host='0.0.0.0')