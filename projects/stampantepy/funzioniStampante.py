from escpos.constants import RT_STATUS_PAPER
from flask import Response, jsonify


def verifica_stato_carta(printer, letturaStatoCarta=True):
    if letturaStatoCarta:
        try:
            stato = printer.query_status(mode=RT_STATUS_PAPER)[0]
            return stato
        except:
            return None  # o un valore di default che indichi un errore
    return 1  # Se non devi leggere lo stato della carta, ritorna un valore che indichi "carta presente"

def risposta_stampante(stato, printer=None):
    if printer:
        printer.close()
    if stato == 1 or stato == 2:
        return Response(response='Stampa effettuata', status=200)
    elif stato == 5 or stato == 0:
        return Response(response='Errore: Carta assente', status=400)
    else:
        return Response(response='Qualcosa è andato storto', status=500)

def risposta_stampante(successo, messaggio='Qualcosa è andato storto', stato=500):
    return jsonify({"message": messaggio}), stato if successo else (jsonify({"error": messaggio}), stato)
