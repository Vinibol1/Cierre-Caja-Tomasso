from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By



options = webdriver.FirefoxOptions()
options.add_argument('-profile')
options.add_argument(r'/home/tobias/.cache/mozilla/firefox/bam1bn0o.default-release')
service = Service(GeckoDriverManager().install())

driver = webdriver.Firefox(service=service, options=options)
driver.get('https://www.mercadopago.com.ar/activities/1?period=today')
driver.implicitly_wait(5)

def sumar_dinero():
        li_elements = driver.find_elements(By.CLASS_NAME, 'ui-rowfeed-container')
        dinero = 0

        for li in li_elements:
                cantidad_dinero = li.find_element(By.CLASS_NAME,'andes-money-amount__fraction')
                cantidad_dinero_sin_coma = cantidad_dinero.text.replace('.', '')
                dinero += float(cantidad_dinero_sin_coma)

        return dinero

total_dinero = sumar_dinero()
print(total_dinero)
driver.implicitly_wait(5)

# Cierra el navegador
driver.quit()