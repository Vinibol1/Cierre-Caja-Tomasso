from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import os
import time
import Interfaz
import Rappi
import MercadoPago
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
usuario = os.getlogin()
inicio = None
fin = None


options = webdriver.FirefoxOptions()
options.add_argument('-profile')
options.add_argument("/home/"+ usuario+"/.cache/mozilla/firefox/bam1bn0o.default-release")
service = Service(executable_path="/usr/local/bin/geckodriver")

driver = webdriver.Firefox(service=service, options=options)



inicio = time.time()
Interfaz.interfaz(driver)
   
print("Tiempo de ejecución:", fin - inicio)
driver.quit()
