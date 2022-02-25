# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# from selenium.webdriver.chrome.options import Options
# options = Options()

# options = webdriver.ChromeOptions()
# options.add_argument("--remote-debugging-port=9225")

#browser = webdriver.Chrome()
browser = webdriver.Firefox()
browser.get('https://sutom.nocle.fr/#')

time.sleep(1)

btn = browser.find_element_by_id("panel-fenetre-bouton-fermeture-icone")
btn.click()

# //*[@id="grille"]/table/tr[1]
# //*[@id="grille"]/table/tr[1]/td[1]

tr = browser.find_element_by_xpath('//*[@id="grille"]/table/tr[1]')
all_td_by_xpath = tr.find_elements_by_xpath(".//*")

first_letter = browser.find_element_by_xpath('//*[@id="grille"]/table/tr[1]/td[1]').text

# time.sleep(5)

print(f"\nNombre de lettre : {len(all_td_by_xpath)}")
print(f"Première lettre : {first_letter}")

# orange_letter = tr.get_attribute("mal-place resultat")

body = browser.find_element_by_tag_name('body')
body.send_keys("N")
body.send_keys("F")
body.send_keys("A")
body.send_keys("N")
body.send_keys("T")
body.send_keys(Keys.ENTER)

time.sleep(2)
# Keys.ENTER


tr = browser.find_element_by_xpath('//*[@id="grille"]/table/tr[1]')
# all_td_by_xpath = tr.find_elements_by_xpath(".//*")
all_td_by_xpath = tr.find_elements_by_tag_name("td")

for elem in all_td_by_xpath:
        # if elem.find_element_by_class_name("")
        print(str(elem.text))
        print(str(elem.get_attribute('class')))
