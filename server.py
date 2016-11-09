#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# Der Flask-Server kann mit folgenden Optionen gestratet
# werden. 
# 
# Usage: python server.py [-p n] [--options 'key1=value1,...'] [-d] [-o]
#
#  -p,  --port n      n ist Port des Servers, default ist 8000
#       --options kv  Weitere Flask-Server-Optionen als kommaseparierte kv-Paare
#  -d,  --debug       Schaltet debug mode ein
#  -o,  --open        Öffnet den Server für LAN und ggf. WAN
#
################################################################################

import os.path as p, logging
from flask import Flask, url_for, send_from_directory, render_template, request, redirect
from sz import IndexPage, ArticlePage, get_topics

resdir       = "ressources"
curdir = p.abspath('.')
font_folder = '%s/%s/fonts' % ( curdir, resdir )
content=dict(issues=get_topics()) 

'''
Webapp definieren und Appserver starten
'''

app = Flask('SZ',static_folder= '%s/%s' % ( curdir, resdir))

@app.route('/')
def index():
  '''
  Lenkt auf die Topthemenseite
  '''
  return redirect( url_for('get_topic', topic="Topthemen"))

@app.route('/res/<path>')
def static_proxy(path):
  '''
  Alles unterhalb resdir
  '''
  # send_static_file will guess the correct MIME type
  return app.send_static_file( path )

@app.route('/sz/<topic>')
def get_topic(topic):
  '''
  Gibt die Indexseite der Rubrik topic zurück
  '''
  issue = IndexPage()
  cont = issue.get_content( content['issues'][topic] )
  content['current'] = topic
  content[topic]=cont
  i=0
  article_refs = map( lambda entry : (entry['href'], entry['link']), cont['articles'] )
  while i < len(article_refs):
    next_target, ntl = article_refs[ (i+1) % len(article_refs) ]
    target, target_link = article_refs[ i ]
    next_path = p.basename( next_target )
    content[target] = ( next_path, target_link )
    i+=1
  response = render_template( issue.template_name, **cont )
  return response

@app.route('/artikel/<article>')
def get_article(article):
  '''
  Liefert eine Artikelseite aus
  '''
  next, link = content[article]
  article_i = ArticlePage( )
  cont = article_i.get_content( content[article][1] )
  cont.update(
      next = next,
      logo = url_for('static', filename="logofficiel-enlong.png"),
      issues = content['issues'],
      home = content[ 'current' ],
  )  
  return render_template( article_i.template_name, **cont )

#  @app.route('/fonts/<fname>')
#  def get_fonts(fname):
#    return send_from_directory( font_folder, fname )

if __name__=='__main__':
  # configure Flask logging
  logger = logging.FileHandler('error.log')
  app.logger.setLevel(logging.ERROR)
  app.logger.addHandler(logger)
    
  # allow for server options
  import argparse
    
  server = argparse.ArgumentParser(description="Startet den Appserver")
  server.add_argument(
    "-p", 
    "--port", 
    help="Port des Servers", 
    type=int, 
    default=8000
  )
  server.add_argument(
    "--options", 
    help="Weitere Flask-Server-Optionen als kommaseparierte key=value-Paare", 
    type=str, 
    default=None
  )
  server.add_argument(
    "-d", 
    "--debug", 
    help="Schaltet debug mode ein", 
    action='store_true'
  )
  server.add_argument(
    "-o", 
    "--open", 
    help="Öffnet den Server für LAN und ggf. WAN", 
    action='store_true'
  )
  opts = server.parse_args()
  server_opts = dict(debug=opts.debug,port=opts.port)
  port = opts.port
  if opts.debug:
    app.logger.setLevel( logging.DEBUG )
  if opts.open: 
    server_opts.update(host='0.0.0.0')
  if opts.options:
    key_value_pattern = re.compile('[a-zA-Z0-9_]*=.*')
    kvs=opts.options.split(',')
    for kv in kvs:
      if key_value_pattern.match( kv ):
        key, value = kv.split('=')
        if value.isdigit(): value = int( value )
        if value=='True': value = True 
        if value=='False': value = False 
        server_opts.update({key:value})
      else:
        app.logger.error('%s will be ignored, because it is not a key value pair!',kv)

  # log Flask events
  from time import asctime
  app.logger.debug(u"Flask server started " + asctime())
  @app.after_request
  def write_access_log(response):
      app.logger.debug(u"%s %s -> %s" % (asctime(), request.path, response.status_code))
      return response

  app.run( **server_opts )

  
