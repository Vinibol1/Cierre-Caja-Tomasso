from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Configurar opciones para Chrome
options = webdriver.ChromeOptions()
# Opcional: Si necesitas usar un perfil específico
options.add_argument('user-data-dir=user_data')
options.add_argument('--disable-blink-features=AutomationControlled')

# Configurar el servicio para ChromeDriver
service = Service(ChromeDriverManager().install())

# Inicializar el controlador de Google Chrome
driver = webdriver.Chrome(service=service, options=options)

# Acceder a la página de MercadoPago
driver.get('https://www.mercadopago.com.ar/activities/1?period=yesterday')

# Esperar que los elementos se carguen
driver.implicitly_wait(120)

def verificar_pedido(li_element):
    elemento = li_element.find_element(By.CLASS_NAME, 'ui-rowfeed-title')
    if "Pedido" in elemento.text:
        return True
    return False

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
    dinero_operaciones = 0
    dinero_fly = 0
    dinero_tomasso = 0

    for li in li_elements:
        script = """
            let li = arguments[0];
            let esNegativo = li.querySelector('.andes-money-amount__negative-symbol') !== null;
            if (esNegativo) {
                return null;
            }
            let fueReembolsado = li.querySelector('.ui-rowfeed-avatar__badge--refunded') !== null;
            return fueReembolsado ? null : true;
        """
        resultado = driver.execute_script(script, li)
        if resultado is None:
            continue

        try:
            monto = sumar_dinero(li)
            es_pedido = verificar_pedido(li)
            if es_pedido:
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
            else:
                dinero_operaciones += monto
        except Exception as e:
            print(f"Error al extraer el valor del elemento: {e}")

    return dinero_operaciones, dinero_fly, dinero_tomasso

def recorrer_paginas():
    driver.get('https://www.mercadopago.com.ar/activities/1?period=today')
    driver.implicitly_wait(5)
    exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    pagina = 2
    dinero_operaciones = 0
    dinero_fly = 0
    dinero_tomasso = 0
    while (exists == False):
        total_dinero = separar_operaciones()
        dinero_operaciones += total_dinero[0]
        dinero_fly += total_dinero[1]
        dinero_tomasso += total_dinero[2]
        driver.get('https://www.mercadopago.com.ar/activities/' + str(pagina) + '?period=today')
        driver.implicitly_wait(5)
        pagina += 1
        exists = driver.execute_script("return document.querySelector('.c-empty-state') !== null;")
    return dinero_operaciones, dinero_fly, dinero_tomasso
        

total_dinero = recorrer_paginas()
print(f'Total dinero operaciones: {total_dinero[0]}\nTotal_fly: {total_dinero[1]}\nTotal_tomasso: {total_dinero[2]}')



driver.quit()