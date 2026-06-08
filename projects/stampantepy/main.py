from flask import Flask
import threading

from printStatus import get_all_devices_usb, check_status as ps_check_status

app = Flask(__name__)
printer_lock = threading.Lock()

# Costanti
STATUS_CODE_OK = 200
STATUS_CODE_ERROR = 500
STATUS_CODE_BAD_REQUEST = 400

from printReceipt import *

def create_response(message, status_code=STATUS_CODE_OK, error=False):
    """Crea una risposta JSON uniforme per l'API."""
    status = "error" if error else "success"
    return jsonify({"status": status, "message": message}), status_code


@app.route('/getAllUsbDevices/', methods=['GET'])
def get_all_usb_devices():
    return get_all_devices_usb(printer_lock)

@app.route('/checkStatus/', methods=['GET'])
def check_status():
    # Qui passiamo printer_lock a check_status in printstatus.py
    return ps_check_status(printer_lock)

def run():
    """Funzione di entry point per avviare il server."""
    app.run(host='0.0.0.0', port=5050)


# Avvio manuale per debug o esecuzione diretta del file
if __name__ == '__main__':
    run()
