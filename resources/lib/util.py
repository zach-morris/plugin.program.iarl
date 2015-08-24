import os, sys, re, shutil, json, zipfile
import os.path
import xbmc, xbmcaddon, xbmcvfs
from xbmcswift2 import xbmcgui
import time
from descriptionparserfactory import *

#
# CONSTANTS AND GLOBALS #
#

iarl_plugin_name = 'plugin.program.iarl'
# iarl_parser_file = 'parserConfig.xml'
# iarl_addon_data_path = xbmc.translatePath(os.path.join("special://profile/addon_data",iarl_plugin_name))
# iarl_addon_profile_path = xbmc.translatePath(os.path.join("special://","profile"))
# iarl_cache_path = os.path.join(xbmc.translatePath("special://profile").decode('utf-8'),"Thumbnails")
# iarl_addon_home_path = xbmc.translatePath(os.path.join("special://","home"))
# iarl_addon_favorites_path = xbmc.translatePath( 'special://profile/favourites.xml' )
# iarl_addon_addons_path = xbmc.translatePath(os.path.join(iarl_addon_home_path,"addons"))
# iarl_addon_current_path = xbmc.translatePath(os.path.join(iarl_addon_addons_path,iarl_plugin_name))
# iarl_addon_parse_file_path = os.path.join(iarl_addon_current_path, 'resources', 'data' , iarl_parser_file)
debugging_enabled = True


__addon__ = xbmcaddon.Addon(id='%s' %iarl_plugin_name)
__language__ = __addon__.getLocalizedString



html_unescape_table = {
		"&amp;" : "&",
		"&quot;" : '"' ,
		"&apos;" : "'",
		"&gt;" : ">",
		"&lt;" : "<",
		"&nbsp;" : " ",
		"&#x26;" : "&",
		"&#x27;" : "\'",
		"&#xB2;" : "2",
		"&#xB3;" : "3",		
		}

def html_unescape(text):
		
		for key in html_unescape_table.keys():
			text = text.replace(key, html_unescape_table[key])
			
		return text
	

html_escape_table = {
		"&" : "%26",
		" " : "%20" ,
		"'" : "%27",
		">" : "%3E",
		"<" : "%3C",		
		}

def html_escape(text):
		
		for key in html_escape_table.keys():
			text = text.replace(key, html_escape_table[key])
			
		return text


def joinPath(part1, *parts):
	path = ''
	if(part1.startswith('smb://')):
		path = part1
		for part in parts:
			path = "%s/%s" %(path, part)
	else:
		path = os.path.join(part1, *parts)
		
	return path


#
# METHODS #
#

def get_Operating_System():
	current_OS = None

	if 'win32' in sys.platform:
		current_OS = 'Windows'
	elif 'linux' in sys.platform:
		current_OS = 'Nix'
	elif 'darwin' in sys.platform:
		if 'USER' in os.environ and os.environ['USER'] in ('mobile','frontrow',):
			current_OS = 'IOS'
		else: 
			current_OS = 'OSX'

	return current_OS

def getEnvironment():
	return ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]

def localize(id):
	try:
		return __language__(id)
	except:
		return "Sorry. No translation available for string with id: " +str(id)

def getAddonDataPath():
	
	path = ''
	path = xbmc.translatePath('special://profile/addon_data/%s' %(iarl_plugin_name))
		
	if not os.path.exists(path):
		try:
			os.makedirs(path)
		except:
			path = ''	
	return path


def getAddonInstallPath():
	path = ''
				
	path = __addon__.getAddonInfo('path')
	
	return path
		
def getDATFilePath():
	path = ''
				
	path = os.path.join(getAddonInstallPath(),'resources/data/dat_files')
	
	return path	

def getMediaFilePath():
	path = ''
				
	path = os.path.join(getAddonInstallPath(),'resources/skins/Default/media/')
	
	return path	

def getSkinFilePath():
	path = ''
				
	path = os.path.join(getAddonInstallPath(),'resources/skins/')
	
	return path	

def getParserFilePath(xmlname):
	path = ''
				
	path = os.path.join(getAddonInstallPath(),'resources/data/'+xmlname)
	
	return path	

def getYouTubePluginurl(videoid):
	url = ''

	url = 'plugin://plugin.video.youtube/play/?video_id='+videoid

	return url

def getAutoexecPath():	
	return xbmc.translatePath('special://profile/autoexec.py')


def getTempDir():
	tempDir = os.path.join(getAddonDataPath(), 'temp_iarl')
	
	try:
		#check if folder exists
		if(not os.path.isdir(tempDir)):
			os.mkdir(tempDir) #If it doesn't exist, make it
		return tempDir
	except Exception, (exc):
		Logutil.log('Error creating temp dir: ' +str(exc), LOG_LEVEL_ERROR)
		return None

def check_temp_folder_and_clean(iarl_options_dl_cache):
	current_path = getTempDir()
	current_path_size = getFolderSize(current_path)

	if current_path_size > iarl_options_dl_cache:
		print 'Deleting IARL Cache'
		shutil.rmtree(current_path)

	current_path = getTempDir()  #Remake the directory


def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size

def getConfigXmlPath():
	if(not ISTESTRUN):
		addonDataPath = getAddonDataPath() 
		configFile = os.path.join(addonDataPath, "config.xml")
	else:
		configFile = os.path.join(getAddonInstallPath(), "resources", "lib", "TestDataBase", "config.xml")
	
	Logutil.log('Path to configuration file: ' +str(configFile), LOG_LEVEL_INFO)
	return configFile

def update_external_launch_commands(current_os,retroarch_path,xml_id):

	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0] + '/'

	parserfile = getParserFilePath('external_launcher_parser.xml')
	launchersfile = getParserFilePath('external_command_databse.xml')
	descParser = DescriptionParserFactory.getParser(parserfile)
	results = descParser.parseDescription(launchersfile,'xml')
	user_options = list()
	launch_command = list()
	new_launch_command = None

	if current_os == 'OSX':
		retroarch_path = retroarch_path.split('.app')[0]+'.app' #Make App Path for OSX only up to the container

	for entries in results: #Create list of available commands for the current OS
		if entries['operating_system'][0] == current_os:
			user_options.append(entries['launcher'][0])
			launch_command.append(entries['launcher_command'][0])

	user_options.append('None')
	launch_command.append('none')

	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Select from the available launch commands', user_options)

	if ret1>=0:
		ret2 = current_dialog.select('Are you sure you want to update[CR]the current External Launch Command?', ['Yes','Cancel'])
		if ret2<1:
			new_launch_command = launch_command[ret1]
			new_launch_command = new_launch_command.replace('%APP_PATH%',retroarch_path)
			update_xml_header(current_xml_path,current_xml_filename,'emu_ext_launch_cmd',new_launch_command)
			ok_ret = current_dialog.ok('Complete','External Launch Command was updated')

def copyFile(oldPath, newPath):
	Logutil.log('new path = %s' %newPath, LOG_LEVEL_INFO)
	newDir = os.path.dirname(newPath)
	if not os.path.isdir(newDir):
		Logutil.log('create directory: %s' %newDir, LOG_LEVEL_INFO)
		try:
			os.mkdir(newDir)
		except Exception, (exc):
			Logutil.log('Error creating directory: %s\%s' %(newDir, str(exc)), LOG_LEVEL_ERROR)
			return
	
	if not os.path.isfile(newPath):
		Logutil.log('copy file from %s to %s' %(oldPath, newPath), LOG_LEVEL_INFO)
		try:
			shutil.copy2(oldPath, newPath)
		except Exception, (exc):
			Logutil.log('Error copying file from %s to %s\%s' %(oldPath, newPath, str(exc)), LOG_LEVEL_ERROR)
	
	
def getSettings():
	settings = xbmcaddon.Addon(id='%s' %iarl_plugin_name)
	return settings


#HACK: XBMC does not update labels with empty strings
def setLabel(label, control):
	if(label == ''):
		label = ' '
		
	control.setLabel(str(label))


#Parses all the xml dat files in the folder and returns them to create the proper directories
def scape_xml_headers():
	dat_path = getDATFilePath()
	subfolders, files = xbmcvfs.listdir(dat_path)
	#debug("Contents of %r:\nSubfolders: %r\nFiles: %r" % (dat_path, subfolders, files))
	emu_location = list()
	emu_name = list()
	emu_parser = list()
	emu_description = list()
	emu_category = list()
	emu_version = list()
	emu_date = list()
	emu_author = list()
	emu_homepage = list()
	emu_baseurl = list()
	emu_downloadpath = list()
	emu_postdlaction = list()
	emu_comment = list()
	emu_thumb = list()
	emu_banner = list()
	emu_fanart = list()
	emu_logo = list()
	emu_trailer = list()
	for ffile in files:
		total_lines = 500  #Read up to this many lines looking for the header
		f=open(os.path.join(dat_path,ffile),'rU')
		f.seek(0)
		header_end=0
		line_num=0
		header_text = ''
		while header_end < 1:
			line=f.readline()    
			header_text+=str(line)
			line_num = line_num+1
			if '</header>' in header_text: #Found the header
				header_end = 1
				header_text = header_text.split('<header>')[1].split('</header>')[0]
				emu_name.append(header_text.split('<emu_name>')[1].split('</emu_name>')[0])
				emu_parser.append(header_text.split('<emu_parser>')[1].split('</emu_parser>')[0])
				emu_location.append(os.path.join(dat_path,ffile))
				emu_description.append(header_text.split('<emu_description>')[1].split('</emu_description>')[0])
				emu_category.append(header_text.split('<emu_category>')[1].split('</emu_category>')[0])
				emu_version.append(header_text.split('<emu_version>')[1].split('</emu_version>')[0])
				emu_date.append(header_text.split('<emu_date>')[1].split('</emu_date>')[0])
				emu_author.append(header_text.split('<emu_author>')[1].split('</emu_author>')[0])
				emu_homepage.append(header_text.split('<emu_homepage>')[1].split('</emu_homepage>')[0])
				emu_baseurl.append(header_text.split('<emu_baseurl>')[1].split('</emu_baseurl>')[0])
				emu_downloadpath.append(header_text.split('<emu_downloadpath>')[1].split('</emu_downloadpath>')[0])
				emu_postdlaction.append(header_text.split('<emu_postdlaction>')[1].split('</emu_postdlaction>')[0])
				emu_comment.append(header_text.split('<emu_comment>')[1].split('</emu_comment>')[0])
				emu_thumb.append(header_text.split('<emu_thumb>')[1].split('</emu_thumb>')[0])
				emu_banner.append(header_text.split('<emu_banner>')[1].split('</emu_banner>')[0])
				emu_fanart.append(header_text.split('<emu_fanart>')[1].split('</emu_fanart>')[0])
				emu_logo.append(header_text.split('<emu_logo>')[1].split('</emu_logo>')[0])
				emu_trailer.append(header_text.split('<emu_trailer>')[1].split('</emu_trailer>')[0])
				f.close()

			if line_num == total_lines:  #Couldn't find the header
				header_end = 1
				f.close()
				print 'IARL Error:  Unable to parse header in xml file'

	dat_file_table = {
	'emu_name' : emu_name,
	'emu_parser' : emu_parser,
	'emu_location' : emu_location,
	'emu_description' : emu_description,
	'emu_category' : emu_category,
	'emu_version' : emu_version,
	'emu_date' : emu_date,
	'emu_author' : emu_author,
	'emu_homepage' : emu_homepage,
	'emu_baseurl' : emu_baseurl,
	'emu_downloadpath' : emu_downloadpath,
	'emu_postdlaction' : emu_postdlaction,
	'emu_comment' : emu_comment,
	'emu_thumb' : emu_thumb,
	'emu_banner' : emu_banner,
	'emu_fanart' : emu_fanart,
	'emu_logo': emu_logo,
	'emu_trailer': emu_trailer
	}
	#print dat_file_table
	return dat_file_table

def get_xml_header_paths(xmlfilename):
	total_lines = 500  #Read up to this many lines looking for the header
	f=open(xmlfilename,'rU')
	f.seek(0)
	header_end=0
	line_num=0
	header_text = ''
	emu_name = list()
	emu_logo = list()
	emu_fanart = list()
	emu_baseurl = list()
	emu_downloadpath = list()
	emu_postdlaction = list()
	emu_launcher = list()
	emu_ext_launch_cmd = list()

	while header_end < 1:
		line=f.readline()    
		header_text+=str(line)
		line_num = line_num+1
		if '</header>' in header_text: #Found the header
			header_end = 1
			header_text = header_text.split('<header>')[1].split('</header>')[0]
			emu_name.append(header_text.split('<emu_name>')[1].split('</emu_name>')[0])
			emu_logo.append(header_text.split('<emu_logo>')[1].split('</emu_logo>')[0])
			emu_fanart.append(header_text.split('<emu_fanart>')[1].split('</emu_fanart>')[0])
			emu_baseurl.append(header_text.split('<emu_baseurl>')[1].split('</emu_baseurl>')[0])
			emu_downloadpath.append(header_text.split('<emu_downloadpath>')[1].split('</emu_downloadpath>')[0])
			emu_postdlaction.append(header_text.split('<emu_postdlaction>')[1].split('</emu_postdlaction>')[0])
			emu_launcher.append(header_text.split('<emu_launcher>')[1].split('</emu_launcher>')[0])
			emu_ext_launch_cmd.append(header_text.split('<emu_ext_launch_cmd>')[1].split('</emu_ext_launch_cmd>')[0])
			f.close()
		if line_num == total_lines:  #Couldn't find the header
			header_end = 1
			f.close()
			print 'IARL Error:  Unable to parse header in xml file'

	dat_file_table = {
	'emu_name' : emu_name,
	'emu_logo': emu_logo,
	'emu_fanart': emu_fanart,
	'emu_baseurl' : emu_baseurl,
	'emu_downloadpath' : emu_downloadpath,
	'emu_postdlaction' : emu_postdlaction,
	'emu_launcher' : emu_launcher,
	'emu_ext_launch_cmd' : emu_ext_launch_cmd,
	}

	return dat_file_table

def set_iarl_window_properties(emu_name):

	if emu_name == 'Sega 32X':
		xbmcgui.Window(10000).setProperty('iarl.current_theme','32x')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','32x_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','32x_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','32x_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','32x_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif emu_name == 'Nintendo Entertainment System - NES':
		xbmcgui.Window(10000).setProperty('iarl.current_theme','NES')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','NES_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','white.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','nes_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','NES_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif emu_name == 'Super Nintendo Entertainment System - SNES':
		xbmcgui.Window(10000).setProperty('iarl.current_theme','SNES')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','SNES_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','white.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','nes_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','SNES_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif emu_name == 'Sega Genesis':
		xbmcgui.Window(10000).setProperty('iarl.current_theme','Genesis')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','genesis_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','sega_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','sega_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','genesis_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif emu_name == 'Nintendo 64 - N64':
		xbmcgui.Window(10000).setProperty('iarl.current_theme','N64')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','N64_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','n64_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','n64_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','N64_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif emu_name == 'MAME - Multiple Arcade Machine Emulator':
		xbmcgui.Window(10000).setProperty('iarl.current_theme','MAME')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','arcade_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','arcade_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','arcade_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','arcade_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	else:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','default')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','arcade_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','white.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','black.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')


def parse_xml_romfile(xmlfilename,parserfile,cleanlist,plugin):

	#Get basic xml path info
	xml_header_info = get_xml_header_paths(xmlfilename)

	#Define the Parser
	descParser = DescriptionParserFactory.getParser(parserfile)
	#Get Results
	results = descParser.parseDescription(xmlfilename,'xml')

	set_iarl_window_properties(xml_header_info['emu_name'][0])

	items = []
	current_item = []
	idx = 0
	total_arts = 10
	for entries in results:
		idx += 1

		current_name = []
		if entries['rom_name']:
			current_name = entries['rom_name'][0]
			if cleanlist:
				current_name = re.sub(r'\([^)]*\)', '', current_name)
		else:
			current_name = None

		current_fname = []
		if entries['rom_filename']:
			current_fname = xml_header_info['emu_baseurl'][0]+str(entries['rom_filename'][0])
			current_fname = html_unescape(current_fname)
		else:
			current_fname = None

		current_save_fname = []
		if entries['rom_filename']:
			current_save_fname = str(entries['rom_filename'][0])
			current_save_fname = html_unescape(current_save_fname)
		else:
			current_save_fname = None

		current_emu_name = []
		if xml_header_info['emu_name']:
			current_emu_name = xml_header_info['emu_name'][0]
		else:
			current_emu_name = None

		current_emu_logo = []
		if xml_header_info['emu_logo']:
			current_emu_logo = xml_header_info['emu_logo'][0]
		else:
			current_emu_logo = None

		current_emu_fanart = []
		if xml_header_info['emu_fanart']:
			current_emu_fanart = xml_header_info['emu_fanart'][0]
		else:
			current_emu_fanart = None

		current_emu_downloadpath = []
		if xml_header_info['emu_downloadpath']:
			current_emu_downloadpath = xml_header_info['emu_downloadpath'][0]
		else:
			current_emu_downloadpath = None

		current_emu_postdlaction = []
		if xml_header_info['emu_postdlaction']:
			current_emu_postdlaction = xml_header_info['emu_postdlaction'][0]
		else:
			current_emu_postdlaction = None

		current_emu_launcher = []
		if xml_header_info['emu_launcher']:
			current_emu_launcher = xml_header_info['emu_launcher'][0]
		else:
			current_emu_launcher = None

		current_emu_ext_launch_cmd = []
		if xml_header_info['emu_ext_launch_cmd']:
			current_emu_ext_launch_cmd = xml_header_info['emu_ext_launch_cmd'][0]
		else:
			current_emu_ext_launch_cmd = None

		current_sfname = []
		if entries['rom_supporting_file']:
			current_sfname = xml_header_info['emu_baseurl'][0]+str(entries['rom_supporting_file'][0])
			current_sfname = html_unescape(current_sfname)
		else:
			current_sfname = None

		current_save_sfname = []
		if entries['rom_supporting_file']:
			current_save_sfname = str(entries['rom_supporting_file'][0])
			current_save_sfname = html_unescape(current_save_sfname)
		else:
			current_save_sfname = None

		current_icon = list()
		for ii in range(0,total_arts):
			if entries['rom_clearlogo'+str(ii+1)]:
				current_icon.append(html_unescape(entries['rom_clearlogo'+str(ii+1)][0]))
			else:
				current_icon.append(None)

		current_icon2 = filter(bool, current_icon)

		if not current_icon2:
			current_icon2 = getMediaFilePath() + xbmcgui.Window(10000).getProperty('iarl.default_thumb') #Use the default thumb if nothing else is avialable
		else:
			current_icon2 = current_icon2[0]

		current_snapshot = list()
		for ii in range(0,total_arts):
			if entries['rom_snapshot'+str(ii+1)]:
				current_snapshot.append(html_unescape(entries['rom_snapshot'+str(ii+1)][0]))
			else:
				current_snapshot.append(None)

		current_thumbnail = list()
		for ii in range(0,total_arts):
			if entries['rom_boxart'+str(ii+1)]:
				current_thumbnail.append(html_unescape(entries['rom_boxart'+str(ii+1)][0]))
				# print html_unescape(entries['rom_boxart'+str(ii+1)][0])
			else:
				current_thumbnail.append(None)

		current_thumbnail2 = filter(bool, current_thumbnail)

		if not current_thumbnail2:
			current_thumbnail2 = getMediaFilePath() + xbmcgui.Window(10000).getProperty('iarl.default_thumb') #Use the default thumb if nothing else is avialable
		else:
			current_thumbnail2 = current_thumbnail2[0]

		if entries['rom_category']:
			current_genre = entries['rom_category'][0]
		else:
			current_genre = None

		if entries['rom_author']:
			current_credits = entries['rom_author'][0]
		else:
			current_credits = None

		if entries['rom_year']:
			current_date = entries['rom_year'][0]
		else:
			current_date = None

		if entries['rom_plot']:
			current_plot = entries['rom_plot'][0]
		else:
			current_plot = None

		if entries['rom_players']:
			current_nplayers = entries['rom_players'][0]
		else:
			current_nplayers = None

		if entries['rom_videoid']:
			current_trailer = getYouTubePluginurl(entries['rom_videoid'][0]) #Return youtube plugin URL
		else:
			current_trailer = None

		current_fanart = list()
		for ii in range(0,total_arts):
			if entries['rom_fanart'+str(ii+1)]:
				current_fanart.append(html_unescape(entries['rom_fanart'+str(ii+1)][0]))
			else:
				current_fanart.append(None)

		current_banner = list()
		for ii in range(0,total_arts):
			if entries['rom_banner'+str(ii+1)]:
				current_banner.append(html_unescape(entries['rom_banner'+str(ii+1)][0]))
			else:
				current_banner.append(None)

		current_clearlogo = list()
		for ii in range(0,total_arts):
			if entries['rom_clearlogo'+str(ii+1)]:
				current_clearlogo.append(html_unescape(entries['rom_clearlogo'+str(ii+1)][0]))
			else:
				current_clearlogo.append(None)

		if current_emu_name == 'MAME - Multiple Arcade Machine Emulator':  #MAME xml filenames dont include the extension
			if current_fname:
				current_fname = current_fname+'.zip'
			if current_sfname:
				current_sfname = current_sfname+'.zip'
			if current_save_fname:
				current_save_fname = current_save_fname+'.zip'
			if current_save_sfname:
				current_save_sfname = current_save_sfname+'.zip'

		current_item = []
		current_item = { 
        'label' : current_name, 'icon': current_icon2,
        'thumbnail' : current_thumbnail2,
        'path' : plugin.url_for('get_selected_rom', romname=entries['rom_name'][0]),
        'info' : {'genre': current_genre, 'studio': current_credits, 'date': current_date, 'plot': current_plot, 'trailer': current_trailer},
        'properties' : {'fanart_image' : current_fanart[0], 'banner' : current_banner[0], 'clearlogo': current_clearlogo[0], 'poster': current_thumbnail[1],
        'fanart1': current_fanart[0], 'fanart2': current_fanart[1], 'fanart3': current_fanart[2], 'fanart4': current_fanart[3], 'fanart5': current_fanart[4], 'fanart6': current_fanart[5], 'fanart7': current_fanart[6], 'fanart8': current_fanart[7], 'fanart9': current_fanart[8], 'fanart10': current_fanart[9],
        'banner1': current_banner[0], 'banner2': current_banner[1], 'banner3': current_banner[2], 'banner4': current_banner[3], 'banner5': current_banner[4], 'banner6': current_banner[5], 'banner7': current_banner[6], 'banner8': current_banner[7], 'banner9': current_banner[8], 'banner10': current_banner[9],
        'snapshot1': current_snapshot[0], 'snapshot2': current_snapshot[1], 'snapshot3': current_snapshot[2], 'snapshot4': current_snapshot[3], 'snapshot5': current_snapshot[4], 'snapshot6': current_snapshot[5], 'snapshot7': current_snapshot[6], 'snapshot8': current_snapshot[7], 'snapshot9': current_snapshot[8], 'snapshot10': current_snapshot[9],
        'boxart1': current_thumbnail[0], 'boxart2': current_thumbnail[1], 'boxart3': current_thumbnail[2], 'boxart4': current_thumbnail[3], 'boxart5': current_thumbnail[4], 'boxart6': current_thumbnail[5], 'boxart7': current_thumbnail[6], 'boxart8': current_thumbnail[7], 'boxart9': current_thumbnail[8], 'boxart10': current_thumbnail[9],
        'nplayers': current_nplayers, 'emu_logo': current_emu_logo, 'emu_fanart': current_emu_fanart, 'emu_name': current_emu_name, 'rom_fname': current_fname, 'rom_sfname': current_sfname, 'rom_save_fname': current_save_fname, 'rom_save_sfname': current_save_sfname,
        'emu_downloadpath': current_emu_downloadpath, 'emu_postdlaction': current_emu_postdlaction, 'emu_launcher': current_emu_launcher, 'emu_ext_launch_cmd': current_emu_ext_launch_cmd}
        }
		items.append(current_item)

	
	return items

#HACK: XBMC does not update labels with empty strings
def getLabel(control):
	label = control.getLabel()
	if(label == ' '):
		label = ''
		
	return label

def get_size_of_folder(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def dlfile(url,dest):
    from urllib2 import Request, urlopen, URLError, HTTPError
    
    # Open the url
    try:
        f = urlopen(url)
        print "IARL: Downloading " + url
        print "IARL: To location " + dest

        # Open our local file for writing
        with open(dest, "wb") as local_file:
            local_file.write(f.read())
            if(os.path.exists(dest)):
                print 'progress:  ' + str(os.path.getsize(dest))
        result = 1

    #handle errors
    except HTTPError, e:
        print "IARL HTTP Error:", e.code, url
        result=0
    except URLError, e:
        print "IARL URL Error:", e.reason, url
        result=0

    return result


def selectlibretrocore():
		
	selectedCore = ''
	addons = ['None']
	
	# success, installedAddons = readLibretroCores("all", True, platform)
	success, installedAddons = readLibretroCores("all")
	if(not success):
		return False, ""
	addons.extend(installedAddons)
	
	# success, uninstalledAddons = readLibretroCores("uninstalled", False, platform)
	success, uninstalledAddons = readLibretroCores("uninstalled")
	if(not success):
		return False, ""
	addons.extend(uninstalledAddons)
	
	dialog = xbmcgui.Dialog()
	index = dialog.select('Select libretro core', addons)
	print "index = " +str(index)
	if(index == -1):
		return False, ""
	elif(index == 0):
		print "return success"
		return True, ""
	else:
		selectedCore = addons[index]
		return True, selectedCore

def readLibretroCores(enabledParam):
	
	addons = []
	addonsJson = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddons", "params": { "type": "kodi.gameclient", "enabled": "%s" } }' %enabledParam)
	jsonResult = json.loads(addonsJson)	
			
	try:
		for addonObj in jsonResult[u'result'][u'addons']:
			id = addonObj[u'addonid']
			# addon = xbmcaddon.Addon(id, installed=installedParam)
			# # extensions and platforms are "|" separated, extensions may or may not have a leading "."
			# addonPlatformStr = addon.getAddonInfo('platforms')
			# addonPlatforms = addonPlatformStr.split("|")
			# # for addonPlatform in addonPlatforms:
			# # 	if(addonPlatform == platform):
			addons.append(id)
	except KeyError:
		#no addons installed or found
		return True, addons
	# Logutil.log("addons: %s" %str(addons), util.LOG_LEVEL_INFO)
	return True, addons

def update_xml_header(current_path,current_filename,reg_exp,new_value):
	full_reg_exp = '</'+reg_exp+'>' #Look for this
	fout = open(current_path+'temp.xml', 'w') # out file
	full_new_val = '<'+reg_exp+'>'+new_value+'</'+reg_exp+'>' #replacement value

	value_updated = False

	with open(current_path+current_filename, 'rU') as fin:
		while True:
			line = fin.readline()
			if full_reg_exp in line:
				try:
					beg_of_line = line.split('<')
					end_of_line = line.split('>')
					my_new_line = beg_of_line[0]+full_new_val+end_of_line[-1:][0] #Match the characters that were previously on the line
					fout.write(my_new_line)
				except:
					fout.write(full_new_val)
				value_updated = True				
			else:
				fout.write(line)
			if not line:
				break
				pass

	fout.close()

	if value_updated:
		os.remove(current_path+current_filename) #Remove Old File
		os.rename(current_path+'temp.xml',current_path+current_filename) #Rename Temp File
		print 'File Updated: '+current_filename

def unzip_file(current_fname):
	zip_success = False
	uz_file_extension = None
	new_fname = None

	if zipfile.is_zipfile(current_fname):
		try:
			current_zip_fileparts = os.path.split(current_fname)
			current_zip_path = current_zip_fileparts[0] + '/'
			z_file = zipfile.ZipFile(current_fname)
			uz_file_extension = os.path.splitext(z_file.namelist()[0])[1] #Get rom extension
			z_file.extractall(current_zip_path)
			zip_success = True
			print 'Unzip Successful'
		except:
			zip_success = False
			print 'Unzip Failed'

		if zip_success:
			os.remove(current_fname)
	else:
		print current_fname + ' was not regognized as a zipfile and not extracted'

	if uz_file_extension is not None: #The file was unzipped, change from zip to rom extension
		new_fname = os.path.splitext(current_fname)[0]+uz_file_extension
		# xbmc.sleep(500) #Some sort of issue with launching after it's been unzipped and calling the launch to quickly, so sleep here
	else:
		new_fname = current_fname #Didn't unzip or didn't find a file extension


	return zip_success, new_fname


def set_new_dl_path(xml_id):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0] + '/'

	current_dialog = xbmcgui.Dialog()

	ret1 = current_dialog.select('Select Download Path Type', ['Default','Custom'])

	if ret1 == 0:
		ret2 = current_dialog.select('Are you sure you want to update the current Download Path for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_downloadpath','default')
			ok_ret = current_dialog.ok('Complete','Download Path was updated to default')
	elif ret1 == 1:
		new_path = current_dialog.browse(0,'Update Download Path','files')
		ret2 = current_dialog.select('Are you sure you want to update the current Download Path for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_downloadpath',new_path)
			ok_ret = current_dialog.ok('Complete','Download Path was updated to your custom folder')
	else:
		pass


def set_new_post_dl_action(xml_id):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0] + '/'

	current_dialog = xbmcgui.Dialog()

	ret1 = current_dialog.select('Select New Post Download Action', ['None','Unzip','Cancel'])

	if ret1 == 0:
		ret2 = current_dialog.select('Are you sure you want to set the post DL action to none for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction','none')
			ok_ret = current_dialog.ok('Complete','Post Download Action Updated to None')
	elif ret1 == 1:
		ret2 = current_dialog.select('Are you sure you want to set the post DL action to Unzip for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction','unzip_rom')
			ok_ret = current_dialog.ok('Complete','Post Download Action Updated to Unzip')
	else:
		pass


def set_new_emu_launcher(xml_id):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0] + '/'

	current_dialog = xbmcgui.Dialog()

	ret1 = current_dialog.select('Select New Emulator Launcher', ['Kodi RetroPlayer','External','Cancel'])

	if ret1 == 0:
		ret2 = current_dialog.select('Are you sure you want to set the Emulator to Kodi Retroplayer for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_launcher','retroplayer')
			ok_ret = current_dialog.ok('Complete','Emulator updated to Kodi Retroplayer')
	elif ret1 == 1:
		ret2 = current_dialog.select('Are you sure you want to set the Emulator to External Program for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_launcher','external')
			ok_ret = current_dialog.ok('Complete','Emulator updated to External Program')
	else:
		pass

def check_downloaded_file(file_path):

	bad_file_found = False

	st = os.stat(file_path)
	# print st
	if st.st_size < 1: #Zero Byte File
		current_dialog = xbmcgui.Dialog()
		ok_ret = current_dialog.ok('Error','The selected file was not available in the Archive[CR]Sorry about that')
		os.remove(file_path) #Remove Zero Byte File
		bad_file_found = True

	return bad_file_found

def getScrapingMode(settings):
	scrapingMode = 0
	scrapingModeStr = settings.getSetting(SETTING_IARL_SCRAPINGMODE)			
	if(scrapingModeStr == 'Automatic: Accurate'):
		scrapingMode = 0
	elif(scrapingModeStr == 'Automatic: Guess Matches'):
		scrapingMode = 1
	elif(scrapingModeStr == 'Interactive: Select Matches'):
		scrapingMode = 2
		
	return scrapingMode


def indentXml(elem, level=0):
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indentXml(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

def debug(message, level=xbmc.LOGNOTICE):
    """
    Write a debug message to xbmc.log
    :type message: str
    :param message: the message to log
    :type level: int
    :param level: (Optional) the log level (supported values are found at xbmc.LOG...)
    """
    if debugging_enabled:
        if isinstance(message, unicode):
            message = message.encode("utf-8")
        for line in message.splitlines():
            xbmc.log(msg="IARL: " + line, level=level)

iarl_plugin_home = getAddonInstallPath()


#
# Logging
#


try:
	from sqlite3 import dbapi2 as sqlite
	print("IARL_INFO: Loading sqlite3 as DB engine")
except:
	from pysqlite2 import dbapi2 as sqlite
	print("IARL_INFO: Loading pysqlite2 as DB engine")

class Logutil:
	
	currentLogLevel = None

	@staticmethod
	def log(message, logLevel):
			
		if(Logutil.currentLogLevel == None):
			print "IARL: init log level"
			Logutil.currentLogLevel = Logutil.getCurrentLogLevel()
			print "IARL: current log level: " +str(Logutil.currentLogLevel)
		
		if(logLevel > Logutil.currentLogLevel):			
			return
			
		prefix = ''
		if(logLevel == LOG_LEVEL_DEBUG):
			prefix = 'IARL_DEBUG: '
		elif(logLevel == LOG_LEVEL_INFO):
			prefix = 'IARL_INFO: '
		elif(logLevel == LOG_LEVEL_WARNING):
			prefix = 'IARL_WARNING: '
		elif(logLevel == LOG_LEVEL_ERROR):
			prefix = 'IARL_ERROR: '
						
		try:
			print prefix + message
		except:
			pass
		
	
	@staticmethod
	def getCurrentLogLevel():
		logLevel = 1
		try:
			settings = getSettings()
			logLevelStr = settings.getSetting(SETTING_IARL_LOGLEVEL)
			if(logLevelStr == 'ERROR'):
				logLevel = LOG_LEVEL_ERROR
			elif(logLevelStr == 'WARNING'):
				logLevel = LOG_LEVEL_WARNING
			elif(logLevelStr == 'INFO'):
				logLevel = LOG_LEVEL_INFO
			elif(logLevelStr == 'DEBUG'):
				logLevel = LOG_LEVEL_DEBUG
		except:
			pass
		return logLevel