#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Autor Andrei Bastos
#  You can contact me by email (andreibastos@outlook.com) or write to:
#  Via Labic/Ufes - Vitória/ES - Brazil

"""
Objetivo: receber e gerar uma lista de links para serem baixados pelo programa AudioDownload.Main.
"""

#################### Importações #################
from environs import Env
import json, datetime, time 
import requests, urllib, urllib3

from os import listdir
from os.path import isfile, join

import subprocess

#################### Variaveis ###################
env = Env()

URL_API_ARTICLES = "http://localhost/radio/article.json"
PATH_FILENAME_LIST = "tempListLinksRadios.txt"
PATH_DIR_AUDIOS = "/var/www/html/radios/"
LIST_DOMAINS_RADIOS = []
JAVA_PROGRAM = 'AudioDownload.Main'

# URL_API_ARTICLES = env('URL_API_ARTICLES')
# PATH_FILENAME_LIST = env('PATH_FILENAME_LIST')
# PATH_DIR_AUDIOS = env('PATH_DIR_AUDIOS')
# LIST_DOMAINS_RADIOS = env.list('LIST_DOMAINS_RADIOS')


################### Funções ######################
"""
pega os artigos através de uma URL_ENDPOINT
"""
def getArticles():
	params = {'dominios':LIST_DOMAINS_RADIOS}
	headers = {'user-agent': 'app-download-audio', 'content-type': 'application/json'}
	try:			
		r = requests.get(URL_API_ARTICLES, params=params, headers = headers)		
		r.raise_for_status()
		articles = r.json()		
		
		return articles
	except Exception as e:
		print e
		return {}
	pass


"""
Salva os links em um arquivo e retorna True ou False se conseguiu salvar.
"""
def saveListFile(articles):
	links = getLinks(articles); 
	links_str = "\n".join(x for x in links);
	return saveInFile(PATH_FILENAME_LIST, links_str);

"""
Gera os links a partir dos artigos e retorna uma lista dos links
"""
def getLinks(articles):
	links = []	
	for article in articles:
		link = article['url']
		links.append(link)
		pass
	return links
	pass
	
"""
Salva uma string em um arquivo
"""
def saveInFile(filename, str_lines):
	saved = False;
	try:
		f = open(filename,'w');
		f.write(str_lines);
		f.close()		
		saved = True;
	except Exception as e:
		print e
		saved = False;
	finally:
		return saved		

"""
Baixa os Áudios usando o código em java AudioDownload.Main
"""
def downloadAudios(articles):
	global PATH_DIR_AUDIOS	
	PATH_DIR_AUDIOS += datetime.datetime.now().strftime("%Y-%m-%d") + "/"
	print subprocess.call(['mkdir', '-p', PATH_DIR_AUDIOS])
	print PATH_DIR_AUDIOS
	try:
				
		downloaded =  subprocess.call(['java', JAVA_PROGRAM,PATH_FILENAME_LIST, PATH_DIR_AUDIOS]) 
		listAudiosDownloaded = checkDownloadedsAudios();
		print listAudiosDownloaded
	except Exception as e:
		raise e
	pass

def checkDownloadedsAudios():
	global PATH_DIR_AUDIOS	
	listAudiosDownloaded = [];
	try:
		listAudiosDownloaded = [join(PATH_DIR_AUDIOS,f) for f in listdir(PATH_DIR_AUDIOS) if isfile(join(PATH_DIR_AUDIOS, f))]		
	except Exception as e:
		listAudiosDownloaded = []
	
	return listAudiosDownloaded;
	pass

"""
Atualiza os artigos no endpoints URL_API_ARTICLES 
"""
def updateArticles(articles):
	pass

def sendArticle(article):
	data=json.dumps(data)
	try:
		headers = {'user-agent': 'app-download-audio', 'content-type': 'application/json'}		

		r = requests.post(URL_API_DATABASE, data=data, headers=headers)
		r.raise_for_status()		
		output = {'ok':1, 'result':'sucess', 'msg':'Salvo com sucesso'}			
	except (requests.exceptions.HTTPError, Exception) as error:
		output = {'ok':1,'result':'error', 'msg':error}			
	finally:
		return output

def main():
	# Procura os ultimos links das rádios 
	articles = getArticles(); 	

	# Gera a lista e salva no arquivo PATH_FILENAME_LIST
	saved = saveListFile(articles);

	try:
		# Baixa os áudios na pasta correta e Adiciona um campo 'audio'
		if (saved):
			articles = downloadAudios(articles);   #[{"id":"10", "url":"http://",  "audio":{"contentUrl":"". "filename":"radio_id", "url":""}}]

		# Atualiza no banco usando o endpoint article['audio'] =  { contentUrl: 'http...' } 
		updateArticles(articles);
		
	except Exception as e:
		print e
	



if __name__ == '__main__':
	main()