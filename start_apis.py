import threading
from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE
import netifaces
import time

from flask_node.txclasses import TempSensorTx, SmartPlugTx, TempControllerTx, \
    DataLoggerTx


def log_to_csv(data):
    timestamp = data[0]
    samples = data[1]

    with open('./data.csv', 'a') as f:
        for s in samples:
            line = '{},{}'.format(timestamp, s)
            for k, v in samples[s].items():
                line += ',{},{}'.format(k, v)
            line += '\n'
            f.write(line)


def main():
    ipaddr = netifaces.ifaddresses('wlan0')[AF_INET][0]['addr']

    temp_sensor = TempSensorTx(
        name="TempSensor",
        host=ipaddr,
        port=5010
    )
    hot_socket = SmartPlugTx(
        name="HeatMat",
        socket=1,
        host=ipaddr,
        port=5020
    )
    cold_socket = SmartPlugTx(
        name="Fridge",
        socket=2,
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
        setpoint=19,
        tolerance=0.15,
        loop_sleep=10,
        pause_sleep=1
    )
    data_logger = DataLoggerTx(
        name='TempLogger',
        host=ipaddr,
        port=5050,
        loop_sleep=10,
        pause_sleep=1,
        save_func=log_to_csv,
        watches='''
            [{
                "host": "192.168.0.210",
                "port": 5010,
                "methods": {
                    "get_value": "Temperature"
                }
            },
            {
                "name": "ChillyFridge",
                "host": "192.168.0.210",
                "port": 5040,
                "methods": {
                    "get_temperature": "Temperature",
                    "get_state": "State"
                }
            }]
        '''
    )

    threads = [
        threading.Thread(setpoint=temp_sensor.run_api),
        threading.Thread(setpoint=hot_socket.run_api),
        threading.Thread(setpoint=cold_socket.run_api),
        threading.Thread(setpoint=temp_control.run_api),
        threading.Thread(setpoint=data_logger.run_api),
    ]

    for t in threads:
        t.start()
        time.sleep(0.5)

if __name__ == "__main__":
    main()
