# import bcrypt
import time

# password = b"Password123"
# # Hash a password for the first time, with a certain number of rounds
#
# hashed = bcrypt.hashpw(password, bcrypt.gensalt(14))
#
# if bcrypt.checkpw(password, hashed):
#     print("It Matches!")
#     print(hashed)
# else:
#     print("It Does not Match :(")

timenow = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
time.sleep(5)
timein5 = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
print(timein5 - timenow)
