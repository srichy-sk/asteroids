
import qrcode

url = input('Enter The URL:').strip()
file_path = 'C:\\Users\\srich\\OneDrive\\Documents\\qrcode.png'

qr = qrcode.QRCode()
qr.add_data(url)

img = qr.make_image()
img.save(file_path)

