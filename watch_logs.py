import sys
import time
import logging
import selenium
import selenium.webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler


if __name__ == "__main__":
    # logging setup
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    # Selenium Setup
    # # Set VV8 as default browser
    vv8_path = "/opt/chromium.org/chromium/chrome"

    # Set Chrome options
    selenium_options = Options()
    selenium_options.add_argument('--no-sandbox')
    selenium_options.add_argument('--headless=new')
    # selenium_options.add_argument('--timeout=300000')
    selenium_options.add_argument('--virtual-time-budget=30000')
    selenium_options.add_argument('--user-data-dir=/tmp')
    selenium_options.add_argument('--disable-gpu')
    selenium_options.add_argument('--disable-dev-shm-usage')
    selenium_options.binary_location = vv8_path

    try:
        selenium_driver = selenium.webdriver.Chrome(options=selenium_options)
        selenium_driver.get("https://google.com")
        # WebDriverWait(selenium_driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception as e:
        print(e)
        selenium_driver.quit()
    # finally:
    #     selenium_driver.quit()

    class MyHandler(FileSystemEventHandler):

        def on_modified(self, event):
            try:
                WebDriverWait(selenium_driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                window_object = selenium_driver.execute_script('return window')
                print(window_object)
            except Exception as e:
                print(e)
                selenium_driver.quit()

    # Watchdog Setup
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
