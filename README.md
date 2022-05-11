# GIAPython.io

## **Instalacion**

 1. Creamos y activamos un entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

 2. Instalamos las dependencias en el entorno virtual

```bash
pip3 install -r requirements.txt
```

## **Servidor**

Para correr el servidor primero debe asegurarse de que en el archivo 
`.env.json` el campob`SERVER_IP` corresponde con la `IP` donde el servidor 
deberia estar montado. Puede colocar `"0.0.0.0"` para usar la `IP` local
Luego puede simplemente ejecutar

```bash
python3 app.py
```

## **Cliente**

Para correr el servidor primero debe asegurarse de que en el archivo `.env.json` el campo
`SERVER_IP` corresponde con la `IP` donde el servidor esta montado. Luego puede
simplemente ejecutar

```bash
python3 play.py [OPTIONS]
```

Siguiendo la siguiente sintaxis:

```
python3  play.py [-h] [-n] [-c CHANNEL CHANNEL CHANNEL] [-i FILENAME] IP PORT

Corre un ciente de python.io

positional arguments:
  IP                    Server IP.
  PORT                  Server port.

optional arguments:
  -h, --help            show this help message and exit
  -n, --no-interface    No se muestra una interfaz.
  -c CHANNEL CHANNEL CHANNEL, --color CHANNEL CHANNEL CHANNEL
                        Permite establecer un color a la serpiente. 
  -i FILENAME, --image FILENAME
                        Archivo donde se guardara la iamgen de cada frame. 
                        (default: images/screenshot.png)
```

## **Observador**

Debido a que cada jugador solo puede observar una seccion del mapa, se creo
un observador capaz de ver el mapa entero. Su sintaxis es:

```bash
python3 watcher.py SERVER_IP SERVER_PORT
```

## **Juego**

Inspirado en `Snake.io`, las instrucciones para jugar son sencillas:
 * Presione `a` para girar en sentido anti-horario.
 * Presione `d` para girar en sentido horario.
 * Presione `w` para acelerar. Esto hace que la serpiente se vaya haciendo más pequeña
 debido al gasto de energía. Si es muy pequeña no logrará acelerar.
 * Los puntos rojos representan manzanas, mientras más coma la serpiente, más grande se 
 hará.
 * Si la serpiente se sale del area del juego (delimitado por marcos blancos), muere.
 * Si una serpiente choca con el cuerpo de otra serpiente, muere.
 * Cuando una serpiente muere deja un rastro de manzanas donde se encontraba su cuerpo.
