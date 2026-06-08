from datetime import date, datetime, time
import locale
from escpos.constants import RT_STATUS_ONLINE, RT_STATUS_PAPER, RT_MASK_NOPAPER, HW_RESET, RT_MASK_ONLINE
from escpos.printer import Network
from escpos.printer import Usb
import json
import jsonschema
from jsonschema import validate
from jsonschema import Draft202012Validator


class Printer:
    def __init__(self,mode,ip,idVendor,idProduct,descrizione,label,count,orarioIngresso="",labelDescrizione="",letturaStatoCarta = False,percorso=False):
        self.mode = mode
        self.ip = ip
        self.idVendor = idVendor
        self.idProduct = idProduct
        self.descrizione = descrizione
        self.label = label
        self.labelDescrizione = labelDescrizione
        self.count = str(count)
        self.orarioIngresso =orarioIngresso
        self.letturaStatoCarta = letturaStatoCarta
        self.percorso = percorso

    @staticmethod
    def CheckJsonFields(jsonData,jsonSchema):
        """
            La funzione controlla l'esistenza delle chiavi del json dato in input
        """    
        try:
            isValid = Draft202012Validator(jsonSchema)
            errors = sorted(isValid.iter_errors(jsonData), key=lambda e: e.path)
            if(len(errors) == 0):
                return ""
            else:
                errore = ""
                for error in errors:
                    errore += error.message
            return errore
        except Exception as e:
            return e

    def printReceipt(self, printer, mode, paperWidth='80mm'):
        dt_string = datetime.now()
        try:
            locale.setlocale(locale.LC_TIME, "it_IT")  # O basato su condizione se necessario
        except Exception as e:
            print(f"Errore di connessione alla stampante: {e}")
        dataOra = dt_string.strftime("%A %d/%m/%Y %H:%M").translate({ord(c): "i'" for c in "ì"})

        printer.text('\x1b\x40')
        printer.text('\x1d\x4c \x00')
        # TODO
        # Stampare il logo se necessario (omesso per brevità)
        # printer.set(align='center', custom_size=True, width=2, height=2)
        # printer.image(img_source="logo.jpg", impl="bitImageColumn")

        # Sezione comune per la stampa di testo, categorie, ecc.
        # (Utilizza condizioni per le impostazioni specifiche di modalità o larghezza della carta)
        printer.text('\n')
        # Stampa della categoria e del codice
        if paperWidth == '56mm' or paperWidth == 56:
            # Impostazioni per carta più stretta
            printer.set(align='center', custom_size=True, width=2, height=2)
        else:
            # Impostazioni per carta standard
            printer.set(align='center', custom_size=True, width=3, height=3)
        printer.text(self.descrizione + '\n\n')

        if paperWidth == '56mm' or paperWidth == 56:
            printer.set(align='center', custom_size=True, width=3, height=3)
        else:
            printer.set(align='center', custom_size=True, width=3, height=3)
        printer.text(self.label + '\n\n')

        # Stampa degli utenti in coda con dimensione standard per tutti i tipi di carta

        if self.count:
            printer.set(align='center', custom_size=True, width=1, height=1)
            printer.text("Utenti in coda: ")
            printer.text(self.count + '\n\n')

        #if self.percorso:
        #    printer.set(align='start', custom_size=True, width=1, height=1)
        #    printer.text("Percorso: ")
        #    printer.text(self.labelDescrizionePercorso + '\n\n')
        # Stampa info aggiuntive se presenti
        if self.labelDescrizione:
            printer.set(align='center', custom_size=True, width=1, height=1)
            printer.text("Info: ")
            printer.text(self.labelDescrizione + '\n\n')

        # Stampa della data di accesso
        printer.set(align='center', custom_size=False)  # Reset delle impostazioni di stampa
        printer.text("Data di Accesso in struttura: \n")
        printer.text(dataOra + '\n')

        # Rollout della carta e taglio parziale
        printer.text("\x1B\x64\x05")  # Rollout della carta
        printer.text('\x1B\x69') # Taglio parziale per alcune stampanti
        printer.text('\x1d\x65')
        printer.text('\x03\x0C')

        # Chiusura della connessione con la stampante
        printer.close()