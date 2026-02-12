from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sutom import Constraints, SutomSolver

SUTOM_URL = "https://sutom.nocle.fr/#"

def _guess_firefox_binary_windows() -> str | None:
    common_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ]
    for p in common_paths:
        if Path(p).exists():
            return p

    pf = os.environ.get("ProgramFiles")
    if pf:
        cand = Path(pf) / "Mozilla Firefox" / "firefox.exe"
        if cand.exists():
            return str(cand)

    pf86 = os.environ.get("ProgramFiles(x86)")
    if pf86:
        cand = Path(pf86) / "Mozilla Firefox" / "firefox.exe"
        if cand.exists():
            return str(cand)

    return None

def build_driver(
    browser: str,
    headless: bool,
    firefox_binary: str | None,
    gecko_path: str | None,
    chromedriver_path: str | None,
):
    browser = browser.lower()
    if browser == "firefox":
        options = FirefoxOptions()
        if firefox_binary:
            options.binary_location = firefox_binary
        elif os.name == "nt":
            auto = _guess_firefox_binary_windows()
            if auto:
                options.binary_location = auto

        if headless:
            options.add_argument("-headless")
        service = FirefoxService(executable_path=gecko_path) if gecko_path else FirefoxService()
        driver = webdriver.Firefox(service=service, options=options)
        return driver

    elif browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1200,900")
        service = ChromeService(executable_path=chromedriver_path) if chromedriver_path else ChromeService()
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    else:
        raise ValueError("browser must be 'firefox' or 'chrome'")

def close_intro_popup(driver, wait: WebDriverWait):
    try:
        btn = wait.until(EC.element_to_be_clickable((By.ID, "panel-fenetre-bouton-fermeture-icone")))
        btn.click()
        return
    except Exception:
        pass

    selectors = [
        '[id^="panel-fenetre-bouton-fermeture-icone"]',
        '#panel-fenetre-bouton-fermeture-icone',
        'button[aria-label="Fermer"]',
    ]
    for sel in selectors:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, sel)
            if elem.is_displayed() and elem.is_enabled():
                elem.click()
                return
        except Exception:
            continue

def disable_grid_animations(driver):
    css = """
    <style id="sutom-no-anim">
      #grille * {
        transition: none !important;
        animation: none !important;
      }
    </style>
    """
    try:
        driver.execute_script("document.head.insertAdjacentHTML('beforeend', arguments[0]);", css)
    except Exception:
        pass


def get_grid_word_length_and_first_letter(driver, wait: WebDriverWait) -> tuple[int, str]:
    tr1 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="grille"]/table/tr[1]')))
    tds = tr1.find_elements(By.TAG_NAME, "td")
    length = len(tds)
    first_letter = tds[0].text.strip().lower()
    return length, first_letter


def focus_body(driver):
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
    except Exception:
        pass


def type_word(driver, word: str, typing_delay: float = 0.08):
    body = driver.find_element(By.TAG_NAME, "body")
    for ch in word:
        body.send_keys(ch)
        if typing_delay:
            time.sleep(typing_delay)
    body.send_keys(Keys.ENTER)

def clear_word(driver, word_len: int, typing_delay: float = 0.03):
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(word_len):
        body.send_keys(Keys.BACKSPACE)
        time.sleep(typing_delay)

def wait_row_result(driver, wait: WebDriverWait, row_index: int, word_len: int, timeout_s: float = 6.0) -> bool:
    start = time.time()
    xpath_row = f'//*[@id="grille"]/table/tr[{row_index}]'
    wait.until(EC.presence_of_element_located((By.XPATH, xpath_row)))

    while time.time() - start < timeout_s:
        try:
            tr = driver.find_element(By.XPATH, xpath_row)
            cells = tr.find_elements(By.TAG_NAME, "td")
            if len(cells) != word_len:
                time.sleep(0.1)
                continue

            result_count = 0
            for td in cells:
                cls = (td.get_attribute("class") or "").lower()
                if "resultat" in cls:
                    result_count += 1

            if result_count == word_len:
                return True

            time.sleep(0.15)

        except StaleElementReferenceException:
            time.sleep(0.1)
            continue

    return False

def parse_row_feedback(driver, row_index: int, retries: int = 6, wait_between: float = 0.15):
    xpath_row = f'//*[@id="grille"]/table/tr[{row_index}]'

    last_exc = None
    for _ in range(retries):
        try:
            tr = driver.find_element(By.XPATH, xpath_row)
            cells = tr.find_elements(By.TAG_NAME, "td")

            if not cells:
                time.sleep(wait_between)
                continue

            feedback = []
            for pos, td in enumerate(cells):
                letter = (td.text or "").strip().lower()
                cls = (td.get_attribute("class") or "").lower()

                if "bien-place" in cls:
                    status = "green"
                elif "mal-place" in cls:
                    status = "yellow"
                elif "non-trouve" in cls:
                    status = "gray"
                elif "resultat" in cls:
                    status = "gray"
                else:
                    last_exc = RuntimeError("feedback incomplet (animation en cours)")
                    time.sleep(wait_between)
                    raise StaleElementReferenceException()

                feedback.append((letter, status, pos))

            return feedback

        except StaleElementReferenceException as e:
            last_exc = e
            time.sleep(wait_between)

    raise RuntimeError(f"Impossible de lire le feedback (ligne {row_index}) après {retries} tentatives") from last_exc

def main():
    parser = argparse.ArgumentParser(description="SUTOM solver (Selenium + heuristique)")
    parser.add_argument("--browser", choices=["firefox", "chrome"], default="firefox", help="Navigateur à utiliser")
    parser.add_argument("--headless", action="store_true", help="Mode headless")
    parser.add_argument("--firefox-binary", default=None, help="Chemin firefox.exe (si non standard / portable)")
    parser.add_argument("--gecko-path", default=None, help="Chemin geckodriver (si nécessaire)")
    parser.add_argument("--chromedriver-path", default=None, help="Chemin chromedriver (si Chrome)")
    parser.add_argument("--dict", default="dictionnaire.txt", help="Chemin du dictionnaire (un mot par ligne)")
    parser.add_argument("--typing-delay", type=float, default=0.08, help="Délai entre frappes clavier (s)")
    parser.add_argument("--max-tries", type=int, default=6, help="Nombre max d’essais (SUTOM=6)")
    parser.add_argument("--disable-animations", action="store_true", help="Désactiver les animations de la grille")
    args = parser.parse_args()

    dict_path = Path(args.dict)
    if not dict_path.exists():
        print(f"[ERREUR] Dictionnaire introuvable : {dict_path.resolve()}")
        sys.exit(1)

    solver = SutomSolver(dict_path)
    constraints = Constraints()

    driver = None
    try:
        driver = build_driver(
            browser=args.browser,
            headless=args.headless,
            firefox_binary=args.firefox_binary,
            gecko_path=args.gecko_path,
            chromedriver_path=args.chromedriver_path,
        )
        wait = WebDriverWait(driver, 15)
        driver.get(SUTOM_URL)

        close_intro_popup(driver, wait)
        if args.disable_animations:
            disable_grid_animations(driver)

        focus_body(driver)

        word_len, first_letter = get_grid_word_length_and_first_letter(driver, wait)
        candidates = solver.candidates_for(word_len, startswith=first_letter)
        if not candidates:
            print("[ERREUR] Aucun candidat ne correspond à la longueur et à la première lettre.")
            return

        guess = solver.best_guess(candidates, constraints)
        print(f"[INFO] Essai 1 → {guess}")
        type_word(driver, guess, typing_delay=args.typing_delay)

        attempt = 1
        while attempt <= args.max_tries:
            ok = wait_row_result(driver, wait, attempt, word_len, timeout_s=6.0)
            if not ok:
                print("[AVERTISSEMENT] Mot non accepté (probable mot hors dico SUTOM). On essaie un autre.")
                clear_word(driver, word_len, typing_delay=0.03)

                if guess in candidates:
                    try:
                        candidates.remove(guess)
                    except ValueError:
                        pass
                if not candidates:
                    print("[ERREUR] Plus aucun candidat disponible.")
                    break
                guess = solver.best_guess(candidates, constraints)
                print(f"[INFO] Ré-essai {attempt} → {guess}")
                
                type_word(driver, guess, typing_delay=args.typing_delay)
                continue

            time.sleep(0.2)
            feedback = parse_row_feedback(driver, attempt)

            resume = "".join(
                {"green": "🟩", "yellow": "🟨", "gray": "⬜", "unknown": "❔"}[st] for _, st, _ in feedback
            )
            print(f"[INFO] Feedback {attempt} : {resume}  ({''.join(l for l,_,_ in feedback)})")

            if all(st == "green" for _, st, _ in feedback):
                print(f"[✅] Gagné en {attempt} essai(s) !")
                break

            constraints.update_from_feedback(feedback)
            candidates = solver.filter_candidates(candidates, constraints)
            if not candidates:
                print("[ERREUR] Plus aucun candidat après filtrage. Conflit de contraintes ?")
                break

            next_guess = solver.best_guess(candidates, constraints)
            attempt += 1
            if attempt <= args.max_tries:
                guess = next_guess
                print(f"[INFO] Essai {attempt} → {guess}")
                type_word(driver, guess, typing_delay=args.typing_delay)
            else:
                print("[ℹ️] Limite d’essais atteinte.")
                break

        print("[FIN] Session terminée.")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()