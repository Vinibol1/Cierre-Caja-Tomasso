from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Configurar opciones para Chrome
options = webdriver.ChromeOptions()
# Opcional: Si necesitas usar un perfil específico
options.add_argument('user-data-dir=C:/Users/Tomasso/AppData/Local/Google/Chrome/User Data/Default')
options.add_argument('--disable-blink-features=AutomationControlled')

# Configurar el servicio para ChromeDriver
service = Service(ChromeDriverManager().install())

# Inicializar el controlador de Google Chrome
driver = webdriver.Chrome(service=service, options=options)

# Acceder a la página de MercadoPago
driver.get('https://www.mercadopago.com.ar/activities/1?period=yesterday')

# Esperar que los elementos se carguen
driver.implicitly_wait(120)

def sumar_dinero():
    # Encontrar todos los elementos con la clase ui-rowfeed-container
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
            elemento = li.find_element(By.CLASS_NAME, 'ui-rowfeed-title')
            # Verificar si el texto contiene la palabra "Pedido"
            if "Pedido" in elemento.text:
                cantidad_dinero = li.find_element(By.CLASS_NAME,'andes-money-amount__fraction')
                cantidad_centavos = li.find_element(By.CLASS_NAME,'andes-money-amount__cents')
                cantidad_dinero_sin_coma = cantidad_dinero.text.replace('.', '')
                print(cantidad_dinero)
                dinero_pedidos += float(cantidad_dinero_sin_coma) + float(cantidad_centavos.text)/100
            else:
                # Extraer la cantidad de dinero en "fracción" y "centavos"
                cantidad_dinero = li.find_element(By.CLASS_NAME,'andes-money-amount__fraction')
                cantidad_centavos = li.find_element(By.CLASS_NAME,'andes-money-amount__cents')

                # Limpiar la coma y sumar el valor total
                cantidad_dinero_sin_coma = cantidad_dinero.text.replace('.', '')
                dinero_operaciones += float(cantidad_dinero_sin_coma) + float(cantidad_centavos.text)/100
        except Exception as e:
            print(f"Error al extraer el valor del elemento: {e}")

    return dinero_operaciones, dinero_pedidos

# Llamar la función y mostrar el total
total_dinero = sumar_dinero()
print(f'Total dinero: {total_dinero[0]},Total_pedidos: {total_dinero[1]}')


# Cerrar el navegador
driver.quit()
