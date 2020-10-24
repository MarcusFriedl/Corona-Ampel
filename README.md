# Corona-Ampel
Liest den Inzidenz-Wert bestimmter Landkreise aus und gibt den Inzidenz-Wert sowie die Ampelfarbe aus.

Auf einem Raspberry Pi ist es möglich, den Inzidenz-Wert auf einem Display auszugeben. Die Ampelfarbe wird per farbiger LED angezeigt.

Python 3 wird empfohlen.
Um das Script auf dem Raspberry zu nutzen, müssen evtl. Packages nachinstalliert werden:

Pandas: 
<code>sudo apt-get install python3-pandas</code>

Selenium:
<code>sudo apt-get install python3-selenium</code>

Chromedriver:
<code>sudo apt-get install chromium-chromedriver</code>

RPi.GPIO
<code>sudo apt-get install python3-rpi.gpio</code>
