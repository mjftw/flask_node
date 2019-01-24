import threading
from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE
import netifaces
import time

from flask_node.txclasses import TempSensorTx, SmartPlugTx, TempControllerTx

def main():
    ipaddr = netifaces.ifaddresses('wlan0')[AF_INET][0]['addr']

    temp_sensor = TempSensorTx(
        name="TempSensor",
        host=ipaddr,
        port=5010
    )
    smart_plug = SmartPlugTx(
        name="Heater",
        host=ipaddr,
        port=5020
    )
    temp_control = TempControllerTx(
        name='TempController',
        host=ipaddr,
        port=5030,
        temp_host=temp_sensor.host,
        temp_port=temp_sensor.port,
        plug_host=smart_plug.host,
        plug_port=smart_plug.port,
        target_temp=18.5,
        tolerance=0.15,
        loop_sleep=5,
        pause_sleep=1
    )

    threads = [
        threading.Thread(target=temp_sensor.run_api),
        threading.Thread(target=smart_plug.run_api),
        threading.Thread(target=temp_control.run_api),
    ]

    for t in threads:
        t.start()
        time.sleep(0.5)

if __name__ == "__main__":
    main()
