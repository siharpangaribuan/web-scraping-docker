from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from bs4 import BeautifulSoup
import json
from datetime import datetime
from selenium.common.exceptions import TimeoutException
import os
import logging

logging.basicConfig(
    level=logging.INFO,  # Level log minimum yang akan ditampilkan
    format='%(asctime)s - %(levelname)s - %(message)s'
)

FLIGHT_HISTORY_URL = "https://www.flightradar24.com/data/aircraft/"
LOGIN_URL = "https://www.flightradar24.com"
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
TIMEOUT = 10

def initialize_browser():
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver

def login_to_flightradar(driver):
    try:
        driver.get(LOGIN_URL)
        logging.info(f'Go to {LOGIN_URL}')
        time.sleep(5)
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div/div[3]/button[2]/span').click()
        time.sleep(5)
        # Clicking login button and entering credentials
        driver.find_element(By.XPATH, '//*[@id="auth-button"]/div').click()
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="headlessui-disclosure-panel-v-1"]/div/div/div/form/div[1]/div/input').send_keys(USERNAME)
        driver.find_element(By.XPATH, '//*[@id="headlessui-disclosure-panel-v-1"]/div/div/div/form/div[2]/div/input').send_keys(PASSWORD)
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="headlessui-disclosure-panel-v-1"]/div/div/div/form/button').click()
        logging.info('Successfully logged in')
        time.sleep(5)

    except Exception as e:
        logging.error(f'Error during login: {e}')
        raise

# Function to scrape flight history from the aircraft's page
def scrape_flight_history(driver, carrier, registration, start_date=None, end_date=None):
    logging.info(f"Scraping flight history for: {registration}")
    try:
        driver.get(f"{FLIGHT_HISTORY_URL}{registration}")
        wait = WebDriverWait(driver, TIMEOUT)
        # Load earlier flights if button exists
        load_earlier_flights(wait, driver,start_date)
        # Parse flight history table
        flights_history = parse_flight_history(driver, start_date, end_date)
        # Save flight history to a file
        save_flight_history_to_file(flights_history, carrier, registration)
    except Exception as e:
        logging.error(f"Error scraping {registration}: {e}")

# Function to load earlier flights by clicking the button multiple times
def load_earlier_flights(wait, driver, start_date):
    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table')
        if table is None:
            print("No flight history table found")
            break

        all_dates = []

        for row in table.select('tbody tr'):
            try:
                date = row.select('td')[2].text.strip()
                flight_date = datetime.strptime(date, "%d %b %Y")
                all_dates.append(flight_date)
            except (IndexError, ValueError):
                continue

        if any(d < start_date for d in all_dates):
            break

        try:
            element = wait.until(EC.element_to_be_clickable((By.ID, "btn-load-earlier-flights")))
            element.click()
            logging.info("Clicked 'Load earlier flights'")
            time.sleep(8)
        except TimeoutException:
            logging.info("No more earlier flights to load")
            break

# Function to parse the flight history table using BeautifulSoup
def parse_flight_history(driver, start_date=None, end_date=None):
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find('table')

    if table is None:
        logging.warning("No flight history table found during parsing")
        return []

    # Extract table headers and rows
    headers = [header.text.strip() for header in table.select('thead th')]
    rows = []

    for row in table.select('tbody tr'):
        data = [cell.text.strip() for cell in row.select('td')]
        flight_info = dict(zip(headers, data))

        # Parse the flight date from the relevant field (adjust the key as necessary)
        flight_date_str = flight_info.get('DATE')  # Replace 'Date' with the actual header name
        if flight_date_str:
            flight_date = datetime.strptime(flight_date_str, "%d %b %Y")  # Adjust format as needed

            # Check if the flight date is within the specified range
            if (start_date and flight_date < start_date) or (end_date and flight_date > end_date):
                continue  # Skip this flight if it's outside the date range

        rows.append(flight_info)

    return rows


# Function to save flight history to a JSON file
def save_flight_history_to_file(flight_history, carrier, registration):
    os.makedirs('json', exist_ok=True)
    filename = f'json/{carrier}_{registration}_flightHistory.json'
    with open(filename, 'w') as outfile:
        json.dump(flight_history, outfile, indent=4)
    logging.info(f"Saved flight history to {filename}")


# Main function to run the scraping process
def main():
      # Adjust the path to your geckodriver
    driver = initialize_browser()

    try:
        login_to_flightradar(driver)

        batik = [
            'PK-LAZ' ,'PK-LUH', 'PK-LUI', 'PK-LUG', 'PK-LUZ', 'PK-LZH',
       'PK-LBW', 'PK-LAI', 'PK-LAL', 'PK-LAQ', 'PK-LAT', 'PK-LAM',
       'PK-LZV', 'PK-LUF', 'PK-LUR', 'PK-LAF', 'PK-LUK', 'PK-LAO',
       'PK-LUW', 'PK-LUJ', 'PK-LUS', 'PK-BDF', 'PK-LUP', 'PK-LUQ',
       'PK-LUY', 'PK-LUO', 'PK-LUU', 'PK-LAW', 'PK-LUT', 'PK-LAY',
       'PK-LUV', 'PK-LAJ', 'PK-LDJ', 'PK-LDK', 'PK-BKF', 'PK-BKG',
       'PK-BKO', 'PK-BGF', 'PK-BKK', 'PK-BKL', 'PK-BKJ', 'PK-BKM',
       'PK-BGZ', 'PK-BLA', 'PK-BLB', 'PK-BKQ', 'PK-BKR', 'PK-BKY',
       'PK-BKP', 'PK-BKT', 'PK-BKU', 'PK-BKV', 'PK-BLC', 'PK-BLD']

        lion = ['PK-LFK', 'PK-LFG', 'PK-LJG', 'PK-LHZ', 'PK-LJV', 'PK-LJZ',
       'PK-LKK', 'PK-LKH', 'PK-LFZ', 'PK-LJR', 'PK-LJY', 'PK-LGO',
       'PK-LGP', 'PK-LHS', 'PK-LHY', 'PK-LOI', 'PK-LGK', 'PK-LHI',
       'PK-LFO', 'PK-LKP', 'PK-LKJ', 'PK-LKQ']

        wings = ['PK-WFH', 'PK-WFI', 'PK-WFJ', 'PK-WFK', 'PK-WJK']

        saj = ['PK-SAJ', 'PK-SAV', 'PK-SAT', 'PK-SAU', 'PK-SAW', 'PK-SAK',
       'PK-SAA', 'PK-SJJ', 'PK-SAE', 'PK-SAL', 'PK-SAM', 'PK-SJD',
       'PK-SJU', 'PK-SJA', 'PK-SAO', 'PK-SAQ', 'PK-SJG', 'PK-SAI',
       'PK-SJS', 'PK-SJW', 'PK-SAZ', 'PK-SJE', 'PK-SAC', 'PK-SJF',
       'PK-SGD', 'PK-SJV', 'PK-SJZ', 'PK-SJR', 'PK-STZ', 'PK-SAP',
       'PK-SAH', 'PK-STG', 'PK-SJP', 'PK-STF', 'PK-SAY', 'PK-SJL',
       'PK-SGB', 'PK-SJH', 'PK-STH', 'PK-SGA', 'PK-SJM', 'PK-SAG',
       'PK-STD', 'PK-STP', 'PK-STC', 'PK-SGC', 'PK-SJI', 'PK-SAS',
       'PK-STI', 'PK-STA', 'PK-STQ', 'PK-SJQ', 'PK-SJK', 'PK-STT']

        pelita = ['PK-PWC', 'PK-PWA', 'PK-PWD', 'PK-PWG', 'PK-PWE', 'PK-PWH',
       'PK-PWF', 'PK-PWI', 'PK-PWK', 'PK-PWL', 'PK-PWJ', 'PK-PWM', 'PK-PWN']

        jt_haji = ['PK-LEF', 'PK-LEG', 'PK-LEH', 'PK-LEW', 'PK-LER']

        # Define date range for filtering (format: YYYY-MM-DD)
        start_date = datetime.strptime('2025-05-01',"%Y-%m-%d")
        end_date = datetime.strptime('2025-05-31', "%Y-%m-%d")  # Example end date

        # Scrape flight history for each aircraft
        for fid in batik:
            time.sleep(3)
            scrape_flight_history(driver, "ID", fid, start_date, end_date)
        logging.info("Batik Done")

        for fjt in lion:
            time.sleep(3)
            scrape_flight_history(driver, "JT", fjt, start_date, end_date)
        logging.info("Lion Done")

        for fiw in wings:
            time.sleep(3)
            scrape_flight_history(driver, "IW", fiw, start_date, end_date)
        logging.info("Wings Done")

        for fiu in saj:
            time.sleep(3)
            scrape_flight_history(driver, "IU", fiu, start_date, end_date)
        logging.info("SAJ Done")

        for fip in pelita:
            time.sleep(3)
            scrape_flight_history(driver, "IP", fip, start_date, end_date)
        logging.info("Pelita Done")

        # for jht in jt_haji:
        #     time.sleep(SLEEP_INTERVAL)
        #     scrape_flight_history(driver, "HJ", jht, start_date, end_date)
        # print("Haji Done!")

        logging.info("All scraping tasks completed successfully")
    finally:
        driver.quit()  # Ensure browser is closed after scraping


# Run the main function
if __name__== '__main__':
    main()