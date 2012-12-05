#!/usr/bin/env python

import os
import MySQLdb
from xml.dom.minidom import parseString

DB_SERVER = os.environ.get('DB_SERVER','localhost')
DB_USER = os.environ.get('DB_USER','baba')
DB_PASSWD = os.environ.get('DB_PASSWD','ganoush')
DB_DATABASE = os.environ.get('DB_DATABASE','yaga')
NS_HEAD = "<readz:ns xmlns:readz='http://readz.com'>"
NS_TAIL = "</readz:ns>"

def fetchTemplates():
  connection = MySQLdb.connect(DB_SERVER,DB_USER,DB_PASSWD,DB_DATABASE)
  cursor = connection.cursor()
  cursor.execute("SELECT id, name, content FROM core_template WHERE content LIKE '%grid_h_%'")
  templates = cursor.fetchall()
  connection.close()
  return templates

def domFromTemplate(templateContent):
  dom = None
  try:
    xmlString = NS_HEAD + templateContent.replace('&','&amp;') + NS_TAIL
    dom = parseString(xmlString)
  except Exception as inst:
    print inst
    dom = None

  return dom

def fixTemplate(templateId,templateName,templateContent):
  #print "Fixing: %s" % templateName
  dom = domFromTemplate(templateContent)
  if dom is None:
    print 'Error (%s): %s' % (str(templateId),templateName)
    return None
  node = dom.documentElement.firstChild
  fixedContent = node.toxml()
  return fixedContent

def saveTemplateContent(templateId,templateContent):
  connection = MySQLdb.connect(DB_SERVER,DB_USER,DB_PASSWD,DB_DATABASE)
  cursor = connection.cursor()
  cursor.execute("UPDATE core_template SET content=%s WHERE id=%s",(templateContent,str(templateId)))
  connection.commit()
  connection.close()
  return True

def runAllFixes():
  templates = fetchTemplates()
  for template in templates:
    fixedContent = fixTemplate(template[0],template[1],template[2])
    if fixedContent is not None:
      saveTemplateContent(template[0],fixedContent)
  return False

if __name__ == "__main__":
  runAllFixes()
