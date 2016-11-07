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

class IndexPage( Content ):
  """
  Content für die Indexseite.
  """

  template_name = 'index.html'
  stylesheet_name = 'css/index_styles.css'
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
      logo = soup.image.url.getText(),
      stylesheet = self.stylesheet_name
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
        stylesheet='css/stylesheet.css'
#        stylesheet_content = 'css/index_styles.css',
#        stylesheet_foundation = 'css/foundation.css',
#        js_foundation = 'js/vendor/foundation.js',
#        js_jquery = 'js/vendor/jquery.js',
#        js_what_input = 'js/vendor/what-input.js',
#        js_app = 'js/app.js'    
    )
    article = soup.article
    authors = soup.find('section',{'class':"authors"})
    authors.script.extract()
    images = soup.find('section',{'class':'topenrichment'})
    if images and images.figure:
      figure = unicode( images.figure.renderContents().decode('utf8') )
      args.update( figure = figure )  
    else:
      args.update( figure = '' )  
    header = article.find( 'section',{'class':'header'} )
    content = article.find('section',{'id':'article-body'})
    
    
    args.update( author = authors.strong.get_text().strip() )
    args.update( teaser=header.strong.get_text().strip() )
    header.strong.extract()
    args.update( title=header.h2.get_text().strip() )
    
    for p in article.findAll('p',{'class':'anzeige'}):
      p.extract()
    for p in soup.article.findAll('div',{'class','article-sidebar-wrapper'}):
      p.extract()
    for p in soup.article.findAll('div',{'class','basebox'}):
      p.extract()
    for p in soup.article.findAll('div',{'class','ad'}):
      p.extract()
    for p in soup.article.findAll('div',{'class','flexible-teaser'}):
      p.extract()
    for p in soup.article.findAll('figure'):
      p.extract()
    for p in soup.article.findAll('script'):
      p.extract()
    authors.extract()
    content.span.extract()
    content.span.extract()
    
    initial = content.p.extract()
    args.update(initial=unicode(initial.renderContents().decode('utf8')))
    args.update(content=unicode(content.renderContents().decode('utf8')))
    self.dic.update(**args)

def get_topics():
  '''
  Gibt eine Liste der Ausgabedaten (datetime.date-Objekte) der letzten 12 
  Ausgaben bis month.year zurück.
  month:  1-12
  year:   vierstellige Jahreszahl
  '''
  t = ('Topthemen','Politik','Panorama', 'Leben','Wirtschaft','Kultur','Wissen','Medien','Digital')
  topics = {}
  for top in t:
    topics[top] = "http://rss.sueddeutsche.de/%s" % top  
  return topics

