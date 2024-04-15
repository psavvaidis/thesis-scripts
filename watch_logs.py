import sys
import time
import logging
import selenium
import selenium.webdriver
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
    try:
        selenium_driver = selenium.webdriver.Chrome(vv8_path)
        selenium_driver.get("https://airbnb.com")
    except Exception:
        pass

    class MyHandler(FileSystemEventHandler):

        def on_modified(self, event):
            selenium_driver.execute_script('() => return window')
            print(event)

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
