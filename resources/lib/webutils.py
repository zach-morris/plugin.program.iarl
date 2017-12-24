# Zach Morris IARL Web Utilities
    
import xbmc,xbmcgui,xbmcaddon,xbmcplugin,urllib,urllib2,tarfile,os,sys,re,gzip,random,time
from StringIO import StringIO
try:
	import requests
	import requests.packages.urllib3
	requests.packages.urllib3.disable_warnings()
except:
	xbmc.log(msg='IARL:  script.module.requests is not installed and is required', level=xbmc.LOGERROR)

try:
	user_agent_options = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5','Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0','Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36']
	user_agent = user_agent_options[random.randint(0,len(user_agent_options)-1)]  #Just pick a random user agent from the top 10 according to the internet
except:
	user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
chunk_size = 102400 #100 KB chunks
download_timeout = 60 #Seems long... according to the internet this is the default

class download_tools():
	#Downloader with login option for archive.org
	def Downloader(self,url,dest,login_opt,username,password,est_filesize,description,heading):
		dp = xbmcgui.DialogProgress()
		dp.create(heading,description,'')
		dp.update(0)
		success = False
		if len(username)>0 and len(password)>0 and login_opt: #Attempt to login for downloading
			try:
				s = requests.Session()
				r = s.get("https://archive.org/account/login.php")
				data={"username":username, "password":password, "remember":"CHECKED","action":"login","submit":"Log+in"}
				r = s.post('https://archive.org/account/login.php', data=data)
				if 'that password seems incorrect' in str(r.text.encode('utf-8')).lower():
					xbmc.log(msg='IARL:  Login and Password were not accepted, we will try to download anyway', level=xbmc.LOGDEBUG)
				xbmc.log(msg='IARL:  Download with login URL: '+str(url), level=xbmc.LOGDEBUG)
				xbmc.log(msg='IARL:  Download save filename: '+str(dest), level=xbmc.LOGDEBUG)
				r = s.get(url,verify=False,stream=True,timeout=download_timeout)
				f = open(dest, 'wb')
				size = 0
				last_time = time.time()
				for chunk in r.iter_content(chunk_size):
					if dp.iscanceled():
						dp.close()
						raise Exception('User Cancelled Download')
					size = size + chunk_size
					percent = 100.0 * size / (est_filesize + 1) #Added 1 byte to avoid div by zero
					f.write(chunk)
					now = time.time()
					diff = now - last_time
					if diff > 1:
						percent = int(percent)
						last_time = now
						dp.update(percent)
						if dp.iscanceled():
							dp.close()
							raise Exception('User Cancelled Download')
				f.flush()
				f.close()
				success = True
				dp.close()
			except Exception as web_except:
				xbmc.log(msg='IARL:  There was a download error (with login): '+str(url)+' - '+str(web_except), level=xbmc.LOGERROR)
				success = False
		else:
			try:
				s = requests.Session()
				xbmc.log(msg='IARL:  Download with no login URL: '+str(url), level=xbmc.LOGDEBUG)
				xbmc.log(msg='IARL:  Download save filename: '+str(dest), level=xbmc.LOGDEBUG)
				r = s.get(url,verify=False,stream=True,timeout=download_timeout)
				f = open(dest, 'wb')
				size = 0
				last_time = time.time()
				for chunk in r.iter_content(chunk_size):
					if dp.iscanceled():
						dp.close()
						raise Exception('User Cancelled Download')
					size = size + chunk_size
					percent = 100.0 * size / (est_filesize + 1) #Added 1 byte to avoid div by zero
					f.write(chunk)
					now = time.time()
					diff = now - last_time
					if diff > 1:
						percent = int(percent)
						last_time = now
						dp.update(percent)
						if dp.iscanceled():
							dp.close()
							raise Exception('User Cancelled Download')
				f.flush()
				f.close()
				success = True
				dp.close()
			except Exception as web_except:
				xbmc.log(msg='IARL:  There was a download error (no login): '+str(url)+' - '+str(web_except), level=xbmc.LOGERROR)
				success = False

		return success

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
	br.addheaders = [('User-agent', user_agent)]
	r = br.open(url)
	html = r.read()
	html_source= br.response().read()
	return html_source
	
def makeRequest(url, headers=None):
	try:
		if not headers:
			headers = {'User-agent' : user_agent}
		req = urllib2.Request(url,None,headers)
		response = urllib2.urlopen(req)
		data = response.read()
		response.close()
		return data
	except:
		return None
		xbmc.log(msg='IARL:  URL request failed', level=xbmc.LOGDEBUG)
		
def url_isup(url, headers=None):
	try:
		if not headers:
			headers = {'User-agent' : user_agent}
		req = urllib2.Request(url,None,headers)
		response = urllib2.urlopen(req)
		data = response.read()
		response.close()
		return True
	except: return False

def quote_url(text):
	if 'drive.google.com' not in text: #Dont quote google drive urls
		new_url = urllib.quote(text,':%/')
	else:
		new_url = text
	return new_url

def get_iarl_extras_update_content():
	xx = 0
	extras_update_content = ''
	url = 'https://raw.githubusercontent.com/zach-morris/iarl.extras/master/iarl_extras.xml'
	try:
		r = requests.get(url, stream=True, timeout=5)
		for lines in r.iter_lines():
			if lines and xx<5:
				extras_update_content = extras_update_content+str(lines)
				if '</last_update_comment>' in lines:
					xx = 5
					break
			else:
				break
			xx = xx+1
	except:
		xbmc.log(msg='IARL:  Unable to reach iarl.extras repo', level=xbmc.LOGDEBUG)

	return extras_update_content

def unquote_name(text):
	new_text = urllib.unquote(text)
	return new_text