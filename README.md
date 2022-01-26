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

Para correr el servidor primero debe asegurarse de que en el archivo `.env.json` el campo
`SERVER_IP` corresponde con la `IP` donde el servidor deberia estar montado, generalmente
la `IP` local, por ejemplo `"192.168.1.106"`. Luego puede simplemente ejecutar
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
python3 play.py [-h] [-p PORT] [-n] [-c CHANNEL CHANNEL CHANNEL]

optional arguments:
  -h, --help            
                        Muestra este mensaje de ayuda y finaliza la ejecucion.
  -p PORT, --port PORT  
                        Puerto a traves del cual se ejecuta el cliente. (default: 4269)
  -n, --no_graphic      
                        No se muestra una ventana grafica.
  -c CHANNEL CHANNEL CHANNEL, --color CHANNEL CHANNEL CHANNEL
                        Permite establecer un color RGB a la serpiente. Si no se especifica,
                        se elige un color aleatorio.
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
