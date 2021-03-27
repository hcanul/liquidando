import smtplib
import email.message


def correo(usuario, password, fecha, correo, tarifa, caso=0):
  if tarifa == 0:
    planC="Tu plan es Gratuito y solo puedes hacer una liquidacion"
  elif tarifa ==1:
    planC="Contrataste el plan basico y tienes derecho a 10 liquidaciones"
  elif tarifa ==2:
    planC="Contrataste el plan avanzado y tienes derecho a 30 dias y realizar todas las liquidaciones que desees!!"
  email_content = """
    <html>
     
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        
       <title>Liquidando</title>
       <style type="text/css">
        a {color: #d80a3e;}
      body, #header h1, #header h2, p {margin: 0; padding: 0;}
      #main {border: 1px solid #cfcece;}
      img {display: block;}
      #top-message p, #bottom p {color: #3f4042; font-size: 12px; font-family: Arial, Helvetica, sans-serif; }
      #header h1 {color: #ffffff !important; font-family: "Lucida Grande", sans-serif; font-size: 24px; margin-bottom: 0!important; padding-bottom: 0; }
      #header p {color: #ffffff !important; font-family: "Lucida Grande", "Lucida Sans", "Lucida Sans Unicode", sans-serif; font-size: 12px;  }
      h5 {margin: 0 0 0.8em 0;}
        h5 {font-size: 18px; color: #444444 !important; font-family: Arial, Helvetica, sans-serif; }
      p {font-size: 12px; color: #444444 !important; font-family: "Lucida Grande", "Lucida Sans", "Lucida Sans Unicode", sans-serif; line-height: 1.5;}
       </style>
    </head>
     
    <body>
     
     
    <table width="100%" cellpadding="0" cellspacing="0" bgcolor="e4e4e4"><tr><td>
    <table id="top-message" cellpadding="20" cellspacing="0" width="600" align="center">
        <tr>
          <td align="center">
          </td>
        </tr>
      </table>
     
    <table id="main" width="600" align="center" cellpadding="0" cellspacing="15" bgcolor="ffffff">
        <tr>
          <td>
            <table id="header" cellpadding="10" cellspacing="0" align="center" bgcolor="8fb3e9">
              <tr>
                <td width="570" align="center"  bgcolor="#d80a3e"><h1>Confirmacion de Correo</h1></td>
              </tr>
              <tr>
                <td width="570" align="center"  bgcolor="#d80a3e" style=""><h1>Usuario: </h1> <h2>""" + usuario +"""</h2></td>
              </tr>
              <tr>
                <td width="570" align="center"  bgcolor="#d80a3e"><h1>Password: </h1> <h2>""" + password +"""</h2></td>
              </tr>
              <tr>
                <td width="570" align="center"  bgcolor="#d80a3e"><h1>Plan contratado: </h1> <h2>""" + planC +"""</h2></td>
              </tr>
              <tr>
                <td width="570" align="right" bgcolor="#d80a3e"><p>"""+ fecha +"""</p></td>
              </tr>
            </table>
          </td>
        </tr>
     
        <tr>
          <td>
            <table id="content-3" cellpadding="0" cellspacing="0" align="center">
              <tr>
                  <td width="250" valign="top" bgcolor="d0d0d0" style="padding:5px;">
                  <img src="http://www.liquidando.com.co/wp-content/uploads/2018/01/logo_simple.png" width ="250" height="150" />
                </td>
                  <td width="15"></td>
                <td width="250" valign="top" bgcolor="d0d0d0" style="padding:5px;">
                    <img src="http://www.liquidando.com.co/wp-content/uploads/2018/02/Imagen-Redes.png" width ="250" height="150" />
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td>
            <table id="content-4" cellpadding="0" cellspacing="0" align="center">
              <tr>
                <td width="200" valign="top">
                  <h5>La mejor herramienta para sus liquidaciones</h5>
                  <p>Ya varios de nuestros usuarios disfrutan de la comodidad que le ofrece Liquidando, permitiendo tramitar procesos de manera Exitosa</p>
                </td>
                <td width="15"></td>
                <td width="200" valign="top">
                  <h5>Nosotros</h5>
                  <p>La plataforma Liquidando es un liquidador de intereses planeado para que los usuarios puedan realizar las liquidaciones de los procesos legales que tengan unas pretensiones monetarias y sea necesario realizar el calculo de los intereses moratorios de acuerdo a las tasas de interes establecidas por la ley o previamente pactadas por las partes involucradas. Con esta plataforma usted podra realizar el calculo de los intereses moratorios en cualquiera de las tasas establecidas por la ley, la cual puede ser una tasa de interes corriente, la maxima legal vigente que se define como la tasa de usura o tasa fija, de igual forma puede realizar actualizaciones a IPC y obtener resultados precisos desglosados mes a mes.</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
         
     
      </table>
      <table id="bottom" cellpadding="20" cellspacing="0" width="600" align="center">
        <tr>
          <td align="center">
            <h2><p>Usted litiga nosotros liquidamos</p><h2>
          </td>
        </tr>
      </table><!-- top message -->
    </td></tr></table><!-- wrapper -->
     
    </body>
    </html>
     
    """

  server = smtplib.SMTP('smtp.gmail.com:587')
  msg = email.message.Message()
  msg['Subject'] = 'Soporte Tecnico Liquidando'
   
   
  msg['From'] = 'pruebas.frenetic@gmail.com'
  msg['To'] = str(correo)
  password = "ha260182ha"
  msg.add_header('Content-Type', 'text/html')
  msg.set_payload(email_content)
   
  s = smtplib.SMTP('smtp.gmail.com: 587')
  s.starttls()
   
  # Login Credentials for sending the mail
  try:
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    return "Exito",200
  except:
    return "Error", 500

