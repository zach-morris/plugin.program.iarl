# -*- coding: utf-8 -*-

""" Web Utils taken from the p2p-streams addon (2014 enen92 fightnight), updated for IARL purposes

    This file contains web utilities
    
    Classes:
    
    download_tools() -> Contains a downloader, a extraction function and a remove function
    
    Functions:
    
    get_page_source -> Get a webpage source code through urllib2
    mechanize_browser(url) -> Get a webpage source code through mechanize module. To avoid DDOS protections.
    makeRequest(url, headers=None) -> check if a page is up and retrieve its source code
    clean(text) -> Remove specific characters from the page source
    url_isup(url, headers=None) -> Check if url is up. Returns True or False.
   	
   	Thanks to primaeval for updated code for login capability
"""
    
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,urllib,urllib2,tarfile,os,sys,re,gzip

try: #Enable login
	if 'Enabled' in xbmcaddon.Addon('plugin.program.iarl').getSetting('iarl_enable_login'):
		import requests
		import time
		import requests.packages.urllib3
		requests.packages.urllib3.disable_warnings()
	else:
		xbmc.log(msg='IARL:  Login not enabled', level=xbmc.LOGDEBUG)
except:
	xbmc.log(msg='IARL:  script.module.requests is not installed, login is not supported without it!', level=xbmc.LOGDEBUG)

from StringIO import StringIO

user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36'

class download_tools():
	def Downloader(self,url,dest,login_opt,username,password,est_filesize,description,heading):
		dp = xbmcgui.DialogProgress()
		dp.create(heading,description,'')
		dp.update(0)
		success = False
		if len(username)>0 and len(password)>0 and login_opt: #Attempt to login for downloading
			s = requests.Session()
			r = s.get("https://archive.org/account/login.php")
			data={"username":username, "password":password, "remember":"CHECKED","action":"login","submit":"Log+in"}
			r = s.post('https://archive.org/account/login.php', data=data)
			if 'that password seems incorrect' in str(r.text.encode('utf-8')).lower():
				xbmc.log(msg='IARL:  Login and Password were not accepted, we will try to download anyway', level=xbmc.LOGDEBUG)
			r = s.get(url,verify=False,stream=True)
			f = open(dest, 'wb')
			size = 0
			last_time = time.time()
			for chunk in r.iter_content(1024):
				size = size + 1024.0
				percent = 100.0 * size / est_filesize
				f.write(chunk)
				now = time.time()
				diff = now - last_time
				if diff > 1:
					percent = int(percent)
					last_time = now
					dp.update(percent)
					if dp.iscanceled():
						dp.close()
						raise
			f.flush()
			f.close()
			success = True
			dp.close()
		else: #No login / pass available or login not enabled, use the old download method
			try:
				xbmc.log(msg='IARL:  Download no login URL: '+str(url), level=xbmc.LOGDEBUG)
				urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: self._pbhook(nb,bs,fs,est_filesize,dp))
				success = True
			except:
				xbmc.log(msg='IARL:  Download was cancelled by the user.', level=xbmc.LOGNOTICE)
				success = False

		return success

	def _pbhook(self,numblocks, blocksize, filesize, est_filesize, dp=None):

		#Filesize from archive.org is not available in most archives, use xml value
		try:
			perc_filesize = max(filesize,est_filesize)
		except:
			perc_filesize = filesize

		try:
			percent = int((int(numblocks)*int(blocksize)*100)/int(perc_filesize))
			dp.update(percent)
			# print 'test'
			# print str(numblocks)
			# print str(blocksize)
			# print str(filesize)
			# print str(percent)
		except:
			percent = 100
			dp.update(percent)
		if dp.iscanceled():
			dp.close()
			raise
	
	def extract(self,file_tar,destination):
		dp = xbmcgui.DialogProgress()
		dp.create(translate(40000),translate(40044))
		tar = tarfile.open(file_tar)
		tar.extractall(destination)
		dp.update(100)
		tar.close()
		dp.close()
		
	def remove(self,file_):
		dp = xbmcgui.DialogProgress()
		dp.create(translate(40000),translate(40045))
		os.remove(file_)
		dp.update(100)
		dp.close()

def get_page_source(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	if response.info().get('Content-Encoding') == 'gzip':
		buf = StringIO(response.read())
		f = gzip.GzipFile(fileobj=buf)
		link = f.read()
	else:
		link = response.read()
	response.close()
	return link

def mechanize_browser(url):
	import mechanize
	br = mechanize.Browser()
	br.set_handle_equiv(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	r = br.open(url)
	html = r.read()
	html_source= br.response().read()
	return html_source
	
def makeRequest(url, headers=None):
	try:
		if not headers:
			headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}
		req = urllib2.Request(url,None,headers)
		response = urllib2.urlopen(req)
		data = response.read()
		response.close()
		return data
	except:
		mensagemok(translate(40000),translate(40122))
		sys.exit(0)
		
def url_isup(url, headers=None):
	try:
		if not headers:
			headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}
		req = urllib2.Request(url,None,headers)
		response = urllib2.urlopen(req)
		data = response.read()
		response.close()
		return True
	except: return False
		
def clean(text):
      command={'\r':'','\n':'','\t':'','&nbsp;':' ','&quot;':'"','&#039;':'','&#39;':"'",'&#227;':'ã','&170;':'ª','&#233;':'é','&#231;':'ç','&#243;':'ó','&#226;':'â','&ntilde;':'ñ','&#225;':'á','&#237;':'í','&#245;':'õ','&#201;':'É','&#250;':'ú','&amp;':'&','&#193;':'Á','&#195;':'Ã','&#202;':'Ê','&#199;':'Ç','&#211;':'Ó','&#213;':'Õ','&#212;':'Ó','&#218;':'Ú'}
      regex = re.compile("|".join(map(re.escape, command.keys())))
      return regex.sub(lambda mo: command[mo.group(0)], text)

def quote_url(text):
	new_url = urllib.quote(text,':%/')
	return new_url

def unquote_name(text):
	new_text = urllib.unquote(text)
	return new_text