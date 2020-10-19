import pandas as pd
import datetime
from selenium import webdriver

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
    #driver.get("https://www.lgl.bayern.de/gesundheit/infektionsschutz/infektionskrankheiten_a_z/coronavirus/karte_coronavirus/index.htm")
    #driver.find_element_by_xpath("//button[@onclick=\"exportTableToCSV('tabelle_04', '#tableLandkreise')\"]").click()

    #stand = pd.read_csv(file, nrows=0)
    stand = open(file, 'r')
    inzidenz = pd.read_csv(file, sep=";", decimal=",", skiprows=1)
    #print(stand.readline())
    #print(inzidenz)

    return stand, inzidenz


def main():
    # CSV von heute öffnen
    # TODO: Das muss noch umgeschrieben werden, so dass die letzte runtergeladene Datei geöffnet wird. Sonst gibts Probleme am WE oder morgens.
    aktuellerTag = datetime.datetime.now()
    aktuellerTag = aktuellerTag.strftime(format="%Y%m%d")

    file = "./csvs/tabelle_04_" + aktuellerTag + ".csv"
    print("Dateiname: ", file)

    stand, inzidenz = load_csv(file)

    print(stand.readline())
    lokaleInzidenz = inzidenz.loc[inzidenz['Landkreis/Stadt'] == LOCATION, :]
    #print(lokaleInzidenz.iloc[0])
    lokaleInzidenz = pd.Dataframe(lokaleInzidenz)
    print(lokaleInzidenz['7-Tage-Inzidenz pro 100.000 Einwohner'])


# starten, wenn kein Aufruf aus einem anderen Modul kommt, wo das Script importiert ist
if __name__ == "__main__":
    main()