from array import array
import numpy as np
import pandas as pd
import calendar 
from calendar import monthrange
from datetime import date, timedelta
import datetime
import time
from models import db, Caso, Tasas, Abono, Resul_Calculo, Desglose, User
from flask import jsonify
from sqlalchemy.sql import func, desc, extract
from .herramientas import Herramientas
from reportes.impGral import printListaInt
from reportes.toExcel import Export

class Amortiza():
	def amortiza(data):
		lista3={}
		lisa3=[]
		lista=[]
		intereses_dias_iniciales=0
		intereses_dias_finales=0
		total_intereses_mensuales=0
		total_intereses=0
		Total=0
		per = 0
		monto = []
		intereses_periodo = []
		tasas_df = []
		abonos_df =[]
		fechas_df =[]
		df_complemento = []
		df = []
		
		tasas = Tasas.query.all()
		abon = Abono.query.filter_by(num_caso=data[0]).all()

		lista_tasa=[]
		lista_abono=[]

		tasa = data[4]

		if tasa=="OTRA":
			tasa_entry = '4'
			tasa=float(data[5])/100
		elif tasa=='BC_MENSUAL':
			tasa_entry='1'
		elif tasa=='IPC':
			tasa_entry='2'
		elif tasa=='USURA_MEN':
			tasa_entry='3'

		year, month, day = map(int, data[2].split('-'))
		fecha_inicial = datetime.date(year, month, day)
		year, month, day = map(int, data[3].split('-'))
		fecha_final = datetime.date(year, month, day)

		monto.append(float(data[1]))

		############### aqui inicia la magia ###################################################################
		for item in tasas:  
			lista_tasa.append((item.fecha, item.bc_ea, item.bc_mensual, item.usura_ea, item.usura_men, item.ipc))
		for item in abon:
			lista_abono.append((item.fecha, item.monto))
		################ Cálculo de períodos ########################################################
		tasas_df = pd.DataFrame(list(lista_tasa), columns=['FECHA', 'BC_EA', 'BC_MENSUAL', 'USURA_EA', 'USURA_MEN', 'IPC'])
		abonos_df=pd.DataFrame(list(lista_abono), columns=['FECHA', 'ABONO'])

		################# Revisar para no admitir fechas repetidas o por fuera de rango ###############
		fechas_df = pd.DataFrame(columns=['FECHA'])

		fechas_df = fechas_df.append({'FECHA':fecha_inicial}, ignore_index=True)
		for ind in abonos_df.index: 
			fechas_df = fechas_df.append({'FECHA':abonos_df['FECHA'][ind]}, ignore_index=True)

		fechas_df = fechas_df.append({'FECHA':fecha_final}, ignore_index=True)
		fechas_df['FECHA'] = pd.to_datetime(fechas_df.FECHA)
		num_periodos=len(fechas_df.index)-1
		# print("Número de períodos: ",num_periodos)
		df_complemento = pd.DataFrame(columns=['Periodo', 'Dias Iniciales','Intereses Dias Iniciales', 'Dias Finales','Intereses Dias Finales'])
		df = pd.DataFrame(columns=['Fecha', 'Tasa', 'Intereses','Monto','Total'])


		################## Para cada período hay que hacer esto #############
		for i in range(0, len(fechas_df.index)-1) :
			per += 1
			fecha_inicial=fechas_df.loc[i,'FECHA']
			fecha_final=fechas_df.loc[i+1,'FECHA']
			################ Cálculo de días iniciales ######################
			if fecha_inicial.day != 1:
			  dias_iniciales= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1] - fecha_inicial.day
			  primer_mes = datetime.date(fecha_inicial.year, fecha_inicial.month+1,1)
			else:
				dias_iniciales=0
				primer_mes = datetime.date(fecha_inicial.year, fecha_inicial.month, fecha_inicial.day)
			################################## Cálculo de tasas de intereses de días iniciales ###########################
			if tasa=="BC_MENSUAL": tasa_equi_anual = 'BC_EA'
			elif tasa=="USURA_MEN": tasa_equi_anual = 'USURA_EA'
			elif tasa=="IPC": tasa_equi_anual = 'IPC'

			tasas_aplicables = tasas_df.loc[tasas_df['FECHA'] == (primer_mes)]
			# print(primer_mes,'Primer mes')
			# print(tasas_aplicables,'Tasas aplicables index indeterminado')
			tasas_aplicables=tasas_aplicables.reset_index(drop=True) # reinicia el índice
			# print(tasas_aplicables, 'index reiniciado')
		
			if tasa_entry != "4":
			  tasa_anual_aplicable = tasas_aplicables.loc[0,tasa_equi_anual]
			else: tasa_anual_aplicable = tasa
			tasa_diaria_aplicable=((1 + float(tasa_anual_aplicable))**(1/365) - 1)

			################################## fecha inicial para cálculo de intereses de meses completos #################
			if dias_iniciales == 0:
			  fecha_busq_tabla = datetime.date(fecha_inicial.year, fecha_inicial.month, fecha_inicial.day) # Crea una fecha en el pricipio del mes para buscar en la tabla de tasas
			else: fecha_busq_tabla= datetime.date(fecha_inicial.year, fecha_inicial.month +1,1) # Pendiente ! revisar cambio de año
			################################## fecha final #########################################


			################ Cálculo de días finales ######################

			if fecha_final.day != calendar.monthrange(fecha_final.year,fecha_final.month)[1]:
			  dias_finales= fecha_final.day
			else: dias_finales=0

			################################## Cálculo de tasas de intereses de días finales ###########################
			ultimo_mes=datetime.date(year, month, 1)
			tasas_aplicables_finales = tasas_df.loc[tasas_df['FECHA'] == (ultimo_mes)]
			tasas_aplicables_finales=tasas_aplicables_finales.reset_index(drop=True) # reinicia el índice

			if tasa_entry != "4":
			  tasa_anual_aplicable_final = tasas_aplicables_finales.loc[0,tasa_equi_anual] 
			else: tasa_anual_aplicable_final = tasa 
			tasa_diaria_aplicable_final=((1 + float(tasa_anual_aplicable_final))**(1/365) - 1)

			indice_inicial=tasas_df.index.get_loc(tasas_df.index[tasas_df['FECHA'] == (fecha_busq_tabla)][0])

			dif_dias = abs(fecha_final - fecha_inicial)

			dif_meses = (fecha_final.year - fecha_busq_tabla.year) * 12 + (fecha_final.month - fecha_busq_tabla.month)


			################################## fecha inicial para cálculo de intereses de meses completos #################
			if dias_finales == 0:
			  indice_final= indice_inicial + dif_meses
			else: indice_final= indice_inicial + dif_meses -1


			########################################################################
			########### calculo del monto inicial del periodo ######################
			if per == 1:
				monto_per_in = monto[0]
			else:
				if abonos_df.loc[per-2,'ABONO'] > total_intereses_mensuales:
					print('El abono alcanzo')
					monto_per_in = float(monto[per-2]) - (float(abonos_df.loc[per-2, 'ABONO']) - total_intereses_mensuales)
					monto.append(monto_per_in)
					total_intereses_mensuales=0
				else:
					# print('El abon no alcanzo')
					if abonos_df.loc[per-2,'ABONO'] < 0:
						print('es capitalización')
						monto_per_in = float(monto[per-2])-float(abonos_df.loc[per-2, 'ABONO'])
					else:
						print('El abono no alcanzo')
						total_intereses_mensuales = total_intereses_mensuales - abonos_df.loc[per-2,'ABONO']
						monto_per_in = monto[per-2]
						monto.append(monto_per_in)



			intereses_dias_iniciales = intereses_dias_iniciales + round(monto_per_in * tasa_diaria_aplicable * dias_iniciales, 2)
			intereses_dias_finales = intereses_dias_finales + round(monto_per_in * tasa_diaria_aplicable_final * dias_finales, 2)

			################ Generación de tabla de intereses ######################
			if tasa_entry != "4": 
			  df = df.append({'Fecha':tasas_df.loc[indice_inicial,'FECHA'], 'Tasa':tasas_df.loc[indice_inicial,tasa], 'Intereses': monto_per_in*float(tasas_df.loc[indice_inicial,tasa]),'Monto':monto_per_in,'Total': (monto_per_in * float(tasas_df.loc[indice_inicial,tasa]))+monto_per_in}, ignore_index=True)
			  for i in range(indice_inicial, indice_final):
				   df = df.append({'Fecha':tasas_df.loc[i+1,'FECHA'], 'Tasa':tasas_df.loc[i+1,tasa], 'Intereses':(monto_per_in*float(tasas_df.loc[i+1,tasa])),'Monto':monto_per_in, 'Total':(df.loc[i-indice_inicial,'Total'] + float(tasas_df.loc[i+1,tasa] )*monto_per_in) }, ignore_index=True)
			else :
			  df = df.append({'Fecha':tasas_df.loc[indice_inicial,'FECHA'], 'Tasa':tasa, 'Intereses': monto_per_in*tasa,'Monto':monto_per_in,'Total': (monto_per_in * tasa)+monto_per_in}, ignore_index=True)
			  for i in range(indice_inicial, indice_final):
				   df = df.append({'Fecha':tasas_df.loc[i+1,'FECHA'], 'Tasa':tasa, 'Intereses':(monto_per_in*tasa),'Monto':monto_per_in,'Total':(df.loc[i-indice_inicial,'Total'] + (tasa*monto_per_in)) }, ignore_index=True)


			df.Intereses = df.Intereses.round()
			df.Total=df.Total.round()

			############### Generacion de tabla de consolidados de dias iniciales y finales #######################
			df_complemento = df_complemento.append({'Periodo': per, 'Dias Iniciales': dias_iniciales, 'Intereses Dias Iniciales':round(monto_per_in*tasa_diaria_aplicable* dias_iniciales,2), 'Dias Finales': dias_finales, 'Intereses Dias Finales': round(monto_per_in*tasa_diaria_aplicable_final*dias_finales,2)}, ignore_index=True)

		df.fillna(0, inplace=True)
		total_intereses_mensuales = df['Intereses'].sum()
		df_complemento.fillna(0, inplace=True)
		total_interes_dias = df_complemento['Intereses Dias Iniciales'].sum() + df_complemento['Intereses Dias Finales'].sum()
		gran_total_intereses = total_intereses_mensuales + total_interes_dias

		lista.append(df.values.tolist())
		lista2=[]
		lista2.append(df_complemento.values.tolist())
		for item in lista2[0]:
			item[2] = Herramientas.SetMoneda(item[2],'$',2)
			item[4] = Herramientas.SetMoneda(item[4],'$',2)


		lista_paso=[]
		envio = {}
		for items in lista:
			for item in items:
				v = 0
				if str(item[4])!="nan":
					v = Herramientas.SetMoneda(item[4])#str(round(item[4],2))
				else:
					v = "0"
				envio = {
					'fecha': str(item[0]),
					'tasa': Herramientas.SetMoneda((round(item[1],4)*100),'',2),
					'interes': Herramientas.SetMoneda(item[2]),#str(round(item[2],2)),
					'total': v,
					'capital': Herramientas.SetMoneda(item[3]),#str(round(item[3],2)),
				}
				lista_paso.append(envio)
		for item in abon:
			lista3 = {
				'fecha': str(item.fecha),
				'abono': Herramientas.SetMoneda(item.monto) if item.monto > 0 else '0',
				'capi': Herramientas.SetMoneda(item.monto*-1) if item.monto < 0 else '0',
			}
			lisa3.append(lista3)
		#df.to_excel (r'liquidacion_df.xlsx', index = False, header=True)
		return ({'data':lista_paso, 'complemento':lista2[0], 'listaAC':lisa3,'totales':(Herramientas.SetMoneda(total_intereses_mensuales),Herramientas.SetMoneda(total_interes_dias), Herramientas.SetMoneda(gran_total_intereses))})


	def saveAmortiza(data):
		existe = Caso.query.filter_by(num_proceso = data['data'][3][0]).first()
		if existe == None:
			try:
				caso = Caso(
					user_id = data['data'][3][0],
					num_proceso = data['data'][3][1].upper(),
			        demandante = data['data'][3][2].upper(),
			        demandado = data['data'][3][3].upper(),
			        juzgado = data['data'][3][4].upper(),
			        c_inicial = data['data'][3][5],
			        fecha_inicial = data['data'][3][6],
			        fecha_final = data['data'][3][7],
			        otra = True if data['data'][3][8] == 'OTRA' else False,
			        tasa = data['data'][3][8].upper(),
				)
				db.session.add(caso)
				db.session.commit()
			except Exception as e:
				return e, 500
			try:
				obj = Caso.query.filter_by(num_proceso = data['data'][3][1]).first()
				for item in data['data'][0]:
					resultado_calculo = Resul_Calculo(
						casos_id = obj.id,
				        fecha = item['fecha'],
				        tasa = item['tasa'],
				        interes = float(item['interes'].replace('$','').replace(',','')),
				        total = float(item['total'].replace('$','').replace(',','')),
				        capital = float(item['capital'].replace('$','').replace(',','')),
					)
					db.session.add(resultado_calculo)
					db.session.commit()
			except Exception as e:
				return e, 500
			try:
				for item in data['data'][1]:
					desglose = Desglose(
						casos_id = obj.id,
				        periodo = item['periodo'],
				        di = item['dIni'],
				        idi = float(item['dIniC'].replace('$','').replace(',','')),
				        df = item['Dfin'],
				        idf = float(item['DfinC'].replace('$','').replace(',','')),
						)
					db.session.add(desglose)
					db.session.commit()
			except Exception as e:
				return e, 500
			return 'El registro de guardo con exito', 200
		else:
			return 'Ya existe el registro', 500
		

	def historial(data):
		listas = {}
		dato = []
		try:
			lista = Caso.query.filter_by(user_id = data).all()
		except Exception as error:
			return error, 500
		if lista != []:
			for item in lista:
				listas = {
					'caso': item.num_proceso,
					'demandante': item.demandante,
					'demandado': item.demandado,
					'fecha': item.created_date,
				}
				dato.append(listas)
			return jsonify({'data':dato}), 200
		else:
			return 'no hay datos', 200


	def imprimirPDF(data):
		lisa = []
		lista = {}
		lisa2 = []
		lista2 = {}
		lisa3 = []
		lista3 = {}
		obj = Caso.query.filter_by(num_proceso = data).first()
		user = User.query.filter_by(id=obj.user_id).first()
		if obj.tasa != 'OTRA':
			tasa = obj.tasa
		else:
			obj_tasa = Resul_Calculo.query.filter_by(casos_id = obj.id).first()
			tasa = str(obj_tasa.tasa).split('.')[0]+'.'+str(obj_tasa.tasa).split('.')[1][:4]
		cabecera = {
			'caso': obj.num_proceso,
			'demandante': obj.demandante,
			'demandado': obj.demandado,
			'juzgado': obj.juzgado,
			'fini': str(obj.fecha_inicial),
			'ffin': str(obj.fecha_final),
			'tasa': tasa,
			'nombre': user.nombre,

		}
		obj2 = Resul_Calculo.query.filter_by(casos_id = obj.id).all()
		for item in obj2:
			lista = {
				'fecha' : item.fecha,
				'tasa' : item.tasa,
				'interes' : item.interes,
				'total' : item.total,
				'capital' : item.capital,
			}
			lisa.append(lista)
		obj3 = Desglose.query.filter_by(casos_id = obj.id).all()
		for item in obj3:
			lista2 = {
				'periodo':item.periodo,
				'di':item.di,
				'idi':item.idi,
				'df':item.df,
				'idf':item.idf,
			}
			lisa2.append(lista2)
		obj4 = Abono.query.filter_by(num_caso = data).all()
		for item in obj4:
			lista3 = {
				'fecha': str(item.fecha),
				'abono': Herramientas.SetMoneda(item.monto) if item.monto > 0 else '0',
				'capi': Herramientas.SetMoneda(item.monto*-1) if item.monto < 0 else '0',
			}
			lisa3.append(lista3)
		result = printListaInt(lisa, lisa3, cabecera, lisa2)
		return result


	def exportExcel(data, ruta):
		lisa = []
		lista = {}
		lisa2 = []
		lista2 = {}
		lisa3 = []
		lista3 = {}
		obj = Caso.query.filter_by(num_proceso = data).first()
		user = User.query.filter_by(id=obj.user_id).first()
		if obj.tasa != 'OTRA':
			tasa = obj.tasa
		else:
			obj_tasa = Resul_Calculo.query.filter_by(casos_id = obj.id).first()
			tasa = str(obj_tasa.tasa).split('.')[0]+'.'+str(obj_tasa.tasa).split('.')[1][:4]
		cabecera = {
			'caso': obj.num_proceso,
			'demandante': obj.demandante,
			'demandado': obj.demandado,
			'juzgado': obj.juzgado,
			'fini': str(obj.fecha_inicial),
			'ffin': str(obj.fecha_final),
			'tasa': tasa,
			'nombre': user.nombre,

		}
		obj2 = Resul_Calculo.query.filter_by(casos_id = obj.id).all()
		for item in obj2:
			lista = {
				'fecha' : item.fecha,
				'tasa' : item.tasa,
				'interes' : item.interes,
				'total' : item.total,
				'capital' : item.capital,
			}
			lisa.append(lista)
		obj3 = Desglose.query.filter_by(casos_id = obj.id).all()
		for item in obj3:
			lista2 = {
				'periodo':item.periodo,
				'di':item.di,
				'idi':item.idi,
				'df':item.df,
				'idf':item.idf,
			}
			lisa2.append(lista2)
		obj4 = Abono.query.filter_by(num_caso = data).all()
		for item in obj4:
			lista3 = {
				'fecha': str(item.fecha),
				'abono': Herramientas.SetMoneda(item.monto) if item.monto > 0 else '0',
				'capi': Herramientas.SetMoneda(item.monto*-1) if item.monto < 0 else '0',
			}
			lisa3.append(lista3)
		data1 = [lisa, lisa3, cabecera, lisa2]
		excel = Export(data1, ruta)
		file_final = excel.toExcel()
		return file_final


	def AdminTazas(self, data):
		x = db.session.query(Tasas).distinct(Tasas.fecha).all() #Tasas.query.all()
		lista = [ str(item.fecha) for item in x  if item.fecha.year == int(data[0][:4]) and item.fecha.month == int(data[0][5:7])]
		if len(lista) == 0:
			try:
				tasa = Tasas(
					fecha = data[0],
				    bc_ea = float(data[1])/100,
				    bc_mensual = float(data[2])/100,
				    usura_ea = float(data[3])/100,
				    usura_men = float(data[4])/100,
				    ipc = float(data[5])/100,
					)
				db.session.add(tasa)
				db.session.commit()
				return {'data':'Registro agregado con exito'}, 200
			except Error as error:
				return error,500
		else:
			return {'data':'Ya se ha capturado este mes'}, 406