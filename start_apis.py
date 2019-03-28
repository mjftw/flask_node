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
    hot_socket = SmartPlugTx(
        name="HeatMat",
        host=ipaddr,
        port=5020
    )
    cold_socket = SmartPlugTx(
        name="Fridge",
        host=ipaddr,
        port=5030
    )
    temp_control = TempControllerTx(
        name='BrewFridge',
        host=ipaddr,
        port=5040,
        sensor_host=temp_sensor.host,
        sensor_port=temp_sensor.port,
        hot_host=hot_socket.host,
        hot_port=hot_socket.port,
        cold_host=cold_socket.host,
        cold_port=cold_socket.port,
        target_temp=19,
        tolerance=0.15,
        loop_sleep=5,
        pause_sleep=1
    )

    threads = [
        threading.Thread(target=temp_sensor.run_api),
        threading.Thread(target=hot_socket.run_api),
        threading.Thread(target=cold_socket.run_api),
        threading.Thread(target=temp_control.run_api),
    ]

    for t in threads:
        t.start()
        time.sleep(0.5)

if __name__ == "__main__":
    main()
