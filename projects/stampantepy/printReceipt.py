import locale
import threading
import time
import select
from flask import Flask, Response, make_response, jsonify
from flask import render_template
# import flask_socketio
# from flask_socketio import emit
from escpos.constants import RT_STATUS_ONLINE, RT_STATUS_PAPER, RT_MASK_NOPAPER, HW_RESET, RT_MASK_ONLINE
from escpos.printer import Network
from escpos.printer import Usb
from escpos.printer import Serial
from flask import Flask, json, request
import json
import jsonschema
from jsonschema import validate
from jsonschema import Draft202012Validator
from __main__ import app, printer_lock
from datetime import datetime
from Printer import Printer
import functools
import time

from funzioniStampante import verifica_stato_carta, risposta_stampante

jsonSendCodaSchema = {
    "type": "object",
    "properties": {
        "mode": {"type": "string"},
        "ip": {"type": "string"},
        "idVendor": {"type": "string"},
        "idProduct": {"type": "string"},
        "descrizione": {"type": "string"},
        "porta_stampante": {"type": "string"},
        "categoria_numero": {"type": "string"},
        "label": {"type": "string"},
        "count": {"type": "number"},
        "prefisso": {"type": "string"},
        "letturaStatoCarta": {"type": "boolean"},
        "tipo_rotolo": {"type": "string"},
        "percorso": {"type": "boolean"}
    },
    "required": ["mode"]
}
def configura_printer(data):
    required_fields = ["mode"]
    if not all(field in data for field in required_fields):
        return None, jsonify({"error": "Campo 'mode' mancante o non valido"}), 400

    device_mode = data["mode"].upper()
    letturaStatoCarta = data.get("letturaStatoCarta", False)

    if device_mode == "USB":
        required_fields = ["idVendor", "idProduct"]
        if not all(field in data for field in required_fields):
            return None,None, jsonify({"error": "Campi 'idVendor' o 'idProduct' mancanti o non validi"}), 400
        try:
            printer = Usb(idVendor=int(data["idVendor"], 16), idProduct=int(data["idProduct"], 16), timeout=30,
                          in_ep=0x82, out_ep=0x1)
        except Exception as e:
            return None,None, jsonify({"error": str(e)}), 500

    elif device_mode == "ETHERNET":
        required_fields = ["ip", "port"]
        if not all(field in data for field in required_fields):
            return None, jsonify({"error": "Campi 'ip' o 'port' mancanti o non validi"}), 400
        try:
            printer = Network(data["ip"], int(data["port"]), 10)
        except Exception as e:
            return None,None, jsonify({"error": str(e)}), 500

    elif device_mode == "SERIALE":
        required_fields = ["serialPort"]
        if not all(field in data for field in required_fields):
            return None, jsonify({"error": "Campo 'serialPort' mancante o non valido"}), 400
        try:
            printer = Serial(data["serialPort"], baudrate=19200, dsrdtr=False, timeout=1)
        except Exception as e:
            return None,None, jsonify({"error": str(e)}), 500

    else:
        return None,None, jsonify({"error": "Modalità di connessione non supportata"}), 400

    return printer, letturaStatoCarta ,None, None  # Restituisce l'oggetto printer e nessun messaggio di errore

@app.route('/printTicket/', methods=['POST'])
def receipt():
    with printer_lock:
       try:
            printer, letturaStatoCarta, error_response, status_code = configura_printer(request.json)
            if error_response:
                return error_response, status_code
            pstatus = verifica_stato_carta(printer, letturaStatoCarta)
            if pstatus == 1 or pstatus == 2 or pstatus is None:
                device = Printer(mode= request.json["mode"].upper(),
                                 ip = request.json.get("ip", ''),
                                 idVendor = request.json.get("idVendor", ''),
                                 idProduct = request.json.get("idProduct", ''),
                                 descrizione = request.json.get("descrizione", ''),
                                 label = request.json.get("label", ''),
                                 count = request.json.get("count", ''),
                                 orarioIngresso = request.json.get("orarioIngresso", ''),
                                 labelDescrizione = request.json.get("labelDescrizione", ''),
                                 letturaStatoCarta = request.json.get("letturaStatoCarta", False),
                                 percorso = request.json.get("percorso",False))
                # Qui implementi la logica specifica di stampa per ciascun dispositivo, esempio per USB
                time.sleep(0.5)
                device.printReceipt(printer, request.json["mode"].upper(), request.json.get("tipo_rotolo", 80))
                return risposta_stampante(True, 'Stampa Scontrino effettuata', 200)
            elif pstatus == 5 or pstatus == 0:
                return risposta_stampante(False, 'Errore: Carta assente', 400)
            else:
                return risposta_stampante(False)
       except Exception as e:
            print(f"Errore di connessione alla stampante: {e}")
            return jsonify({"error": "Non sono riuscito a collegarmi alla stampante"}), 500
       finally:
            if 'printer' in locals():
                printer.close()  # Assicurati che questa operazione sia supportata dal tuo oggetto printer


@app.route('/paperstatus/', methods=['POST'])
def get_all_devices(printer_lock):
    with printer_lock:
        printer, letturaStatoCarta, error_response, status_code = configura_printer(request.json)
        if error_response:
            return error_response, status_code
        pstatus = verifica_stato_carta(printer, letturaStatoCarta)
        printer.close()
        if pstatus == 1 or pstatus == 2:
            response = make_response('Carta Presente')
            response.status_code = 200
            response.mimetype = 'application/json'
            return response
        elif pstatus == 5 or pstatus == 0:
            response = make_response('Carta Assente')
            response.status_code = 200
            response.mimetype = 'application/json'
            return response
        else:
            response = make_response("Non sono riuscito a rilevare la carta")
            response.status_code = 400
            response.mimetype = 'application/json'
            return response
