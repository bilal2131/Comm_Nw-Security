
# this module is to test the encryption
import cyptocode

key = 'test key'
message = 'test message that can be long and broad'

enc = cryptocode.encrypt(message=message, password=key)
print(enc)
dec = cryptocode.decrypt(enc,password=key)
print(dec)

