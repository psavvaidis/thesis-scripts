#type: ignore

import time
import sys
from threading import Timer
import os
import re
import logging
import selenium
import selenium.webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from selenium.common.exceptions import TimeoutException

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler


if __name__ == "__main__":
    
    # logging setup
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = '.'
    website = sys.argv[1] # if len(sys.argv) > 1
    full_url = 'https://www.'+website


    # Selenium Setup
    # # Set VV8 as default browser
    vv8_path = "/opt/chromium.org/chromium/chrome"

    # Set Chrome options
    selenium_options = Options()
    # selenium_options.add_argument("start-maximized")
    selenium_options.add_argument("--no-sandbox")
    selenium_options.add_argument("--headless=new")
    # selenium_options.add_argument("--screenshot")
    # selenium_options.add_argument("--timeout=30000")
    # selenium_options.add_argument("--virtual-time-budget=30000")
    # selenium_options.add_argument('--user-data-dir=/tmp')
    selenium_options.add_argument("--load-extension=/data/ConsentOMatic/Extension")
    # selenium_options.add_argument('--disable-dev-shm-usage')
    selenium_options.binary_location = vv8_path
    selenium_options.set_capability('pageLoadStrategy', 'none')
    # selenium_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # selenium_options.add_experimental_option('useAutomationExtension', False)
    # service = selenium.webdriver.ChromeService(port=80)
    selenium_driver = selenium.webdriver.Chrome(options=selenium_options)
    try:
        # Selenium Stealth settings
        # stealth(selenium_driver,
        #     languages=["en-US", "en"],
        #     vendor="Google Inc.",
        #     platform="Win32",
        #     webgl_vendor="Intel Inc.",
        #     renderer="Intel Iris OpenGL Engine",
        #     fix_hairline=True,
        # )
        # selenium_driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": """
        #         Object.defineProperty(navigator, 'webdriver', {
        #         get: () => undefined
        #         })
        #     """
        #     })
        # selenium_driver.execute_cdp_cmd("Page.removeScriptToEvaluateOnNewDocument", {"identifier":"1"})

        # js = """
        #     let objectToInspect = window,
        #     result = [];
        #     while(objectToInspect !== null)
        #         { result = result.concat(Object.getOwnPropertyNames(objectToInspect));
        #         objectToInspect = Object.getPrototypeOf(objectToInspect); }
        #     result.forEach(p => p.match(/.+_.+_(Array|Promise|Symbol)/ig)
        #         &&delete window[p]&&console.log('removed',p))
        # """
        # selenium_driver.execute_cdp_cmd("Page.removeScriptToEvaluateOnNewDocument", {"source":js})
        selenium_driver.get(full_url)
        # print(selenium_driver.inspect)
        # 
        # Timer(10, lambda _: selenium_driver.close())
        # Timer.start()
    except Exception as e:

        print("selenium exception: ")
        # selenium_driver.quit()
    



    class MyHandler(FileSystemEventHandler):

        properties = []        
        lines_counted = 0

        def on_modified(self, event):
            try:
                # WebDriverWait(selenium_driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                # print(event)
                with open(event.src_path, "r") as f:
                    # logging.info(f"Going for {event.src_path}")
                    read_lines = f.readlines()
                    new_lines_counted = len(read_lines)
                    last_lines = read_lines[(self.lines_counted - new_lines_counted):] if (self.lines_counted - new_lines_counted) < 0 else []
                    self.lines_counted = new_lines_counted

                    for last_line in last_lines:
                        try:
                            if re.match("s.", last_line) is not None:
                                logging.info("New set detected")
                                # logging.info("Last Line: %s", last_line)
                                # logging.info(last_line)
                                last_line_words = last_line.split(":")
                                set_object = last_line_words[-3].split(',')[1].replace("}","")
                                set_property = last_line_words[-2].replace("\"","")
                                set_value = last_line_words[-1].replace("\"","")
                                set_object = "window" if set_object == "Window" else set_object
                                try:
                                    # logging.info(f"about to run return {set_object}.{set_property}")
                                    window_object = selenium_driver.execute_script(f'if( typeof {set_object}.{set_property} == "object"){{return JSON.stringify({set_object}.{set_property})}} else {{return {set_object}.{set_property}.toString()}}')
                                    # logging.info(f"window object Returned {window_object}")
                                    self.properties.append(f"{set_object}.{set_property}: Log value: {set_value}, Retrieved Value: {window_object}")
                                    # logging.info(f"Confirm that in {set_object}.{set_property}, the value {set_value} was written")
                                except Exception as e:
                                    logging.error("window object read exception: ")
                                    self.properties.append(f"{set_object}.{set_property}: Log value: {set_value}, Retrieved Value: not retrieved")
                                # if window_object:
                                #     # if window_object == set_value:
                                # self.properties.append(f"{set_object}.{set_property}: {set_value}")
                                # logging.info(f"Confirm that in {set_object}.{set_property}, the value {set_value} was written")
                                # print(window_object)
                        except Exception as e:
                            print(f"Line read exception: ")
            except Exception as e:
                print("Watchdog Exception: ")
                # selenium_driver.quit()

    # Watchdog Setup
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    website_file_friendly = website.replace(".","_")
    
    try:
        WebDriverWait(selenium_driver, 30).until(EC.presence_of_element_located(('id', 'imaginary_element')))
        print("Element found")
        # time.sleep(5)
        # while True:
        #     time.sleep(1)
            # continue
    except TimeoutException as e:
        print("Exception caught")
    except KeyboardInterrupt:
        with open(f"./{website_file_friendly}_properties_report.txt", "w") as fp:
            fp.write("\n".join(event_handler.properties))
        # selenium_driver.quit()
        # print(event_handler.properties)
    except Exception as e:
        print("Overall Exception: ")
    finally:
        with open(f"./{website_file_friendly}_properties_report.txt", "w") as fp:
            fp.write("\n".join(event_handler.properties))
    
        observer.stop()
        observer.join()
    
    selenium_driver.quit()
        