# 📘 SUTOM Solver – (Selenium)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A.svg?logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![OS](https://img.shields.io/badge/OS-Windows%20%7C%20Linux-blue.svg)](#)
[![License: GPL](https://img.shields.io/badge/License-GPL-blue.svg)](LICENSE)

Un bot Python utilisant **Selenium** et une stratégie intelligente pour **résoudre automatiquement SUTOM** (https://sutom.nocle.fr).  
Il saisit les mots, lit les feedbacks (🟩🟨⬜), met à jour les contraintes et sélectionne les meilleurs candidats jusqu’à la solution.

---

![Aperçu de l’outil](démo.gif)

---

## ✨ Fonctionnalités

- Automatisation complète via **Selenium** (Firefox ou Chrome)
- Stratégie “best guess” par **fréquence de lettres** et **positions non figées**
- Gestion des contraintes : **verts**, **jaunes**, **gris**, occurrences minimales, **positions interdites**
- Anti‑stale robuste (DOM réactif / animations)
- Option pour **désactiver les animations CSS**
- Mode **headless**
- **Windows** et **Linux** supportés

---

## 📦 Installation

1. Cloner le repo et placer à la racine avec la commande : 
```git
git clone https://github.com/PierreChrd/py-sutom-cheat
```
2. Installer la dépendance Python :
```
pip install -r requirements.txt
```
3. Installer le WebDriver :
- **Firefox** : geckodriver (https://github.com/mozilla/geckodriver/releases)
- **Chrome** : chromedriver (https://googlechromelabs.github.io/chrome-for-testing/)

---

## ▶️ Utilisation

### Firefox (installation standard)
```
python scrap.py --browser firefox --gecko-path geckodriver.exe
```
### Firefox avec animations désactivées
```
python scrap.py --browser firefox --gecko-path geckodriver.exe --disable-animations
```
### Chrome
```
python scrap.py --browser chrome --chromedriver-path "C:\Tools\chromedriver.exe" --dict dictionnaire.txt
```
### Mode headless (sans fenêtre)
```
python scrap.py --browser firefox --headless --gecko-path geckodriver.exe
```
> Astuce : si `geckodriver.exe` / `chromedriver` est dans ton **PATH**, tu peux omettre `--gecko-path` / `--chromedriver-path`.  
> `--firefox-binary` n’est nécessaire que si Firefox est portable ou installé dans un chemin non standard.

---

## ⚙️ Options CLI

- `--browser firefox|chrome` : choix du navigateur  
- `--gecko-path` / `--chromedriver-path` : chemin vers le driver  
- `--firefox-binary` : chemin vers `firefox.exe` si installation non standard/portable  
- `--headless` : exécution sans fenêtre  
- `--dict` : chemin du fichier dictionnaire  
- `--typing-delay` : délai entre frappes (par défaut 0.08 s)  
- `--max-tries` : essais max (par défaut 6)  
- `--disable-animations` : désactive les animations CSS de la grille

---

## 📂 Structure
```
.
├── scrap.py          # Automatisation Selenium
├── sutom.py          # Moteur de filtrage + heuristique
├── dictionnaire.txt  # Liste de mots (1 par ligne)
└── README.md
```

---

## 🧠 Fonctionnement

1. Lecture **taille du mot** et **première lettre** dans la grille SUTOM  
2. Génération de candidats depuis `dictionnaire.txt`  
3. Choix du **meilleur mot** via score de fréquences (bonus positions non figées)  
4. Saisie automatisée du mot  
5. Lecture du **feedback** (🟩🟨⬜)  
6. Mise à jour des **contraintes**  
7. Filtrage des candidats et répétition jusqu’à succès ou épuisement des essais

---

## 📝 Dictionnaire

- 1 mot par ligne  
- minuscules  
- idéalement sans accents  
- plus il est pertinent, plus le solveur est efficace

---

## ❗ Dépannage rapide

- **Firefox introuvable** → préciser `--firefox-binary "C:\Program Files\Mozilla Firefox\firefox.exe"`  
- **StaleElementReferenceException** → lancer avec `--disable-animations`  
- **Mot refusé par SUTOM** → le bot réessaie automatiquement avec un autre candidat

---

## 📄 Licence


Ce projet est distribué sous licence **GNU GPL**.  
Voir le fichier `LICENSE` pour les détails.

---

## 🤝 Contributions

Les contributions sont les bienvenues ! Ouvre une **issue** ou une **pull request** pour proposer des améliorations.

> [Cet autre script](https://github.com/Gyrfalc0n/SUTOM-Resolver/) fait par [Gyrfalc0n](https://github.com/Gyrfalc0n/) résoud également le jeu de la même manière 🙏.