import usb.core
from flask import jsonify, make_response

class Device:
    def __init__(self, idVendor, idProduct):
        self.idVendor = idVendor
        self.idProduct = idProduct

    @staticmethod
    def make_device(idVendor, idProduct):
        return {"idVendor": idVendor, "idProduct": idProduct}

def get_all_devices_usb(printer_lock):
    with printer_lock:
        try:
            dev = usb.core.find(find_all=True)
            deviceList = []
            for cfg in dev:
                device_id = {"Decimal VendorID": str(cfg.idVendor),
                             "Decimal ProductID": str(cfg.idProduct),
                             "Hexadecimal VendorID": hex(cfg.idVendor),
                             "Hexadecimal ProductID": hex(cfg.idProduct)}
                deviceList.append(device_id)
            return jsonify(deviceList), 200
        except Exception as e:
            return make_response(jsonify({"error": "Nessun dispositivo connesso in modalità USB o errore nel rilevamento dei dispositivi", "details": str(e)}), 500)

# Supponiamo che printer_lock venga passato alla funzione all'atto della chiamata
def check_status(printer_lock):
    with printer_lock:
        # Qui potresti inserire qualsiasi logica specifica per controllare lo stato.
        # Per ora, restituiamo semplicemente un messaggio che indica che il servizio è attivo.
        return jsonify({"status": "Service is up and running"}), 200