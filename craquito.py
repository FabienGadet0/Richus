import time
from undetected_chromedriver import Chrome, ChromeOptions
from selenium import webdriver
from selenium_stealth import stealth
import random

if __name__ == "__main__":
    from multiprocessing import freeze_support

    options = webdriver.ChromeOptions()

    # Add user-agent rotation
    user_agents = [
        # Your list of user agents goes here
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        # More user agents
    ]
    user_agent = random.choice(user_agents)
    options.add_argument("--headless")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--auto-open-devtools-for-tabs")
    options.add_argument("--disable-popup-blocking")

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(options=options)

    # Apply stealth settings to the driver
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    freeze_support()

    print("Doing stuff")
    driver.execute_script("window.open('https://www.vulbis.com', '_blank')")
    time.sleep(15)
    driver.switch_to.window(driver.window_handles[1])
    # driver.get("https://www.vulbis.com/")
    # time.sleep(30)  # Wait for Cloudflare to possibly redirect

    driver.save_screenshot("screenshotA.png")
    print("ok finished")
    driver.quit()
