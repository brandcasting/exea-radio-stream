ExeaInternetRadio - English Version
===================================

Scripts for convert a Raspberry Pi into an Internet Radio Player.

About
=====

The ExeaInternetRadio is a python script that allows the user to play music from an URL, or locally when the URL isn't available, for example, when the raspberry pi doesn't have internet connection or when the streming source is not available.
The ExeaInternetRadio also has a script for detecting output sound. When it detects silence, it automatically restart the player.

Quickstart
==========

Install the latest raspbian lite image on a SD card.

Run the file "setup.sh"

Change the configuration file "config.ini" with the URL of your streaming, the name of your radio and the serial number if necessary.

Upload the music backup on the folder "Music" classified in "Dias", "Tardes" and "Noches".

If you want to automatically refresh your backup, configure syncthing following this guide http://www.htpcguides.com/install-syncthing-raspberry-pi-bittorrent-sync-alternative/.

Fix the desired volume executing the command "alsamixer". Save your settings with the command "sudo alsactl store".

Execute the command "sudo crontab -e" and add the line: "@reboot sudo /usr/bin/checkSound.sh".


ExeaInternetRadio - Versión en Español
======================================

Guía para convertir una Raspberry Pi en un radio para reproducción de streaming via internet.

Acerca de
=========

El "ExeaInternetRadio" es un desarrollo en Python que permite al usuario reproducir música desde una URL, o localmente cuando la URL no está disponible, por ejemplo, cuando la rasperry pi no tiene conexión a internet o cuando la señal de streaming no está disponible.
El "ExeaInternetRadio" también tiene una función para detectar salida de sonido. Cuando se detecta silencio automáticamente se reinicia el reproductor.

Inicio rápido
=============

Instale la última versíon de raspbian lite en una tarjeta SD.

Corra el archivo "setup.sh".

Cambiar el archivo de configuración "config.ini" con la URL del streaming, el nombre del radio y el número serial de ser necesario.

Subir la música de respaldo en la carpeta "Music" clasificada en "Dias", "Tardes" y "Noches".

Si se requiere actualizar automáticamente el respaldo, configure syncthing siguiendo esta guía http://www.htpcguides.com/install-syncthing-raspberry-pi-bittorrent-sync-alternative/.

Fije el volumen deseado ejecutando el comando "alsamixer". Guarde la configuración con el comando "sudo alsactl store".

Ejecute el comando "sudo crontab -e" y agregue la siguiente línea: "@reboot sudo /usr/bin/checkSound.sh".
