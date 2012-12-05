#!/usr/bin/env python

import os
import re
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

def fixNode(node,groups,templateId):
  if not node.hasAttribute('class'):
    return False

  classAttr = node.getAttribute('class')
  if node.hasAttribute('group'):
    m = re.search(r'grid-h-',classAttr,flags=re.IGNORECASE)
    if m is not None:
      group = node.getAttribute('group')
      if not group in groups:
        groups[group] = []
      groups[group].append(node)
      return False

  m = re.search(r'grid-h-',classAttr)
  if m is not None:
    classAttr = re.sub(r'grid-h-',r'grid-H-',classAttr)
    node.setAttribute('class', classAttr)
    return True

  return False

def fixGroup(groupName,group,templateId):
  memberCount = len(group)
  if memberCount == 0:
    return False
  elif memberCount == 1:
    node = group[0]
    classAttr = node.getAttribute('class')
    m = re.search(r'grid-h-',classAttr)
    if m is not None:
      classAttr = re.sub(r'grid-h-',r'grid-H-',classAttr)
      node.setAttribute('class',classAttr)
      return True
  else:
    capCount = 0
    for node in group:
      classAttr = node.getAttribute('class')
      m = re.search(r'grid-H-',classAttr)
      if m is not None:
        capCount += 1
    if capCount != 1:
      print "fixGroup(%s) has bad capital count in template (%s)" % (groupName,str(templateId))
      #TODO: fix groups

  return False

def fixDom(dom,templateId):
  groups = {}
  fixed = False

  nodes = dom.getElementsByTagName('*')
  for node in nodes:
    if fixNode(node,groups,templateId):
      fixed = True

  for group in groups:
    if fixGroup(group,groups[group],templateId):
      fixed = True

  return fixed

def fixTemplate(templateId,templateName,templateContent):
  dom = domFromTemplate(templateContent)
  if dom is None:
    print 'Error in template (id=%s): %s' % (str(templateId),templateName)
    return None
  if fixDom(dom,templateId):
    node = dom.documentElement.firstChild
    fixedContent = node.toxml()
  else:
    fixedContent = None
  return fixedContent

def saveTemplateContent(templateId,templateContent):
  connection = MySQLdb.connect(DB_SERVER,DB_USER,DB_PASSWD,DB_DATABASE)
  cursor = connection.cursor()
  cursor.execute("UPDATE core_template SET content=%s WHERE id=%s",(templateContent,str(templateId)))
  connection.commit()
  connection.close()
  return True

def runAllFixes():
  fixedCount = 0
  templates = fetchTemplates()
  for template in templates:
    fixedContent = fixTemplate(template[0],template[1],template[2])
    if fixedContent is not None:
      fixedCount += 1
      print 'Saving (%s): %s' % (template[0],template[1])
      saveTemplateContent(template[0],fixedContent)
    #else:
    #  print 'Failed (%s): %s' % (template[0],template[1])

  print 'Fixed %d of %d' % (fixedCount, len(templates))
  return True

if __name__ == "__main__":
  runAllFixes()
