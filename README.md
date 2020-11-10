# Corona-Ampel
Liest den Inzidenz-Wert bestimmter Landkreise von der API des RKI  und des LGL aus und gibt den Inzidenz-Wert sowie die Ampelfarbe aus.

Auf einem Raspberry Pi ist es möglich, den Inzidenz-Wert auf einem Display auszugeben. Die Ampelfarbe wird per farbiger LED angezeigt.
Die Hardware-Ampel basiert auf dem folgenden Baukasten (Affiliate-Link):
<a target="_blank" href="https://www.amazon.de/gp/product/B06VTH7L28/ref=as_li_tl?ie=UTF8&camp=1638&creative=6742&creativeASIN=B06VTH7L28&linkCode=as2&tag=marcusf-21&linkId=b6bdb33a04379f8a279d8580a5e8a041">Freenove RFID Starter Kit für Raspberry Pi 4 B 3 B+, 423 Seiten Ausführliche Anleitungen, Python C Java, 204 Elemente, 53 Projekte, Lernen Sie Elektronik und Programmierung, Lötfreies Steckbrett</a><img src="//ir-de.amazon-adsystem.com/e/ir?t=marcusf-21&l=am2&o=3&a=B06VTH7L28" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />

Mein RaspberryPi-Bausatz ist folgender (Affiliate-Link):
<a target="_blank" href="https://www.amazon.de/gp/product/B07BNPZVR7/ref=as_li_tl?ie=UTF8&camp=1638&creative=6742&creativeASIN=B07BNPZVR7&linkCode=as2&tag=marcusf-21&linkId=f7278a2fcda2aab4902c19990cacc065">UCreate Raspberry Pi 3 Model B+ Desktop Starter Kit (16 GB, schwarz)</a><img src="//ir-de.amazon-adsystem.com/e/ir?t=marcusf-21&l=am2&o=3&a=B07BNPZVR7" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />

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
