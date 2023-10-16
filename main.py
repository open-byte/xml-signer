#!/usr/bin/env python3
################################################################
# Date: 15 Oct 2023
# Author: Izcar J. Muñoz Torrez
# --------------------------------------------------------------
#   ____                     ____        _
#  / __ \                   |  _ \      | |
# | |  | |_ __   ___ _ __   | |_) |_   _| |_ ___
# | |  | | '_ \ / _ \ '_ \  |  _ <| | | | __/ _ \
# | |__| | |_) |  __/ | | | | |_) | |_| | ||  __/
#  \____/| .__/ \___|_| |_| |____/ \__, |\__\___|
#        | |                        __/ |
#        |_|                       |___/
# --------------------------------------------------------------
################################################################

from xml.etree.ElementTree import XML
from signer import XMLSigner
import typer


def signer(
        xml_path: str = typer.Option(help='Path or name to xml file to sign (Factura Electrónica CR)'),
        p12_path: str = typer.Option(help='Path or name to p12 certificate'),
        pin: str = typer.Option(help='Pin of the certificate (4 digits)'),
        base64: bool = typer.Option(default=False, help='If True, the output will be in base64 format')
    )-> None: 
    
    xml_signer = XMLSigner()
    
    p12_certificate: bytes
    xml: str
    
    with open(p12_path, 'rb') as p12_certificate_file:
        p12_certificate = p12_certificate_file.read()
    
    with open(xml_path, 'r') as xml_file:
        xml = xml_file.read()
    
    if base64:
        print('\nSigned xml in base64 format saved in signed_base64.txt 🎯💯🔑\n')
        print(
            xml_signer.sign_xml(xml, p12_certificate, pin, base64),
            file=open('signed_base64.txt', 'w')
        )
        
    else:
        print(
            xml_signer.sign_xml(xml, p12_certificate, pin, base64),
            file=open('signed.xml', 'w')
        )
        print('\nSigned xml saved in signed.xml 🎯💯🔑\n')
        

if __name__ == '__main__':
    typer.run(signer)
