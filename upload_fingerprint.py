#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import the PyOTA library
import iota

# Import json
import json

# Import PyFingerprint library
from pyfingerprint.pyfingerprint import PyFingerprint

# Get seed where fingerprints are to be uploaded
MySeed = raw_input("\nWrite or paste seed here: ")

# Define full node to be used when uploading fingerprints from the tangle
NodeURL = "https://nodes.thetangle.org:443"

# Create IOTA object
api=iota.Iota(NodeURL, seed = MySeed) # if you do not specify a seed, PyOTA library randomly generates one for you under the hood
    
# Get a new IOTA address to be used when uploading fingerprints
result = api.get_new_addresses(index=0, count=1, security_level=2)
addresses = result['addresses']
addr = str(addresses[0].with_valid_checksum())

## Tries to initialize the reader
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Gets some sensor information
print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

## Tries to enroll new finger
try:
    print('Waiting for finger...')

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)
    
    ## Downloads the characteristics of template loaded in charbuffer 1
    mychar = f.downloadCharacteristics(0x01)   
    
    # Convert list of characteristics to string
    mystring = json.dumps(mychar)
    
    # Define new IOTA transaction
    pt = iota.ProposedTransaction(address = iota.Address(addr), message = iota.TryteString.from_unicode(mystring), tag = iota.Tag(b'HOTELIOTA'), value=0)

    # Print waiting message
    print("\nSending transaction...Please wait...")

    # Send transaction to the tangle
    FinalBundle = api.send_transfer(depth=3, transfers=[pt], min_weight_magnitude=14)['bundle']
    
    # Print confirmation message 
    print("\nTransaction completed.")

    print("\nAddress used for the transaction was:")
    print(addr)
    

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
