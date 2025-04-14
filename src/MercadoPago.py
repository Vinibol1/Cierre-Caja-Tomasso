from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from tkinter import *
from tkinter import ttk
from tkinter import  PhotoImage
import Rappi
from tkcalendar import DateEntry
from selenium.webdriver.common.by import By
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QDateEdit, QFrame
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt, QDate
import sys
import time
usuario = os.getlogin()


options = webdriver.FirefoxOptions()
options.add_argument('-profile')
options.add_argument("/home/"+ usuario+"/.cache/mozilla/firefox/bam1bn0o.default-release")
service = Service(GeckoDriverManager().install())

driver = webdriver.Firefox(service=service, options=options)

def ejecutar_programa(fecha,driver,etiquetas_totales):
    fecha_seleccionada = fecha_seleccionada = fecha.date().toPython()
    print(fecha_seleccionada)
    dinero_mercado = recorrer_paginas(fecha_seleccionada)
    dinero_rappi = Rappi.Pagina_rappi(driver,fecha_seleccionada)
    total_dinero = dinero_mercado + dinero_rappi
    for i in range(8):
        etiquetas_totales[i].setText(str(total_dinero[i]))


def interfaz():
    app = QApplication(sys.argv)

    ventana = QWidget()
    ventana.setWindowTitle("Cierre de caja")
    ventana.setFixedSize(550, 370)
    ventana.setStyleSheet("background-color: black;")

    layout_principal = QVBoxLayout(ventana)

    # Imagen/logo
    imagen_label = QLabel()
    imagen_label.setAlignment(Qt.AlignRight)
    imagen_label.setStyleSheet("background-color: black;")

    # Layouts
    layout_cabecera = QHBoxLayout()
    layout_formulario = QGridLayout()
    layout_botones = QHBoxLayout()

    Nombres = [
        "Total tarjeta", "Total Transferencias", "Total Tomasso", "Total fly",
        "Total Rappi Tomasso", "Total Rappi Fly", "Total Tomasso Turbo", "Total Fly Turbo"
    ]
    etiquetas_totales = []

    fuente = QFont("Helvetica", 15)
    for i, nombre in enumerate(Nombres):
        etiqueta_titulo = QLabel(nombre)
        etiqueta_titulo.setFont(fuente)
        etiqueta_titulo.setStyleSheet("color: white;")
        layout_formulario.addWidget(etiqueta_titulo, i, 0)

        etiqueta_valor = QLabel("0")
        etiqueta_valor.setFont(fuente)
        etiqueta_valor.setStyleSheet("color: white;")
        layout_formulario.addWidget(etiqueta_valor, i, 1)
        etiquetas_totales.append(etiqueta_valor)

    # Selector de fecha
    fecha_selector = QDateEdit()
    fecha_selector.setCalendarPopup(True)
    fecha_selector.setDisplayFormat("dd/MM/yyyy")
    fecha_selector.setDate(QDate.currentDate())
    fecha_selector.setStyleSheet("background-color: #1e1e1e; color: white; padding: 5px; border-radius: 4px;")
    layout_botones.addWidget(fecha_selector)

    # Botón Confirmar
    boton_confirmar = QPushButton("Confirmar")
    boton_confirmar.setStyleSheet("""
        QPushButton {
            background-color: #14140F;
            color: white;
            font-size: 12px;
            padding: 6px 12px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #2b2b2b;
        }
    """)
    boton_confirmar.clicked.connect(lambda: ejecutar_programa(fecha_selector, driver, etiquetas_totales))
    layout_botones.addWidget(boton_confirmar)

    # Botón Salir
    boton_salir = QPushButton("Salir")
    boton_salir.setStyleSheet("""
        QPushButton {
            background-color: #600000;
            color: white;
            font-size: 12px;
            padding: 6px 12px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #800000;
        }
    """)
    boton_salir.clicked.connect(app.quit)
    layout_botones.addWidget(boton_salir)

    # Ensamblado final
    layout_cabecera.addStretch()
    layout_cabecera.addWidget(imagen_label)

    layout_principal.addLayout(layout_formulario)
    layout_principal.addSpacing(10)
    layout_principal.addLayout(layout_botones)
    layout_principal.addLayout(layout_cabecera)

    ventana.setLayout(layout_principal)
    ventana.show()
    sys.exit(app.exec())




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


def sumar_operaciones():
    li_elements = driver.find_elements(By.CLASS_NAME, 'ui-rowfeed-container')
    monto = 1
    for li in li_elements:
        try:
            monto += sumar_dinero(li)
        except Exception as e:
            print(f"Error al extraer el valor del elemento: {e}")
    return monto

def realizar_pagina():
    exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    total_transferencia = 0
    while (exists == False):
        time.sleep(1)
        total_transferencia += sumar_operaciones()
        siguiente = driver.execute_script("return document.querySelectorAll('.andes-pagination__link');")
        if len(siguiente) == 0 or not siguiente[3].is_displayed():
            break
        elif len(siguiente) == 4:
            siguiente[3].click()
        elif not siguiente[4].is_displayed():
            break
        else:
            siguiente[4].click()
        exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    return total_transferencia

def sumar_transferencias(fecha):
    driver.get("https://www.mercadopago.com.ar/activities/1?period=other&date_from=2025-04-12&date_to=2025-04-12&status=approved&operation=transfers")
    driver.implicitly_wait(5)
    return realizar_pagina()

def sumar_tarjeta_debito(fecha):
    driver.get("https://www.mercadopago.com.ar/activities/1?period=other&date_from=2025-03-30&date_to=2025-03-30&status=approved&appliance=mixed_non_mp_debit")
    return realizar_pagina()

def sumar_tarjeta_credito(fecha):
    driver.get("https://www.mercadopago.com.ar/activities/1?period=other&date_from=2025-03-30&date_to=2025-03-30&status=approved&appliance=mixed_non_mp_credit")
    driver.implicitly_wait(5)
    return realizar_pagina()

def recorrer_paginas(fecha):
    
    driver.get("https://www.mercadopago.com.ar/activities/1?period=other&date_from=2025-03-30&date_to=2025-03-30&status=approved&operation=transfers")
    driver.implicitly_wait(5)
    exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    pagina = 2
    dinero_transferencias = sumar_transferencias(fecha)
    dinero_tarjeta = sumar_tarjeta_debito(fecha) + sumar_tarjeta_credito(fecha)
    dinero_tomasso = 0
    dinero_fly = 0
    dinero_mercado = [dinero_tarjeta, dinero_transferencias, dinero_tomasso, dinero_fly]
    return dinero_mercado
        

interfaz()


driver.quit()



