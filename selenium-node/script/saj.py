from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time
from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging
import os

logging.basicConfig(
    level=logging.INFO, # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
FLIGHT_HISTORY_URL = "https://www.flightradar24.com/data/aircraft/"
LOGIN_URL = "https://www.flightradar24.com"
USERNAME = ""
PASSWORD = ""
TIMEOUT = 10  
SLEEP_INTERVAL = 2

def init_driver():
    options = Options()
    # options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    options.set_capability("se:nodeLabels", ["firefox", "node3"])

    driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",options=options)
    driver.maximize_window()
    return driver


def login_to_flightradar(driver):
    try:
        driver.get(LOGIN_URL)
        logging.info(f'Navigated to {LOGIN_URL}')

        wait = WebDriverWait(driver, TIMEOUT)

        # Terima cookie (jika muncul)
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/div/div/div[3]/button[2]/span')))
            cookie_btn.click()
            logging.info("Clicked accept")
        except TimeoutException:
            logging.info("No accept button found")

        # Klik tombol login
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "auth-button")))
        login_button.click()
        logging.info("Clicked login button")

        # Isi form login
        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "props.name").send_keys(PASSWORD)

        # Klik submit
        submit_button = driver.find_element(By.XPATH, "//*[@id='headlessui-disclosure-panel-v-1']/div/div/div/form/button")
        submit_button.click()
        logging.info("Submitted login form")
        # Tunggu sampai login selesai
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[2]/div[2]/div[2]/button/div/span")))
        logging.info("Login success")
    except Exception as e:
        logging.error(f"Error during login: {e}")
        raise


# Function to load earlier flights by clicking the button multiple times
def load_earlier_flights(wait, driver, start_date):
    while True:
        try:
            # Tunggu tabel tersedia
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table')

            if not table:
                logging.warning("No flight table found")
                break

            # Ambil semua tanggal dari kolom ke-3
            rows = table.select('tbody tr')
            dates = []
            for row in rows:
                try:
                    date_text = row.select('td')[2].text.strip()
                    flight_date = datetime.strptime(date_text, "%d %b %Y")
                    dates.append(flight_date)
                except (IndexError, ValueError):
                    continue

            # Stop jika tanggal terlama sudah lebih kecil dari start_date
            if not dates:
                logging.warning("No dates parsed from table rows")
                break
            if min(dates) < start_date:
                logging.info("Reached flights before start_date")
                break

            # Klik tombol 'Load earlier flights' jika masih ada
            try:
                load_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-load-earlier-flights")))
                load_button.click()
                logging.info("Clicked 'Load earlier flights'")
                time.sleep(5)  # bisa diturunkan jika koneksi cepat
            except TimeoutException:
                logging.info("No more earlier flights to load")
                break

        except Exception as e:
            logging.error(f"Error during loading earlier flights: {e}")
            break

# Function to parse the flight history table using BeautifulSoup
def parse_flight_history(driver, start_date=None, end_date=None):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table")

    if not table:
        logging.warning("No flight history table found")
        return []

    headers = [th.get_text(strip=True) for th in table.select("thead th")]
    rows = []

    for tr in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]

        # Skip jika kolom tidak lengkap
        if len(cells) != len(headers):
            continue

        flight = dict(zip(headers, cells))

        date_str = flight.get("DATE") or flight.get("Date") or cells[2]
        try:
            flight_date = datetime.strptime(date_str, "%d %b %Y")
        except ValueError:
            continue

        # Filter berdasarkan tanggal jika diset
        if start_date and flight_date < start_date:
            continue
        if end_date and flight_date > end_date:
            continue

        flight["flight_date_obj"] = flight_date.strftime("%Y-%m-%d")  # opsional
        rows.append(flight)

    return rows


# Function to save flight history to a JSON file
def save_flight_history_to_file(flight_history, carrier, registration):
    os.makedirs('data', exist_ok=True) 
    filename = f'data/{carrier}_{registration}_flightHistory.json'
    with open(filename, 'w') as outfile:
        json.dump(flight_history, outfile, indent=4)
    logging.info(f"Saved flight history to {filename}")


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

# Main function to run the scraping process
def main_saj():

    driver = init_driver()
    logging.info("Initialized browser with Selenium hoost")
    driver.implicitly_wait(TIMEOUT)  # Set implicit wait for elements to load
    logging.info("Starting flight history scraping...")

    try:
        login_to_flightradar(driver)

        saj = ['PK-SAJ', 'PK-SAV', 'PK-SAT', 'PK-SAU', 'PK-SAW', 'PK-SAK',
       'PK-SAA', 'PK-SJJ', 'PK-SAE', 'PK-SAL', 'PK-SAM', 'PK-SJD',
       'PK-SJU', 'PK-SJA', 'PK-SAO', 'PK-SAQ', 'PK-SJG', 'PK-SAI',
       'PK-SJS', 'PK-SJW', 'PK-SAZ', 'PK-SJE', 'PK-SAC', 'PK-SJF',
       'PK-SGD', 'PK-SJV', 'PK-SJZ', 'PK-SJR', 'PK-STZ', 'PK-SAP',
       'PK-SAH', 'PK-STG', 'PK-SJP', 'PK-STF', 'PK-SAY', 'PK-SJL',
       'PK-SGB', 'PK-SJH', 'PK-STH', 'PK-SGA', 'PK-SJM', 'PK-SAG',
       'PK-STD', 'PK-STP', 'PK-STC', 'PK-SGC', 'PK-SJI', 'PK-SAS',
       'PK-STI', 'PK-STA', 'PK-STQ', 'PK-SJQ', 'PK-SJK', 'PK-STT']

        # Define date range for filtering (format: YYYY-MM-DD)
        start_date = datetime.strptime('2025-04-30', "%Y-%m-%d")  # Example start date
        end_date = datetime.strptime('2025-05-31', "%Y-%m-%d")  # Example end date

        # Scrape flight history for each aircraft
        for fiu in saj:
            time.sleep(SLEEP_INTERVAL)
            scrape_flight_history(driver, "IU", fiu, start_date, end_date)
        logging.info("SAJ Done")

        
        logging.info("All scraping tasks completed successfully")
    finally:
        driver.quit()  # Ensure browser is closed after scraping

