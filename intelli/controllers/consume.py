import xmlrpc.client
import base64
host='localhost'
port=8069
url = "https://novias-temp-intelli-981049.dev.odoo.com/xmlrpc"
db = 'novias-temp-intelli-981049'
username = 'admin'
password = 'adminadmin'
print ("URLL", url)
common = xmlrpc.client.ServerProxy(url +'/common')
print(common)

uid = common.login(db, username, password)
print ("UIDDD", uid)

models = xmlrpc.client.ServerProxy(url +'/object')
prodid = models.execute_kw(db, uid, password, 'intelli.tower', 'search_read', [[('name','like',"")]] )
img = prodid[0]['tower_picture']


with open("imageToSave.png", "wb") as fh:
    fh.write(base64.b64decode(img))
print(fh)