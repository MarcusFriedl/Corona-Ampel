import pandas as pd
import datetime
import locale
import os
import time
from selenium import webdriver

# Configuration
# Lokalisierung für die korrekte Erkennung der Werte
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Hier die entsprechende Stadt bzw. den Landkreis erfassen gem. den Eintragungen in der Liste
LOCATION = 'Miltenberg'

# Dateipfad, wo die CSVs abgelegt werden sollen
PATH = './csvs/'

# Läuft das Script auf dem RPi und ist die Ampel und die Digitalanzeige aktiviert (True/False)?
RaspberryPi_Ampel = False
RaspberryPi_Digit = False

if RaspberryPi_Ampel == True | RaspberryPi_Digit == True:
    from RPi import GPIO


options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
prefs = {"download.default_directory" : PATH}
options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome("./Chromedriver/chromedriver", options=options)

# Download des CSVs
def load_csv(file):
    # Webseite aufrufen und den Button zum Download des CSVs klicken
    try:
        driver.get("https://www.lgl.bayern.de/gesundheit/infektionsschutz/infektionskrankheiten_a_z/coronavirus/karte_coronavirus/index.htm")
        driver.find_element_by_xpath("//button[@onclick=\"exportTableToCSV('tabelle_04', '#tableLandkreise')\"]").click()
    except:
        print('Fehler beim Abrufen der CSV-Datei. Erneuter Versuch.')
        time.sleep(1)
        load_csv(file)

    stand = open(file, 'r')
    inzidenz = pd.read_csv(file, sep=";", decimal=",", skiprows=1, header=None)

    return stand, inzidenz


def main():
    # CSV von heute öffnen
    # TODO: Ich lass den Code mal stehen, evtl. will ich mal ein bestimmtes Datum auswerten
    aktuellerTag = datetime.datetime.now()
    aktuellerTag = aktuellerTag.strftime(format="%Y%m%d")

    newfile = PATH + "tabelle_04_" + aktuellerTag + ".csv"
    file = PATH + max(os.listdir(PATH))

    print("Dateiname: ", file)

    if newfile != file:
        print("Heute noch keine Aktualisierung.")

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

    # Steuerung der Ampel und der Digitalanzeige auf dem Raspberry Pi
    if RaspberryPi_Ampel == True:
        Ampelsteuerung(farbe)
    if RaspberryPi_Digit == True:
        Anzeige(wert)

def Ampelsteuerung(farbe):
    # Dies steuert die Ampel auf dem Pi
    LED_setup()
    if farbe == 'grün':
        LED_setColor(0,100,0)
    elif farbe == 'gelb':
        LED_setColor(100,100,0)
    elif farbe == 'rot':
        LED_setColor(100,0,0)

def LED_setup():
    # pins = [11, 12, 13]  # define the pins for R:11,G:12,B:13
    pins = [31, 32, 33]
    global pwmRed, pwmGreen, pwmBlue
    GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(pins, GPIO.OUT)  # set RGBLED pins to OUTPUT mode
    GPIO.output(pins, GPIO.HIGH)  # make RGBLED pins output HIGH level
    pwmRed = GPIO.PWM(pins[0], 2000)  # set PWM Frequence to 2kHz
    pwmGreen = GPIO.PWM(pins[1], 2000)  # set PWM Frequence to 2kHz
    pwmBlue = GPIO.PWM(pins[2], 2000)  # set PWM Frequence to 2kHz
    pwmRed.start(0)  # set initial Duty Cycle to 0
    pwmGreen.start(0)
    pwmBlue.start(0)

def LED_setColor(r_val, g_val, b_val):  # change duty cycle for three pins to r_val,g_val,b_val
    pwmRed.ChangeDutyCycle(r_val)  # change pwmRed duty cycle to r_val
    pwmGreen.ChangeDutyCycle(g_val)
    pwmBlue.ChangeDutyCycle(b_val)


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


# starten, wenn kein Aufruf aus einem anderen Modul kommt, wo das Script importiert ist
if __name__ == "__main__":
    while True:
        print("Aktualisierung der Werte am " + datetime.datetime.strftime(datetime.datetime.now(), format="%d.%m.%y, %H:%M Uhr"))
        main()
        time.sleep(600)
