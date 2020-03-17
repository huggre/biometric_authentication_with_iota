# Integrating physical devices with IOTA — Bio-metric authentication

The 10th part in a series of beginner tutorials on integrating physical devices with the IOTA protocol.

![img](https://miro.medium.com/max/700/1*H4YNvmU8494lDhrfU-7CzA.jpeg)

------

## Introduction

This is the 10th part in a series of beginner tutorials where we explore integrating physical devices with the IOTA protocol. In this tutorial we will be exploring a concept known as Bio-metric authentication. If you own a smart-phone with a fingerprint reader chances are you already use this technology every day.

So what does all of this have to do with IOTA?

I guess the most obvious use-case for integrating Bio-metric technology with IOTA would be something like logging in to your IOTA wallet (as implemented in the mobile Trinity wallet). However, my interest in this area is of a more profound nature. What if combing these technologies could be used to address the worlds bigger problems, such as voter fraud, air-traffic safety or human identification in disaster areas?

To understand how integrating Bio-metric technology with IOTA could help solve these problems we need to look at the bigger picture. When using the fingerprint reader on your phone, the fingerprints used for comparison and authentication is typically stored inside the reader (phone) itself. This works fine as long as you are using the same reader every time. Problem comes when you need to be authenticated by a different reader that does not already have your fingerprints registered. Imagine trying to implement fingerprint authentication as a voter fraud protection mechanism in a national election. There would have to be thousands of fingerprint readers across every voting location in the country. Now imagine having to store all the fingerprints of every citizen in each reader. This would be close to impossible. A better option might be to have all fingerprints stored in a secure and tamper proof location where they could be retrieved when needed. This is where DLT and the IOTA tangle shines.

We will not be solving any world scale problems today. However, the use-case proposed in this tutorial deals with the same problem, just on a smaller scale.

------

## The Use Case

Let’s image our trusted hotel owner have a safe in each hotel where he stores cash for his daily business. Now and then one of his employees needs to access a safe to make deposits or withdrawals. To prevent any unauthorized individuals accessing the safes he decide to install a Bio-metric authentication mechanism in the form of a fingerprint reader at each safe. As he gets new employees, or his current staff rotates between his hotels, it would be difficult to keep the fingerprint database in every reader up to date with the current staff situation. After puzzling over this problem for a while he comes up with an alternative solution. What if he could store the staff fingerprints on the IOTA tangle instead of the fingerprint readers themselves? Whenever a staff member needs to access a safe at any hotel, his or her fingerprints would automatically be downloaded from the IOTA tangle to the reader before being authenticated. Would this even be possible?

Let’s see if we can help him out…

*Warning!*
*We will be using IOTA transaction message fragments to store the actual fingerprint data on the IOTA tangle. It is important to be aware that IOTA transaction messages are not encrypted, and that any fingerprint data uploaded to the tangle could easily be decoded and recreated by a bad actor. To simplify coding for this project i decided not to include any data encryption/decryption. If you feel uncomfortable uploading non-encrypted fingerprint data to the tangle you should consider adding your own encryption/decryption mechanism in the code, or use some other object as a replacement for your fingers.*

------

## Components

The components you will need to build this project is as follows:

1. Any internet connected computer running a Debian based Linux variant.
   Personally, i’m using a Raspberry PI with the Raspbian operating system.
2. ZhianTec ZFM optical fingerprint reader
3. FTDI232 USB to serial adapter

**The ZhianTec** **ZFM optical fingerprint reader**
The ZhianTec ZMF optical fingerprint reader is popular for its low cost and comp ability with both the Raspberry PI and Arduino ecosystems. The ZMF comes in several different models (ZFM-20, ZFM-60, ZFM-70 and ZFM-100). I’m not exactly sure what model my reader is as there is no marking on it. However, the python library used for this project should support all the models listed above.

![img](https://miro.medium.com/max/700/0*CmM9IVjdnkV8hlFm.jpg)

**FTDI232 USB to serial adapter**
The FTDI232 is a handy USB to TTL serial adapter module that provides an easy way of connecting TTL serial devices to a PC using the USB port. You should be able to get the FTDI232 off-ebay for a couple of bucks.

![img](https://miro.medium.com/max/700/0*x7qrCGnFV5GiALpP.jpg)

*Note!*
*Some FTDI232 adapters plugs directly in to the USB port on your computer while others come as separate module (as the one pictured above). In case you buy a separate module, make sure you also get a compatible USB cable.*

*Note!*
*When using a Raspberry PI it should be possible to hook up the fingerprint reader directly to the GPIO pins of the PI without the FTDI232 adapter. However, i have not tested this myself.*

------

## Wiring the project

Se the following link for information on how to connect the ZhianTec ZMF reader with the FTDI232 adapter. https://tutorials-raspberrypi.com/how-to-use-raspberry-pi-fingerprint-sensor-authentication/

*Note!*
*If you read the comments section below the article you will see the some people suggest switching the TX and RX connections as appose to how it was described in the article. This was true in my case. I’m not sure if this problem is related to my reader being a different model than the one used in the article. If you can’t get your reader to work i suggest you try the same. Also note that the reader only lights up when reading, so the fact that it is not lit when connected does not indicate that its not working correctly.*

------

## Required Software and libraries

Before we start writing our Python code for this project we need to make sure we have all the required software and libraries installed on our computer. See previous tutorials for more information on installing Python and the PyOTA library. Also make sure you install the [PyFingerprint](https://github.com/bastianraschke/pyfingerprint) library before continuing. Instructions on how to install and use the PyFingerprint library can be found on the [PyFingerprint Github](https://github.com/bastianraschke/pyfingerprint) page.

------

## The Python code

Now that we have our fingerprint reader hooked up and the PyFingerprint library installed, we can start looking at the Python code used for this project.

Before looking at the code itself, we should take a moment to get a general idea on how it works.

The code used for this project is split into two separate Python scripts. One script is used for uploading new fingerprints to the IOTA tangle. The other is used for validating against existing fingerprints stored on the tangle.

First, let’s look at the process of uploading new fingerprints to the tangle.

The general idea here is that each user (or in our case, each hotel employee who needs access to the safe) is provided with a unique IOTA seed. This seed will then be used to generate an IOTA address that further will be used when uploading fingerprint data (belonging to that particular employee) to the IOTA tangle. The fingerprint data itself is created by the reader and sent to the tangle in the form of a bundle of transactions. Each transaction inside the bundle holds a part of the fingerprint data inside its message fragment. Notice that there will be one bundle for each individual fingerprint. You may upload as many fingerprint bundles as you want. You may even upload multiple fingerprint bundles of each finger. Just notice that the more bundles you upload, the longer it will take to download them later on when they are used for validation. Also notice that the ZhianTec ZMF reader has a limit of 1000 prints being stored in memory at the same time.

Next, let’s look at the process of validating a fingerprint taken on the reader with existing fingerprints stored on the tangle.

The process starts with an employee wanting to access the safe. The script will then ask for his/her seed so that we know what IOTA seed to use when searching for his/her fingerprint bundles on the tangle. Next, the script starts downloading all the employees fingerprint bundles, while at the same time uploading them to the internal memory of the reader. Finally, the employee will be asked to put a finger on the reader. If the reader finds a match between the fingerprint being taken, and a fingerprint stored in the reader memory, we have a match, and the employee have been authenticated.

*Note!
As mentioned, the validation script require a valid IOTA seed as input. However, can it really be expected that every employee can remember, or even type, a 81 character seed whenever they need to access the safe? Probably not. This problem could however be solved using some other technology discussed in a* [*previous tutorial*](https://medium.com/coinmonks/integrating-physical-devices-with-iota-the-iota-debit-card-part-1-42dc1a05f18)*, namely RFID. The seed could be stored on the employees ID card, adding an additional level of security. You would now have to have both a valid employee ID card and a valid fingerprint to access the safe.*

Here is the script for uploading fingerprints to the tangle..

```python
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
```

The source code for this python script can be downloaded from [here](https://gist.github.com/huggre/48fcc863c8edf27689817a568a014bd8)

And here is the script for validating a new fingerprint against existing prints stored on the tangle..

```python
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
```

The source code for this python script can be downloaded from [here](https://gist.github.com/huggre/300c87c9c8b2b97115a48a8e7de8d694)

------

## Running the project

To run the the project, you first need to save the scrips from the previous section as text files on your computer.

Notice that Python program files uses the .py extension, so save the files as **upload_fingerprint.py** *and* **validate_fingerprint.py**

To execute the scripts, simply start a new terminal window, navigate to the folder where you saved the scripts and type:

**python upload_fingerprint.py** or **python validate_fingerprint.py**

You should now see the code being executed in your terminal window.

When running the **upload_fingerprint.py** script you will be asked for a valid IOTA seed. This is the seed that will be used when uploading the new fingerprint bundle to the tangle. Make sure you create a new seed for every user (employee) that has no prior transaction history. Also make sure you use the same seed when uploading multiple fingerprints of the same user. After providing the seed you will be asked to place a finger on the reader. As soon as the reader has captured your fingerprint, it will be uploaded to the IOTA tangle. Repeat the process for each finger.

When running the **validate_fingerprint.py** script you will again be asked for a valid IOTA seed. This is the seed that will be used when searching for existing fingerprint bundles on the tangle. Make sure you use the same seed as was used when uploading fingerprints for that particular user (employee). When the script has completed the process of downloading the prints from the tangle, and uploading them to the internal memory of the reader, you will be asked to place a finger on the reader. As soon as the reader has captured your fingerprint, it will start looking for a match between the print just taken and the prints currently stored in memory. You will be notified if a match was found. If a match was not found, or you want to validate another finger, use the “search again” option.

*Note!*
*If you have problems getting a match it could be that the finger was placed in a slightly different position between the two readings. Try searching again doing some minor adjustments to the position of your finger.*

------

# Donations

If you like this tutorial and want me to continue making others, feel free to make a small donation to the IOTA address shown below.

![img](https://miro.medium.com/max/382/1*j2ENIzmDzXcGSgAdY4w-Jw.png)

NYZBHOVSMDWWABXSACAJTTWJOQRPVVAWLBSFQVSJSWWBJJLLSQKNZFC9XCRPQSVFQZPBJCJRANNPVMMEZQJRQSVVGZ

