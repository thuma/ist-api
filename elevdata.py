# -*- coding: utf-8 -*-
import bottle
import json
from bottle import route, run, response, post, get, request
from login import login, getElever

@route('/elever', method=['OPTIONS'])
def option():
    return ""


@get('/elever')
def elever():
    try:
      (user, password) = request.auth
    except Exception as pwd:
      response.set_header("WWW-Authenticate", 'Basic realm="Restricted"')
      response.status = 401
      return ""
    try:
      s = login(user,password)
    except Exception as e:
     response.set_header("WWW-Authenticate", 'Basic realm="Restricted"')
     response.status = 401
     return str(e)
    elever = getElever(s)
    return json.dumps({"elever":elever})

run(host='localhost', port=8568)
