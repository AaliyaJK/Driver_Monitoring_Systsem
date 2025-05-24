import time
from pyfingerprint.pyfingerprint import PyFingerprint

# Initialize the Fingerprint Sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if not f.verifyPassword():
        raise ValueError("Fingerprint sensor password is incorrect!")

except Exception as e:
    print(f"Fingerprint sensor error: {e}")
    exit(1)

print("Place your finger to register...")

# Step 1: Wait for Finger
while not f.readImage():
    pass

# Step 2: Convert Image
f.convertImage(0x01)

# Step 3: Check for Existing Fingerprints
result = f.searchTemplate()
positionNumber = result[0]

if positionNumber >= 0:
    print("Fingerprint already exists at position #", positionNumber)
    exit(0)

# Step 4: Find Empty Storage Position
positionNumber = f.getTemplateCount()
if positionNumber >= f.getStorageCapacity():
    print("Fingerprint storage is full!")
    exit(1)

# Step 5: Ask User to Place Finger Again
print("Remove finger and place it again...")
time.sleep(2)

while not f.readImage():
    pass

f.convertImage(0x02)

# Step 6: Create a Template & Store it
if f.compareCharacteristics() == 0:
    print("Fingerprints do not match!")
    exit(1)

f.createTemplate()
f.storeTemplate(positionNumber)

print(f"Fingerprint stored successfully at position #{positionNumber}")