# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

browser = webdriver.Chrome()
browser.get('https://sutom.nocle.fr/#')

time.sleep(1)

btn = browser.find_element_by_id("panel-fenetre-bouton-fermeture-icone")
btn.click()

# //*[@id="grille"]/table/tr[1]
# //*[@id="grille"]/table/tr[1]/td[1]

tr = browser.find_element_by_xpath('//*[@id="grille"]/table/tr[1]')
all_td_by_xpath = tr.find_elements_by_xpath(".//*")

first_letter = browser.find_element_by_xpath('//*[@id="grille"]/table/tr[1]/td[1]').text

time.sleep(5)

# orange_letter = tr.get_attribute("mal-place resultat")

body = browser.find_element_by_tag_name('body')
body.send_keys("N")
body.send_keys("F")
body.send_keys("A")
body.send_keys("N")
body.send_keys("T")
body.send_keys(Keys.ENTER)
# Keys.ENTER

for elem in all_td_by_xpath:
        if (elem.get_attribute("class")):
                print(elem)


print(f"\nNombre de lettre : {len(all_td_by_xpath)}")
print(f"Première lettre : {first_letter}")
