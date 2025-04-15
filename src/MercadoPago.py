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
    for i in range(9):
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
        "Total Debito", "Total Credito", "Total Transferencias", "Total Tomasso", "Total fly",
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



def sumar_dinero(li):
    cantidad_dinero = li.find_element(By.CLASS_NAME,'andes-money-amount__fraction').text.replace('.', '')
    cantidad_centavos = li.find_element(By.CLASS_NAME,'andes-money-amount__cents').text
    return float(cantidad_dinero) + float(cantidad_centavos)/100


def sumar_operaciones():
    total = driver.execute_script("""
    let monto = 1;
    const items = document.querySelectorAll('.ui-rowfeed-container');

    items.forEach(el => {
        try {
            let esNegativo = el.querySelector('.andes-money-amount__negative-symbol') !== null;
            if (!esNegativo) {
                const entero = el.querySelector('.andes-money-amount__fraction')?.textContent.replace(/\\./g, '') || '0';
                const centavos = el.querySelector('.andes-money-amount__cents')?.textContent || '0';
                monto += parseFloat(entero) + parseFloat(centavos) / 100;
            }
        } catch (e) {
            console.log('Error al sumar en elemento:', e.message);
        }
    });

    return monto;
    """)
    return total

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
    base_url = "https://www.mercadopago.com.ar/"
    driver.get(f"{base_url}activities/1?period=other&date_from={fecha}&date_to={fecha}&status=approved&operation=transfers")
    total = realizar_pagina()
    driver.get(f"{base_url}activities/1?period=other&date_from={fecha}&date_to={fecha}&status=approved&operation=sales&appliance=payment_source_account_money&channel=off")
    total += sumar_operaciones()
    driver.get(f"{base_url}dashboards/v2?channels=QR&selected_tab=point_qr_tabs&start_period_dashboard={fecha}T15:00:00.000Zto{fecha}T15:00:00.000Z")
    time.sleep(1)
    total += int(driver.execute_script("return document.querySelector('.tfs-dashboard-tab-header__value')?.textContent.replace('.', '').slice(2) || '0'"))
    return total

def sumar_tarjeta(fecha, tipo):
    tipo_map = {
        "debito": "debit_card",
        "credito": "credit_card|prepaid_card"
    }
    driver.get(f"https://www.mercadopago.com.ar/dashboards/v2?channels=Point&payments={tipo_map[tipo]}&selected_tab=point_qr_tabs&start_period_dashboard={fecha}T15:00:00.000Zto{fecha}T15:00:00.000Z")
    time.sleep(1)
    return driver.execute_script("return document.querySelector('.tfs-dashboard-tab-header__value')?.textContent.replace('.', '').slice(2) || '0'")

def verificar_pedido(li):
    texto = li.find_element(By.CLASS_NAME, 'ui-rowfeed-title').text
    return "Pedido" in texto

def verificar_fly_o_tomasso():
    try:
        contenido = driver.find_element(By.CLASS_NAME, 'info-v2__title').text
        if "Fly" in contenido:
            return 0
        elif "Tomasso" in contenido:
            return 1
    except:
        return -1

def sumar_pedido(fecha):
    url = f"https://www.mercadopago.com.ar/activities/1?period=other&date_from={fecha}&date_to={fecha}&status=approved&operation=sales&appliance=payment_source_account_money"
    driver.get(url)
    dinero_fly = dinero_tomasso = 0

    while True:
        pedidos = driver.find_elements(By.CLASS_NAME, 'ui-rowfeed-container')
        for li in pedidos:
            if not verificar_pedido(li):
                continue
            monto = sumar_dinero(li)
            link = li.find_element(By.TAG_NAME, 'a').get_attribute('href')
            driver.execute_script("window.open(arguments[0])", link)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(0.5)
            tipo = verificar_fly_o_tomasso()
            if tipo == 0:
                dinero_fly += monto
            elif tipo == 1:
                dinero_tomasso += monto
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        siguiente = driver.execute_script("return document.querySelectorAll('.andes-pagination__link');")
        if len(siguiente) == 0 or not siguiente[3].is_displayed():
            break
        elif len(siguiente) == 4:
            siguiente[3].click()
        elif not siguiente[4].is_displayed():
            break
        else:
            siguiente[4].click()
    return dinero_tomasso, dinero_fly

def recorrer_paginas(fecha):
    return [
        sumar_tarjeta(fecha, "debito"),
        sumar_tarjeta(fecha, "credito"),
        sumar_transferencias(fecha),
        sumar_pedido(fecha)
    ]

if __name__ == "__main__":
    interfaz()
    driver.quit()
