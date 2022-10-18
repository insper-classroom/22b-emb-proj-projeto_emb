import pyautogui
import serial
import argparse
import time
import logging

class MyControllerMap:
    def __init__(self):
        self.first = True
        self.initialBand = 0;
        self.button = {'21': ['ctrl', 'left'], '22':'space', '23':['ctrl', 'right']} # Fast forward (10 seg) pro Youtube
        self.acceptable = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\x09', b'\x0A', b'\x0B', b'\x0C', b'\x0D', b'\x0E', b'\x0F', b'\x10' ]

class SerialControllerInterface:
    # Protocolo
    # byte 1 -> Botão 1 (estado - Apertado 1 ou não 0)
    # byte 2 -> EOP - End of Packet -> valor reservado 'X'
    
    def control_volume(self, mult):
        logging.info("KEYDOWN Control Left")
        type = 'inc' if mult > 0 else 'dec';
        for i in range(0,abs(mult)):
            pyautogui.keyDown('ctrl')
            pyautogui.keyDown('up' if type=='inc' else 'down')
            pyautogui.keyUp('ctrl')
            pyautogui.keyUp('up' if type=='inc' else 'down')
        

    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate=baudrate)
        self.mapping = MyControllerMap()
        self.incoming = '0'
        pyautogui.PAUSE = 0  ## remove delay
    
    def update(self):
        ## Sync protocol
        while self.incoming != b'X':
            self.incoming = self.ser.read()
            logging.debug("Received INCOMING: {}".format(self.incoming))

        data = self.ser.read()
        logging.debug("Received DATA: {}".format(data))

        if (data == b'\x15'):
            # print("1\n")
            logging.info("KEYDOWN Control Left")
            pyautogui.keyDown(self.mapping.button['21'][0])
            pyautogui.keyDown(self.mapping.button['21'][1])
            pyautogui.keyUp(self.mapping.button['21'][0])
            pyautogui.keyUp(self.mapping.button['21'][1])
        elif (data == b'\x16'):
            # print("2\n")
            logging.info("KEYDOWN Space ")
            pyautogui.press(self.mapping.button['22'])
        elif (data == b'\x17'):
            # print("3\n")
            logging.info("KEYDOWN Control Right")
            pyautogui.keyDown(self.mapping.button['23'][0])
            pyautogui.keyDown(self.mapping.button['23'][1])
            pyautogui.keyUp(self.mapping.button['23'][0])
            pyautogui.keyUp(self.mapping.button['23'][1])
        elif data in self.mapping.acceptable:
            newBand =  self.mapping.acceptable.index(data)
            if self.mapping.first:
                self.control_volume(newBand*-1)
                self.mapping.first= False
            elif (newBand != self.mapping.initialBand):
                mult = newBand-self.mapping.initialBand;
                self.mapping.initialBand = newBand;
                self.control_volume(mult)
 
        self.incoming = self.ser.read()


class DummyControllerInterface:
    def __init__(self):
        self.mapping = MyControllerMap()

    def update(self):
        pyautogui.keyDown(self.mapping.button['A'])
        time.sleep(0.1)
        pyautogui.keyUp(self.mapping.button['A'])
        logging.info("[Dummy] Pressed A button")
        time.sleep(1)


if __name__ == '__main__':
    interfaces = ['dummy', 'serial']
    argparse = argparse.ArgumentParser()
    argparse.add_argument('serial_port', type=str)
    argparse.add_argument('-b', '--baudrate', type=int, default=115200)
    argparse.add_argument('-c', '--controller_interface', type=str, default='serial', choices=interfaces)
    argparse.add_argument('-d', '--debug', default=False, action='store_true')
    args = argparse.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    print("Connection to {} using {} interface ({})".format(args.serial_port, args.controller_interface, args.baudrate))
    if args.controller_interface == 'dummy':
        controller = DummyControllerInterface()
    else:
        controller = SerialControllerInterface(port=args.serial_port, baudrate=args.baudrate)

    while True:
        controller.update()
