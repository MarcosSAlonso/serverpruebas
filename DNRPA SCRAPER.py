from playwright.sync_api import sync_playwright
import time

def runScraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.new_page()
        page.goto("https://www2.jus.gov.ar/dnrpa-site/#!/estimador")        
    
        time.sleep(2)

        resultados = request_info(page)

        if resultados:
            marca, modelo, anio = resultados

            print(f"Marca: {marca}")
            print(f"Modelo: {modelo}")
            print(f"Año: {anio}")

        browser.close()

def request_info(page):
    try:
        param = "TRANSFERENCIA"
        patente = "A211SDM"
        valor = "1"
        provincia = "BUENOS AIRES"

        page.select_option("#codigoTramite", param)
        time.sleep(2)

        #Enviamos patente-dominio
        page.click("#dominio", force=True)
        time.sleep(1)
        page.fill("#dominio", '')
        time.sleep(1)
        page.fill("#dominio", patente)

        #Enviamos valor declarado
        page.click("#cuerpo > div.ng-scope > div > form > div:nth-child(3) > div:nth-child(1) > div > input", force=True)
        time.sleep(1)
        page.fill("#cuerpo > div.ng-scope > div > form > div:nth-child(3) > div:nth-child(1) > div > input", '')
        time.sleep(1)
        page.fill("#cuerpo > div.ng-scope > div > form > div:nth-child(3) > div:nth-child(1) > div > input", valor)

        #Seleccionamos provincia
        time.sleep(2)
        page.select_option("#codigoProvincia", provincia)
        time.sleep(1)

        #Click continuar
        page.click("#cuerpo > div.ng-scope > div > form > div:nth-child(5) > button", force=True)
        time.sleep(2)

        #Guardamos lo obtenido
        Marca = page.inner_text("#cuerpo > div.ng-scope > div.panel.panel-info.ng-scope > div.panel-body > table > tbody > tr:nth-child(3) > td:nth-child(2)", timeout=5000)
        Modelo = page.inner_text("#cuerpo > div.ng-scope > div.panel.panel-info.ng-scope > div.panel-body > table > tbody > tr:nth-child(3) > td:nth-child(4)",timeout=5000)
        Anio = page.inner_text("#cuerpo > div.ng-scope > div.panel.panel-info.ng-scope > div.panel-body > table > tbody > tr:nth-child(4) > td:nth-child(4)", timeout=5000)

        return Marca, Modelo, Anio

    except Exception as e:
        print(f"Error obteniendo info de DNRPA: {e}")

runScraper()
