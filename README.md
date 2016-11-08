# SZ
Einige Feeds der Süddeutschen auf die reine Information reduziert, aber mit Bildchen. Das ganze als flask app. 
Benötigt neben flask bs4 für das web-scraping.

####Usage:
    python server.py [-p n] [--options 'key1=value1,...'] [-d] [-o]

      -p,  --port n      n ist Port des Servers, default ist 8000
           --options kv  Weitere Flask-Server-Optionen als kommaseparierte kv-Paare
      -d,  --debug       Schaltet debug mode ein
      -o,  --open        Öffnet den Server für LAN und ggf. WAN
