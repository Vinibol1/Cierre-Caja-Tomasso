from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import Tk, Label, Button, PhotoImage
from tkinter import ttk
from tkinter import  PhotoImage
from tkcalendar import DateEntry
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


usuario = os.getlogin()
options = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
options.add_argument(r'--user-data-dir=C:/Users/' + usuario + '/AppData/Local/Google/Chrome/User Data/Default')
options.add_argument(r'--profile-directory=Caja')
options.add_argument('--disable-blink-features=AutomationControlled')




driver = webdriver.Chrome(service=service, options=options)


def ejecutar_programa(fecha,etiquetas_totales):
    fecha_seleccionada = fecha.get_date()
    total_dinero = recorrer_paginas(fecha_seleccionada)
    for i in range(4):
        etiquetas_totales[i].config(text=total_dinero[i])


def interfaz():
    root = Tk()
    root.configure(bg='black')
    root.geometry("500x250")
    root.title("Cierre de caja")
    style_frame = ttk.Style()
    style_frame.configure('My.TFrame', background='black')

    frm = ttk.Frame(root, style='My.TFrame')
    frm.grid(padx=50, pady=10)
    frm.configure()

    style_label = ttk.Style()
    style_label.configure('My.TLabel', background='black', foreground='white', font=('Helvetica', 14))
    ttk.Label(frm, text="Total transferencias:",background="black",style="My.TLabel" ).grid(column=0, row=0, padx=5, pady=10)
    ttk.Label(frm, text="Total tarjeta:",background="black",style="My.TLabel" ).grid(column=0, row=1, padx=5, pady=10)
    ttk.Label(frm, text="Total fly: ",style="My.TLabel").grid(column=0, row=2, padx=10, pady=5)
    ttk.Label(frm, text="Total tomasso: ",style="My.TLabel").grid(column=0, row=3, padx=10, pady=5)
    btn_salir = Button(frm, text="Salir", command=root.destroy, bg="#14140F", fg="white", font=("Helvetica", 11), padx=10, pady=5)
    btn_salir.grid(column=3, row=5, pady=5)


    etiquetas_totales = []
    for i in range(4):
        etiqueta = ttk.Label(frm, text="0",style="My.TLabel")
        etiquetas_totales.append(etiqueta)
        etiqueta.grid(column=1, row=i, padx=10, pady=5)

    fecha = DateEntry(frm, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
    fecha.grid(column=0, row=5, padx=5, pady=5)
    
    btn_confirmar = Button(frm, text="Confirmar", command=lambda: ejecutar_programa(fecha, etiquetas_totales), bg="#14140F", fg="white", font=("Helvetica", 11), padx=10, pady=5)
    btn_confirmar.grid(column=1, row=5, padx=40, pady=5)


    root.mainloop()



def verificar_pedido_o_tarjeta(li_element):
    elemento = li_element.find_element(By.CLASS_NAME, 'ui-rowfeed-title')
    if "Pedido" in elemento.text:
        return 1
    elif "Point Smart" in elemento.text:
        return 0
    return -1

# 0 es para fly morfi 1 es para tomasso
def verificar_fly_o_tomasso():
    try:
        contenido_pedido = driver.find_element(By.CLASS_NAME, 'info-v2__title').text
        if "Fly" in contenido_pedido:
            return 0
        elif "Tomasso" in contenido_pedido:
            return 1
    except Exception as e:
        print(f"Error al verificar Fly o Tomasso: {e}")


def sumar_dinero(li):
    cantidad_dinero = li.find_element(By.CLASS_NAME,'andes-money-amount__fraction').text.replace('.', '')
    cantidad_centavos = li.find_element(By.CLASS_NAME,'andes-money-amount__cents').text
    return float(cantidad_dinero) + float(cantidad_centavos)/100


def separar_operaciones():
    li_elements = driver.find_elements(By.CLASS_NAME, 'ui-rowfeed-container')
    dinero_transferencias = 0
    dinero_tarjeta = 0
    dinero_fly = 0
    dinero_tomasso = 0

    for li in li_elements:
        script = """
            let li = arguments[0];
            let esNegativo = li.querySelector('.andes-money-amount__negative-symbol') !== null;
            if (esNegativo) {
                return null;
            }
            let paragraphs = li.querySelectorAll('.ui-rowfeed-description p');
            for (let p of paragraphs) {
                if (p.innerText.includes('Rechazado')) {
                    return null;
                }
            }
            let fueReembolsado = li.querySelector('.ui-rowfeed-avatar__badge--refunded') !== null;
            return fueReembolsado ? null : true;

        """
        resultado = driver.execute_script(script, li)
        if resultado is None:
            continue

        try:
            monto = sumar_dinero(li)
            es_pedido = verificar_pedido_o_tarjeta(li)
            if es_pedido == 1:
                link_pedido = li.find_element(By.TAG_NAME, 'a').get_attribute('href')

                driver.execute_script("window.open(arguments[0], '_blank');", link_pedido)
                driver.switch_to.window(driver.window_handles[-1])
                
                driver.implicitly_wait(2)  
                es_fly_tomasso = verificar_fly_o_tomasso()
                if es_fly_tomasso == 0:
                    dinero_fly += monto
                elif es_fly_tomasso == 1:
                    dinero_tomasso += monto

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            elif es_pedido == 0:
                dinero_tarjeta += monto
            else:
                dinero_transferencias += monto
        except Exception as e:
            print(f"Error al extraer el valor del elemento: {e}")

    return dinero_transferencias,dinero_tarjeta, dinero_fly, dinero_tomasso

def recorrer_paginas(fecha):
    driver.get('https://www.mercadopago.com.ar/activities/1?period=other&date_from=' + str(fecha) + '&date_to='+ str(fecha))
    driver.implicitly_wait(120)
    driver.get_cookie(name="mp")
    exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    pagina = 2
    dinero_transferencias = 0
    dinero_tarjeta = 0
    dinero_fly = 0
    dinero_tomasso = 0
    while (exists == False):
        total_dinero = separar_operaciones()
        dinero_transferencias += total_dinero[0]
        dinero_tarjeta += total_dinero[1]
        dinero_fly += total_dinero[2]
        dinero_tomasso += total_dinero[3]
        driver.get('https://www.mercadopago.com.ar/activities/' + str(pagina) + '?period=other&date_from=' + str(fecha) + '&date_to='+ str(fecha))
        driver.implicitly_wait(5)
        pagina += 1
        exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    return dinero_transferencias,dinero_tarjeta , dinero_fly, dinero_tomasso
        

interfaz()


driver.quit()


