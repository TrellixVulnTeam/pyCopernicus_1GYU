
# pyCopernicus
REST API per la gestione di un GeoServer per l'applicazione SIT-WG

## Installazione

```
git clone https://github.com/gzileni-copernicus/pyCopernicus.git
python3 -m venv venv
. venv/bin/activate
pip install -e .
```

## Esecuzione
```
export FLASK_APP=pycopernicus
flask run
```
or run script
```
./start.sh
```

### Ambiente virtuale
Bisogna utilizza un ambiente virtuale per gestire le dipendenze sia in fase di sviluppo che in produzione, affinchè si possa lavorare con diverse versioni delle librerie Python, o anche con lo stesso Python.

Gli ambienti virtuali sono gruppi indipendenti di librerie Python, i pacchetti installati per un progetto non influiranno su altri progetti o sui pacchetti del sistema operativo.

Python viene fornito in bundle con il modulo venv per creare ambienti virtuali.

Per avviare un ambiente virtuale in ambiente MacOS/Linux eseguire:
```
python3 -m venv venv
```

per ambiente Windows invece:
```
py -3 -m venv venv
```

## Docker


