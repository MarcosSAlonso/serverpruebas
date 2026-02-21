from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import time
import pandas as pd

def runScraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.new_page()
        page.goto('https://secure.thetollroads.com/accounts/login')
        
        time.sleep(3)

        login(page)
    
        loadTolls(page)
        
        #excel_file = 'C:/Users/limit/Downloads/TRA_Sample.xlsx'
        #add_multiple_vehicles_from_excel(excel_file, page)

        time.sleep(5)
        browser.close()

def login(page):
    try:
        page.fill("#accountNum", "tollaid")
        page.fill("#password", "Tollaid2019T")
        page.click("#btn-submit", force=True)
        time.sleep(3)
        print("Login done!")
    except Exception as e:
        print("An exception occurred during login: {e}")

def loadTolls(page):
    try:
        today = datetime.now()
        seven_days = today - timedelta(days=7)

        first_datetime = seven_days.strftime("%m/%d/%Y")
        last_datetime = today.strftime("%m/%d/%Y")

        time.sleep(3)
        page.click("#main-content > div > div > app-sidebar > aside > li:nth-child(7) > a", force=True)

        time.sleep(3)
        print("Button clicked!")

        print("Now try to create report")
        try:
            time.sleep(3)
            page.click("text=Create Report")

            #Fill start date
            time.sleep(2)
            page.click("#fromDate", force=True)
            time.sleep(1)
            page.fill("#fromDate", '')
            time.sleep(1)
            page.fill("#fromDate", first_datetime)

            #Fill end date
            time.sleep(2)
            page.click("#toDate",force=True)
            time.sleep(1)
            page.fill("#toDate", '')
            time.sleep(1)
            page.fill("#toDate", last_datetime)

            time.sleep(2)
            page.click("#btc-download-menu", force=True)
            time.sleep(1)

            with page.expect_download(timeout=60000) as download_info:
                page.click("text=CSV")
            
            time.sleep(1)

            download = download_info.value
            file_name = f"Statement_TCA_{last_datetime.replace('/','')}.csv"
            download.save_as(f"C:/Users/limit/Downloads/{file_name}")
            print(f"Report downloaded in: {file_name}")
            print(f"Original path: {download.path()}")

        except Exception as e:
            print(f"Error creating report: {e}")

    except :
        print("Error trying to click on Statements & Activity")

def add_plate_from_excel(plate_data : dict, page, file_path):

    plate = plate_data['License Plate'].replace('.0', '').strip()
    state = plate_data['State'].strip().upper()
    year = plate_data['Year']
    make = plate_data['Make'].strip()

    yesterday = datetime.now() - timedelta(days=1)
    yesterday_fix = yesterday.strftime("%m/%d/%Y")

    try:
        page.click("#main-content > div > div > app-sidebar > aside > li:nth-child(5) > a", force=True)
        time.sleep(2)
        page.click('#main-content > div > div > main > app-information-dashboard > div > div > div > div > a', force=True)

        time.sleep(2)

        #Fill start date
        page.click("#start_date", force=True)
        time.sleep(1)
        page.fill("#start_date", '')
        time.sleep(1)
        page.type('#start_date', yesterday_fix, delay=50)

        #Fill license plate
        page.click("#plate", force=True)
        time.sleep(1)
        page.fill("#plate", '')
        time.sleep(1)
        page.fill('#plate', plate)

        #Confirm License plate
        page.click("#confirm_plate", force=True)
        time.sleep(1)
        page.fill("#confirm_plate", '')
        time.sleep(1)
        page.fill('#confirm_plate', plate)

        time.sleep(2)

        #Select state
        state_mapping = {
            'UT': "UTAH",  # Utah
            'CA': "CALIFORNIA",   # California
            'TX': "TEXAS",  # Texas
            'FL': "FLORIDA",   # Florida
            'TN': "TENNESSEE",  # Tennessee
            'AL': "ALABAMA"    # Alabama
            # Add more states as needed
        }

        page.select_option("#state", value=state)
        time.sleep(1)

        #Year
        page.click("#year", force=True)
        time.sleep(1)
        page.fill("#year", '')
        time.sleep(1)
        page.fill("#year", str(year))

        #Make
        page.click("#make", force=True)
        time.sleep(1)
        page.fill('#make', '')
        time.sleep(1)
        page.fill("#make", make)

        #Model
        page.click("#model", force=True)
        time.sleep(1)
        page.fill("#model", '')
        time.sleep(1)
        page.fill("#model", "OTHER")

        time.sleep(2)

        #Sticker and confirm
        page.click("#sticker", force=True)
        time.sleep(2)
        page.click("#btn-close-main", force=True)
        time.sleep(7)
                  
    except Exception as e:
        raise Exception(f"Error adding plates : {e}")

def read_excel_file(file_path : str):
    try:
        df = pd.read_excel(file_path)
        print(f'Total de filas en el Excel: {len(df)}')
        
        #Filtrar solo las filas que no han sido agregadas
        if 'Added' in df.columns:
            # Mostrar el estado actual de la columna Added
            print(f'Estado de la columna Added:')
            print(df['Added'].value_counts(dropna=False))
            
            #Filtrar placas que NO están marcadas como 'Yes'
            #Incluye: NaN (vacío), 'No', False, '', etc.
            df_filtered = df[df['Added'].fillna('').astype(str).str.upper() != 'YES']
            
            print(f'Placas filtradas (no marcadas como Yes): {len(df_filtered)}')
            
            #Mostrar las placas que se van a procesar
            if len(df_filtered) > 0:
                print('Placas a procesar:')
                for idx, row in df_filtered.iterrows():
                    print(f"  - {row['License Plate']} (Added: '{row['Added']}')")
        else:
            print('No se encontró la columna "Added" en el Excel')
            df_filtered = df
        
        #Convertir a lista de diccionarios
        plate_data_list = df_filtered.to_dict('records')
        print(f'Se encontraron {len(plate_data_list)} placas para procesar')
        return plate_data_list
    except Exception as e:
        print(f'Error leyendo el archivo Excel: {e}')
        return []
    
def add_multiple_vehicles_from_excel(file_path, page):
    """Procesa múltiples vehículos desde un archivo Excel"""
    plate_data_list = read_excel_file(file_path)
    errors = []
    
    for plate_data in plate_data_list:
        plate = plate_data.get('License Plate', 'Unknown')
        try:
            print(f'Adding plate: {plate}')
            add_plate_from_excel(plate_data, page, file_path=file_path)
            print(f'Placa {plate} agregada exitosamente!')
            
        except Exception as e:
            print(f'Error agregando placa {plate}: {e}')
            errors.append((plate, str(e)))

    if errors:
        print('Resumen de errores:')
        for plate, error in errors:
            print(f"- {plate}: {error}")

runScraper()