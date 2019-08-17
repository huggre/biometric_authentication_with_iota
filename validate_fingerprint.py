#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports from the PyOTA library
from iota import Iota
from iota import Address
from iota import Transaction
from iota import TryteString

# Import json library
import json

# Import PyFingerprint library
from pyfingerprint.pyfingerprint import PyFingerprint

## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

# Clear any fingerprints currently stored in the reader
f.clearDatabase()

# Get seed where fingerprints are stored
MySeed = raw_input("\nWrite or paste seed here: ")

# Define full node to be used when retrieving fingerprints from the tangle
iotaNode = "https://nodes.thetangle.org:443"

# Create an IOTA object
api = Iota(iotaNode, seed=MySeed)

print("\nRetrieving fingerprint characteristics from the tangle..")

# Get seed account data from the tangle
accdata = api.get_account_data(start=0, stop=None)

print("\nUploading fingerprint characteristics to the reader..")

# Get all bundles related to the seed
bundles = accdata['bundles']

# Define bundle counter
i=0

# For each bundle...
for bundle in bundles:
    
    # Get Bundle message
    msg = bundle.get_messages()
    
    # Converts message to a list of fingerprint characteristics
    mychar = json.loads(msg[0])
    
    # Upload characteristics to buffer 2
    print("\nUploading fingerprint characteristics to buffer 2")
    f.uploadCharacteristics(0x02, mychar)
    
    # Save buffer 2 as template
    print("Saving buffer 2 as template in pos " + str(i))
    f.storeTemplate(i, 0x02)
    
    # Increase bundle counter
    i = i + 1
    
print("\nCompleted..")


retry=True

## Tries to search the finger and calculate hash
while retry is True:
    try:
        print('\nWaiting for finger...')

        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        ## Searchs template
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]

        if ( positionNumber == -1 ):
            print('No match found!')
        else:
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))
            
        answer = raw_input("Search again? (y/n): ")
        if answer == "y":
            retry=True
        elif answer == "n":
            retry=False
        else:
            exit(0)
    
    
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)
