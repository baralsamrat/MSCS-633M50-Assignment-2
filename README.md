# MSCS-633M50-Assignment-2
 construct an application that generates a QR code when you input a URL address. Construct a Q code generator at Biox Systems using Python. 


# Run src/run.sh on MacOS or Linux System
```cmd
chmod +x run.sh

./run.sh "https://www.ucumberlands.edu/" --out qr-image-ucmberland.png --title "Univeristy of Cumberlands at Kentucky"
```
OUTPUT: 
```cmd
Saved: qr-image-ucmberland.png
✅ Done.
```


#  Create a virtual env named .venv
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install packages
pip install qrcode pillow

# Run your script
python /path/to/biox_qr.py "https://your-url.com" --out qr.png

# deactivate
deactivate