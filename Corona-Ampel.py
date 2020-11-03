import pandas as pd
import datetime
import locale
import os
import time
import requests
import threading
from selenium import webdriver
import telepot

# Configuration
# Lokalisierung für die korrekte Erkennung der Werte
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Hier die entsprechende Stadt bzw. den Landkreis erfassen gem. den Eintragungen in der Liste
LOCATION = 'Miltenberg'

# Dateipfad, wo die CSVs vom LGL abgelegt werden sollen
PATH = '/ftp/Corona-Ampel/csvs/'

# Telegram Chatbot
API_KEY = '1238405665:AAH0gx0IE9tuZJN98AC3cSdvK4E70abgz0k'
CHATBOTURL = 'https://api.telegram.org/bot' + API_KEY + '/sendmessage?chat_id=-433144245&text='
TelegramMessageLGL = 0.0
TelegramMessageRKI = 0.0
LGL_wert= ''
standLGL= ''
LGL_farbe= ''
RKI_inzidenz= ''
lastUpdate= ''
RKI_farbe= ''

# Läuft das Script auf dem RPi und ist die Ampel, die Digitalanzeige und/oder die Matrix aktiviert (True/False)?
RaspberryPi_Ampel = True
LED_pins = [31, 32, 33]

RaspberryPi_Digit = True
dataPin = 18  # DS Pin of 74HC595
latchPin = 16  # ST_CP Pin of 74HC595
clockPin = 12  # SH_CP Pin of 74HC595
digitPin = (11, 13, 15, 19)  # Define the pin of 7-segment display common end
num = (0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90)
num2 = (0x40, 0x79, 0x24, 0x30, 0x19, 0x12, 0x02, 0x78, 0x00, 0x10)
LSBFIRST = 1
MSBFIRST = 2
DigitWert = 0
t = 0


RaspberryPi_Matrix = True
Matrix_LSBFIRST = 1
Matrix_MSBFIRST = 2
# define the pins connect to 74HC595
Matrix_dataPin   = 36      # DS Pin of 74HC595(Pin14)
Matrix_latchPin  = 38      # ST_CP Pin of 74HC595(Pin12)
Matrix_clockPin = 40       # SH_CP Pin of 74HC595(Pin11)
#data = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
data = [0x00, 0xFE, 0xfc, 0xf8, 0xf0, 0xe0, 0xc0, 0x80, 0x00]
xdata = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
m = 0
digits = []
wertehistorie = []


RaspberryPi_Servo = True
OFFSE_DUTY = 0.5        #define pulse offset of servo
SERVO_MIN_DUTY = 2.5+OFFSE_DUTY     #define pulse duty cycle for minimum angle of servo
SERVO_MAX_DUTY = 12.5+OFFSE_DUTY    #define pulse duty cycle for maximum angle of servo
servoPin = 35

if RaspberryPi_Ampel == True | RaspberryPi_Digit == True | RaspberryPi_Matrix == True:
    from RPi import GPIO
    GPIO.setwarnings(False)

def main():
    global TelegramMessageLGL, TelegramMessageRKI, t, DigitWert, LGL_wert, standLGL, LGL_farbe, RKI_inzidenz, lastUpdate, RKI_farbe, wertehistorie

    # Daten besorgen
    AktualisierungLGL, stand, LGL_inzidenz, LGL_wert = download_csv()
    lastUpdate, RKI_inzidenz, AktualisierungRKI = getJson()

    # LGL-Farbe errechnen
    if LGL_wert >= 100.0:
        LGL_farbe = 'dunkelrot'
    elif 50.0 <= LGL_wert < 100.0:
        LGL_farbe = 'rot'
    elif 35.0 <= LGL_wert < 50.0:
        LGL_farbe = 'gelb'
    else:
        LGL_farbe = 'grün'

    # RKI-Farbe errechnen
    if RKI_inzidenz >= 100.0:
        RKI_farbe = 'dunkelrot'
    elif 50.0 <= RKI_inzidenz < 100.0:
        RKI_farbe = 'rot'
    elif 35.0 <= RKI_inzidenz < 50.0:
        RKI_farbe = 'gelb'
    else:
        RKI_farbe = 'grün'

    # Ausgabe der Werte auf allen Kanälen
    # Ausgabe in der Konsole
    print("\nDer aktuelle Wert des LGL für " + LOCATION + ' ist: ' + str(LGL_wert) + "!")
    print("Die Corona-Ampel ist somit: " + LGL_farbe + "!")
    standLGL = stand.readline()
    print(standLGL)
    print("Der aktuelle Wert des RKI für " + LOCATION + ' ist: ' + str(RKI_inzidenz) + "!")
    print("Die Corona-Ampel ist somit: " + RKI_farbe + "!")
    print('Stand:', lastUpdate)

    # Telegram-Bot
    # Bot starten
    try:
        bot.message_loop({'chat': Telegrambot})
        print('Telegram-Bot gestartet')
    except:
        pass

    if (RKI_farbe == 'dunkelrot') | (RKI_farbe == 'rot'):
        RKI_Ampel = "\U0001F534"
    elif RKI_farbe == 'gelb':
        RKI_Ampel = "\U0001F7E1"
    elif RKI_farbe == 'grün':
        RKI_Ampel = "\U0001F7E2"

    if (LGL_farbe == 'dunkelrot') | (LGL_farbe == 'rot'):
        LGL_Ampel = "\U0001F534"
    elif LGL_farbe == 'gelb':
        LGL_Ampel = "\U0001F7E1"
    elif LGL_farbe == 'grün':
        LGL_Ampel = "\U0001F7E2"

    # Ausgabe auf dem Telegram-Bot
    #if (AktualisierungLGL == True) & (TelegramMessageLGL == False):
    if (AktualisierungLGL == True) & (TelegramMessageLGL != LGL_wert):
        chaturlLGL = CHATBOTURL + 'Der Wert des LGL ist: ' + str(LGL_wert) + '!\nSomit ist die Ampel: ' + LGL_farbe + ' ' + LGL_Ampel + '\n' + standLGL
        requests.post(chaturlLGL)
        #TelegramMessageLGL = True
        TelegramMessageLGL = LGL_wert

    #if (AktualisierungRKI == True) & (TelegramMessageRKI == False):
    if (AktualisierungRKI == True) & (TelegramMessageRKI != RKI_inzidenz):
        chaturlRKI = CHATBOTURL + 'Der Wert des RKI ist: ' + str(RKI_inzidenz) + '!\nSomit ist die Ampel: ' + RKI_farbe + ' ' + RKI_Ampel + '\nStand: ' + lastUpdate
        requests.post(chaturlRKI)
      #  TelegramMessageRKI = True
        TelegramMessageRKI = RKI_inzidenz

    # Ausgabe auf der Ampel und der Digitalanzeige
    # Definition welcher Wert auf der Ampel und der Anzeige ausgegeben wird
    if (AktualisierungLGL == False) & (RKI_inzidenz > LGL_wert):
        farbe = RKI_farbe
        DigitWert = RKI_inzidenz
        Servo = 'RKI'
    elif (AktualisierungLGL == False) & (RKI_inzidenz <= LGL_wert):
        farbe = LGL_farbe
        DigitWert = LGL_wert
        Servo = 'LGL'
    elif (AktualisierungLGL == True) & (RKI_inzidenz <= LGL_wert):
        farbe = LGL_farbe
        DigitWert = LGL_wert
        Servo = 'LGL'
    elif (AktualisierungLGL == True) & (RKI_inzidenz > LGL_wert):
        farbe = RKI_farbe
        DigitWert = RKI_inzidenz
        Servo = 'RKI'
    else:
        farbe = LGL_farbe
        DigitWert = LGL_wert
        Servo = 'LGL'

    # Steuerung der Ampel und der Digitalanzeige auf dem Raspberry Pi
    if RaspberryPi_Ampel == True:
        Ampelsteuerung(farbe)

    #if RaspberryPi_Digit == True:   läuft schon, es muss nur der DigitWert geändert werden
    if RaspberryPi_Matrix == True:
        Matrix_checkfiles()

    if RaspberryPi_Servo == True:
        if Servo == 'RKI':
            servoWrite(0)
        elif Servo == 'LGL':
            servoWrite(180)

    # Bescheid geben, ob eine Aktualisierung des LGL erfolgt ist, oder nicht.
    # Bis die Aktualisierung erfolgt ist, wird alle 10 Minuten gecheckt. Danach nur noch alle 2 Stunden.
    return AktualisierungLGL

# Download des JSON vom RKI
def getJson():
    try:
        url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=GEN%20%3D%20%27" + LOCATION + "%27&outFields=GEN,last_update,cases7_per_100k&outSR=4326&f=json"
        r = requests.get(url)
        result = r.json()
        # location = result['features'][0]['attributes']['GEN']
        lastUpdate = result['features'][0]['attributes']['last_update']
        RKI_inzidenz = round(result['features'][0]['attributes']['cases7_per_100k'], 2)

        print('JSON-Retrieve erfolgreich.')

        aktuellerTag = datetime.datetime.now()
        # aktuellerTag = aktuellerTag.strftime(format="%Y%m%d")

        if lastUpdate == aktuellerTag.strftime(format="%d.%m.%Y") + ', 00:00 Uhr':
            AktualisierungRKI = True
        else:
            AktualisierungRKI = False

        return lastUpdate, RKI_inzidenz, AktualisierungRKI
    except:
        print('Fehler beim Abrufen der JSON-Daten. Erneuter Versuch.')
        time.sleep(5)
        getJson()

# Download des CSVs vom LGL
def download_csv():
    # Webseite aufrufen und den Button zum Download des CSVs klicken
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    prefs = {"download.default_directory": PATH}
    options.add_experimental_option("prefs", prefs)
    if RaspberryPi_Ampel == True:
        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=options)
    else:
        driver = webdriver.Chrome("./chromedriver", options=options)

    try:
        driver.get("https://www.lgl.bayern.de/gesundheit/infektionsschutz/infektionskrankheiten_a_z/coronavirus/karte_coronavirus/index.htm")
        driver.find_element_by_xpath("//button[@onclick=\"exportTableToCSV('tabelle_04', '#tableLandkreise')\"]").click()
        print('CSV-Download erfolgreich')
    except:
        print('Fehler beim Abrufen der CSV-Datei. Erneuter Versuch.')
        time.sleep(5)
        download_csv()

    time.sleep(2)

    # Prüfen, ob es bereits eine neue Datei von heute gibt, ansonsten die alte öffnen.
    aktuellerTag = datetime.datetime.now()
    aktuellerTag = aktuellerTag.strftime(format="%Y%m%d")

    newfile = "tabelle_04_" + aktuellerTag + ".csv"  # Welches CSV müsste das neuste sein?
    file = max(os.listdir(PATH))  # Welches CSV ist das aktuellste im Verzeichnis?

    if newfile != file:
        print("Heute ist noch keine Aktualisierung durch das LGL Bayern erfolgt.\nEs wird der Wert von gestern angezeigt")
        AktualisierungLGL = False
    else:
        AktualisierungLGL = True

    stand, LGL_inzidenz = load_csv(file)
    LGL_wert = extract_inzidenz(LGL_inzidenz)

    return AktualisierungLGL, stand, LGL_inzidenz, LGL_wert

def load_csv(file):
    stand = open(PATH + file, 'r')
    LGL_inzidenz = pd.read_csv(PATH + file, sep=";", decimal=",", skiprows=1, header=None)

    return stand, LGL_inzidenz

def extract_inzidenz(LGL_inzidenz):
    lokaleInzidenz = LGL_inzidenz.loc[LGL_inzidenz[0] == LOCATION, :]
    lokaleInzidenz = pd.DataFrame(lokaleInzidenz)
    lokaleInzidenz.reset_index(drop=True, inplace=True)
    LGL_wert = lokaleInzidenz.loc[0, 5]
    LGL_wert = float(locale.atof(LGL_wert))

    return LGL_wert

# LED
def Ampelsteuerung(farbe):
    # Dies steuert die Ampel auf dem Pi
    if farbe == 'grün':
        LED_setColor(100,0,100)
    elif farbe == 'gelb':
        LED_setColor(0,0,100)
    elif farbe == 'rot':
        LED_setColor(0,100,100)
    elif farbe == 'dunkelrot':
        LED_setColor(80,100,0)

def LED_setup():
    global pwmRed, pwmGreen, pwmBlue

    #GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
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
def Anzeige():
    global DigitWert

    while True:
        if 1000 > DigitWert >= 100:
            dec = int(DigitWert * 10)
        elif DigitWert >= 1000:
            dec = int(DigitWert)
        elif DigitWert < 100:
            dec = int(DigitWert * 100)

        Digit_display(dec, DigitWert)

def Digit_setup():
    #GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(dataPin, GPIO.OUT)  # Set pin mode to OUTPUT
    GPIO.setup(latchPin, GPIO.OUT)
    GPIO.setup(clockPin, GPIO.OUT)
    for pin in digitPin:
        GPIO.setup(pin, GPIO.OUT)

def Digit_shiftOut(dPin,cPin,order,val):
    for i in range(0,8):
        GPIO.output(cPin,GPIO.LOW);
        if(order == LSBFIRST):
            GPIO.output(dPin,(0x01&(val>>i)==0x01) and GPIO.HIGH or GPIO.LOW)
        elif(order == MSBFIRST):
            GPIO.output(dPin,(0x80&(val<<i)==0x80) and GPIO.HIGH or GPIO.LOW)
        GPIO.output(cPin,GPIO.HIGH)

def Digit_outData(data):  # function used to output data for 74HC595
    GPIO.output(latchPin, GPIO.LOW)
    Digit_shiftOut(dataPin, clockPin, MSBFIRST, data)
    GPIO.output(latchPin, GPIO.HIGH)

def Digit_selectDigit(digit):  # Open one of the 7-segment display and close the remaining three, the parameter digit is optional for 1,2,4,8
    GPIO.output(digitPin[0], GPIO.LOW if ((digit & 0x08) == 0x08) else GPIO.HIGH)
    GPIO.output(digitPin[1], GPIO.LOW if ((digit & 0x04) == 0x04) else GPIO.HIGH)
    GPIO.output(digitPin[2], GPIO.LOW if ((digit & 0x02) == 0x02) else GPIO.HIGH)
    GPIO.output(digitPin[3], GPIO.LOW if ((digit & 0x01) == 0x01) else GPIO.HIGH)

def Digit_display(dec, wert):  # display function for 7-segment display
    Digit_outData(0xff)  # eliminate residual display
    Digit_selectDigit(0x01)  # Select the first, and display the single digit
    Digit_outData(num[dec % 10])
    time.sleep(0.003)  # display duration

    Digit_outData(0xff)
    Digit_selectDigit(0x02)  # Select the second, and display the tens digit
    if wert >= 100:
        Digit_outData(num2[dec % 100 // 10])
    else:
        Digit_outData(num[dec % 100 // 10])
    time.sleep(0.003)

    Digit_outData(0xff)
    Digit_selectDigit(0x04)  # Select the third, and display the hundreds digit
    if 10 <= wert < 100:
        Digit_outData(num2[dec % 1000 // 100])
    else:
        Digit_outData(num[dec % 1000 // 100])
    time.sleep(0.003)

    Digit_outData(0xff)
    Digit_selectDigit(0x08)  # Select the fourth, and display the thousands digit
    Digit_outData(num[dec % 10000 // 1000])
    time.sleep(0.003)

# Matrix
def Matrix():
    while True:
        Matrix_loop(digits)

def Matrix_checkfiles():
    global digits, wertehistorie

    # Die letzten 8 Dateien bestimmen
    files = os.listdir(PATH)
    files.sort()
    wertehistorie = []
    digits = []

    # Solange noch keine 8 Dateien vorhanden sind...
    if len(files) < 8:
        l = len(files) - 1  # -1 wegen der Hidden Files. Falls keine vorhanden, dann kann das weg
    else:
        l = 8

    for i in range(-l, 0):
        stand, inzidenz = load_csv(files[i])
        wert = extract_inzidenz(inzidenz)
        wertehistorie.append(wert)

    for d in wertehistorie:
        hoehe = round(
            d / max(wertehistorie) / 0.125)  # Die Matrix hat 8 mögliche LEDs, daher ist der Max-Wert ganz oben
        digits.append(data[hoehe])

def Matrix_setup():
    #GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(Matrix_dataPin, GPIO.OUT)
    GPIO.setup(Matrix_latchPin, GPIO.OUT)
    GPIO.setup(Matrix_clockPin, GPIO.OUT)

def Matrix_shiftOut(dPin, cPin, order, val):
    for i in range(0, 8):
        GPIO.output(cPin, GPIO.LOW);
        if (order == Matrix_LSBFIRST):
            GPIO.output(dPin, (0x01 & (val >> i) == 0x01) and GPIO.HIGH or GPIO.LOW)
        elif (order == Matrix_MSBFIRST):
            GPIO.output(dPin, (0x80 & (val << i) == 0x80) and GPIO.HIGH or GPIO.LOW)
        GPIO.output(cPin, GPIO.HIGH);

def Matrix_loop(digits):
    for y in range(0, len(digits)):
        x = xdata[y]
        GPIO.output(Matrix_latchPin, GPIO.LOW)
        Matrix_shiftOut(Matrix_dataPin, Matrix_clockPin, Matrix_MSBFIRST, ~digits[y]) # Welche Reihe ist an? Das ~ dreht den Binärwert um
        Matrix_shiftOut(Matrix_dataPin, Matrix_clockPin, Matrix_MSBFIRST, ~x) # Welche Spalte ist an?
        GPIO.output(Matrix_latchPin, GPIO.HIGH)
        time.sleep(0.002)

# Servo steuern
def Servo_map(value, fromLow, fromHigh, toLow, toHigh):  # map a value from one range to another range
    return (toHigh - toLow) * (value - fromLow) / (fromHigh - fromLow) + toLow

def Servo_setup():
    global p

    #GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(servoPin, GPIO.OUT)  # Set servoPin to OUTPUT mode
    GPIO.output(servoPin, GPIO.LOW)  # Make servoPin output LOW level

    p = GPIO.PWM(servoPin, 50)  # set Frequence to 50Hz
    p.start(0)  # Set initial Duty Cycle to 0

def servoWrite(angle):  # make the servo rotate to specific angle, 0-180
    p.ChangeDutyCycle(Servo_map(angle, 0, 180, SERVO_MIN_DUTY, SERVO_MAX_DUTY))  # map the angle to duty cycle and output it
    time.sleep(1)
    p.ChangeDutyCycle(0)

def destroy():
    global t, p

    if RaspberryPi_Ampel == True:
        pwmRed.stop()
        pwmGreen.stop()
        pwmBlue.stop()

    if RaspberryPi_Digit == True:
        GPIO.output(digitPin[0], GPIO.LOW)
        GPIO.output(digitPin[1], GPIO.LOW)
        GPIO.output(digitPin[2], GPIO.LOW)
        GPIO.output(digitPin[3], GPIO.LOW)

    if RaspberryPi_Servo == True:
        p.stop()

    GPIO.cleanup()

# Telegram-Bot
def Telegrambot(msg):
    global digits, wertehistorie

    if (RKI_farbe == 'dunkelrot') | (RKI_farbe == 'rot'):
        RKI_Ampel = "\U0001F534"
    elif RKI_farbe == 'gelb':
        RKI_Ampel = "\U0001F7E1"
    elif RKI_farbe == 'grün':
        RKI_Ampel = "\U0001F7E2"

    if (LGL_farbe == 'dunkelrot') | (LGL_farbe == 'rot'):
        LGL_Ampel = "\U0001F534"
    elif LGL_farbe == 'gelb':
        LGL_Ampel = "\U0001F7E1"
    elif LGL_farbe == 'grün':
        LGL_Ampel = "\U0001F7E2"

    if wertehistorie[len(wertehistorie) - 1] > wertehistorie[len(wertehistorie) - 2]:
        trend = "steigend \U00002197"
        trend2 = str(round(wertehistorie[len(wertehistorie) - 1] - wertehistorie[len(wertehistorie) - 2], 2)) + " gestiegen \U00002197"
    elif wertehistorie[len(wertehistorie) - 1] <= wertehistorie[len(wertehistorie) - 2]:
        trend = "fallend \U00002198"
        trend2 = str(round(wertehistorie[len(wertehistorie) - 2] - wertehistorie[len(wertehistorie) - 1], 2)) + " gefallen \U00002198"

    #print("\U00002B06")
    #print("\U00002B07")
    #print("\U000027A1")
    #print("\U00002197")
    #print("\U00002198")


    try:
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            user_id = msg['chat']['id']
            if msg['text'] in ["/rki", "/RKI", "/Rki"]:
                bot.sendMessage(user_id, "Der Wert vom RKI ist " + str(RKI_inzidenz) + ".\nDie Ampelfarbe ist " + RKI_farbe + " " + RKI_Ampel + "\nStand: " + lastUpdate)

            elif msg['text'] in ["/lgl", "/LGL", "/Lgl", "Bayern"]:
                bot.sendMessage(user_id, "Der Wert vom LGL ist " + str(LGL_wert) + ".\nDie Ampelfarbe ist " + LGL_farbe + " " + LGL_Ampel + "\nDer Wert ist um " + trend2 + "\n" + standLGL)

            elif msg['text'] in ["/regeln", "/wasgilt"]:
                bot.sendMessage(user_id, "Hier gibts weitere Infos: https://www.stmgp.bayern.de/coronavirus/")

            elif msg['text'] in ["/trend", "/Trend"]:
                bot.sendMessage(user_id, "Der Wert auf Basis der Zahlen des LGL ist um " + trend2)

            elif msg['text'] in ["/start", "/help", "/?"]:
                bot.sendMessage(user_id, "Folgende Befehle sind möglich:\n/rki - um die aktuellen Zahlen des RKI abzurufen.\n/lgl - um die aktuellen Zahlen des LGL abzurufen.\n/trend - um den aktuellen Trend auf Basis der LGL-Zahlen abzurufen.\n/regeln - um einen Link auf die geltenden Regeln zu erhalten.")

            elif msg['text'].startswith("/"):
                bot.sendMessage(user_id, "Mit dem Befehl `" + msg['text'] + "` kann ich leider nichts anfangen.")
                bot.sendMessage(user_id, "Ich verstehe nur /rki, /lgl und /trend.")
    except telepot.exception.BotWasBlockedError:
        pass

# starten, wenn kein Aufruf aus einem anderen Modul kommt, wo das Script importiert ist
if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)

    if RaspberryPi_Ampel == True:
        LED_setup()
    if RaspberryPi_Digit == True:
        Digit_setup()
        t = threading.Thread(target=Anzeige)
        t.start()
    if RaspberryPi_Servo == True:
        Servo_setup()
    if RaspberryPi_Matrix == True:
        Matrix_setup()
        m = threading.Thread(target=Matrix)
        m.start()

    # Set up Telegram Bot
    bot = telepot.Bot(API_KEY)

    # Endlosschleife
    try:
        while True:
            print("\nAktualisierung der Werte am " + datetime.datetime.strftime(datetime.datetime.now(), format="%d.%m.%y, %H:%M Uhr"))

            AktualisierungLGL = main()
            uhrzeit = time.localtime()

            if (AktualisierungLGL == False) & (14 <= uhrzeit.tm_hour <= 16):
                print("\nAktualisierung erfolgt alle 5 Minuten")
                time.sleep(300)
            #elif (5 <= uhrzeit.tm_hour <= 14) | (16 <= uhrzeit.tm_hour <= 20):
            elif (5 <= uhrzeit.tm_hour <= 20):
                print("\nAktualisierung erfolgt alle 15 Minuten")
                time.sleep(900)
            elif (20 <= uhrzeit.tm_hour <= 23) | (0 <= uhrzeit.tm_hour <=4):
                destroy()   # Ampel abschalten
                time.sleep(3550)
            else:
                destroy()
                exit() # Das Script muss ausgeschaltet werden, so dass es per Cronjob erneut gestartet werden kann
                break
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()