#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# Die Klassen Content mit ihren Unterklassen dienen der Erzeugung von Web content.
#
################################################################################

import logging, re, os.path as p
from urllib import urlopen
from bs4 import BeautifulSoup as BS

log = logging.getLogger('SZ.Content')

class Content:
  '''
  Oberklasse, die einen Parser für das Web-Scraping enthält.
  Nutzung etwa so:
  
  p=Content()
  response = p.get_content( web-scrape-url )
  
  Die vererbten Klassen enthalten jeweils ein Standard-Template. In den 
  vererbten Klassen muss die Funktion parse() überschrieben werden, damit 
  Wertepaare aus der von web-scrape-url bezogenen Seite extrahiert werden 
  können. 
  '''

  has_more_pages = False
  more_url = None
  dic = {}
  template_name = None
  bs4opts = {}  # Etwaige Optionen für BeautifulSoup
  baseurl = ''

  def __init__( self, **args):
    '''
    args: an das Template zu übergebende Wertepaare
    '''
    self.dic.update(**args)
    
  def get_content( self, url = None ):
    '''
    Gibt alle zwischengespeicherten Wertepaare zurück
    '''
    if url:
      self.more_url = [url]
      while self.more_url:
        href = self.more_url.pop(0)
        log.debug('Going to fetch %s', href )
        soup = self.fetch_soup( href )
        self.parse( soup )
      self.has_more_pages = False
      log.debug('Successfully parsed %s', soup.title.get_text() )
    return self.dic
    
  def fetch_soup( self, fname ):
    '''
    Holt eine Seite und gibt diese als BeautifulSoup zurück
    fname: URL der zu parsenden Seite
    '''
    try:
      log.debug("Fetching %s", fname )
      f=urlopen( fname )
    except Exception:
      log.error( "Could not fetch %s", fname )
      return
    p=f.read()
    f.close()
    return BS( p, **self.bs4opts )
    
  def parse( self, soup ):
    '''
    Extrahiert aus einer wundervollen Suppe die zur Erzeugung eines Templates
    erforderlichen Wertepaare und speichert diese in self.dic zwischen. Muss 
    in Unterklasse erledigt werden.
    soup: BeautifulSoup-Objekt. In der Regel von einer geholten Seite.
    '''
    pass

  def replace_url( self, f_url_for, f_server, string ):
    '''
    Finde urls und ersetze diese geeignet
    @f_url_for: dafür muss im richtigen Kontext url_for eingesetzt werden
    @f_server:  das target in url_for
    @string:    die gerenderte Seite
    Gibt die gerenderte Seite zurück
    '''
    def repl( mtch ):
      url = mtch.group(1)
      if mtch.group(2).startswith('thema'):
        # hack, weil thema Seiten keine Artikelseiten
        href=url
      else:
        article = p.basename( mtch.group(2) )
        href = f_url_for( f_server, article = article, link = url)
      return "href=\"%s\"" % href
    pat = 'href="(%s/(.*?))"' % self.baseurl
    pattern = re.compile( pat )
    return pattern.sub( repl, string )


