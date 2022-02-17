
# pyGeoServer
REST API per la gestione di un GeoServer per l'applicazione SIT-WG

## Installazione

```
git clone http://10.23.8.200:8080/sitdev/pygeoserver.git
. venv/bin/activate
pip install -e .
```

## Esecuzione
```
export FLASK_APP=pycopernicus
flask run
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

```
curl --location --request POST '127.0.0.1:5000/sentinel5p' \
--header 'Authorization: Basic YWRtaW46Z2Vvc2VydmVy' \
--form 'xmin="40.873292"' \
--form 'ymin="16.850661"' \
--form 'xmax="40.742011"' \
--form 'ymax="17.192127"' \
--form 'product="CO"'
```

## Docker


