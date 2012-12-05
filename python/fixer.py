#!/usr/bin/env python

import os
import MySQLdb

DB_SERVER = os.environ.get('DB_SERVER','localhost')
DB_USER = os.environ.get('DB_USER','baba')
DB_PASSWD = os.environ.get('DB_PASSWD','ganoush')
DB_DATABASE = os.environ.get('DB_DATABASE','yaga')

def fetchTemplates():
  connection = MySQLdb.connect(DB_SERVER,DB_USER,DB_PASSWD,DB_DATABASE)
  cursor = connection.cursor()
  cursor.execute("SELECT id, name, content FROM core_template")
  templates = cursor.fetchall()
  connection.close()
  return templates

def fixTemplate(templateId,templateName,templateContent):
  print "Fixing: %s" % templateName
  return False

def runAllFixes():
  templates = fetchTemplates()
  for template in templates:
    fixTemplate(template[0],template[1],template[2])
  return False

if __name__ == "__main__":
  runAllFixes()
