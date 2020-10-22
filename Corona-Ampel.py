import pandas as pd
import datetime
import locale
import os
import time
import json
import requests
import urllib.request
from selenium import webdriver

# Configuration
# Lokalisierung für die korrekte Erkennung der Werte
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Hier die entsprechende Stadt bzw. den Landkreis erfassen gem. den Eintragungen in der Liste
LOCATION = 'Miltenberg'

# Dateipfad, wo die CSVs vom LGL abgelegt werden sollen
PATH = './csvs/'

# Läuft das Script auf dem RPi und ist die Ampel, die Digitalanzeige und/oder die Matrix aktiviert (True/False)?
RaspberryPi_Ampel = False
LED_pins = [31, 32, 33]
RaspberryPi_Digit = False
RaspberryPi_Matrix = False

if RaspberryPi_Ampel == True | RaspberryPi_Digit == True | RaspberryPi_Matrix == True:
    from RPi import GPIO
    GPIO.setwarnings(False)

def main():
    download_csv()
    lastUpdate, inzidenz = getJson()

    # Prüfen, ob es bereits eine neue Datei von heute gibt, ansonsten die alte öffnen.
    aktuellerTag = datetime.datetime.now()
    aktuellerTag = aktuellerTag.strftime(format="%Y%m%d")

    newfile = "tabelle_04_" + aktuellerTag + ".csv"  # Welches CSV müsste das neuste sein?
    file = max(os.listdir(PATH))                     # Welches CSV ist das aktuellste im Verzeichnis?

    print("Neuste CSV-Datei: ", file)

    if newfile != file:
        print("Heute noch keine Aktualisierung.")
        Aktualisierung = False
    else:
        Aktualisierung = True

    stand, inzidenz = load_csv(file)
    wert = extract_inzidenz(inzidenz)

    if 35.0 <= wert < 50.0:
        farbe = 'gelb'
    elif wert >= 50.0:
        farbe = 'rot'
    else:
        farbe = 'grün'

    print("\nDer aktuelle Wert für " + LOCATION + ' ist: ' + str(wert) + "!")
    print("Die Corona-Ampel ist somit: " + farbe + "!")
    print(stand.readline())

    # Steuerung der Ampel und der Digitalanzeige auf dem Raspberry Pi
    if RaspberryPi_Ampel == True:
        Ampelsteuerung(farbe)
    if RaspberryPi_Digit == True:
        Anzeige(wert)
    if RaspberryPi_Matrix == True:
        Matrix()

    return Aktualisierung

# Download des JSON vom RKI
def getJson():
    try:
        url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=GEN%20%3D%20%27" + LOCATION + "%27&outFields=GEN,last_update,cases7_per_100k&outSR=4326&f=json"
        r = requests.get(url)
        result = r.json()
        # location = result['features'][0]['attributes']['GEN']
        lastUpdate = result['features'][0]['attributes']['last_update']
        inzidenz = round(result['features'][0]['attributes']['cases7_per_100k'], 2)

        return lastUpdate, inzidenz
    except:
        print('Fehler beim Abrufen der JSON-Daten. Erneuter Versuch.')
        time.sleep(5)
        getJson()


# Download des CSVs vom LGL
def download_csv():
    # Webseite aufrufen und den Button zum Download des CSVs klicken
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    prefs = {"download.default_directory": PATH}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("./chromedriver", options=options)

    try:
        driver.get("https://www.lgl.bayern.de/gesundheit/infektionsschutz/infektionskrankheiten_a_z/coronavirus/karte_coronavirus/index.htm")
        driver.find_element_by_xpath("//button[@onclick=\"exportTableToCSV('tabelle_04', '#tableLandkreise')\"]").click()
        print('Download erfolgreich')
    except:
        print('Fehler beim Abrufen der CSV-Datei. Erneuter Versuch.')
        time.sleep(5)
        download_csv()

    time.sleep(2)
    return

def load_csv(file):
    stand = open(PATH + file, 'r')
    inzidenz = pd.read_csv(PATH + file, sep=";", decimal=",", skiprows=1, header=None)

    return stand, inzidenz

def extract_inzidenz(inzidenz):
    lokaleInzidenz = inzidenz.loc[inzidenz[0] == LOCATION, :]
    lokaleInzidenz = pd.DataFrame(lokaleInzidenz)
    lokaleInzidenz.reset_index(drop=True, inplace=True)
    wert = lokaleInzidenz.loc[0, 5]
    wert = float(locale.atof(wert))

    return wert

# LED
def Ampelsteuerung(farbe):
    # Dies steuert die Ampel auf dem Pi
    if farbe == 'grün':
        LED_setColor(100,0,100)
    elif farbe == 'gelb':
        LED_setColor(0,0,100)
    elif farbe == 'rot':
        LED_setColor(0,100,100)

def LED_setup():
    global pwmRed, pwmGreen, pwmBlue

    GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(LED_pins, GPIO.OUT)  # set RGBLED pins to OUTPUT mode
    GPIO.output(LED_pins, GPIO.HIGH)  # make RGBLED pins output HIGH level

    pwmRed = GPIO.PWM(LED_pins[0], 2000)  # set PWM Frequence to 2kHz
    pwmGreen = GPIO.PWM(LED_pins[1], 2000)  # set PWM Frequence to 2kHz
    pwmBlue = GPIO.PWM(LED_pins[2], 2000)  # set PWM Frequence to 2kHz
    pwmRed.start(0)  # set initial Duty Cycle to 0
    pwmGreen.start(0)
    pwmBlue.start(0)

def LED_setColor(r_val, g_val, b_val):  # change duty cycle for three pins to r_val,g_val,b_val
    pwmRed.ChangeDutyCycle(r_val)  # change pwmRed duty cycle to r_val
    pwmGreen.ChangeDutyCycle(g_val)
    pwmBlue.ChangeDutyCycle(b_val)

# Display
def Anzeige(wert):
    Digit_setup()

def Digit_setup():
    # define the pins for 74HC595
    dataPin = 11  # DS Pin of 74HC595(Pin14)
    latchPin = 13  # ST_CP Pin of 74HC595(Pin12)
    clockPin = 15  # CH_CP Pin of 74HC595(Pin11)
    # Zahlen von 0-9
    # TODO: Für alle Zahlen noch eine Version mit . anlegen
    num = [0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90]

    GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(dataPin, GPIO.OUT)
    GPIO.setup(latchPin, GPIO.OUT)
    GPIO.setup(clockPin, GPIO.OUT)

def Digit_shiftOut(dPin, cPin, order, val):
    LSBFIRST = 1
    MSBFIRST = 2

    for i in range(0, 8):
        GPIO.output(cPin, GPIO.LOW)
        if (order == LSBFIRST):
            GPIO.output(dPin, (0x01 & (val >> i) == 0x01) and GPIO.HIGH or GPIO.LOW)
        elif (order == MSBFIRST):
            GPIO.output(dPin, (0x80 & (val << i) == 0x80) and GPIO.HIGH or GPIO.LOW)
        GPIO.output(cPin, GPIO.HIGH)

def Digit_loop():
    while True:
        for i in range(0, len(num)):
            GPIO.output(latchPin, GPIO.LOW)
            shiftOut(dataPin, clockPin, MSBFIRST, num[i])  # Send serial data to 74HC595
            GPIO.output(latchPin, GPIO.HIGH)
            time.sleep(0.5)
        for i in range(0, len(num)):
            GPIO.output(latchPin, GPIO.LOW)
            shiftOut(dataPin, clockPin, MSBFIRST, num[i] & 0x7f)  # Use "&0x7f" to display the decimal point.
            GPIO.output(latchPin, GPIO.HIGH)
            time.sleep(0.5)

# Matrix
def Matrix():
    # Die letzten 8 Dateien bestimmen
    files = os.listdir(PATH)
    wertehistorie = []
    digits = []

    # Solange noch keine 8 Dateien vorhanden sind...
    if len(files) < 8:
        l = len(files) - 1  # -1 wegen der Hidden Files. Falls keine vorhanden, dann kann das weg
    else:
        l = 8

    for i in range (-l, 0):
        stand, inzidenz = load_csv(files[i])
        wert = extract_inzidenz(inzidenz)
        wertehistorie.append(wert)

    for d in wertehistorie:
        hoehe = round(d / max(wertehistorie) / 0.125)  # Die Matrix hat 8 mögliche LEDs, daher ist der Max-Wert ganz oben
        digits.append(hoehe)

    print(digits)

def Matrix_setup():
    # define the pins connect to 74HC595
    dataPin = 11  # DS Pin of 74HC595(Pin14)
    latchPin = 13  # ST_CP Pin of 74HC595(Pin12)
    clockPin = 15  # SH_CP Pin of 74HC595(Pin11)
    pic = [0x1c, 0x22, 0x51, 0x45, 0x45, 0x51, 0x22, 0x1c]  # data of smiling face
    data = [  # data of "0-F"
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # " "
        0x00, 0x00, 0x3E, 0x41, 0x41, 0x3E, 0x00, 0x00,  # "0"
        0x00, 0x00, 0x21, 0x7F, 0x01, 0x00, 0x00, 0x00,  # "1"
        0x00, 0x00, 0x23, 0x45, 0x49, 0x31, 0x00, 0x00,  # "2"
        0x00, 0x00, 0x22, 0x49, 0x49, 0x36, 0x00, 0x00,  # "3"
        0x00, 0x00, 0x0E, 0x32, 0x7F, 0x02, 0x00, 0x00,  # "4"
        0x00, 0x00, 0x79, 0x49, 0x49, 0x46, 0x00, 0x00,  # "5"
        0x00, 0x00, 0x3E, 0x49, 0x49, 0x26, 0x00, 0x00,  # "6"
        0x00, 0x00, 0x60, 0x47, 0x48, 0x70, 0x00, 0x00,  # "7"
        0x00, 0x00, 0x36, 0x49, 0x49, 0x36, 0x00, 0x00,  # "8"
        0x00, 0x00, 0x32, 0x49, 0x49, 0x3E, 0x00, 0x00,  # "9"
    ]

    GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(dataPin, GPIO.OUT)
    GPIO.setup(latchPin, GPIO.OUT)
    GPIO.setup(clockPin, GPIO.OUT)

def Matrix_shiftOut(dPin, cPin, order, val):
    LSBFIRST = 1
    MSBFIRST = 2

    for i in range(0, 8):
        GPIO.output(cPin, GPIO.LOW);
        if (order == LSBFIRST):
            GPIO.output(dPin, (0x01 & (val >> i) == 0x01) and GPIO.HIGH or GPIO.LOW)
        elif (order == MSBFIRST):
            GPIO.output(dPin, (0x80 & (val << i) == 0x80) and GPIO.HIGH or GPIO.LOW)
        GPIO.output(cPin, GPIO.HIGH);

def Matrix_loop():
    while True:
        for j in range(0, 500):  # Repeat enough times to display the smiling face a period of time
            x = 0x80
            for i in range(0, 8):
                GPIO.output(latchPin, GPIO.LOW)
                shiftOut(dataPin, clockPin, MSBFIRST,
                         pic[i])  # first shift data of line information to first stage 74HC959

                shiftOut(dataPin, clockPin, MSBFIRST,
                         ~x)  # then shift data of column information to second stage 74HC959
                GPIO.output(latchPin, GPIO.HIGH)  # Output data of two stage 74HC595 at the same time
                time.sleep(0.001)  # display the next column
                x >>= 1
        for k in range(0, len(data) - 8):  # len(data) total number of "0-F" columns
            for j in range(0,
                           20):  # times of repeated displaying LEDMatrix in every frame, the bigger the "j", the longer the display time.
                x = 0x80  # Set the column information to start from the first column
                for i in range(k, k + 8):
                    GPIO.output(latchPin, GPIO.LOW)
                    shiftOut(dataPin, clockPin, MSBFIRST, data[i])
                    shiftOut(dataPin, clockPin, MSBFIRST, ~x)
                    GPIO.output(latchPin, GPIO.HIGH)
                    time.sleep(0.001)
                    x >>= 1

def destroy():
    if RaspberryPi_Ampel == True:
        pwmRed.stop()
        pwmGreen.stop()
        pwmBlue.stop()
        GPIO.cleanup()

# starten, wenn kein Aufruf aus einem anderen Modul kommt, wo das Script importiert ist
if __name__ == "__main__":
    if RaspberryPi_Ampel == True:
        LED_setup()

    # Endlosschleife
    try:
        while True:
            print("\nAktualisierung der Werte am " + datetime.datetime.strftime(datetime.datetime.now(), format="%d.%m.%y, %H:%M Uhr"))
            Aktualisierung = main()
            uhrzeit = time.localtime()

            if (Aktualisierung == False) & (7 <= uhrzeit.tm_hour <= 20):
                print("Aktualisierung erfolgt alle 10 Minuten")
                time.sleep(600)
            elif uhrzeit.tm_hour >= 21:     # Ab 21 Uhr wird keine Aktualisierung mehr vorgenommen. Das Skript wird per Cronjob morgens erneut gestartet.
                break
            else:
                print("Aktualisierung erfolgt alle 2 Stunden")
                time.sleep(12000)
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()