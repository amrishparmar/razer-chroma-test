import sys
import signal
from threading import Thread
from time import sleep
import requests


class RazerApp():
    def __init__(self, payload):
        r = requests.post("http://localhost:54235/razer/chromasdk", json=payload)
        self.uri = r.json()['uri']  # assign the uri from the SDK server response
        self.alive = True
        self._start_heartbeat()

    def set_static_colour(self, colour):
        """Set Razer Chroma keyboard LEDs to a given colour

        :param colour: An integer representing a BGR colour
        """
        payload = {
            'effect': 'CHROMA_STATIC',
            'param': {
                'color' : colour,
            }
        }

        # send put request to set the colour
        requests.put(self.uri + '/keyboard', json=payload)

    def disconnect(self):
        """End connection to the SDK server"""
        self.alive = False
        self._hb_thread.join()
        requests.delete(self.uri)

    def _heartbeat(self):
        """Send a heartbeat to the SDK every second"""
        while self.alive:
            requests.put(self.uri + '/heartbeat')
            sleep(1)

    def _start_heartbeat(self):
        """Start the heartbeat thread to keep the SDK server connection alive"""
        self._hb_thread = Thread(target=self._heartbeat)
        self._hb_thread.start()
        

def main():
    try:
        colour = int(sys.argv[1])
        if colour < 0 or colour > 16777215: 
            raise ValueError
    except (ValueError, IndexError):
        print('Usage: python razer_test.py [integer, 0 - 16777215]')
        sys.exit(1)

    app_data = {
        "title": "RazerTestApp",
        "description": "A test application with the Razer SDK",
        "author": {
            "name": "Amrish Parmar",
            "contact": "amrish@example.com"
        },
        "device_supported": ["keyboard"],
        "category": "application"
    }
    
    print('Initialising...')
    app = RazerApp(app_data)
    
    print('Setting colour to {}...'.format(colour), end='')
    app.set_static_colour(colour)
    print('Colour set.')

    def quit_program(signal, frame):
        """Signal interrupt handler for quitting program"""
        app.disconnect()
        print('Goodbye!')
        sys.exit(0)

    signal.signal(signal.SIGINT, quit_program)
    print('Press Ctrl-C to exit...')
    
    # keep waiting until the user quits (using sleep since signal.pause() doesn't work on windows)
    while True:
        sleep(60)
    

if __name__ == '__main__':
    main()