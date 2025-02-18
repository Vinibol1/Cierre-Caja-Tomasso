from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import time


options = webdriver.FirefoxOptions()
options.add_argument('-profile')
options.add_argument(r'/home/tobias/.cache/mozilla/firefox/bam1bn0o.default-release')
service = Service(GeckoDriverManager().install())

driver = webdriver.Firefox(service=service, options=options)


def verificar_pedido(li_element):
    elemento = li_element.find_element(By.CLASS_NAME, 'ui-rowfeed-title')
    if "Pedido" in elemento.text:
        return True
    return False

def sumar_dinero(li):
    dinero = 0
    cantidad_dinero = li.find_element(By.CLASS_NAME,'andes-money-amount__fraction')
    cantidad_centavos = li.find_element(By.CLASS_NAME,'andes-money-amount__cents')
    cantidad_dinero_sin_coma = cantidad_dinero.text.replace('.', '')
    dinero += float(cantidad_dinero_sin_coma) + float(cantidad_centavos.text)/100
    return dinero


def separar_operaciones():
        li_elements = driver.find_elements(By.CLASS_NAME, 'ui-rowfeed-container')
        dinero_operaciones = 0
        dinero_pedidos = 0


        for li in li_elements:
            script = """
                let li = arguments[0];
                let esNegativo = li.querySelector('.andes-money-amount__negative-symbol') !== null;
                if (esNegativo) return null;
                else return true;
            """
            script2 = """
                let li = arguments[0];
                let esNegativo = li.querySelector('.ui-rowfeed-avatar__badge--refunded') !== null;
                if (esNegativo) return null;
                else return true;
            """
            resultado = driver.execute_script(script, li)
            resultado2 = driver.execute_script(script2, li)
            if resultado is None or resultado2 is None:
                continue  

            try:
                es_pedido = verificar_pedido(li)
                if es_pedido:
                    dinero_pedidos += sumar_dinero(li)
                else:
                    dinero_operaciones += sumar_dinero(li)
            except Exception as e:
                print(f"Error al extraer el valor ddriver.implicitly_wait(5)el elemento: {e}")

        return dinero_operaciones, dinero_pedidos

def recorrer_paginas():
    driver.get('https://www.mercadopago.com.ar/activities/1?period=other&date_from=2025-02-16&date_to=2025-02-16')
    exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    pagina = 2
    dinero_operaciones = 0
    dinero_pedidos = 0
    while (exists == False):
        total_dinero = separar_operaciones()
        print(f'Total dinero: {total_dinero[0]},Total_pedidos: {total_dinero[1]}')
        dinero_operaciones += total_dinero[0]
        dinero_pedidos += total_dinero[1]
        driver.get('https://www.mercadopago.com.ar/activities/' + str(pagina) + '?period=other&date_from=2025-02-16&date_to=2025-02-16')
        driver.implicitly_wait(5)
        pagina += 1
        exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    return dinero_operaciones, dinero_pedidos
        

total_dinero = recorrer_paginas()
print(f'Total dinero: {total_dinero[0]},Total_pedidos: {total_dinero[1]}')



driver.quit()
