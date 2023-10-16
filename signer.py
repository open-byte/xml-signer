from lxml import etree
from OpenSSL import crypto
from xades import XAdESContext, template
from uuid import uuid4
import base64
import xmlsig
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

import xmlformatter
"""
We need to use another pretty print function because in etree library 
the pretty print function doesn't work correctly (it doesn't indent the xml file)
"""

class XMLSigner(): 
    
    def __init__(self) -> None:
        ...

    def pretty_print_xml_minidom(self, xml_string: str) -> str:
        """
        This function pretty prints an xml file using minidom

        Args:
            xml_string (str): xml file in string format

        Returns:
            str: pretty printed xml file in string format
        """
        formatter = xmlformatter.Formatter(indent="4", indent_char=" ", encoding_output="utf-8", preserve=["literal"])
        
        pretty_xml: str = formatter.format_string(xml_string).decode('utf-8')

        return pretty_xml


    def sign_xml(self, xml: str, p12_certificate: bytes, certificate_code: str, output_base64: bool = False) -> str:
        """
        This function signs an xml file with a certificate and returns the signed xml file

        Args:
            xml (str): xml file in string format
            certificate (bytes): p12 certificate
            certificate_code (str): pin (4 digits)
            output_base64 (bool, optional): If True, the output will be in base64 format. Defaults to False.

        Returns:
            str: signed xml file in string format simple or base64
        """
        parsed_file = etree.fromstring(xml.encode('utf-8'))

        signature_id = f'Signature-{str(uuid4())}'
        reference_id = f'Reference-{str(uuid4())}'
        signature = xmlsig.template.create(
            xmlsig.constants.TransformInclC14N,
            xmlsig.constants.TransformRsaSha256,
            signature_id,
        )
        ref = xmlsig.template.add_reference(
            signature, 
            xmlsig.constants.TransformSha256,
            uri="", 
            name=reference_id
        )
        xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)

        xmlsig.template.add_reference(
            signature,
            xmlsig.constants.TransformSha256, 
            uri=f"#KeyInfoId-{signature_id}", 
            name="ReferenceKeyInfo"
        )

        xmlsig.template.add_reference(
            signature, 
            xmlsig.constants.TransformSha256,
            uri=f"#SignedProperties-{signature_id}",
            uri_type="http://uri.etsi.org/01903#SignedProperties",
        )

        key = xmlsig.template.ensure_key_info(signature, name=f"KeyInfoId-{signature_id}")
        x509_data = xmlsig.template.add_x509_data(key)
        xmlsig.template.x509_data_add_certificate(x509_data)
        xmlsig.template.add_key_value(key)
        qualifying = template.create_qualifying_properties(
            signature, name=f"Qualifying-Properties-{signature_id}", etsi='xades'
        )
        props = template.create_signed_properties(qualifying, name=f'SignedProperties-{signature_id}')
        template.add_production_place(props)
        parsed_file.append(signature)
        cryto_certificate = crypto.load_pkcs12(p12_certificate, certificate_code.encode('utf-8'))

        ctx = XAdESContext(
            None,
            (cryto_certificate.get_certificate().to_cryptography(), ),
        )
        ctx.load_pkcs12(cryto_certificate)
        ctx.sign(signature)

        parsed_file.append(signature) 
        signed_xml = etree.ElementTree(parsed_file)
        
        output_signed_xml: str = etree.tostring(signed_xml, pretty_print=True).decode('utf-8')
        
        if output_base64:
            return base64.b64encode(output_signed_xml.encode('utf-8')).decode('utf-8')
        
        pretty_signed_xml: str = self.pretty_print_xml_minidom(output_signed_xml)
        
        return pretty_signed_xml
