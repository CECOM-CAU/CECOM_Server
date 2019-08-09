from InstagramAPI import Instagram

username = 'test_cecom'
password = '2579*2579*'
debug = False

photo = 'C:\\Users\\tngus\\OneDrive\\Pictures\\Saved Pictures\\packt.jpeg'
caption = 'test'


i = Instagram(username, password, debug)

try:
    i.login()
except Exception as e:
    print(e.message)
    exit()

try:
    i.uploadPhoto(photo, caption)
except Exception as e:
    print(e.message)
