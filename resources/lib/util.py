import os, sys, re, shutil, json, zipfile, subprocess
# import os.path
import xbmc, xbmcaddon, xbmcvfs
from xbmcswift2 import xbmcgui
# import time
from descriptionparserfactory import *

#
# CONSTANTS AND GLOBALS #
#

iarl_plugin_name = 'plugin.program.iarl'
debugging_enabled = True
LOG_LEVEL_INFO = 'LOG_LEVEL_INFO'

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
	elif 'win64' in sys.platform:
		current_OS = 'Windows'
	elif 'linux' in sys.platform:
		if 'XBMC_ANDROID_APK' in os.environ.keys():
			current_OS = 'Android' #Similar method to find android as done below for IOS
		elif os.path.exists('/etc/os-release'):
				try:
					with open('/etc/os-release', 'r') as content_file:
						os_content_file = content_file.read().replace('\n', '')
					if 'OpenELEC'.lower() in os_content_file.lower():
						current_OS = 'OpenElec' #Best method I could find to determine if its OE
				except:
					current_OS = 'Nix'
		else:
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

def update_addonxml(option):

	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Are you sure you want to update this setting?', ['No','Yes'])

	if ret1 == 0:
		pass
	else:
		ok_ret = current_dialog.ok('Complete','The addon was updated.[CR]You may have to restart Kodi for the settings to take effect.')
		update_xml_header(getAddonInstallPath(),'/addon.xml','provides',option)
		print 'IARL:  Addon provides was updated to ' + option

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

def check_if_rom_exits(current_save_fname,current_path):
	
	file_already_exists = False
	do_not_download_flag = False
	fname_found = None

	file_basename = os.path.basename(current_save_fname)
	file_basename_no_ext = os.path.splitext(file_basename)

	files_in_current_path = []
	for (dp, dn, ff) in os.walk(current_path):
		files_in_current_path.extend(ff)

	if len(files_in_current_path)>0:
		for check_f in files_in_current_path:
			if file_basename_no_ext[0] in check_f:
				file_already_exists = True
				fname_found = check_f
				print fname_found + ' already exists in the directory'

	if file_already_exists:
		current_dialog = xbmcgui.Dialog()
		ret1 = current_dialog.select('The ROM already appears to exist.[CR]Re-Download and overwrite?', ['No','Yes'])

		if ret1 == 0:
			do_not_download_flag = True
		else:
			pass

	return fname_found, do_not_download_flag

def check_for_warn(current_filename):
	file_extension = current_filename.split('.')[-1]
	chd_warn = False
	iso_warn = False

	if 'chd' in file_extension.lower():
		chd_warn = True
	if 'img' in file_extension.lower():
		iso_warn = True
	if 'img' in file_extension.lower():
		iso_warn = True

	if 'true' in __addon__.getSetting(id='iarl_setting_warn_chd').lower():
		print __addon__.getSetting(id='iarl_setting_warn_chd')
		if chd_warn:
			current_dialog = xbmcgui.Dialog()
			ret1 = current_dialog.yesno('Warning','Warning:  This ROM is in CHD Format[CR]It will have to be converted prior to use[CR]These files are also typically large[CR]Check addon settings and wiki for more info',nolabel='OK',yeslabel='OK! Stop showing this!')
			print ret1
			if ret1>0:
				__addon__.setSetting(id='iarl_setting_warn_chd',value='false') #No longer show the warning

	if 'true' in __addon__.getSetting(id='iarl_setting_warn_iso').lower():
		if iso_warn:
			current_dialog = xbmcgui.Dialog()
			ret1 = current_dialog.yesno('Warning','Warning:  This ROM is in ISO/IMG Format[CR]These files are also typically large!',nolabel='OK',yeslabel='OK! Stop showing this!')
			print ret1
			if ret1>0:
				__addon__.setSetting(id='iarl_setting_warn_iso',value='false') #No longer show the warning


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

def advanced_setting_action_clear_cache(plugin):
	plugin.clear_function_cache()
	__addon__.setSetting(id='iarl_setting_clear_cache_value',value='false') #Set back to false, no need to clear it next run
	print 'IARL:  Advanced Setting Cache Clear Completed'

def update_external_launch_commands(current_os,retroarch_path,xml_id,plugin):

	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0] + '/'

	parserfile = getParserFilePath('external_launcher_parser.xml')
	launchersfile = getParserFilePath('external_command_database.xml')
	# helper_script_1 = os.path.join(getAddonInstallPath(),'resources/bin/applaunch.sh')
	# helper_script_2 = os.path.join(getAddonInstallPath(),'resources/bin/romlaunch_OE.sh')
	# helper_script_3 = os.path.join(getAddonInstallPath(),'resources/bin/applaunch-vbs.bat')

	descParser = DescriptionParserFactory.getParser(parserfile)
	results = descParser.parseDescription(launchersfile,'xml')
	user_options = list()
	launch_command = list()
	new_launch_command = None
	current_path = None

	if current_os == 'OSX':
		current_path = retroarch_path.split('.app')[0]+'.app' #Make App Path for OSX only up to the container
	elif current_os == 'Windows':
		current_path = os.path.split(retroarch_path)
		current_path = current_path[0]

	if current_path is not None: #Update %APP_PATH%
		retroarch_path = current_path

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
			# new_launch_command = new_launch_command.replace('%HELPER_SCRIPT_1%',helper_script_1) #Quick and dirty for now, may make this more efficient later
			# new_launch_command = new_launch_command.replace('%HELPER_SCRIPT_2%',helper_script_2)
			# new_launch_command = new_launch_command.replace('%HELPER_SCRIPT_3%',helper_script_3)
			new_launch_command = new_launch_command.replace('%ADDON_DIR%',getAddonInstallPath()) #Replace helper script with the more generic ADDON_DIR
			update_xml_header(current_xml_path,current_xml_filename,'emu_ext_launch_cmd',new_launch_command)
			ok_ret = current_dialog.ok('Complete','External Launch Command was updated[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()

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

	if '32X' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','32x')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','32x_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','32x_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','32x_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'Nintendo Entertainment System - NES' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','NES')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','NES_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','white.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','nes_dark_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'Super Nintendo Entertainment System - SNES' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','SNES')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','SNES_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','white.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','nes_dark_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'Genesis' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','Genesis')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','genesis_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','sega_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','sega_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'Game Gear' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','Game Gear')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','genesis_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','sega_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','sega_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'Master System' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','Master System')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','genesis_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','white.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','sega_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'N64' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','N64')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','N64_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','n64_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','n64_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'MAME' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','MAME')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','arcade_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','arcade_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','arcade_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif '2600' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','2600')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','arcade_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','atari_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','atari_bg.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'Jaguar' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','Jaguar')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','arcade_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','jaguar_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','black.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'Lynx' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','Lynx')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','arcade_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','lynx_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','black.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme','button-highlight1.png')
		xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme','button-nofocus2.png')
	elif 'TurboGrafx' in emu_name:
		xbmcgui.Window(10000).setProperty('iarl.current_theme','TurboGrafx')
		xbmcgui.Window(10000).setProperty('iarl.default_thumb','arcade_default_box.jpg')
		xbmcgui.Window(10000).setProperty('iarl.header_color','tg16_head.png')
		xbmcgui.Window(10000).setProperty('iarl.bg_color','tg16_bg.png')
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
	iarl_setting_naming = plugin.get_setting('iarl_setting_naming',unicode)

	items = []
	current_item = []
	idx = 0
	total_arts = 10
	replacement_h = re.compile(r'\([^)]*\)')

	for entries in results:
		idx += 1

		current_name = []
		if entries['rom_name']:
			current_name = entries['rom_name'][0]
			try:
				current_rom_tag = replacement_h.search(current_name).group(0).replace('(','').replace(')','').strip()
			except:
				current_rom_tag = None

			if cleanlist:
				current_name = replacement_h.sub('', current_name).strip()
		else:
			current_name = None
			current_rom_tag = None

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
		try:
			if entries['rom_supporting_file'][0]:
				current_sfname = xml_header_info['emu_baseurl'][0]+str(entries['rom_supporting_file'][0])
				current_sfname = html_unescape(current_sfname)
			else:
				current_sfname = None
		except:
			current_sfname = None

		current_save_sfname = []
		try:
			if entries['rom_supporting_file'][0]:
				current_save_sfname = str(entries['rom_supporting_file'][0])
				current_save_sfname = html_unescape(current_save_sfname)
			else:
				current_save_sfname = None
		except:
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

		try:
			if entries['rom_size']:
				current_filesize = sum(map(int,entries['rom_size'])) #Sum all the rom_sizes for the current entry.  This may not be accurate for zips, but better than ???
			else:
				current_filesize = None
		except:
			current_filesize = None

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

		if entries['rom_emu_command']:
			current_rom_emu_command = entries['rom_emu_command'][0]
		else:
			current_rom_emu_command = None

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

		label_sep = '  |  '
		xstr = lambda s: s or ''

		if iarl_setting_naming == 'Title':
			current_label = xstr(current_name)
		elif iarl_setting_naming == 'Title, Genre':
			current_label = xstr(current_name) + label_sep + xstr(current_genre)
		elif iarl_setting_naming == 'Title, Date':
			current_label = xstr(current_name) + label_sep + current_date
		elif iarl_setting_naming == 'Title, Genre, Date':
			current_label = xstr(current_name) + label_sep + xstr(current_genre) + label_sep + xstr(current_date)
		elif iarl_setting_naming == 'Genre, Title':
			current_label = xstr(current_genre) + label_sep + xstr(current_name)
		elif iarl_setting_naming == 'Date, Title':
			current_label = xstr(current_date) + label_sep + xstr(current_name)
		elif iarl_setting_naming == 'Genre, Title, Date':
			current_label = xstr(current_genre) + label_sep + xstr(current_name) + label_sep + xstr(current_date)
		elif iarl_setting_naming == 'Date, Title, Genre':
			current_label = xstr(current_date) + label_sep + xstr(current_name) + label_sep + xstr(current_genre)
		elif iarl_setting_naming == 'Title, Genre, Date, ROM Tag':
			current_label = xstr(current_name) + label_sep + xstr(current_genre) + label_sep + xstr(current_date) + label_sep + xstr(current_rom_tag)
		else:
			current_label = xstr(current_name)

		current_item = []
		current_item = { 
        'label' : current_label, 'icon': current_icon2,
        'thumbnail' : current_thumbnail2,
        'path' : plugin.url_for('get_selected_rom', romname=entries['rom_name'][0]),
        'info' : {'title' : current_name, 'genre': current_genre, 'studio': current_credits, 'date': current_date, 'plot': current_plot, 'trailer': current_trailer, 'size': current_filesize},
        'properties' : {'fanart_image' : current_fanart[0], 'banner' : current_banner[0], 'clearlogo': current_clearlogo[0], 'poster': current_thumbnail[1], 'rom_tag': current_rom_tag,
        'fanart1': current_fanart[0], 'fanart2': current_fanart[1], 'fanart3': current_fanart[2], 'fanart4': current_fanart[3], 'fanart5': current_fanart[4], 'fanart6': current_fanart[5], 'fanart7': current_fanart[6], 'fanart8': current_fanart[7], 'fanart9': current_fanart[8], 'fanart10': current_fanart[9],
        'banner1': current_banner[0], 'banner2': current_banner[1], 'banner3': current_banner[2], 'banner4': current_banner[3], 'banner5': current_banner[4], 'banner6': current_banner[5], 'banner7': current_banner[6], 'banner8': current_banner[7], 'banner9': current_banner[8], 'banner10': current_banner[9],
        'snapshot1': current_snapshot[0], 'snapshot2': current_snapshot[1], 'snapshot3': current_snapshot[2], 'snapshot4': current_snapshot[3], 'snapshot5': current_snapshot[4], 'snapshot6': current_snapshot[5], 'snapshot7': current_snapshot[6], 'snapshot8': current_snapshot[7], 'snapshot9': current_snapshot[8], 'snapshot10': current_snapshot[9],
        'boxart1': current_thumbnail[0], 'boxart2': current_thumbnail[1], 'boxart3': current_thumbnail[2], 'boxart4': current_thumbnail[3], 'boxart5': current_thumbnail[4], 'boxart6': current_thumbnail[5], 'boxart7': current_thumbnail[6], 'boxart8': current_thumbnail[7], 'boxart9': current_thumbnail[8], 'boxart10': current_thumbnail[9],
        'nplayers': current_nplayers, 'emu_logo': current_emu_logo, 'emu_fanart': current_emu_fanart, 'emu_name': current_emu_name, 'rom_fname': current_fname, 'rom_sfname': current_sfname, 'rom_save_fname': current_save_fname, 'rom_save_sfname': current_save_sfname,
        'emu_downloadpath': current_emu_downloadpath, 'emu_postdlaction': current_emu_postdlaction, 'emu_launcher': current_emu_launcher, 'emu_ext_launch_cmd': current_emu_ext_launch_cmd, 'rom_emu_command': current_rom_emu_command},
        'context_menu': None}
		
		items.append(current_item)

	return items

#HACK: XBMC does not update labels with empty strings
def getLabel(control):
	label = control.getLabel()
	if(label == ' '):
		label = ''
		
	return label

def size_to_bytes(size_str):
	conversion = {'K' : 1024,
                  'M' : 1048576,
                  'G' : 1073741824,}

	try:
	    RE_GMK = ('(\w[GMK]?)B')
	    RE_DIGIT = ('(\d*\.?\d*)')
	    re_obj_gmk = re.compile(RE_GMK)
	    re_obj_digit = re.compile(RE_DIGIT)
	    gmk = re_obj_gmk.search(size_str)
	    unit = 1
	    if gmk:
	        unit = conversion[gmk.groups()[0]]
	    digit = re_obj_digit.search(size_str)
	    if digit:
	        size = int((float(digit.groups()[0]) * unit)) #Removed math function, no need to import for a byte difference
	    else:
	        size = 0
	except:
		size = None

	return size


def query_favorites_xml():
	favorites_xml_filename = None
	emu_info = scape_xml_headers() #Find all xml dat files and get the header info
	favorite_xmls = dict()
	favorite_xmls['emu_name'] = list()
	favorite_xmls['emu_location'] = list()

	for ii in range(0,len(emu_info['emu_name'])):
		if 'IARL_Favorites'.lower() in emu_info['emu_description'][ii].lower():
			favorite_xmls['emu_name'].append(emu_info['emu_name'][ii])
			favorite_xmls['emu_location'].append(emu_info['emu_location'][ii])

	favorite_xmls['emu_name'].append('+ Create New Favorites List')
	favorite_xmls['emu_name'].append('Cancel')
	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Choose Favorites List',favorite_xmls['emu_name'])

	if favorite_xmls['emu_name'][ret1] == favorite_xmls['emu_name'][-2]: #Create new list
		ret2 = current_dialog.input('Enter Favorites Label')
		if len(ret2)>0:
			saved_filename = create_new_favorites_list(''.join([x if x.isalnum() else "_" for x in ret2])) #Pass filename safe string to create favorites xml
			if saved_filename is not None:
				current_xml_fileparts = os.path.split(saved_filename)
				current_xml_filename = current_xml_fileparts[1]
				current_xml_path = current_xml_fileparts[0] + '/'
				update_xml_header(current_xml_path,current_xml_filename,'emu_name',ret2)
				favorites_xml_filename = saved_filename
	elif favorite_xmls['emu_name'][ret1] == favorite_xmls['emu_name'][-1]: #Cancel adding favorite
		print 'IARL:  Adding Favorite Cancelled'
		favorites_xml_filename = None
	else:
		favorites_xml_filename = favorite_xmls['emu_location'][ret1]

	return favorites_xml_filename

def create_new_favorites_list(new_filename):
	saved_filename = None
	template_path = getParserFilePath('Favorites_Template.xml')
	dat_path = getDATFilePath()
	new_xml_filename = os.path.join(dat_path,new_filename+'.xml')
	copyFile(template_path, new_xml_filename)
	if os.path.exists(new_xml_filename):
		saved_filename = new_xml_filename
	return saved_filename

def add_favorite_to_xml(fav_item,favorites_xml_filename):
	add_success = False
	xml_string = ''
	current_rom_command = ''
	strip_base_url_string_1 = 'http://archive.org/download/'
	strip_base_url_string_2 = 'https://archive.org/download/'
	xstr = lambda s: s or ''
	try: current_rom_command = current_rom_command+xstr(fav_item['properties']['emu_postdlaction'])
	except: pass
	try: current_rom_command = current_rom_command+'|'+xstr(fav_item['properties']['rom_emu_command'])
	except: pass
	if current_rom_command[0] == '|':
		current_rom_command = current_rom_command[1:]
	if current_rom_command[-1] == '|':
		current_rom_command = current_rom_command[:-1]

	try: xml_string = xml_string+'<game name="%GAME_TITLE%">\r\n'.replace('%GAME_TITLE%',fav_item['info']['title'])
	except: pass
	try: xml_string = xml_string+'<description>%GAME_TITLE%</description>\r\n'.replace('%GAME_TITLE%',fav_item['info']['title'])
	except: pass
	try: xml_string = xml_string+'<rom name="%ROM_URL%" size="%ROM_SIZE%"/>\r\n'.replace('%ROM_URL%',fav_item['properties']['rom_fname'].replace(strip_base_url_string_1,'').replace(strip_base_url_string_2,'')).replace('%ROM_SIZE%',str(fav_item['info']['size']))
	except: pass
	try: xml_string = xml_string+'<plot>%GAME_PLOT%</plot>\r\n'.replace('%GAME_PLOT%',xstr(fav_item['info']['plot']))
	except: pass
	try: xml_string = xml_string+'<releasedate>%GAME_DATE%</releasedate>\r\n'.replace('%GAME_DATE%',xstr(fav_item['info']['date']))
	except: pass
	try: xml_string = xml_string+'<genre>%GAME_GENRE%</genre>\r\n'.replace('%GAME_GENRE%',xstr(fav_item['info']['genre']))
	except: pass
	try: xml_string = xml_string+'<studio>%GAME_STUDIO%</studio>\r\n'.replace('%GAME_STUDIO%',xstr(fav_item['info']['studio']))
	except: pass
	try: xml_string = xml_string+'<nplayers>%GAME_NPLAYERS%</nplayers>\r\n'.replace('%GAME_NPLAYERS%',xstr(fav_item['properties']['nplayers']))
	except: pass
	try: xml_string = xml_string+'<videoid>%GAME_VIDEOID%</videoid>\r\n'.replace('%GAME_VIDEOID%',xstr(fav_item['info']['trailer']).split('=')[-1]) #Only add the video ID
	except: pass
	try: xml_string = xml_string+'<boxart1>%GAME_boxart1%</boxart1>\r\n'.replace('%GAME_boxart1%',xstr(fav_item['properties']['boxart1']))
	except: pass
	try: xml_string = xml_string+'<boxart2>%GAME_boxart2%</boxart2>\r\n'.replace('%GAME_boxart2%',xstr(fav_item['properties']['boxart2']))
	except: pass
	try: xml_string = xml_string+'<boxart3>%GAME_boxart3%</boxart3>\r\n'.replace('%GAME_boxart3%',xstr(fav_item['properties']['boxart3']))
	except: pass
	try: xml_string = xml_string+'<boxart4>%GAME_boxart4%</boxart4>\r\n'.replace('%GAME_boxart4%',xstr(fav_item['properties']['boxart4']))
	except: pass
	try: xml_string = xml_string+'<boxart5>%GAME_boxart5%</boxart5>\r\n'.replace('%GAME_boxart5%',xstr(fav_item['properties']['boxart5']))
	except: pass
	try: xml_string = xml_string+'<boxart6>%GAME_boxart6%</boxart6>\r\n'.replace('%GAME_boxart6%',xstr(fav_item['properties']['boxart6']))
	except: pass
	try: xml_string = xml_string+'<boxart7>%GAME_boxart7%</boxart7>\r\n'.replace('%GAME_boxart7%',xstr(fav_item['properties']['boxart7']))
	except: pass
	try: xml_string = xml_string+'<boxart8>%GAME_boxart8%</boxart8>\r\n'.replace('%GAME_boxart8%',xstr(fav_item['properties']['boxart8']))
	except: pass
	try: xml_string = xml_string+'<boxart9>%GAME_boxart9%</boxart9>\r\n'.replace('%GAME_boxart9%',xstr(fav_item['properties']['boxart9']))
	except: pass
	try: xml_string = xml_string+'<boxart10>%GAME_boxart10%</boxart10>\r\n'.replace('%GAME_boxart10%',xstr(fav_item['properties']['boxart10']))
	except: pass
	try: xml_string = xml_string+'<snapshot1>%GAME_snapshot1%</snapshot1>\r\n'.replace('%GAME_snapshot1%',xstr(fav_item['properties']['snapshot1']))
	except: pass
	try: xml_string = xml_string+'<snapshot2>%GAME_snapshot2%</snapshot2>\r\n'.replace('%GAME_snapshot2%',xstr(fav_item['properties']['snapshot2']))
	except: pass
	try: xml_string = xml_string+'<snapshot3>%GAME_snapshot3%</snapshot3>\r\n'.replace('%GAME_snapshot3%',xstr(fav_item['properties']['snapshot3']))
	except: pass
	try: xml_string = xml_string+'<snapshot4>%GAME_snapshot4%</snapshot4>\r\n'.replace('%GAME_snapshot4%',xstr(fav_item['properties']['snapshot4']))
	except: pass
	try: xml_string = xml_string+'<snapshot5>%GAME_snapshot5%</snapshot5>\r\n'.replace('%GAME_snapshot5%',xstr(fav_item['properties']['snapshot5']))
	except: pass
	try: xml_string = xml_string+'<snapshot6>%GAME_snapshot6%</snapshot6>\r\n'.replace('%GAME_snapshot6%',xstr(fav_item['properties']['snapshot6']))
	except: pass
	try: xml_string = xml_string+'<snapshot7>%GAME_snapshot7%</snapshot7>\r\n'.replace('%GAME_snapshot7%',xstr(fav_item['properties']['snapshot7']))
	except: pass
	try: xml_string = xml_string+'<snapshot8>%GAME_snapshot8%</snapshot8>\r\n'.replace('%GAME_snapshot8%',xstr(fav_item['properties']['snapshot8']))
	except: pass
	try: xml_string = xml_string+'<snapshot9>%GAME_snapshot9%</snapshot9>\r\n'.replace('%GAME_snapshot9%',xstr(fav_item['properties']['snapshot9']))
	except: pass
	try: xml_string = xml_string+'<snapshot10>%GAME_snapshot10%</snapshot10>\r\n'.replace('%GAME_snapshot10%',xstr(fav_item['properties']['snapshot10']))
	except: pass
	try: xml_string = xml_string+'<fanart1>%GAME_fanart1%</fanart1>\r\n'.replace('%GAME_fanart1%',xstr(fav_item['properties']['fanart1']))
	except: pass
	try: xml_string = xml_string+'<fanart2>%GAME_fanart2%</fanart2>\r\n'.replace('%GAME_fanart2%',xstr(fav_item['properties']['fanart2']))
	except: pass
	try: xml_string = xml_string+'<fanart3>%GAME_fanart3%</fanart3>\r\n'.replace('%GAME_fanart3%',xstr(fav_item['properties']['fanart3']))
	except: pass
	try: xml_string = xml_string+'<fanart4>%GAME_fanart4%</fanart4>\r\n'.replace('%GAME_fanart4%',xstr(fav_item['properties']['fanart4']))
	except: pass
	try: xml_string = xml_string+'<fanart5>%GAME_fanart5%</fanart5>\r\n'.replace('%GAME_fanart5%',xstr(fav_item['properties']['fanart5']))
	except: pass
	try: xml_string = xml_string+'<fanart6>%GAME_fanart6%</fanart6>\r\n'.replace('%GAME_fanart6%',xstr(fav_item['properties']['fanart6']))
	except: pass
	try: xml_string = xml_string+'<fanart7>%GAME_fanart7%</fanart7>\r\n'.replace('%GAME_fanart7%',xstr(fav_item['properties']['fanart7']))
	except: pass
	try: xml_string = xml_string+'<fanart8>%GAME_fanart8%</fanart8>\r\n'.replace('%GAME_fanart8%',xstr(fav_item['properties']['fanart8']))
	except: pass
	try: xml_string = xml_string+'<fanart9>%GAME_fanart9%</fanart9>\r\n'.replace('%GAME_fanart9%',xstr(fav_item['properties']['fanart9']))
	except: pass
	try: xml_string = xml_string+'<fanart10>%GAME_fanart10%</fanart10>\r\n'.replace('%GAME_fanart10%',xstr(fav_item['properties']['fanart10']))
	except: pass
	try: xml_string = xml_string+'<banner1>%GAME_banner1%</banner1>\r\n'.replace('%GAME_banner1%',xstr(fav_item['properties']['banner1']))
	except: pass
	try: xml_string = xml_string+'<banner2>%GAME_banner2%</banner2>\r\n'.replace('%GAME_banner2%',xstr(fav_item['properties']['banner2']))
	except: pass
	try: xml_string = xml_string+'<banner3>%GAME_banner3%</banner3>\r\n'.replace('%GAME_banner3%',xstr(fav_item['properties']['banner3']))
	except: pass
	try: xml_string = xml_string+'<banner4>%GAME_banner4%</banner4>\r\n'.replace('%GAME_banner4%',xstr(fav_item['properties']['banner4']))
	except: pass
	try: xml_string = xml_string+'<banner5>%GAME_banner5%</banner5>\r\n'.replace('%GAME_banner5%',xstr(fav_item['properties']['banner5']))
	except: pass
	try: xml_string = xml_string+'<banner6>%GAME_banner6%</banner6>\r\n'.replace('%GAME_banner6%',xstr(fav_item['properties']['banner6']))
	except: pass
	try: xml_string = xml_string+'<banner7>%GAME_banner7%</banner7>\r\n'.replace('%GAME_banner7%',xstr(fav_item['properties']['banner7']))
	except: pass
	try: xml_string = xml_string+'<banner8>%GAME_banner8%</banner8>\r\n'.replace('%GAME_banner8%',xstr(fav_item['properties']['banner8']))
	except: pass
	try: xml_string = xml_string+'<banner9>%GAME_banner9%</banner9>\r\n'.replace('%GAME_banner9%',xstr(fav_item['properties']['banner9']))
	except: pass
	try: xml_string = xml_string+'<banner10>%GAME_banner10%</banner10>\r\n'.replace('%GAME_banner10%',xstr(fav_item['properties']['banner10']))
	except: pass
	try: xml_string = xml_string+'<clearlogo1>%GAME_clearlogo1%</clearlogo1>\r\n'.replace('%GAME_clearlogo1%',xstr(fav_item['properties']['clearlogo1']))
	except: pass
	try: xml_string = xml_string+'<clearlogo2>%GAME_clearlogo2%</clearlogo2>\r\n'.replace('%GAME_clearlogo2%',xstr(fav_item['properties']['clearlogo2']))
	except: pass
	try: xml_string = xml_string+'<clearlogo3>%GAME_clearlogo3%</clearlogo3>\r\n'.replace('%GAME_clearlogo3%',xstr(fav_item['properties']['clearlogo3']))
	except: pass
	try: xml_string = xml_string+'<clearlogo4>%GAME_clearlogo4%</clearlogo4>\r\n'.replace('%GAME_clearlogo4%',xstr(fav_item['properties']['clearlogo4']))
	except: pass
	try: xml_string = xml_string+'<clearlogo5>%GAME_clearlogo5%</clearlogo5>\r\n'.replace('%GAME_clearlogo5%',xstr(fav_item['properties']['clearlogo5']))
	except: pass
	try: xml_string = xml_string+'<clearlogo6>%GAME_clearlogo6%</clearlogo6>\r\n'.replace('%GAME_clearlogo6%',xstr(fav_item['properties']['clearlogo6']))
	except: pass
	try: xml_string = xml_string+'<clearlogo7>%GAME_clearlogo7%</clearlogo7>\r\n'.replace('%GAME_clearlogo7%',xstr(fav_item['properties']['clearlogo7']))
	except: pass
	try: xml_string = xml_string+'<clearlogo8>%GAME_clearlogo8%</clearlogo8>\r\n'.replace('%GAME_clearlogo8%',xstr(fav_item['properties']['clearlogo8']))
	except: pass
	try: xml_string = xml_string+'<clearlogo9>%GAME_clearlogo9%</clearlogo9>\r\n'.replace('%GAME_clearlogo9%',xstr(fav_item['properties']['clearlogo9']))
	except: pass
	try: xml_string = xml_string+'<clearlogo10>%GAME_clearlogo10%</clearlogo10>\r\n'.replace('%GAME_clearlogo10%',xstr(fav_item['properties']['clearlogo10']))
	except: pass
	try: xml_string = xml_string+'<emu_command>%GAME_COMMAND%</emu_command>\r\n'.replace('%GAME_COMMAND%',current_rom_command)
	except: pass
	try: xml_string = xml_string+'</game>\r\n'
	except: pass

	xml_string = xml_string.replace('<plot></plot>','').replace('<releasedate></releasedate>','').replace('<studio></studio>','').replace('<nplayers></nplayers>','').replace('<videoid></videoid>','').replace('<genre></genre>','')
	xml_string = xml_string.replace('<boxart1></boxart1>','').replace('<boxart2></boxart2>','').replace('<boxart3></boxart3>','').replace('<boxart4></boxart4>','').replace('<boxart5></boxart5>','').replace('<boxart6></boxart6>','').replace('<boxart7></boxart7>','').replace('<boxart8></boxart8>','').replace('<boxart9></boxart9>','').replace('<boxart10></boxart10>','')
	xml_string = xml_string.replace('<snapshot1></snapshot1>','').replace('<snapshot2></snapshot2>','').replace('<snapshot3></snapshot3>','').replace('<snapshot4></snapshot4>','').replace('<snapshot5></snapshot5>','').replace('<snapshot6></snapshot6>','').replace('<snapshot7></snapshot7>','').replace('<snapshot8></snapshot8>','').replace('<snapshot9></snapshot9>','').replace('<snapshot10></snapshot10>','')
	xml_string = xml_string.replace('<fanart1></fanart1>','').replace('<fanart2></fanart2>','').replace('<fanart3></fanart3>','').replace('<fanart4></fanart4>','').replace('<fanart5></fanart5>','').replace('<fanart6></fanart6>','').replace('<fanart7></fanart7>','').replace('<fanart8></fanart8>','').replace('<fanart9></fanart9>','').replace('<fanart10></fanart10>','')
	xml_string = xml_string.replace('<banner1></banner1>','').replace('<banner2></banner2>','').replace('<banner3></banner3>','').replace('<banner4></banner4>','').replace('<banner5></banner5>','').replace('<banner6></banner6>','').replace('<banner7></banner7>','').replace('<banner8></banner8>','').replace('<banner9></banner9>','').replace('<banner10></banner10>','')
	xml_string = xml_string.replace('<clearlogo1></clearlogo1>','').replace('<clearlogo2></clearlogo2>','').replace('<clearlogo3></clearlogo3>','').replace('<clearlogo4></clearlogo4>','').replace('<clearlogo5></clearlogo5>','').replace('<clearlogo6></clearlogo6>','').replace('<clearlogo7></clearlogo7>','').replace('<clearlogo8></clearlogo8>','').replace('<clearlogo9></clearlogo9>','').replace('<clearlogo10></clearlogo10>','')
	xml_string = xml_string.replace('\r\n\r\n','')

	full_reg_exp = '</datafile>' #Look for this
	fout = open(os.path.join(getDATFilePath(),'temp.xml'), 'w') # out file
	value_updated = False

	with open(favorites_xml_filename, 'rU') as fin:
		while True:
			line = fin.readline()
			if not value_updated:  #Only update the first instance of the requested tag
				if full_reg_exp in line:
					try:
						my_new_line = xml_string+full_reg_exp
						fout.write(my_new_line)
					except:
						fout.write(full_reg_exp)
					value_updated = True				
				else:
					fout.write(line)
			else:
				fout.write(line)
			if not line:
				break
				pass

	fout.close()

	if value_updated:
		os.remove(favorites_xml_filename) #Remove Old File
		os.rename(os.path.join(getDATFilePath(),'temp.xml'),favorites_xml_filename) #Rename Temp File
		add_success = True

	return add_success

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


def update_xml_header(current_path,current_filename,reg_exp,new_value):
	full_reg_exp = '</'+reg_exp+'>' #Look for this
	fout = open(current_path+'temp.xml', 'w') # out file
	full_new_val = '<'+reg_exp+'>'+new_value+'</'+reg_exp+'>' #replacement value

	value_updated = False

	with open(current_path+current_filename, 'rU') as fin:
		while True:
			line = fin.readline()
			if not value_updated:  #Only update the first instance of the requested tag
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
			z_file.close()
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
	else:
		new_fname = current_fname #Didn't unzip or didn't find a file extension


	return zip_success, new_fname

def unzip_dosbox_file(current_fname,current_rom_emu_command):
	zip_success = False
	new_fname = None

	if zipfile.is_zipfile(current_fname):
		try:
			current_zip_fileparts = os.path.split(current_fname)
			current_zip_path = current_zip_fileparts[0] + '/'
			z_file = zipfile.ZipFile(current_fname)
			# uz_file_extension = os.path.splitext(z_file.namelist()[0])[1] #Get rom extension
			z_file.extractall(current_zip_path)
			zip_success = True
			z_file.close()
			print 'Unzip Successful'
		except:
			zip_success = False
			print 'Unzip Failed'

		if zip_success:
			os.remove(current_fname)
	else:
		print current_fname + ' was not regognized as a zipfile and not extracted'

	if current_rom_emu_command: #The file was unzipped, change from zip to rom extension
		try:
			new_fname = current_zip_path+current_rom_emu_command
		except:
			new_fname = current_fname #Didn't unzip or didn't find a file extension
	else:
		new_fname = current_fname #Didn't unzip or didn't find a file extension


	return zip_success, new_fname

def convert_chd_bin(current_fname,iarl_setting_chdman_path):
	chd_success = False
	new_file_extension = None
	new_fname = None
	current_dialog = xbmcgui.Dialog()

	if iarl_setting_chdman_path is None: #Check if there's a CHDMAN available
		ok_ret = current_dialog.ok('Error','No CHDMAN path appears to be set in your addon settings.')
		return chd_success, new_fname

	current_dialog.notification('Please Wait', 'Just a moment, converting CHD to BIN/CUE', xbmcgui.NOTIFICATION_INFO, 500000)

	current_chd_fileparts = os.path.split(current_fname)
	file_path = current_chd_fileparts[0]
	file_extension = current_chd_fileparts[-1]
	file_base_name = os.path.splitext(os.path.split(current_fname)[-1])[0]

	if 'chd' in file_extension.lower():
		# try:
		output_cue = os.path.join(file_path,file_base_name+'.cue')
		output_bin = os.path.join(file_path,file_base_name+'.bin')
		command = '"%CHD_APP_PATH%" extractcd -i "%INPUT_CHD%" -o "%OUTPUT_CUE%" -ob "%OUTPUT_BIN%"' #May need to provide other OS options here
		command = command.replace('%CHD_APP_PATH%',iarl_setting_chdman_path)
		command = command.replace("%INPUT_CHD%",current_fname)
		command = command.replace("%OUTPUT_CUE%",output_cue)
		command = command.replace("%OUTPUT_BIN%",output_bin)
		print 'IARL:  Attempting CHD Conversion: '+command
		failed_text = 'Unhandled exception'
		already_exists_text = 'file already exists'
		success_text = 'Extraction complete'
		conversion_process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) #Convert CHD to BIN/CUE
		results1 = conversion_process.stdout.read().replace('\n', '')
		conversion_process.kill() #End the process after its completed

		if success_text.lower() in results1.lower():
			print 'IARL:  CHD Conversion Successful'
			new_fname = output_bin
			chd_success = True
		elif already_exists_text.lower() in results1.lower():
			print 'IARL:  BIN File already exists, conversion not required'
			new_fname = output_bin
			chd_success = True
		elif failed_text.lower() in results1.lower():
			chd_success = False
			print 'IARL:  CHD Conversion Failed'
			print results1
		else:
			chd_success = False
			print 'IARL:  CHD Conversion Failed'
		# except:
		# 	chd_success = False
		# 	print 'IARL:  CHD Conversion Failed'

		if chd_success:
			os.remove(current_fname) #Delete the CHD and leave the new BIN/CUE if the conversion was a success
			current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		else:
			current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
	else:
		print current_fname + ' was not regognized as a chd and not converted'

	# current_dialog.close()
	return chd_success, new_fname

def convert_chd_cue(current_fname,iarl_setting_chdman_path):
	#Quick and dirty to point to cue if needed, may fix later
	chd_success = False
	new_file_extension = None
	new_fname = None
	current_dialog = xbmcgui.Dialog()

	if iarl_setting_chdman_path is None: #Check if there's a CHDMAN available
		ok_ret = current_dialog.ok('Error','No CHDMAN path appears to be set in your addon settings.')
		return chd_success, new_fname

	current_dialog.notification('Please Wait', 'Just a moment, converting CHD to BIN/CUE', xbmcgui.NOTIFICATION_INFO, 500000)

	current_chd_fileparts = os.path.split(current_fname)
	file_path = current_chd_fileparts[0]
	file_extension = current_chd_fileparts[-1]
	file_base_name = os.path.splitext(os.path.split(current_fname)[-1])[0]

	if 'chd' in file_extension.lower():
		# try:
		output_cue = os.path.join(file_path,file_base_name+'.cue')
		output_bin = os.path.join(file_path,file_base_name+'.bin')
		command = '"%CHD_APP_PATH%" extractcd -i "%INPUT_CHD%" -o "%OUTPUT_CUE%" -ob "%OUTPUT_BIN%"' #May need to provide other OS options here
		command = command.replace('%CHD_APP_PATH%',iarl_setting_chdman_path)
		command = command.replace("%INPUT_CHD%",current_fname)
		command = command.replace("%OUTPUT_CUE%",output_cue)
		command = command.replace("%OUTPUT_BIN%",output_bin)
		print 'IARL:  Attempting CHD Conversion: '+command
		failed_text = 'Unhandled exception'
		already_exists_text = 'file already exists'
		success_text = 'Extraction complete'
		conversion_process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) #Convert CHD to BIN/CUE
		results1 = conversion_process.stdout.read().replace('\n', '')
		conversion_process.kill() #End the process after its completed

		if success_text.lower() in results1.lower():
			print 'IARL:  CHD Conversion Successful'
			new_fname = output_cue
			chd_success = True
		elif already_exists_text.lower() in results1.lower():
			print 'IARL:  CUE File already exists, conversion not required'
			new_fname = output_cue
			chd_success = True
		elif failed_text.lower() in results1.lower():
			chd_success = False
			print 'IARL:  CHD Conversion Failed'
			print results1
		else:
			chd_success = False
			print 'IARL:  CHD Conversion Failed'
		# except:
		# 	chd_success = False
		# 	print 'IARL:  CHD Conversion Failed'

		if chd_success:
			os.remove(current_fname) #Delete the CHD and leave the new BIN/CUE if the conversion was a success
			current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		else:
			current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
	else:
		print current_fname + ' was not regognized as a chd and not converted'

	# current_dialog.close()
	return chd_success, new_fname

def rename_rom_postdl(current_fname,new_extension):
	rename_success = False
	new_fname = None

	if os.path.exists(current_fname):
		file_basename_no_ext = os.path.splitext(current_fname)
		new_fname = file_basename_no_ext[0]+'.'+new_extension.replace('.','').replace("'",'') #Clean extension
		os.rename(current_fname,new_fname) #Rename file with new extension
		print 'IARL: Renamed filename to: '+new_fname
		rename_success = True

	return rename_success, new_fname

def lynx_header_fix(current_fname):
	success = False
	new_fname = None
	header_text = '???'
	# This is a hack to make these headerless roms work
	# $0000- Empty - Not used?
	# $0100- 64KB
	# $0200- 128KB
	# $0400- 256KB
	# $0800- 512KB
	temp_filename = os.path.join(os.path.split(current_fname)[0],'temp.lnx')
	lynx_header = dict()
	lynx_header['64'] = 'LYNX\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Atari\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	lynx_header['128'] = 'LYNX\x00\x02\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Atari\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	lynx_header['256'] = 'LYNX\x00\x04\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Atari\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	lynx_header['512'] = 'LYNX\x00\x08\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Atari\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

	if os.path.exists(current_fname):
		zip_success1, new_rom_fname = unzip_file(current_fname)
		if zip_success1:
			st = os.stat(new_rom_fname)
			if st.st_size<65000: #Add a little extra in terms of size depending on system
				use_header = lynx_header['64']
				header_text = '64'
			elif 65000<=st.st_size<130000:
				use_header = lynx_header['128']
				header_text = '128'
			elif 130000<=st.st_size<270000:
				use_header = lynx_header['256']
				header_text = '256'
			elif st.st_size>=270000:
				use_header = lynx_header['512']
				header_text = '512'
			else:
				use_header = lynx_header['256']
				header_text = '???'

			with open(new_rom_fname, 'rb') as old:
				with open(temp_filename, 'wb') as new:
				    new.write(use_header)
				    new.write(old.read())

			os.remove(new_rom_fname) #Remove Old File
			os.rename(temp_filename,new_rom_fname) #Rename Temp File
			new_fname = new_rom_fname
			success = True
			print 'IARL:  Lynx ROM Updated with '+header_text+' bytes'

	return success, new_fname

def set_new_dl_path(xml_id,plugin):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0] + '/'

	current_dialog = xbmcgui.Dialog()

	ret1 = current_dialog.select('Select Download Path Type', ['Default','Custom'])

	if ret1 == 0:
		ret2 = current_dialog.select('Are you sure you want to update the current Download Path for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_downloadpath','default')
			ok_ret = current_dialog.ok('Complete','Download Path was updated to default[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	elif ret1 == 1:
		new_path = current_dialog.browse(0,'Update Download Path','files')
		ret2 = current_dialog.select('Are you sure you want to update the current Download Path for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_downloadpath',new_path)
			ok_ret = current_dialog.ok('Complete','Download Path was updated to your custom folder[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	else:
		pass


def set_new_post_dl_action(xml_id,plugin):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0] + '/'

	current_dialog = xbmcgui.Dialog()

	ret1 = current_dialog.select('Select New Post Download Action', ['None','Unzip','Unzip and Update DOSBox CMD','Convert CHD to BIN/CUE','Convert CHD to CUE/BIN','Rename with .gg ext','Cancel'])

	if ret1 == 0:
		ret2 = current_dialog.select('Are you sure you want to set the post DL action to none for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction','none')
			ok_ret = current_dialog.ok('Complete','Post Download Action Updated to None[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	elif ret1 == 1:
		ret2 = current_dialog.select('Are you sure you want to set the post DL action to Unzip for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction','unzip_rom')
			ok_ret = current_dialog.ok('Complete','Post Download Action Updated to Unzip[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	elif ret1 == 2:
		ret2 = current_dialog.select('Are you sure you want to set the post DL action to Unzip and Update DOSBox CMDs for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction','unzip_update_rom_path_dosbox')
			ok_ret = current_dialog.ok('Complete','Post Download Action Updated to Unzip and Update DOSBox CMDs[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	elif ret1 == 3:
		ret2 = current_dialog.select('Are you sure you want to set the post DL action to convert CHD to BIN/CUE (launch BIN) for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction','convert_chd_bin')
			ok_ret = current_dialog.ok('Complete','Post Download Action Updated to convert CHD to BIN/CUE[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	elif ret1 == 4:
		ret2 = current_dialog.select('Are you sure you want to set the post DL action to convert CHD to CUE/BIN (launch CUE) for'+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction','convert_chd_cue')
			ok_ret = current_dialog.ok('Complete','Post Download Action Updated to convert CHD to CUE/BIN[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	elif ret1 == 5:
		ret2 = current_dialog.select('Are you sure you want to set the post DL action to rename file with .gg extension for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction','rename_rom_postdl('"'gg'"')')
			ok_ret = current_dialog.ok('Complete','Post Download Action Updated to rename file with .gg extension[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	else:
		pass


def set_new_emu_launcher(xml_id,plugin):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0] + '/'

	current_dialog = xbmcgui.Dialog()

	ret1 = current_dialog.select('Select New Emulator Launcher', ['Kodi RetroPlayer','External','Cancel'])

	if ret1 == 0:
		ret2 = current_dialog.select('Are you sure you want to set the Emulator to Kodi Retroplayer for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_launcher','retroplayer')
			ok_ret = current_dialog.ok('Complete','Emulator updated to Kodi Retroplayer[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
	elif ret1 == 1:
		ret2 = current_dialog.select('Are you sure you want to set the Emulator to External Program for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_launcher','external')
			ok_ret = current_dialog.ok('Complete','Emulator updated to External Program[CR]Cache was cleared for new settings')
			plugin.clear_function_cache()
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