from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


def do_one_trans(driver, text):
    print("Translate text of length:", len(text))
    input_box = driver.find_element(By.NAME, "source")
    input_box.click()
    input_box.send_keys(Keys.COMMAND, 'a')
    input_box.send_keys(Keys.DELETE)

    input_box.send_keys(text)
    print("Wait for finish...")
    target = driver.find_element(By.NAME, "target")
    result = ""
    last_result = ""
    while True:
        last_result = result
        result = target.text
        if last_result == result and len(result) > 0:
            break
        time.sleep(5)
    paragraphs = target.find_elements(By.TAG_NAME, "p")
    joined_text = ""
    for paragraph in paragraphs:
        joined_text += paragraph.text + "\n"
    input_box.click()
    input_box.send_keys(Keys.COMMAND, 'a')
    input_box.send_keys(Keys.DELETE)
    time.sleep(2)
    print("Length after translation:", len(joined_text))
    return joined_text

def translate_with_deepl(text):
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Safari()
    driver.get("https://www.deepl.com/translator")

    time.sleep(5)

    language_selector = driver.find_element(By.XPATH, "//button[@data-testid='translator-target-lang-btn']")
    language_selector.click()

    target_language_option = driver.find_element(By.XPATH, "//button[@data-testid='translator-lang-option-zh']")
    target_language_option.click()

    paragraphs = text.split('\n')
    length = 0
    batch = []
    results = []
    for p in paragraphs:
        if length + len(p) < 1500:
            batch.append(p)
            length += len(p)+1
        else:
            origin = '\n'.join(batch)
            if len(origin) > 1500:
                print("Translate length cannot exceed 1500!")
            trans = do_one_trans(driver, origin)
            results.append(trans)
            batch = [p]
            length = len(p)
            continue
    # do the last part
    if length > 0:
        trans = do_one_trans(driver, '\n'.join(batch))
        results.append(trans)
    
    driver.quit()
    print("Total translation times:", len(results))
    chinese_text = '\n'.join(results)
    return chinese_text