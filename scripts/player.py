#!/usr/bin/env python3

import errno
import logging
import logging.handlers
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from threading import Thread
from time import sleep
from urllib.error import URLError
from urllib.request import urlopen

try:
    from termcolor import colored
except ImportError:
    def colored(text, _color):
        return text


def is_raspberry_pi():
    model_path = "/sys/firmware/devicetree/base/model"
    try:
        if os.path.exists(model_path):
            with open(model_path, "r", encoding="utf-8", errors="ignore") as model_file:
                return "raspberry" in model_file.read().lower()
    except OSError:
        return False
    return False


IS_RASPBERRY = is_raspberry_pi()
HAS_GPIO = False
HAS_LCD = False
GPIO = None
LCD = None

if IS_RASPBERRY:
    try:
        import RPi.GPIO as imported_gpio
        GPIO = imported_gpio
        HAS_GPIO = True
    except ImportError:
        HAS_GPIO = False

    try:
        from lcd import LCD as imported_lcd
        LCD = imported_lcd
        HAS_LCD = True
    except ImportError:
        HAS_LCD = False


RUN_RADIO_MODE = IS_RASPBERRY and HAS_GPIO and HAS_LCD

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Basic commands
cmd_ip = "hostname -I | awk '{print $1}'"
cmd_play_bkp1 = "mpg123 -z /home/pi/Music/Dias/* &"
cmd_play_bkp2 = "mpg123 -z /home/pi/Music/Tardes/* &"
cmd_play_bkp3 = "mpg123 -z /home/pi/Music/Noches/* &"
cmd_stop_all = "killall mpg123"
cmd_check_sound = "pgrep -x mpg123 | wc -l"
cmd_check_device = "cat /proc/asound/card0/pcm0p/sub0/status | awk '/state/ {print $2}'"

logger = logging.getLogger("ExeaMediaPlayer")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="[%(asctime)s] %(name)s [%(levelname)s]: %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
)

file_handler = logging.handlers.RotatingFileHandler(
    filename=os.path.join(LOGS_DIR, "player.log"),
    mode="a",
    maxBytes=1024000,
    backupCount=30,
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if not RUN_RADIO_MODE:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

thread_finished = False
url = ""
title = ""
serial = ""
ledTest = 2


if RUN_RADIO_MODE:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ledTest, GPIO.OUT)


def run_cmd(cmd, capture_output=True):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if capture_output:
        output, _ = process.communicate()
        return output.decode("utf-8", errors="ignore").strip()
    return None


def checkInternetConnection():
    try:
        urlopen(url, timeout=10).close()
        logger.info("Checking Internet... [OK]")
        return True
    except URLError:
        logger.warning("Checking Internet... [Failed]")
        return False
    except socket.error as socket_error:
        if socket_error.errno != errno.ECONNRESET:
            raise
        return False


def dateInRange(initialHour, initialMinute, finalHour, finalMinute):
    currentHour = datetime.now().hour
    currentMinute = datetime.now().minute

    if initialHour <= currentHour <= finalHour:
        if currentHour == initialHour:
            return currentMinute >= initialMinute
        if currentHour == finalHour:
            return currentMinute <= finalMinute
        return True
    return False


def playOnline():
    run_cmd(cmd_stop_all, True)
    cmd_play_streaming = "mpg123 " + url + " &"
    if RUN_RADIO_MODE:
        GPIO.output(ledTest, 0)
    logger.info("Playing online")
    run_cmd(cmd_play_streaming, True)
    return True


def playBackup():
    run_cmd(cmd_stop_all, False)
    logger.info("Playing backup")
    if RUN_RADIO_MODE:
        GPIO.output(ledTest, 1)

    if dateInRange(0, 0, 11, 0):
        run_cmd(cmd_play_bkp1, True)
        return "Dias"
    if dateInRange(11, 0, 18, 0):
        run_cmd(cmd_play_bkp2, True)
        return "Tardes"
    if dateInRange(18, 0, 23, 59):
        run_cmd(cmd_play_bkp3, True)
        return "Noches"
    return True


def reboot():
    global thread_finished
    logger.info("Button reboot pressed... [OK]")
    if RUN_RADIO_MODE:
        run_cmd("/sbin/reboot", False)
    else:
        logger.info("Reboot requested in console mode (omitted).")
    print("Reboot pressed!")
    thread_finished = True


def buttons():
    global thread_finished
    if not RUN_RADIO_MODE:
        logger.info("Buttons thread skipped (console mode).")
        return

    buttonShutdown = 11
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buttonShutdown, GPIO.IN)

    while True:
        if GPIO.input(buttonShutdown):
            lcd = LCD()
            lcd.clear()
            lcd.begin(16, 1)
            lcd.message("Reiniciando\nSistema...")
            sleep(2)
            lcd.clear()
            reboot()
        sleep(4)
    thread_finished = True


def checkSoundOutput():
    global thread_finished
    sleep(60)

    while True:
        output = run_cmd(cmd_check_sound, True)[:1]
        if output != "1":
            logger.error("mpg123 is not running")
            logger.critical("The software will be restarted")
            run_cmd(cmd_stop_all, False)
            playStreaming()
        sleep(60)
    thread_finished = True


def playStreaming():
    if checkInternetConnection():
        playOnline()
        return True
    playBackup()
    return False


def stateoff():
    global thread_finished
    while True:
        if not checkInternetConnection():
            if playStreaming():
                logger.info("Changing to backup mode")
                run_cmd(cmd_stop_all, False)
                playStreaming()
        sleep(60)
    thread_finished = True


def stateon():
    global thread_finished
    while True:
        if checkInternetConnection():
            if not playStreaming():
                logger.info("Changing to online mode")
                run_cmd(cmd_stop_all, False)
                playStreaming()
        sleep(60)
    thread_finished = True


def get_ip():
    if shutil.which("hostname"):
        return run_cmd(cmd_ip, True)
    return ""


def get_device_status():
    if os.path.exists("/proc/asound/card0/pcm0p/sub0/status"):
        return run_cmd(cmd_check_device, True)[:16]
    return "N/A"


def lcd_main():
    logger.info("Player started in radio mode!")
    lcd = LCD()
    lcd.clear()
    lcd.begin(16, 1)

    while True:
        status = get_device_status()
        lcd.clear()
        lcd.message("ExeaMusicPlayer\n")
        lcd.message("Estado: " + status)
        sleep(2)

        lcd.clear()
        lcd.message("Escuchas:\n")
        lcd.message(title[:16])
        sleep(2)

        lcd.clear()
        lcd.message("Serial:\n")
        lcd.message(serial[:16])
        sleep(3)

        lcd.clear()
        ipaddr = get_ip()
        if not ipaddr:
            lcd.message("Sin Internet\n")
        else:
            lcd.message(ipaddr[:16])

        for _ in range(10):
            lcd.message(datetime.now().strftime("%b %d %H:%M:%S\n"))
            sleep(1)


def console_main():
    logger.info("Player started in console mode!")
    while True:
        status = get_device_status()
        ipaddr = get_ip() or "Sin Internet"
        logger.info("Estado=%s | Radio=%s | Serial=%s | IP=%s", status, title.strip(), serial, ipaddr)
        sleep(5)


def main():
    if RUN_RADIO_MODE:
        lcd_main()
    else:
        console_main()


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        url = sys.argv[1]
        serial = sys.argv[2]
        title = " ".join(sys.argv[3:]).strip()
        print("The url of the streaming is:", colored(url, "green"))
        print("The name of the radio is:", colored(title, "green"))
        print("The serial of the radio is", colored(serial, "green"))
        logger.info("Execution mode: %s", "radio" if RUN_RADIO_MODE else "console")
        logger.info("The url of the streaming is: %s", url)
        logger.info("The name of the radio is: %s", title)
        logger.info("The serial of the radio is: %s", serial)
    else:
        print("Usage: player.py {url} {serial} {title}")
        logger.error("Usage: player.py {url} {serial} {title}")
        sys.exit(1)

    try:
        Thread(target=playStreaming, args=(), daemon=True).start()
        Thread(target=main, args=(), daemon=True).start()
        Thread(target=stateoff, args=(), daemon=True).start()
        Thread(target=stateon, args=(), daemon=True).start()
        Thread(target=checkSoundOutput, args=(), daemon=True).start()
        if RUN_RADIO_MODE:
            Thread(target=buttons, args=(), daemon=True).start()

        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Bye!")
        logger.info("Bye!")
    except Exception as errtxt:
        logger.info("Program finished by external exception")
        logger.error(errtxt)
