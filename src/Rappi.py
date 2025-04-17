
from selenium.webdriver.common.by import By
import time

def modificar_fecha(fecha):
        return fecha.strftime('%d/%m/%Y')

def Pagina_rappi(driver,fecha_seleccionada):
        driver.get("https://aliados.rappi.com/sales-summary")
        driver.implicitly_wait(120)
        time.sleep(2)
        driver.execute_script("return document.getElementsByClassName('MuiButtonBase-root MuiButton-root jss108 jss105 jss115 jss118 MuiButton-outlined MuiButton-outlinedPrimary')[0].click()")
        tiendas = driver.execute_script("""return document.querySelectorAll('.MuiFormGroup-root input[type="radio"]');""")
        texto_dinero = []
        fecha_seleccionada = modificar_fecha(fecha_seleccionada)
        driver.execute_script("""
                let input = document.getElementsByClassName("MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedEnd MuiOutlinedInput-inputAdornedEnd")[1];
                
                if (input) {
                        let valor = '""" + str(fecha_seleccionada) + """';
                        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        nativeInputValueSetter.call(input, valor);

                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                }
                """)
        for i in range(len(tiendas)):
                driver.execute_script("return document.getElementsByClassName('MuiButtonBase-root MuiButton-root jss108 jss105 jss115 jss118 MuiButton-outlined MuiButton-outlinedPrimary')[0].click()")
                driver.execute_script("""document.querySelectorAll('.MuiFormGroup-root input[type="radio"]')["""+str(i)+"""].click()""")
                time.sleep(1)
                driver.find_element(By.XPATH, """//button[.//span[contains(text(), "Aplicar filtros")]]""").click()
                time.sleep(1)
                try:
                        dinero = driver.execute_script("""
                        return (document.evaluate("//div[contains(text(), 'Total con descuentos')]", document, null, 9, null) || {}).singleNodeValue.textContent;
                        """)
                        if dinero == "Total acumulado: -":
                                dinero = "0"
                        else:
                                dinero = dinero[23:].replace(".","")
                        texto_dinero.append(dinero)
                except:
                        dinero = driver.execute_script("""
                return (document.evaluate("//div[contains(text(), 'Total acumulado')]", document, null, 9, null) || {}).singleNodeValue.textContent;
                        """)
                        print(dinero)
                        if dinero == "Total acumulado: -":
                                dinero = "0"
                        else:
                                dinero = dinero[18:].replace(".","")
                        texto_dinero.append(dinero)

                if texto_dinero[i] == "":
                        texto_dinero[i] = "0"
        return texto_dinero
