#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# Die Klassen Content mit ihren Unterklassen dienen der Erzeugung von Web content.
#
################################################################################

import logging
from urllib import urlopen
from bs4 import BeautifulSoup as BS

log = logging.getLogger(__name__)

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

  has_updated = False
  dic = {}
  template_name = None
  bs4opts = {}  # Etwaige Optionen für BeautifulSoup

  def __init__( self, **args):
    '''
    args: an das Template zu übergebende Wertepaare
    '''
    self.dic.update(**args)
    
  def get_content( self, url = None ):
    '''
    Gibt alle zwischengespeicherten Wertepaare zurück
    '''
    if url and not self.has_updated:
      log.debug('Cache is empty. Going to fetch %s', url )
      soup = self.fetch_soup( url )
      log.debug('Going to parse %s', soup.title.get_text() )
      self.parse( soup )
      log.debug('Successfully parsed %s', soup.title.get_text() )
      self.has_updated = True
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

