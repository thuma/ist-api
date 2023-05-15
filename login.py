"""
ist cli

Usage:
  ist <username> <password>
"""
import requests
import json
from operator import itemgetter
from datetime import datetime, date

def login(user, pwd):
  headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language':'sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding':'gzip, deflate, br',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1',
    'Sec-Fetch-Dest':'document',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-Site':'none',
    'Sec-Fetch-User':'1',
    'TE':'trailers'
  }

  s = requests.Session()
  r = s.get('https://goteborggy.se.ist.com/teacher', headers = headers)
  url2 = r.text.split("0;URL='")[1].split("'")[0]
  rurl2 = s.get(url2, headers = headers)
  saml = rurl2.text.split('name="SAMLRequest" value="')[1].split('"')[0]
  rs = rurl2.text.split('name="RelayState" value="')[1].split('"')[0]

  r = s.post("https://auth.goteborg.se/FED/sps/idp/saml20/login",data={"SAMLRequest":saml, "RelayState":rs})

  path = r.text.split('form class="c-form" method="POST" name="loginform" id="loginform" action="')[1].split('"')[0]
  keytarget = r.text.split('input type="hidden" name="templateTarget" value="')[1].split('"')[0]

  r2 = s.post('https://auth.goteborg.se'+path, data={'username':user,'password':pwd,'operation':'verify','gbgtemplate':'login','templateTarget':keytarget})

  if r2.text.__contains__('name="SAMLResponse" value="'):
    saml = r2.text.split('name="SAMLResponse" value="')[1].split('"')[0]
    rs = r2.text.split('name="RelayState" value="')[1].split('"')[0]
    url = r2.text.split('form method="post" action="')[1].split('"')[0]
  else:
    print(r2.text())
    raise Exception("Fel lösenord / användarnamn")

  headers["Origin"] = "https://auth.goteborg.se"
  headers["Referer"] = "https://auth.goteborg.se/"
  r3 = s.post(url, data={"RelayState":rs,"SAMLResponse":saml}, headers = headers)
  return s

def getElever(s):
  elever = []
  context = s.get("https://goteborggy.se.ist.com/teacher/api/v1/roles/teacher/contexts",
    headers={"Content-Type":"application/json;charset=UTF-8"}) 
  skolor = context.json()
  for skola in skolor:
    r4 = s.get("https://goteborggy.se.ist.com/teacher/teacher/api/v1/units/"+skola['id']+"/hierarchy?_locale=sv_SE",
      headers={"Content-Type":"application/json;charset=UTF-8"})
    r5 = s.post("https://goteborggy.se.ist.com/teacher/teacher/api/v1/units/"+skola['id']+"/stud",
      json=r4.json(),
      headers={"Content-Type":"application/json;charset=UTF-8"})
    elever.extend(r5.json())
  return elever

if __name__ == "__main__":
  from docopt import docopt
  args = docopt(__doc__)
  s = login(args["<username>"],args["<password>"])
  print(getElever(s))
