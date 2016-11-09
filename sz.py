#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# Die Klassen Content mit ihren Unterklassen dienen der Erzeugung von Web 
# content. Statt einer Datenbank wird das Web genutzt, d.h. der Content von
# irgendwelchen Seiten gekratzt.
# 
################################################################################

import logging, os.path as p
from utils import Content

log = logging.getLogger(__name__)
logging.basicConfig()
stylesheet = 'css/stylesheet.css'

class IndexPage( Content ):
  """
  Content für die Indexseite.
  """

  template_name = 'index.html'
  bs4opts = dict(features='xml')
  log = logging.getLogger(__name__)

  def parse( self, soup ):
    '''
    Parsed die Übersichtsseite mit den Artikel-Links
    '''
    args = dict(
      title=soup.title.getText(),
      charset='utf8',
      builtdate = soup.lastBuildDate.getText(),
      stylesheet = stylesheet
    )
    articles = []
    toc = soup.findAll('item')
    for item in toc: 
      article={}
      title = item.title.getText()
      link = item.link.getText()
      log.debug( 'Found article %s with url %s', title, link )                 
      article.update(
        title = title,
        link = link,
        href = p.basename( item.link.getText() ),
        author = item.category.getText(),
        description = item.description.getText() )
      articles.append( article )
    args.update(articles=articles)
    self.dic.update(**args)

class ArticlePage( Content ):
  '''
  Content für eine Artikelseite. Default ist die Web-Darstellung
  '''

  template_name = 'article.html'

  def parse( self, soup ):
    '''
    Parsed eine Artikelseite
    '''
    args = dict(
        charset='utf8',
        stylesheet=stylesheet
#        stylesheet_content = 'css/index_styles.css',
#        stylesheet_foundation = 'css/foundation.css',
#        js_foundation = 'js/vendor/foundation.js',
#        js_jquery = 'js/vendor/jquery.js',
#        js_what_input = 'js/vendor/what-input.js',
#        js_app = 'js/app.js'    
    )
    # Den eigentlichen Content finden
    article = soup.article
    
    if self.has_more_pages:
      # Textkörper finden 
      body = article.find('section',{'id':'article-body'})
      text_body = filter(lambda c : hasattr(c,'name') and (c.name=='p' or c.name=='h3'), body.children )
      content = u''
      for child in text_body:
         content += child.prettify() 
      self.dic['content']+=content
    else:
      # Autoren finden und merken
      authors = soup.find('section',{'class':"authors"})
      authors.script.extract()
      args.update( author = authors.strong.get_text().strip() )

      # Das Bild zum Text finden
      images = soup.find('section',{'class':'topenrichment'})
      if images and images.figure:
        figure = images.figure.prettify()
        args.update( figure = figure )  
      else:
        args.update( figure = '' )  

      # Überschrift finden
      header = article.find( 'section',{'class':'header'} )
      args.update( teaser=header.strong.get_text().strip() )
      header.strong.extract()
      args.update( title=header.h2.get_text().strip() )

      # Textkörper finden und ersten Absatz hervorheben
      body = article.find('section',{'id':'article-body'})
      text_body = filter(lambda c : hasattr(c,'name') and (c.name=='p' or c.name=='h3'), body.children )
      initial = text_body.pop(0).prettify()
      content = u''
      for child in text_body:
         content += child.prettify() 
      args.update(initial=initial)
      args.update(content=content)
      
      # Alles zwischenspeichern
      self.dic.update(**args)
      
      # Falls es noch weitere Seiten gibt...
      more = map(lambda i:i.a['href'],filter(lambda i:i.a,
              soup.findAll('li',{'class':'article-paging-list-item'})))
      if more:
        log.debug('Found %i more pages', len(more) )
        self.more_url = more
        self.has_more_pages = True

def get_topics():
  '''
  Gibt eine Liste der Ausgabedaten (datetime.date-Objekte) der letzten 12 
  Ausgaben bis month.year zurück.
  month:  1-12
  year:   vierstellige Jahreszahl
  '''
  t = ('Topthemen','Politik','Panorama', 'Sport','Wirtschaft','Kultur','Wissen','Medien','Digital')
  topics = {}
  for top in t:
    topics[top] = "http://rss.sueddeutsche.de/%s" % top  
  return topics

