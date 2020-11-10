# Corona-Ampel
Liest den Inzidenz-Wert bestimmter Landkreise von der API des RKI  und des LGL aus und gibt den Inzidenz-Wert sowie die Ampelfarbe aus.

Auf einem Raspberry Pi ist es möglich, den Inzidenz-Wert auf einem Display auszugeben. Die Ampelfarbe wird per farbiger LED angezeigt.

Außerdem gibts einen Telegram-Bot!

Python 3 wird empfohlen.
Um das Script auf dem Raspberry zu nutzen, müssen evtl. Packages nachinstalliert werden:

Pandas: 
<code>sudo apt-get install python3-pandas</code>

Selenium (für CSV-Download):
<code>sudo apt-get install python3-selenium</code>

Chromedriver (für CSV-Download):
<code>sudo apt-get install chromium-chromedriver</code>

RPi.GPIO (für die Raspberry-Ampel):
<code>sudo apt-get install python3-rpi.gpio</code>
<code>sudo apt-get install python3-pigpio</code>

Telegram-Bot (für Telegram):
<code>pip3 install python-telegram-bot
  pip3 install teleport
  pip3 install teleport --upgrade</code>
  
  
Folgende Variablen müssen noch angepasst werden:
<code>LOCATION - Hier den Landkreis/Ort eintragen, für den die Inzidenzwerte geladen werden sollen.</code>
<code>API-KEY - Hier euren API-Key für den Telegram-Bot eintragen.</code>

Der Code ist sicherlich nicht zu 100% professionell und kann durchaus verbessert werden. Dennoch erfüllt er seinen Zweck.
Sofern mich jemand unterstützen möchte, gerne per BTC an: 
