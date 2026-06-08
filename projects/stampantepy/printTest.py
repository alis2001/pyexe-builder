from __main__ import app, printer_lock
from flask import Flask, Response, make_response
from flask import render_template
# import flask_socketio
# from flask_socketio import emit
from escpos.constants import RT_STATUS_ONLINE, RT_STATUS_PAPER, RT_MASK_NOPAPER, HW_RESET, RT_MASK_ONLINE
from escpos.printer import Network, Serial
from escpos.printer import Usb
from flask import Flask, json, request

import json
import jsonschema
from jsonschema import validate
from jsonschema import Draft202012Validator
from Printer import *


jsonSendCodaSchema = {
    "type": "object",
    "properties": {
        "mode": {"type": "string"},
        "ip": {"type": "string"},
        "idVendor": {"type": "string"},
        "idProduct": {"type": "string"}
    },
    "required": ["mode"]
}


@app.route('/test/', methods=['POST'])
def escpostest():
    """
        La funzione effettua una serie di stampe per poter testare le funzionalità della stampante
    """
    with printer_lock:
        if (Printer.CheckJsonFields(request.json, jsonSendCodaSchema) == ""):
            mode = request.json["mode"]
            if mode == "USB":
                idvendor = int(request.json["idVendor"], 16)
                idproduct = int(request.json["idProduct"], 16)
                try:
                    printer = Usb(idVendor=idvendor, idProduct=idproduct,
                                  timeout=60, in_ep=0x82, out_ep=0x1)
                except:
                    response = make_response(
                        'Non sono riuscito a collegarmi alla stampante')
                    response.status_code = 500
                    response.mimetype = 'application/json'
                    return response
                a = printer.query_status(mode=RT_STATUS_PAPER)
                if a[0] == 1:
                    printer.set(align='center', custom_size=True,
                                width=1, height=1)
                    printer.text("Test 1" + '\n\n')
                    printer.set(align='center', custom_size=True,
                                width=2, height=2)
                    printer.text("Test 2" + '\n')
                    printer.set(align='center', custom_size=True,
                                width=3, height=3)
                    printer.text("Test 3" + '\n')
                    printer.set(align='center', custom_size=True,
                                width=4, height=4)
                    printer.text("Test 4" + '\n')
                    printer.set(align='center', custom_size=True,
                                width=5, height=5)
                    printer.text("Test 5" + '\n')
                    printer.set(align='center', custom_size=True,
                                width=6, height=6)
                    printer.text("Test 6" + '\n\n\n')
                    printer.set(align='center', custom_size=True,
                                width=3, height=3)
                    printer.text("STAMPA QR1" + '\n\n')
                   # printer.qr(data["label"], size=8, impl="bitImageColumn")
                   # printer.text("STAMPA QR2" + '\n\n')
                   # printer.qr(data["label"], size=12, center=True)
                  #  printer.set(align='center', custom_size=True, width=1, height=1)
                   # printer.text("\x1B\x64\x0B")
                    printer.text("Prova taglio parziale" + '\n')
                    printer.text('\x1B\x69')
                    printer.text("\x1B\x64\x03")
                    printer.text("Prova taglio totale" + '\n')
                    printer.text('\x1B\x6D')
                    printer.text("\x1B\x64\x03")
                    printer.close()
                    response = make_response('Test effettuato')
                    response.status_code = 200
                    response.mimetype = 'application/json'
                    return response
                elif a[0] == 5:
                    printer.close()
                    response = make_response('Errore: Carta assente')
                    response.status_code = 400
                    response.mimetype = 'application/json'
                    return response
                else:
                    printer.close()
                    response = make_response('Errore')
                    response.status_code = 400
                    response.mimetype = 'application/json'
                    return response
            elif mode == "ETHERNET":
                ipaddress = request.json["ip"]
                try:
                    printer = Network(ipaddress, 9100, 5)
                except:
                    response = make_response(
                        'Non sono riuscito a collegarmi alla stampante')
                    response.status_code = 500
                    response.mimetype = 'application/json'
                    return response
                pstatus = printer.paper_status()
                if pstatus == 2:
                    printer.set(align='center', custom_size=True,
                                width=1, height=1)
                    printer.text("Test 1" + '\n\n')
                    printer.set(align='center', custom_size=True,
                                width=2, height=2)
                    printer.text("Test 2" + '\n')
                    printer.set(align='center', custom_size=True,
                                width=3, height=3)
                    printer.text("Test 3" + '\n')
                    printer.set(align='center', custom_size=True,
                                width=4, height=4)
                    printer.text("Test 4" + '\n')
                    printer.set(align='center', custom_size=True,
                                width=5, height=5)
                    printer.text("Test 5" + '\n')
                    printer.set(align='center', custom_size=True,
                                width=6, height=6)
                    printer.text("Test 6" + '\n\n\n')
                    printer.set(align='center', custom_size=True,
                                width=3, height=3)
                    printer.text("STAMPA QR1" + '\n\n')
                   # printer.qr(data["label"], size=8, impl="bitImageColumn")
                   # printer.text("STAMPA QR2" + '\n\n')
                   # printer.qr(data["label"], size=12, center=True)
                   # printer.set(align='center', custom_size=True, width=1, height=1)
                    printer.text("\x1B\x64\x0B")
                    printer.text("Prova taglio parziale" + '\n')
                    printer.text('\x1B\x69')
                    printer.text("\x1B\x64\x03")
                    printer.text("Prova taglio totale" + '\n')
                    printer.text('\x1B\x6D')
                    printer.text("\x1B\x64\x03")
                    printer.close()
                    response = make_response('Test effettuato')
                    response.status_code = 200
                    response.mimetype = 'application/json'
                    return response
                elif pstatus == 0:
                    printer.close()
                    response = make_response('Errore: Carta assente')
                    response.status_code = 400
                    response.mimetype = 'application/json'
                    return response
            elif mode == "SERIALE":
                port = request.json["serialPort"]
                # collegamento serial
                try:
                    printer = Serial(port, baudrate=19200)
                except Exception as inst:
                    print(type(inst))  # the exception instance
                    print(inst.args)  # arguments stored in .args
                    print(inst)
                    return Response(response='Non sono riuscito a collegarmi alla stampante', status=500)

                # controllo dello stato della carta nella stampante
                try:
                    pstatus = printer.paper_status()
                    if pstatus == 2:
                        printer.set(align='center', custom_size=True,
                                    width=1, height=1)
                        printer.text("Test 1" + '\n\n')
                        printer.set(align='center', custom_size=True,
                                    width=2, height=2)
                        printer.text("Test 2" + '\n')
                        printer.set(align='center', custom_size=True,
                                    width=3, height=3)
                        printer.text("Test 3" + '\n')
                        printer.set(align='center', custom_size=True,
                                    width=4, height=4)
                        printer.text("Test 4" + '\n')
                        printer.set(align='center', custom_size=True,
                                    width=5, height=5)
                        printer.text("Test 5" + '\n')
                        printer.set(align='center', custom_size=True,
                                    width=6, height=6)
                        printer.text("Test 6" + '\n\n\n')
                        printer.set(align='center', custom_size=True,
                                    width=3, height=3)
                        printer.text("STAMPA QR1" + '\n\n')
                        # printer.qr(data["label"], size=8, impl="bitImageColumn")
                        # printer.text("STAMPA QR2" + '\n\n')
                        # printer.qr(data["label"], size=12, center=True)
                        # printer.set(align='center', custom_size=True, width=1, height=1)
                        printer.text("\x1B\x64\x0B")
                        printer.text("Prova taglio parziale" + '\n')
                        printer.text('\x1B\x69')
                        printer.text("\x1B\x64\x03")
                        printer.text("Prova taglio totale" + '\n')
                        printer.text('\x1B\x6D')
                        printer.text("\x1B\x64\x03")
                        printer.close()
                        response = make_response('Test effettuato')
                        response.status_code = 200
                        response.mimetype = 'application/json'
                        return response
                    elif pstatus == 0:
                        printer.close()
                        response = make_response('Errore: Carta assente')
                        response.status_code = 400
                        response.mimetype = 'application/json'
                        return response
                except Exception as inst:
                    print(type(inst))  # the exception instance
                    print(inst.args)  # arguments stored in .args
                    print(inst)
                    return Response(response='Non sono riuscito a collegarmi alla stampante', status=500)
            else:
                response = make_response("Indicare la modalità di connessione")
                response.status_code = 400
                response.mimetype = 'application/json'
                return response
        else:
            response = make_response(Printer.CheckJsonFields(
                request.json, jsonSendCodaSchema))
            response.status_code = 400
            response.mimetype = 'application/json'
            return response
