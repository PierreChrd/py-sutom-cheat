# pip install selenium

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from sutom import *
import time
import random

# from selenium.webdriver.chrome.options import Options
# options = Options()

# options = webdriver.ChromeOptions()
# options.add_argument("--remote-debugging-port=9225")

#browser = webdriver.Chrome()

def complet_word(word):
    body = browser.find_element_by_tag_name('body')
    for letter in word:
            time.sleep(0.1)
            body.send_keys(letter)

    body.send_keys(Keys.ENTER)
    time.sleep(3)

options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
browser = webdriver.Firefox(executable_path=r'geckodriver.exe', options=options)
browser.get('https://sutom.nocle.fr/#')

time.sleep(1)

btn = browser.find_element_by_id("panel-fenetre-bouton-fermeture-icone")
btn.click()

def main_loop(index = 1, list = None):

    # //*[@id="grille"]/table/tr[1]
    # //*[@id="grille"]/table/tr[1]/td[1]

    xpath = '//*[@id="grille"]/table/tr[' + str(index) + ']'
    tr = browser.find_element_by_xpath(xpath)
    all_td_by_xpath = tr.find_elements_by_xpath(".//*")
    if index ==1:
        first_letter = browser.find_element_by_xpath('//*[@id="grille"]/table/tr[1]/td[1]').text

        # time.sleep(5)
        size = len(all_td_by_xpath)

        print(f"\nNombre de lettre : {size}")
        print(f"Première lettre : {first_letter}")

        word = get_first_word(size, first_letter)
        print(word)
        # orange_letter = tr.get_attribute("mal-place resultat")

        body = browser.find_element_by_tag_name('body')
        complet_word(word)

    tr = browser.find_element_by_xpath(xpath)
    # all_td_by_xpath = tr.find_elements_by_xpath(".//*")
    all_td_by_xpath = tr.find_elements_by_tag_name("td")
    dict = {}
    for i, elem in enumerate(all_td_by_xpath):
            # if elem.find_element_by_class_name("")
            print(str(elem.text))
            css_class = str(elem.get_attribute('class'))
            print(css_class)
            if css_class == "bien-place resultat":
                dict[i] = (str(elem.text).lower(), 'red', i)
            elif css_class == "mal-place resultat":
                dict[i] = (str(elem.text).lower(), 'orange')
            elif css_class == "non-trouve resultat":
                dict[i] = (str(elem.text).lower(), '')

    print(dict)
    if index == 1:
        print('EWAAAA')
        result = dict_to_words(dict)
        print('================')
        print(result)
        print('================')
        complet_word(random.choice(result))
    else:
        result = dict_to_words_with_array(dict ,list)
        print(result)
        r = random.choice(result)
        for ind, elem in enumerate(result):
            if elem ==r:
                result.pop(ind)
        complet_word(r)

    main_loop(index + 1, list = result)
main_loop()
