# Web Scraper Flight Radar

This project is a web scraper that uses Selenium and BeautifulSoup to extract flight history data from [FlightRadar24](https://www.flightradar24.com). The scraper uses the Firefox browser to perform the scraping.

## Features

- **Automated login** to FlightRadar24.
- **Scraping flight history** for specific aircraft by registration number.
- **Saving flight history** in JSON format.
- **Supports date filtering** to download flight history within a specific date range.
- **Supports headless mode** (no graphical user interface) for efficiency.


## Installation and Running the Project

1. **Clone the repository**:
   ```bash
   git clone https://github.com/username/webscraper-flight-radar.git
   cd webscraper-flight-radar
2. **Build and run docker compose**:
    ```bash
    docker compose up --build