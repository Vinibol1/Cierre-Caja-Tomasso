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
    cantidad_dinero = li.find_element(By.CLASS_NAME,'andes-money-amount__fraction')
    cantidad_centavos = li.find_element(By.CLASS_NAME,'andes-money-amount__cents')
    cantidad_dinero_sin_coma = cantidad_dinero.text.replace('.', '')
    print(cantidad_dinero)
    dinero_pedidos += float(cantidad_dinero_sin_coma) + float(cantidad_centavos.text)/100


def separar_operaciones():
    exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    pagina = 1
    while (exists == False):
        driver.get('https://www.mercadopago.com.ar/activities/' + pagina + '?period=today')
        pagina += 1
        driver.implicitly_wait(5)
        exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")

        li_elements = driver.find_elements(By.CLASS_NAME, 'ui-rowfeed-container')
        dinero_operaciones = 0
        dinero_pedidos = 0

            

        for li in li_elements:
            # Usar JavaScript para verificar si el valor es negativo
            script = """
                let li = arguments[0];
                let esNegativo = li.querySelector('.andes-money-amount__negative-symbol') !== null;
                if (esNegativo) return null;
                else return true;
            """
            resultado = driver.execute_script(script, li)
            if resultado is None:
                continue  # Si es negativo, saltar al siguiente elemento

            try:
                es_pedido = verificar_pedido(li)
                if es_pedido:
                    dinero_pedidos += sumar_dinero(li)
                else:
                    dinero_operaciones += sumar_dinero(li)
            except Exception as e:
                print(f"Error al extraer el valor del elemento: {e}")

        return dinero_operaciones, dinero_pedidos

# Llamar la función y mostrar el total
total_dinero = separar_operaciones()
print(f'Total dinero: {total_dinero[0]},Total_pedidos: {total_dinero[1]}')


# Cerrar el navegador
driver.quit()
