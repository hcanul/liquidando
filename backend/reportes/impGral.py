from fpdf import FPDF
import os, time
from datetime import datetime, date
from flask import make_response
from models import db
import flask
from tools.herramientas import Herramientas



# consulta para pedir datos de las tablas directamente


def current_date_format(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    messsage = "{} de {} del {}".format(day, month, year)

    return messsage


class PDF(FPDF):

    def header(self):
        # Ruta del la carpeta imagenes del servidor
        imagenes = os.path.abspath("img/")
        # Logo  con esta ruta se dirige al server y no a la maquina cliente
        if tamaño:
            self.image(os.path.join(imagenes, "liquidando2.png"), 10, 5, 50)
        else:
            self.image(os.path.join(imagenes, "liquidando2.png"), 10, 5, 270)
        # Arial bold 15

        self.set_font('Arial', 'B', 8)
        self.set_fill_color( 184, 184, 187 )
        self.cell(70, 5, '', 0,0, 0)
        self.cell(20, 5, 'Demandante:', border=1,align='C', fill=True)
        self.cell(100, 5, Cabeza['demandante'], border=1,align='L', fill=False)
        self.ln(7)
        self.cell(70, 5, 'Usted Litiga, Nosotros Liquidamos', 0, 0, 'L')
        self.cell(20, 5, 'Demandado:', border=1,align='C', fill=True)
        self.cell(100, 5, Cabeza['demandado'], border=1,align='L', fill=False)
        self.ln(7)
        self.cell(70, 5, '', 0,0, 0)
        self.cell(20, 5, 'Radicado:', border=1,align='L', fill=True)
        self.cell(100, 5, Cabeza['caso'], border=1,align='L', fill=False)
        self.ln(7)
        self.cell(70, 5, '', 0,0, 0)
        self.cell(20, 5, 'Juzgado:', border=1,align='L', fill=True)
        self.cell(100, 5, Cabeza['juzgado'], border=1,align='L', fill=False)
        self.ln(7)
        self.cell(70, 5, '', 0,0, 0)
        self.cell(20, 5, 'F. Inicial:', border=1,align='L', fill=True)
        self.cell(18, 5, Cabeza['fini'], border=1,align='L', fill=False)
        self.cell(20, 5, 'F. Final:', border=1,align='L', fill=True)
        self.cell(18, 5, Cabeza['ffin'], border=1,align='L', fill=False)
        self.cell(20, 5, 'Tasa Interes:', border=1,align='L', fill=True)
        self.cell(24, 5, Cabeza['tasa'], border=1,align='L', fill=False)
  
        # Move to the right
        # self.cell(100)
        # Title
        
        # self.ln(0)
        
        self.ln(4)
        self.cell(150, 10, '', 0, 0)
        self.set_fill_color(184, 188, 191)
        self.ln()


    def footer(self):
        # Position at 1.5 cm from bottom
        self.ln()
        self.set_y(-30)
        # Arial italic 8
        self.set_font('Arial', 'B', 8)
        self.ln(3)
        self.cell(0, 10, 'www.liquidando.com.co', 0, 0, 'C')
        self.ln(3)
        #page number
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


def printListaInt(data, dato, cabecera, periodos):
    global tamaño
    global Cabeza
    Cabeza = cabecera
    tamaño = True #Vertical True
    pdf = PDF("P", 'mm', 'LETTER')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_fill_color( 184, 184, 187 )
    pdf.set_text_color(64)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(.3)
    pdf.set_font('', 'B')
    pdf.set_font('Arial', '', 8.0)

    # Effective page width, or just epw
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 5
    data3 = ('Fecha', 'Tasa', 'Interes', 'Total', 'Capital')

    # Text height is the same as current font size
    th = pdf.font_size
    #########################################
    ###       Cuerpo del procedimiento    ###
    #########################################
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, 'Interteses del proceso', 0, 0, 'C')
    pdf.ln()
    pdf.set_font('Arial', '', 8.0)
    for item in data3:
        pdf.cell(col_width, th + 2, str(item),fill=True,border=1,align='C')
    pdf.ln()
    total = 0
    banda=0
    linea=0
    interes = 0
    for i in data:
        interes += i['interes']
        linea+=1
        if linea == 41:
            pdf.add_page()
            linea=0
        banda+=1
        m = banda % 2
        if m == 0:
            pdf.cell(col_width, th+2, str(i['fecha']), border=1,align='C', fill=True)
            pdf.cell(col_width, th+2, Herramientas.SetMoneda(i['tasa'],'%',4), border=1,align='C', fill=True)
            pdf.cell(col_width, th+2, Herramientas.SetMoneda(i['interes']), border=1,align='C', fill=True)
            pdf.cell(col_width, th+2, Herramientas.SetMoneda(i['total']), border=1,align='C', fill=True)
            pdf.cell(col_width, th+2, Herramientas.SetMoneda(i['capital']), border=1,align='C', fill=True)
        else:
            pdf.cell(col_width, th+2, str(i['fecha']), border=1,align='C', fill=False)
            pdf.cell(col_width, th+2, Herramientas.SetMoneda(i['tasa'],'%',4), border=1,align='C', fill=False)
            pdf.cell(col_width, th+2, Herramientas.SetMoneda(i['interes']), border=1,align='C', fill=False)
            pdf.cell(col_width, th+2, Herramientas.SetMoneda(i['total']), border=1,align='C', fill=False)
            pdf.cell(col_width, th+2, Herramientas.SetMoneda(i['capital']), border=1,align='C', fill=False)
        pdf.ln()
        total = i['capital']
    pdf.ln()

    # Effective page width, or just epw
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 3
    data3 = ('Fecha', 'Abono', 'Capitalizacion')

    # Text height is the same as current font size
    th = pdf.font_size
    #########################################
    ###       Cuerpo del procedimiento    ###
    #########################################
    if dato:
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, 'Desglose de Abonos y Capitalizaciones', 0, 0, 'C')
        pdf.ln()
        pdf.set_font('Arial', '', 8.0)
        for item in data3:
            pdf.cell(col_width, th + 2, str(item),fill=True,border=1,align='C')
        pdf.ln()
        banda=0
        linea=0
        for i in dato:
            linea+=1
            if linea == 41:
                pdf.add_page()
                linea=0
            banda+=1
            m = banda % 2
            if m == 0:
                pdf.cell(col_width, th+2, i['fecha'], border=1,align='C', fill=True)
                pdf.cell(col_width, th+2, i['abono'], border=1,align='C', fill=True)
                pdf.cell(col_width, th+2, i['capi'], border=1,align='C', fill=True)
            else:
                pdf.cell(col_width, th+2, i['fecha'], border=1,align='C', fill=False)
                pdf.cell(col_width, th+2, i['abono'], border=1,align='C', fill=False)
                pdf.cell(col_width, th+2, i['capi'], border=1,align='C', fill=False)
            pdf.ln()
    pdf.ln()

    print(periodos)
    sumadias = 0
    for sub in periodos:
        sumadias += sub['idi'] + sub['idf']
    print(sumadias, interes)
    pdf.set_font('Arial', 'B', 8.0)
    pdf.cell(30, th + 2, 'Intereses Totales',fill=True,border=1,align='C')
    pdf.cell(50, th + 2, Herramientas.SetMoneda(sumadias+interes),fill=False,border=1,align='R')
    pdf.ln()
    pdf.cell(30, th + 2, 'Capital',fill=True,border=1,align='C')
    pdf.cell(50, th + 2, Herramientas.SetMoneda(total),fill=False,border=1,align='R')
    pdf.ln()
    pdf.set_font('Arial', 'B', 10.0)
    pdf.cell(30, th + 2, 'Gran Total',fill=True,border=1,align='C')
    pdf.cell(50, th + 2, Herramientas.SetMoneda(sumadias+interes+total),fill=False,border=1,align='R')
    
    ### aqui pondremos los totales

    ################################
    #########################################
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=%s.pdf' % 'listado'
    return response, 200



