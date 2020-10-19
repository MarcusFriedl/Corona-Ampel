import pandas as pd
import datetime
import locale
from selenium import webdriver

# Lokalisierung für die korrekte Erkennung der Werte
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Hier die entsprechende Stadt bzw. den Landkreis erfassen gem. den Eintragungen in der Liste
LOCATION = 'Miltenberg'

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
prefs = {"download.default_directory" : "./csvs/"}
options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome("./Chromedriver/chromedriver", options=options)

# Download des CSVs
def load_csv(file):
    # Webseite aufrufen und den Button zum Download des CSVs klicken
    driver.get("https://www.lgl.bayern.de/gesundheit/infektionsschutz/infektionskrankheiten_a_z/coronavirus/karte_coronavirus/index.htm")
    driver.find_element_by_xpath("//button[@onclick=\"exportTableToCSV('tabelle_04', '#tableLandkreise')\"]").click()

    stand = open(file, 'r')
    inzidenz = pd.read_csv(file, sep=";", decimal=",", skiprows=1, header=None)

    return stand, inzidenz


def main():
    # CSV von heute öffnen
    # TODO: Das muss noch umgeschrieben werden, so dass die letzte runtergeladene Datei geöffnet wird. Sonst gibts Probleme am WE oder morgens.
    aktuellerTag = datetime.datetime.now()
    aktuellerTag = aktuellerTag.strftime(format="%Y%m%d")

    file = "./csvs/tabelle_04_" + aktuellerTag + ".csv"
    print("Dateiname: ", file)

    stand, inzidenz = load_csv(file)

    lokaleInzidenz = inzidenz.loc[inzidenz[0] == LOCATION, :]
    lokaleInzidenz = pd.DataFrame(lokaleInzidenz)
    lokaleInzidenz.reset_index(drop=True, inplace=True)
    wert = lokaleInzidenz.loc[0, 5]
    wert = float(locale.atof(wert))

    if 35.0 <= wert < 50.0:
        farbe = 'gelb'
    elif wert >= 50.0:
        farbe = 'rot'
    else:
        farbe = 'grün'

    print("\nDer aktuelle Wert für " + LOCATION + ' ist: ' + str(wert) + "!")
    print("Die Corona-Ampel ist somit: " + farbe + "!")
    print(stand.readline())

    Ampelsteuerung(wert, farbe)

def Ampelsteuerung(wert, farbe):
    



# starten, wenn kein Aufruf aus einem anderen Modul kommt, wo das Script importiert ist
if __name__ == "__main__":
    main()