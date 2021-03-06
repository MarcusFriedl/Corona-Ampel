# Corona-Ampel
## Was macht die Ampel?
Liest den Inzidenz-Wert bestimmter Landkreise von der API des RKI  und des LGL aus und gibt den Inzidenz-Wert sowie die Ampelfarbe aus.
Das LGL listet die Werte für Bayern auf. Für andere Bundesländer müsste der Code entsprechend angepasst werden. Einzelne Parts können natürlich auch aus dem Code entfernt werden.

Auf einem Raspberry Pi ist es möglich, den Inzidenz-Wert auf einem 4-Digit-Display auszugeben. Die Ampelfarbe wird per farbiger LED angezeigt und der Trend in einer Matrix. Weiterhin wird über einen Servo ein Schild gesteuert, welches sich dreht und anzeigt, von welcher Quelle (RKI oder LGL) der angezeigte Wert stammt.

**Die Hardware-Ampel basiert auf dem folgenden Baukasten (Affiliate-Link):**

<a target="_blank" href="https://www.amazon.de/gp/product/B06VTH7L28/ref=as_li_tl?ie=UTF8&camp=1638&creative=6742&creativeASIN=B06VTH7L28&linkCode=as2&tag=marcusf-21&linkId=b6bdb33a04379f8a279d8580a5e8a041">Freenove RFID Starter Kit für Raspberry Pi 4 B 3 B+, 423 Seiten Ausführliche Anleitungen, Python C Java, 204 Elemente, 53 Projekte, Lernen Sie Elektronik und Programmierung, Lötfreies Steckbrett</a><img src="//ir-de.amazon-adsystem.com/e/ir?t=marcusf-21&l=am2&o=3&a=B06VTH7L28" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />  

Im oben erwähnten Baukasten sind die entsprechenden Anleitungen und Verdrahtungsabbildungen enthalten. Bitte die geänderte Pin-Belegung berücksichtigen - ergibt sich aber aus dem Code.


**Mein RaspberryPi-Bausatz ist folgender (Affiliate-Link):**

<a target="_blank" href="https://www.amazon.de/gp/product/B07BNPZVR7/ref=as_li_tl?ie=UTF8&camp=1638&creative=6742&creativeASIN=B07BNPZVR7&linkCode=as2&tag=marcusf-21&linkId=f7278a2fcda2aab4902c19990cacc065">UCreate Raspberry Pi 3 Model B+ Desktop Starter Kit (16 GB, schwarz)</a><img src="//ir-de.amazon-adsystem.com/e/ir?t=marcusf-21&l=am2&o=3&a=B07BNPZVR7" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />  


Außerdem gibts einen Telegram-Bot!

## Raspberry-Applikation

**Python 3 wird empfohlen.**
Um das Script auf dem Raspberry zu nutzen, müssen evtl. Packages nachinstalliert werden:

* Pandas: 
<code>sudo apt-get install python3-pandas</code>

* Selenium (für CSV-Download):
<code>sudo apt-get install python3-selenium</code>

* Chromedriver (für CSV-Download):
<code>sudo apt-get install chromium-chromedriver</code>

* RPi.GPIO (für die Raspberry-Ampel):
<code>sudo apt-get install python3-rpi.gpio</code>
<code>sudo apt-get install python3-pigpio</code>

* Telegram-Bot (für Telegram):
<code>pip3 install python-telegram-bot
  pip3 install teleport
  pip3 install teleport --upgrade</code>
  
  
**Folgende Variablen müssen noch angepasst werden:**  
<code>LOCATION - Hier den Landkreis/Ort eintragen, für den die Inzidenzwerte geladen werden sollen.</code>  
<code>API-KEY - Hier euren API-Key für den Telegram-Bot eintragen.</code>

## Sonstiges

Der Code ist sicherlich nicht zu 100% professionell und kann durchaus verbessert werden. Dennoch erfüllt er seinen Zweck. Anpassungen und Verbesserungen nehme ich gerne an und lerne davon!  

Sofern mich jemand unterstützen möchte, gerne per BTC an <code>3NAbijqnAxAT5mCSXzxNLzUoLXyjTtcR7P</code>  
oder per ETH an <code>0x570790cD48676fb49387b1BB160d38181Eeb380c</code>  
Oder damit auch unsere Gastronomie nach dem Lockdown etwas davon hat, spendiert mir ein Bier :beer:: http://paypal.me/marcusfriedl



