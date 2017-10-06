#Internet Archive ROM Launcher
#Zach Morris
#https://github.com/zach-morris/plugin.program.iarl

import os, sys, re, shutil, json, zipfile, urllib, glob, difflib
import xbmc, xbmcaddon, xbmcvfs, xbmcgui
# 	from resources.lib.xbmcswift2b import xbmcgui
from descriptionparserfactory import *
from webutils import *
from dateutil import parser as date_parser
try:
    import cPickle as pickle
except ImportError:
    import pickle

import subprocess
try:
    check_output = subprocess.check_output
except AttributeError:
	xbmc.log(msg='IARL:  Subprocess check_output not supported, defining check_output', level=xbmc.LOGDEBUG)
	def check_output(*popenargs, **kwargs):
		r"""Run command with arguments and return its output as a byte string.
		Backported from Python 2.7 as it's implemented as pure python on stdlib.
		>>> check_output(['/usr/bin/python', '--version'])
		Python 2.6.2
		"""
		process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
		output, unused_err = process.communicate()
		retcode = process.poll()
		if retcode:
			cmd = kwargs.get("args")
			if cmd is None:
				cmd = popenargs[0]
			error = subprocess.CalledProcessError(retcode, cmd)
			error.output = output
			raise error
		return output

	subprocess.check_output = check_output

#Define util constants
iarl_plugin_name = 'plugin.program.iarl'
__addon__ = xbmcaddon.Addon(id='%s' %iarl_plugin_name)
__language__ = __addon__.getLocalizedString
rom_tag_regex = re.compile(r'\([^)]*\)')
total_arts = 10
addon_date_format = '%m/%d/%Y'
addon_year_format = '%Y'

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

html_escape_table = {
		"&" : "%26",
		" " : "%20" ,
		"'" : "%27",
		">" : "%3E",
		"<" : "%3C",		
		}

txt_escape_table = {
		"&" : "&amp;",
		">" : "&gt;",
		"<" : "&lt;",		
		}

def unquote_text(text_in):
	text_out = urllib.unquote(text_in)
	return text_out

def html_unescape(text_in):
	text_out = text_in
	try:
		for key in html_unescape_table.keys():
			text_out = text_out.replace(key, html_unescape_table[key])
	except:
		xbmc.log(msg='IARL:  Unable to html unescape string '+str(text_in), level=xbmc.LOGERROR)
	return text_out

def html_escape(text_in):
	text_out = text_in
	try:
		for key in html_escape_table.keys():
			text_out = text_out.replace(key, html_escape_table[key])
	except:
		xbmc.log(msg='IARL:  Unable to html escape string '+str(text_in), level=xbmc.LOGERROR)
	return text_out

def txt_escape(text_in):
	text_out = text_in
	try:
		for key in txt_escape_table.keys():
			text_out = text_out.replace(key, txt_escape_table[key])
	except:
		xbmc.log(msg='IARL:  Unable to escape text '+str(text_in), level=xbmc.LOGERROR)
	return text_out

def clean_file_folder_name(text_in):
	text_out = text_in
	keep_characters = [' ','_']
	try:
		text_out = ''.join(c for c in text_in if c.isalnum() or c in keep_characters).rstrip()
		text_out = text_out.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
		text_out = text_out.replace(' ','_')
	except:
		text_out = text_in

	return text_out

def localize_string(id_in):
	try:
		return __language__(id)
	except:
		xbmc.log(msg='IARL:  No translation available for string with id: '+str(id), level=xbmc.LOGERROR)
		return ''

def get_operating_system():
	current_OS = None

	if 'win32' in sys.platform:
		current_OS = 'Windows'
	elif 'win64' in sys.platform:
		current_OS = 'Windows'
	elif 'linux' in sys.platform:
		current_OS = 'Nix' #Default to Nix, then look for other alternatives
		if 'XBMC_ANDROID_APK' in os.environ.keys():
			current_OS = 'Android' #Similar method to find android as done below for IOS
		elif os.path.exists('/etc/os-release'):
			try:
				with open('/etc/os-release', 'r') as content_file: #Best method I could find to determine if its OE
					os_content_file = content_file.read().replace('\n', '')
				if 'OpenELEC'.lower() in os_content_file.lower():
					if 'RPi2.arm'.lower() in os_content_file.lower():
						current_OS = 'OpenElec RPi'
					else:
						current_OS = 'OpenElec x86'
				elif 'LibreElec'.lower() in os_content_file.lower():
					if 'RPi2.arm'.lower() in os_content_file.lower():
						current_OS = 'LibreElec RPi'
					else:
						current_OS = 'LibreElec x86'
			except:
				current_OS = 'Nix'
		else:
			current_OS = 'Nix'
	elif 'darwin' in sys.platform:
		if 'USER' in os.environ and os.environ['USER'] in ('mobile','frontrow',):
			current_OS = 'IOS'
		else: 
			current_OS = 'OSX'

	try:
		make_scripts_executable()
	except:
		xbmc.log(msg='IARL:  chmod failed', level=xbmc.LOGDEBUG)

	return current_OS

def execute_subprocess_command(command_in):
	try:
		return_data = check_output([command_in],shell=True)
		xbmc.log(msg='IARL:  Subprocess command returned: '+str(return_data), level=xbmc.LOGDEBUG)
	except:
		xbmc.log(msg='IARL:  Unable to execute subprocess command, trying OS command', level=xbmc.LOGDEBUG)
		os.system(command_in) #Android is frustrating...

def make_scripts_executable():
	#Attempt to make addon scripts executable
	bin_path = get_addondata_bindir()

	bin_file_list = [os.path.join('7za','7za.android'), os.path.join('7za','7za.armv6l'), os.path.join('7za','7za.armv7l'), os.path.join('7za','7za.exe'), os.path.join('7za','7za.OSX'),os.path.join('7za','7za.Nix'),os.path.join('7za','7za.x86_64'), 'applaunch_OE.sh', 'applaunch-vbs.bat', 'applaunch.bat', 'applaunch.sh',os.path.join('chdman','chdman.armhf'),os.path.join('chdman','chdman.OSX'),os.path.join('chdman','chdman.Nix'),os.path.join('chdman','chdman.exe'),'LaunchKODI.vbs', 'romlaunch_OE_RPi2.sh', 'romlaunch_OE.sh', 'libreelec-fs-uae.sh', 'libreelec-fs-uae.start', 'Sleep.vbs']
	
	for ffiles in bin_file_list:
		try:
			os.chmod(os.path.join(bin_path,ffiles), os.stat(os.path.join(bin_path,ffiles)).st_mode | 0o111)
		except:
			xbmc.log(msg='IARL:  chmod failed for '+str(ffiles), level=xbmc.LOGDEBUG)

def get_userdata_path():
	path = ''
	path = xbmc.translatePath('special://profile/addon_data/%s'%(iarl_plugin_name))
	if not os.path.exists(path):
		try:
			os.makedirs(path)
		except:
			xbmc.log(msg='IARL:  Error creating userdata path: ' +str(path), level=xbmc.LOGERROR)

	return path

def get_addon_install_path():
	return __addon__.getAddonInfo('path')

def get_skin_install_path(skin_name):
	return xbmcaddon.Addon(id='%s' %skin_name).getAddonInfo('path')

def get_XML_files_path():
	return get_userdata_xmldir()

def get_media_files_path():
	return os.path.join(get_addon_install_path(),'resources','skins','Default','media')

def get_skin_files_path():
	return os.path.join(get_addon_install_path(),'resources','skins')

def get_parser_file(xml_filename):
	return os.path.join(get_addon_install_path(),'resources','data',xml_filename)

def get_userdata_temp_dir():
	temp_dir = os.path.join(get_userdata_path(),'temp_iarl')
	try:
		#check if folder exists
		if(not os.path.isdir(temp_dir)):
			os.mkdir(temp_dir) #If it doesn't exist, make it
		return temp_dir
	except Exception, (exc):
		xbmc.log(msg='IARL:  Error creating temp_iarl dir: ' +str(temp_dir), level=xbmc.LOGERROR)
		return None

def get_userdata_list_cache_dir():
	list_cache_dir = os.path.join(get_userdata_path(),'list_cache')
	try:
		#check if folder exists
		if(not os.path.isdir(list_cache_dir)):
			os.mkdir(list_cache_dir) #If it doesn't exist, make it
		return list_cache_dir
	except Exception, (exc):
		xbmc.log(msg='IARL:  Error creating list_cache dir: ' +str(list_cache_dir), level=xbmc.LOGERROR)
		return None

def clear_userdata_list_cache_dir():
	list_cache_dir = get_userdata_list_cache_dir()
	clear_success = False
	try:
		shutil.rmtree(list_cache_dir)
		list_cache_dir = get_userdata_list_cache_dir() #Recreate the directory after deleting
		clear_success = True
	except Exception, (exc):
		xbmc.log(msg='IARL:  Error clearing list_cache dir: ' +str(list_cache_dir), level=xbmc.LOGERROR)
	return clear_success

def save_userdata_list_cache_file(list_object,category_id):
	save_success = False
	list_cache_dir = get_userdata_list_cache_dir()
	pickle_filename = os.path.join(get_userdata_list_cache_dir(),category_id+'.pickle')

	#Removed this code, wb file writing overwrites the old file anyway, so no need to delete
	# if os.path.isfile(pickle_filename): #File already exists, so delete it
	# 	try:
	# 		os.remove(pickle_filename)
	# 	except:
	# 		xbmc.log(msg='IARL:  Error deleting current list cache file '+str(pickle_filename)+' prior to save.', level=xbmc.LOGERROR)
	# else: #File doesn't exist, so save it
	try:
		pickle.dump(list_object,open(pickle_filename,'wb')) #Save/overwrite file as pickle
		save_success = True
		xbmc.log(msg='IARL:  List cached to file '+str(pickle_filename), level=xbmc.LOGDEBUG)
	except:
		xbmc.log(msg='IARL:  Unable to save list cache file '+str(pickle_filename), level=xbmc.LOGERROR)
		try:
			file_object.close() #Close the file if there was an error
			os.remove(pickle_filename) #Delete the attempted saved file
		except:
			xbmc.log(msg='IARL:  Unable to save list cache file '+str(pickle_filename)+', the file may be corrupted', level=xbmc.LOGERROR)

	return save_success

def update_history_cache_file(iarl_data,plugin):
	save_success = False
	load_success = False
	list_cache_dir = get_userdata_list_cache_dir()
	pickle_filename = os.path.join(get_userdata_list_cache_dir(),'iarl_history.pickle')
	list_out = []

	if iarl_data['settings']['iarl_setting_history'] > 0 and iarl_data['settings']['cache_list']: #History is set to something other than 0, so save the current list item to history
		if os.path.isfile(pickle_filename):
			xbmc.log(msg='IARL:  Loading history cache '+str(pickle_filename), level=xbmc.LOGDEBUG)
			try:
				with open(pickle_filename,'rb') as content_file:
					history_list = pickle.load(content_file)
				load_success = True
			except:
				load_success = False
				history_list = []
				xbmc.log(msg='IARL:  Unable to load list cache file '+str(pickle_filename), level=xbmc.LOGERROR)
		else:
			load_success = True #No file to load
			history_list = []

		if load_success:
			#Top of the list is last played
			list_out.append({
	        'label' : iarl_data['current_rom_data']['rom_label'],
	        'label2' : iarl_data['current_rom_data']['rom_name'],
	        'icon': iarl_data['current_rom_data']['rom_icon'],
	        'thumbnail' : iarl_data['current_rom_data']['rom_thumbnail'],
	        'path' : plugin.url_for('get_selected_rom', category_id=iarl_data['current_archive_data']['category_id'], romname=iarl_data['current_rom_data']['rom_name']),
	        'info' : {'title' : iarl_data['current_rom_data']['rom_title'],
	        		  'genre': iarl_data['current_rom_data']['rom_genre'],
	        		  'year': iarl_data['current_rom_data']['rom_year'],
	        		  'studio': iarl_data['current_rom_data']['rom_studio'],
	        		  'date': iarl_data['current_rom_data']['rom_date'],
	        		  'plot': iarl_data['current_rom_data']['rom_plot'],
	        		  'trailer': iarl_data['current_rom_data']['rom_trailer'],
	        		  'rating': iarl_data['current_rom_data']['rom_rating'],
	        		  'mpaa' : iarl_data['current_rom_data']['rom_esrb'],
	        		  'size': sum(map(int,iarl_data['current_rom_data']['rom_size'])) #For display purposes only
	        		  },
	        'properties' : {'fanart_image' : iarl_data['current_rom_data']['rom_fanarts'][0],
							'banner' : iarl_data['current_rom_data']['rom_banners'][0],
							'clearlogo': iarl_data['current_rom_data']['rom_logos'][0],
							'poster': iarl_data['current_rom_data']['rom_thumbnail'],
							'tag': iarl_data['current_rom_data']['rom_tag'],
							'rating': iarl_data['current_rom_data']['rom_rating'],
							'perspective': iarl_data['current_rom_data']['rom_perspective'],
							'esrb': iarl_data['current_rom_data']['rom_esrb'],
							'rom_name': iarl_data['current_rom_data']['rom_name'],
							'rom_icon': iarl_data['current_rom_data']['rom_icon'],
							'rom_thumbnail': iarl_data['current_rom_data']['rom_thumbnail'],
							'rom_title': iarl_data['current_rom_data']['rom_title'],
							'rom_studio': iarl_data['current_rom_data']['rom_studio'],
							'rom_genre': iarl_data['current_rom_data']['rom_genre'],
							'rom_date': iarl_data['current_rom_data']['rom_date'],
							'rom_year': iarl_data['current_rom_data']['rom_year'],
							'rom_plot': iarl_data['current_rom_data']['rom_plot'],
							'rom_trailer': iarl_data['current_rom_data']['rom_trailer'],
							'rom_label': iarl_data['current_rom_data']['rom_label'],
							'fanart1': iarl_data['current_rom_data']['rom_fanarts'][0],
							'fanart2': iarl_data['current_rom_data']['rom_fanarts'][1],
							'fanart3': iarl_data['current_rom_data']['rom_fanarts'][2],
							'fanart4': iarl_data['current_rom_data']['rom_fanarts'][3],
							'fanart5': iarl_data['current_rom_data']['rom_fanarts'][4],
							'fanart6': iarl_data['current_rom_data']['rom_fanarts'][5],
							'fanart7': iarl_data['current_rom_data']['rom_fanarts'][6],
							'fanart8': iarl_data['current_rom_data']['rom_fanarts'][7],
							'fanart9': iarl_data['current_rom_data']['rom_fanarts'][8],
							'fanart10': iarl_data['current_rom_data']['rom_fanarts'][9],
							'banner1': iarl_data['current_rom_data']['rom_banners'][0],
							'banner2': iarl_data['current_rom_data']['rom_banners'][1],
							'banner3': iarl_data['current_rom_data']['rom_banners'][2],
							'banner4': iarl_data['current_rom_data']['rom_banners'][3],
							'banner5': iarl_data['current_rom_data']['rom_banners'][4],
							'banner6': iarl_data['current_rom_data']['rom_banners'][5],
							'banner7': iarl_data['current_rom_data']['rom_banners'][6],
							'banner8': iarl_data['current_rom_data']['rom_banners'][7],
							'banner9': iarl_data['current_rom_data']['rom_banners'][8],
							'banner10': iarl_data['current_rom_data']['rom_banners'][9],
							'snapshot1': iarl_data['current_rom_data']['rom_snapshots'][0],
							'snapshot2': iarl_data['current_rom_data']['rom_snapshots'][1],
							'snapshot3': iarl_data['current_rom_data']['rom_snapshots'][2],
							'snapshot4': iarl_data['current_rom_data']['rom_snapshots'][3],
							'snapshot5': iarl_data['current_rom_data']['rom_snapshots'][4],
							'snapshot6': iarl_data['current_rom_data']['rom_snapshots'][5],
							'snapshot7': iarl_data['current_rom_data']['rom_snapshots'][6],
							'snapshot8': iarl_data['current_rom_data']['rom_snapshots'][7],
							'snapshot9': iarl_data['current_rom_data']['rom_snapshots'][8],
							'snapshot10': iarl_data['current_rom_data']['rom_snapshots'][9],
							'boxart1': iarl_data['current_rom_data']['rom_boxarts'][0],
							'boxart2': iarl_data['current_rom_data']['rom_boxarts'][1],
							'boxart3': iarl_data['current_rom_data']['rom_boxarts'][2],
							'boxart4': iarl_data['current_rom_data']['rom_boxarts'][3],
							'boxart5': iarl_data['current_rom_data']['rom_boxarts'][4],
							'boxart6': iarl_data['current_rom_data']['rom_boxarts'][5],
							'boxart7': iarl_data['current_rom_data']['rom_boxarts'][6],
							'boxart8': iarl_data['current_rom_data']['rom_boxarts'][7],
							'boxart9': iarl_data['current_rom_data']['rom_boxarts'][8],
							'boxart10': iarl_data['current_rom_data']['rom_boxarts'][9],
							'logo1': iarl_data['current_rom_data']['rom_logos'][0],
							'logo2': iarl_data['current_rom_data']['rom_logos'][1],
							'logo3': iarl_data['current_rom_data']['rom_logos'][2],
							'logo4': iarl_data['current_rom_data']['rom_logos'][3],
							'logo5': iarl_data['current_rom_data']['rom_logos'][4],
							'logo6': iarl_data['current_rom_data']['rom_logos'][5],
							'logo7': iarl_data['current_rom_data']['rom_logos'][6],
							'logo8': iarl_data['current_rom_data']['rom_logos'][7],
							'logo9': iarl_data['current_rom_data']['rom_logos'][8],
							'logo10': iarl_data['current_rom_data']['rom_logos'][9],
							'nplayers': iarl_data['current_rom_data']['rom_nplayers'],
							#Need to convert lists into comma seperated strings for listitem properties
							'rom_filenames': ','.join(map(str, iarl_data['current_rom_data']['rom_filenames'])),
							'rom_file_sizes': ','.join(map(str, iarl_data['current_rom_data']['rom_size'])),
							'rom_supporting_filenames': ','.join(map(str, iarl_data['current_rom_data']['rom_supporting_filenames'])),
							'rom_save_filenames': ','.join(map(str, iarl_data['current_rom_data']['rom_save_filenames'])),
							'rom_save_supporting_filenames': ','.join(map(str, iarl_data['current_rom_data']['rom_save_supporting_filenames'])),
							'rom_emu_command': iarl_data['current_rom_data']['rom_emu_command'],
							'rom_override_cmd': iarl_data['current_rom_data']['rom_override_cmd'],
							'rom_override_postdl': iarl_data['current_rom_data']['rom_override_postdl'],
							'rom_override_downloadpath': iarl_data['current_rom_data']['rom_override_downloadpath'],
							'emu_name' : iarl_data['current_archive_data']['emu_name'],
							'category_id' : iarl_data['current_archive_data']['category_id'],
							'emu_parser' : iarl_data['current_archive_data']['emu_parser'],
							'emu_filepath' : iarl_data['current_archive_data']['emu_filepath'],
							'emu_plot' : iarl_data['current_archive_data']['emu_plot'],
							'emu_category' : iarl_data['current_archive_data']['emu_category'],
							'emu_version' : iarl_data['current_archive_data']['emu_version'],
							'emu_date' : iarl_data['current_archive_data']['emu_date'],
							'emu_author' : iarl_data['current_archive_data']['emu_author'],
							'emu_base_url' : iarl_data['current_archive_data']['emu_base_url'],
							'emu_download_path' : iarl_data['current_archive_data']['emu_download_path'],
							'emu_post_download_action' : iarl_data['current_archive_data']['emu_post_download_action'],
							'emu_launcher' : iarl_data['current_archive_data']['emu_launcher'],
							'emu_ext_launch_cmd' : iarl_data['current_archive_data']['emu_ext_launch_cmd'],
							'emu_boxart' : iarl_data['current_archive_data']['emu_boxart'],
							'emu_banner' : iarl_data['current_archive_data']['emu_banner'],
							'emu_fanart' : iarl_data['current_archive_data']['emu_fanart'],
							'emu_logo': iarl_data['current_archive_data']['emu_logo'],
							'emu_trailer': iarl_data['current_archive_data']['emu_trailer']
							},
	        				'context_menu': None
							})

			for ii in range(0,max(0,min(iarl_data['settings']['iarl_setting_history'],len(history_list)))): #Iterate up to either the max number of items allowed or the total number of history items
				if ii < iarl_data['settings']['iarl_setting_history']-1:
					list_out.append(history_list[ii])

			save_success = save_userdata_list_cache_file(list_out,'iarl_history')

	else: #History is set to 0 items, if the file exists, delete it
		if os.path.isfile(pickle_filename):
			try:
				os.remove(pickle_filename)
				xbmc.log(msg='IARL:  History set to 0, deleted cache '+str(pickle_filename), level=xbmc.LOGDEBUG)
			except:
				xbmc.log(msg='IARL:  Error deleting current list cache file '+str(pickle_filename), level=xbmc.LOGERROR)

	return save_success

def load_userdata_list_cache_file(category_id):
	load_success = False
	list_object = None
	list_cache_dir = get_userdata_list_cache_dir()
	pickle_filename = os.path.join(get_userdata_list_cache_dir(),category_id+'.pickle')

	if os.path.isfile(pickle_filename):
		try:
			with open(pickle_filename,'rb') as content_file:
				list_object = pickle.load(content_file)
			load_success = True
		except:
			xbmc.log(msg='IARL:  Unable to load list cache file '+str(pickle_filename), level=xbmc.LOGERROR)

	if load_success:
		xbmc.log(msg='IARL: Loaded list cache from file for '+str(category_id), level=xbmc.LOGDEBUG)

	return load_success, list_object

def delete_userdata_list_cache_file(category_id):
	clear_success = False
	list_cache_dir = get_userdata_list_cache_dir()
	pickle_filename = os.path.join(get_userdata_list_cache_dir(),category_id+'.pickle')
	if os.path.isfile(pickle_filename):
		try:
			os.remove(pickle_filename) #Delete the attempted saved file
			clear_success = True
			xbmc.log(msg='IARL:  List_cache file was deleted: ' +str(pickle_filename), level=xbmc.LOGDEBUG)
		except Exception, (exc):
			xbmc.log(msg='IARL:  Error deleting list_cache file: ' +str(pickle_filename), level=xbmc.LOGERROR)
	else:
		clear_success = True
		xbmc.log(msg='IARL:  List_cache file did not exist, so was not deleted', level=xbmc.LOGDEBUG)

	return clear_success

def get_userdata_xmldir():
	xmlDir = os.path.join(get_userdata_path(),'dat_files')
	try:
		#check if folder exists
		if(not os.path.isdir(xmlDir)):
			os.mkdir(xmlDir) #If it doesn't exist, make it
		return xmlDir
	except Exception, (exc):
		xbmc.log(msg='IARL:  Error creating userdata XML dir: ' +str(exc), level=xbmc.LOGERROR)
		return None

def get_addondata_xmldir():
	return os.path.join(get_addon_install_path(),'resources','data','dat_files')

def get_addondata_bindir():
	return os.path.join(get_addon_install_path(),'resources','bin')

def get_youtube_plugin_url(videoid):
	if 'http' in videoid:
		return videoid
	else:
		return 'plugin://plugin.video.youtube/play/?video_id=%s'%videoid

def update_addonxml(option):
	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Are you sure you want to update this setting?', ['No','Yes'])
	if ret1 == 0:
		pass
	else:
		ok_ret = current_dialog.ok('Complete','The addon was updated.[CR]You may have to restart Kodi for the settings to take effect.')
		update_xml_header(get_addon_install_path(),'addon.xml','provides',option)
		xbmc.log(msg='IARL:  Addon was updated to provide ' +str(option), level=xbmc.LOGDEBUG)

def get_folder_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += get_folder_size(itempath)
    return total_size

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
	        size = int((float(digit.groups()[0]) * unit))
	    else:
	        size = 0
	except:
		size = None
	return size

def bytes_to_string_size(num, suffix='B'):
	num_sum = sum(map(int,num))
	for unit in ['','k','M','G','T','P','E','Z']:
		if abs(num_sum) < 1024.0:
			return "%3.1f%s%s" % (num_sum, unit, suffix)
		num_sum /= 1024.0
	return str("%.1f%s%s") % (num_sum, 'Yi', suffix)

def copyFile(oldPath, newPath):
	xbmc.log(msg='IARL:  New Path '+str(newPath), level=xbmc.LOGDEBUG)
	newDir = os.path.dirname(newPath)
	if not os.path.isdir(newDir):
		xbmc.log(msg='IARL:  New Dir Created '+str(newDir), level=xbmc.LOGDEBUG)
		try:
			os.mkdir(newDir)
		except Exception, (exc):
			xbmc.log(msg='IARL:  Could not create directory: %s\%s'%(str(newDir), str(exc)), level=xbmc.LOGERROR)
			return
	if not os.path.isfile(newPath):
		xbmc.log(msg='IARL: Copied file from %s to %s'%(str(oldPath),str(newPath)), level=xbmc.LOGDEBUG)
		try:
			shutil.copy2(oldPath, newPath)
		except Exception, (exc):
			xbmc.log(msg='IARL:  Error copying file from %s to %s\%s' %(str(oldPath),str(newPath), str(exc)), level=xbmc.LOGERROR)

def check_temp_folder_and_clean(iarl_options_dl_cache):
	current_path = get_userdata_temp_dir()
	current_path_size = get_folder_size(current_path)

	if current_path_size > iarl_options_dl_cache:
		xbmc.log(msg='IARL: Current directory size is '+str(current_path_size)+'.  Limit is '+str(iarl_options_dl_cache), level=xbmc.LOGDEBUG)
		xbmc.log(msg='IARL: Deleting Temp Directory Cache', level=xbmc.LOGDEBUG)
		shutil.rmtree(current_path)

	current_path = get_userdata_temp_dir()  #Remake the directory

def show_busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialog)')

def hide_busy_dialog():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    # while xbmc.getCondVisibility('Window.IsActive(busydialog)'):
    #     xbmc.sleep(100)

def initialize_userdata():
	addondata_xmldir = get_addondata_xmldir()
	userdata_xmldir = get_userdata_xmldir()
	addondata_subfolders, addondata_files = xbmcvfs.listdir(addondata_xmldir)
	userdata_subfolders, userdata_files = xbmcvfs.listdir(userdata_xmldir)

	if len(addondata_files) > 0:
		# show_busy_dialog()
		xbmc.log(msg='IARL:  Initializing XML Files', level=xbmc.LOGDEBUG)
		for file_name in addondata_files:
			if file_name in userdata_files: #The file already exists in userdata
				xbmc.log(msg='IARL: '+str(file_name)+' already exists, check version', level=xbmc.LOGDEBUG)
				addon_file_info = get_xml_header_version(os.path.join(addondata_xmldir,file_name))
				userdata_file_info = get_xml_header_version(os.path.join(userdata_xmldir,file_name))
				if addon_file_info['emu_version'][0] == userdata_file_info['emu_version'][0]: #Files are the same, delete addondata file
					xbmc.log(msg='IARL: '+str(file_name)+' same version detected, deleting addondata file', level=xbmc.LOGDEBUG)
					os.remove(os.path.join(addondata_xmldir,file_name))
				else:
					current_dialog = xbmcgui.Dialog()
					current_dialog.ok('New Version Found', 'New version '+addon_file_info['emu_version'][0]+' for the file:', addon_file_info['emu_name'][0], 'was detected.')
					ret1 = current_dialog.select('Overwrite old file: '+addon_file_info['emu_name'][0]+' ?', ["Yes, Replace!", "Remind me later", "No, Never!"])
					if ret1 == 0: #Yes, replace!
						xbmc.log(msg='IARL:  Copying new file '+str(file_name)+' to userdata', level=xbmc.LOGDEBUG)
						try:
							os.remove(os.path.join(userdata_xmldir,file_name)) #Remove the old userdata file
						except:
							xbmc.log(msg='IARL:  Attempt to delete the old XML file '+str(file_name)+' failed.', level=xbmc.LOGERROR)
						copyFile(os.path.join(addondata_xmldir,file_name), os.path.join(userdata_xmldir,file_name))
						if os.path.isfile(os.path.join(userdata_xmldir,file_name)): #Copy was successful, delete addondata file
							os.remove(os.path.join(addondata_xmldir,file_name)) #Remove the file from the addondata folder
						else:
							xbmc.log(msg='IARL:  Copying the XML file '+str(file_name)+' failed.', level=xbmc.LOGERROR)
					elif ret1 == 1: #Remind me later
						xbmc.log(msg='IARL:  XML File will not be copied at this time', level=xbmc.LOGDEBUG)
					else: #No, delete the file
						xbmc.log(msg='IARL:  XML File will be deleted', level=xbmc.LOGDEBUG)
						os.remove(os.path.join(addondata_xmldir,file_name)) #Remove the file from the addondata folder
			else: #The files does not yet exist in userdata
				xbmc.log(msg='IARL:  Copying new file '+str(file_name)+' to userdata', level=xbmc.LOGDEBUG)
				copyFile(os.path.join(addondata_xmldir,file_name), os.path.join(userdata_xmldir,file_name))
				if os.path.isfile(os.path.join(userdata_xmldir,file_name)): #Copy was successful, delete addondata file
					os.remove(os.path.join(addondata_xmldir,file_name)) #Remove the file from the addondata folder
				else:
					xbmc.log(msg='IARL:  Copying the XML file '+str(file_name)+' failed.', level=xbmc.LOGERROR)
		xbmc.sleep(500) #Sleep for a moment
		# hide_busy_dialog()

#Parses all the xml dat files in the folder and returns them to create the proper directories
def get_archive_info():
	dat_path = get_XML_files_path()
	# subfolders, files = xbmcvfs.listdir(dat_path)
	files = os.listdir(dat_path)

	archive_data = {
	'xml_id' : list(),
	'category_id' : list(),
	'emu_filepath' : list(),
	'emu_name' : list(),
	'emu_parser' : list(),
	'emu_description' : list(),
	'emu_category' : list(),
	'emu_version' : list(),
	'emu_date' : list(),
	'emu_author' : list(),
	'emu_homepage' : list(),
	'emu_base_url' : list(),
	'emu_launcher' : list(),
	'emu_ext_launch_cmd' : list(),
 	'emu_download_path' : list(),
	'emu_post_download_action' : list(),
	'emu_plot' : list(),
	'emu_boxart' : list(),
	'emu_banner' : list(),
	'emu_fanart' : list(),
	'emu_logo': list(),
	'emu_trailer': list(),
	'total_num_archives' : None,
	}
	total_lines = 500  #Read up to this many lines looking for the header
	for ffile in files:
		if '.xml' in ffile.lower():
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
					archive_data['emu_name'].append(header_text.split('<emu_name>')[1].split('</emu_name>')[0])
					archive_data['emu_parser'].append(header_text.split('<emu_parser>')[1].split('</emu_parser>')[0])
					archive_data['emu_filepath'].append(os.path.join(dat_path,ffile)) #Full path to xml files
					archive_data['xml_id'].append(os.path.splitext(ffile)[0]) #Name of XML file with no extension
					archive_data['emu_description'].append(header_text.split('<emu_description>')[1].split('</emu_description>')[0])
					archive_data['emu_category'].append(header_text.split('<emu_category>')[1].split('</emu_category>')[0])
					archive_data['emu_version'].append(header_text.split('<emu_version>')[1].split('</emu_version>')[0])
					archive_data['emu_date'].append(header_text.split('<emu_date>')[1].split('</emu_date>')[0])
					archive_data['emu_author'].append(header_text.split('<emu_author>')[1].split('</emu_author>')[0])
					archive_data['emu_homepage'].append(header_text.split('<emu_homepage>')[1].split('</emu_homepage>')[0])
					archive_data['emu_base_url'].append(header_text.split('<emu_baseurl>')[1].split('</emu_baseurl>')[0])
					archive_data['emu_launcher'].append(header_text.split('<emu_launcher>')[1].split('</emu_launcher>')[0])
					archive_data['emu_ext_launch_cmd'].append(header_text.split('<emu_ext_launch_cmd>')[1].split('</emu_ext_launch_cmd>')[0])
					archive_data['emu_download_path'].append(header_text.split('<emu_downloadpath>')[1].split('</emu_downloadpath>')[0])
					archive_data['emu_post_download_action'].append(header_text.split('<emu_postdlaction>')[1].split('</emu_postdlaction>')[0])
					archive_data['emu_plot'].append(header_text.split('<emu_comment>')[1].split('</emu_comment>')[0])
					archive_data['emu_boxart'].append(header_text.split('<emu_thumb>')[1].split('</emu_thumb>')[0])
					archive_data['emu_banner'].append(header_text.split('<emu_banner>')[1].split('</emu_banner>')[0])
					archive_data['emu_fanart'].append(header_text.split('<emu_fanart>')[1].split('</emu_fanart>')[0])
					archive_data['emu_logo'].append(header_text.split('<emu_logo>')[1].split('</emu_logo>')[0])
					archive_data['emu_trailer'].append(header_text.split('<emu_trailer>')[1].split('</emu_trailer>')[0])
					archive_data['category_id'].append(archive_data['xml_id'][-1]) #Simpler way to keep track of URL routing
					f.close()
				if line_num == total_lines:  #Couldn't find the header
					header_end = 1
					f.close()
					xbmc.log(msg='IARL:  Unable to parse header in xml file '+str(ffile), level=xbmc.LOGERROR)

	archive_data['total_num_archives'] = len(archive_data['emu_name'])

	return archive_data

def unhide_all_archives(plugin):
	archive_data = get_archive_info()
	for ii in range(0,len(archive_data['emu_category'])):
		if ', hidden' in archive_data['emu_category'][ii]: #Don't include the archive if it's tagged hidden
			new_xml_category = archive_data['emu_category'][ii].replace(', hidden','')
			current_xml_fileparts = os.path.split(archive_data['emu_filepath'][ii])
			current_xml_filename = current_xml_fileparts[1]
			current_xml_path = current_xml_fileparts[0]
			update_xml_header(current_xml_path,current_xml_filename,'emu_category',new_xml_category)
			delete_userdata_list_cache_file(current_xml_filename.split('.')[0])

	xbmc.log(msg='IARL:  Unhide all archives is completed.', level=xbmc.LOGDEBUG)

def check_for_warn(current_sizes):
	try:
		total_size = sum(map(int,current_sizes))
	except:
		total_size = 0 #Size is unknown

	if type(total_size) is int:
		if total_size > 100*1e6: #Picked an arbitrary size of 100MB to warn about
			if 'true' in __addon__.getSetting(id='iarl_setting_warn_size').lower():
				current_dialog = xbmcgui.Dialog()
				ret1 = current_dialog.yesno('Warning','Selected files are over 100MB in size',nolabel='OK',yeslabel='OK! Stop showing this!')
				if ret1>0:
					__addon__.setSetting(id='iarl_setting_warn_size',value='false') #No longer show the warning

def advanced_setting_action_clear_cache(plugin):
	clear_userdata_list_cache_dir()
	__addon__.setSetting(id='iarl_setting_clear_cache_value',value='false') #Set back to false, no need to clear it next run
	xbmc.log(msg='IARL:  Advanced Setting Cache Clear Completed', level=xbmc.LOGDEBUG)

def update_external_launch_commands(iarl_data,xml_id,plugin):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0]

	parserfile = get_parser_file('external_launcher_parser.xml')
	launchersfile = get_parser_file('external_command_database.xml')

	descParser = DescriptionParserFactory.getParser(parserfile)
	results = descParser.parseDescription(launchersfile,'xml')
	user_options = list()
	launch_command = list()
	new_launch_command = None

	#Create list of available commands for the current external launch environment
	if 'select' not in iarl_data['settings']['external_launch_env']:
		if 'enabled' in iarl_data['settings']['external_launch_close_kodi'].lower():
			external_launch_database_os = iarl_data['settings']['external_launch_env'] + ' Close_Kodi' #Look for launch commands to close Kodi
		else:
			external_launch_database_os = iarl_data['settings']['external_launch_env']
		if iarl_data['settings']['external_launch_env'] in 'OpenElec x86 (tssemek Addon)|LibreElec x86|LibreElec SX05|RPi Gamestarter Addon|Android'.split('|'):
			external_launch_database_os = external_launch_database_os.replace(' Close_Kodi','') #By default, the above setups auto close Kodi, so there's only one list of launchers to choose from
		for entries in results:
			if entries['operating_system'][0] == external_launch_database_os:
				user_options.append(entries['launcher'][0])
				launch_command.append(entries['launcher_command'][0])
		user_options.append('Manually entered command line')
		user_options.append('None')
		launch_command.append('manual_command')
		launch_command.append('none')

		current_dialog = xbmcgui.Dialog()
		ret1 = current_dialog.select('Select a Launch Command', user_options)
		new_launch_command = launch_command[ret1]

		#Option for manual launch command entry
		if new_launch_command == 'manual_command':
			new_launch_command = current_dialog.input('Enter your new launch command:')

		if ret1>=0:
			ret2 = current_dialog.select('Are you sure you want to update[CR]the current External Launch Command?', ['Yes','Cancel'])
			if ret2<1:
				xbmc.log(msg='IARL:  New External Launch Command is '+str(new_launch_command), level=xbmc.LOGDEBUG)
				update_xml_header(current_xml_path,current_xml_filename,'emu_ext_launch_cmd',new_launch_command)
				ok_ret = current_dialog.ok('Complete','External Launch Command was updated[CR]Cache was cleared for new settings')
				delete_userdata_list_cache_file(current_xml_filename.split('.')[0])
	else: #User didn't setup external launch commands yet
		current_dialog = xbmcgui.Dialog()
		ok_ret = current_dialog.ok('Notice','External Launch Addon Settings are not available.')

def review_archive_launch_commands(xml_id):

	archive_info = get_archive_info()
	
	try:
		current_index = archive_info['xml_id'].index(os.path.splitext(os.path.split(xml_id)[-1])[0])
	except:
		xbmc.log(msg='IARL:  The archive '+str(xml_id)+' could not be found for review.', level=xbmc.LOGERROR)
		current_index = None

	if current_index is not None:
		current_dialog = xbmcgui.Dialog()
		line1 = str('Launch with: '+archive_info['emu_launcher'][current_index])
		line2 = str('Post DL CMD: '+archive_info['emu_post_download_action'][current_index])
		line3 = str('Launch CMD: '+archive_info['emu_ext_launch_cmd'][current_index])
		xbmc.log(msg='IARL:  Command Review - '+line1, level=xbmc.LOGDEBUG)
		xbmc.log(msg='IARL:  Command Review - '+line2, level=xbmc.LOGDEBUG)
		xbmc.log(msg='IARL:  Command Review - '+line3, level=xbmc.LOGDEBUG)
		ok_ret = current_dialog.ok('Launch Command',line1,line2,line3)

def replace_external_launch_variables(iarl_data):

	if iarl_data['current_rom_data']['rom_override_cmd'] is not None and len(iarl_data['current_rom_data']['rom_override_cmd']) > 0:
		xbmc.log(msg='IARL:  ROM Override command detected for '+str(iarl_data['current_rom_data']['rom_name'])+' - '+str(iarl_data['current_rom_data']['rom_override_cmd']), level=xbmc.LOGDEBUG)
		command_out = str(iarl_data['current_rom_data']['rom_override_cmd']) #Use individual ROM override command if present
	else:
		command_out = str(iarl_data['current_archive_data']['emu_ext_launch_cmd'])  #Otherwise use the default command for the entire archive listing

	#Define %APP_PATH% Variable
	if iarl_data['addon_data']['operating_system'] == 'OSX':
		current_retroarch_path = iarl_data['settings']['path_to_retroarch'].split('.app')[0]+'.app' #Make App Path for OSX only up to the container
	elif iarl_data['addon_data']['operating_system'] == 'Windows':
		current_retroarch_path = os.path.split(iarl_data['settings']['path_to_retroarch'])[0]
	else:
		current_retroarch_path = iarl_data['settings']['path_to_retroarch']

	#Define %CFG_PATH% Variable
	current_cfg_path = ''
	if 'android' in iarl_data['settings']['external_launch_env'].lower():
		default_config_locations = ['/mnt/internal_sd/Android/data/com.retroarch/files/retroarch.cfg','/sdcard/Android/data/com.retroarch/files/retroarch.cfg','/data/data/com.retroarch/retroarch.cfg']
		current_cfg_path = None
		if len(iarl_data['settings']['path_to_retroarch_cfg'])<1: #Config is not defined in settings, try to find it in one of the default locales
			for cfg_files in default_config_locations:
				try:
					if os.path.exists(cfg_files):
						if current_cfg_path is None: #If the current config path is not yet defined and the file was found, then define it
							current_cfg_path = cfg_files
				except:
					xbmc.log(msg='IARL:  The config file does not exist: '+str(cfg_files), level=xbmc.LOGERROR)
		else:
			current_cfg_path = iarl_data['settings']['path_to_retroarch_cfg'] #If the config path is defined in settings, use that
		if current_cfg_path is None:
			current_cfg_path = ''
			xbmc.log(msg='IARL:  No config file could be defined, please set your config file location in addon settings', level=xbmc.LOGERROR)

	command_out = command_out.replace('%APP_PATH%',current_retroarch_path) #Replace app path with user setting
	command_out = command_out.replace('%ADDON_DIR%',iarl_data['addon_data']['addon_install_path']) #Replace helper script with the more generic ADDON_DIR
	command_out = command_out.replace('%CFG_PATH%',current_cfg_path) #Replace config path user setting
	command_out = command_out.replace('%ROM_PATH%',iarl_data['current_save_data']['launch_filename']) #Replace ROM filepath
	command_out = command_out.replace('%ROM_BASE_PATH%',os.path.join(os.path.split(iarl_data['current_save_data']['launch_filename'])[0],'')) #Replace ROM Base path

	if '%RETROARCH_CORE_DIR%' in command_out:
		possible_core_dirs = ['/usr/lib/libretro','/usr/lib/x86_64-linux-gnu/libretro','/usr/lib/i386-linux-gnu/libretro','/usr/local/lib/libretro','/tmp/cores']
		default_core_dir = '/usr/lib/libretro'
		core_found_idx = None
		for jj in range(0,len(possible_core_dirs)):
			try:
				if os.path.isfile(os.path.join(possible_core_dirs[jj],os.path.split(command_out.split('%RETROARCH_CORE_DIR%')[-1].split('.so')[0]+'.so')[-1])):
					core_found_idx = jj
			except:
				pass
		if core_found_idx is not None:
			xbmc.log(msg='IARL:  The Retroarch Core directory was found at '+str(possible_core_dirs[core_found_idx]), level=xbmc.LOGDEBUG)
			command_out = command_out.replace('%RETROARCH_CORE_DIR%',possible_core_dirs[core_found_idx])
		else:
			xbmc.log(msg='IARL:  The Retroarch Core directory could not be found.  Defaulting to '+str(default_core_dir), level=xbmc.LOGERROR)
			command_out = command_out.replace('%RETROARCH_CORE_DIR%',default_core_dir)

	for jj in range(0,len(iarl_data['settings']['enable_additional_emulators'])):
	    if 'FS-UAE' in iarl_data['settings']['enable_additional_emulators'][jj]:
	        command_out = command_out.replace('%APP_PATH_FS_UAE%',iarl_data['settings']['path_to_additional_emulators'][jj])
	    if 'WIN-UAE' in iarl_data['settings']['enable_additional_emulators'][jj]:
	        command_out = command_out.replace('%APP_PATH_WIN_UAE%',iarl_data['settings']['path_to_additional_emulators'][jj])
	    if 'Project 64 (Win)' in iarl_data['settings']['enable_additional_emulators'][jj]:
	        command_out = command_out.replace('%APP_PATH_PJ64%',iarl_data['settings']['path_to_additional_emulators'][jj])
	    if 'Dolphin' in iarl_data['settings']['enable_additional_emulators'][jj]:
	        command_out = command_out.replace('%APP_PATH_DOLPHIN%',iarl_data['settings']['path_to_additional_emulators'][jj])
	    if 'MAME Standalone' in iarl_data['settings']['enable_additional_emulators'][jj]:
	        command_out = command_out.replace('%APP_PATH_MAME%',iarl_data['settings']['path_to_additional_emulators'][jj])

	if iarl_data['settings']['enable_netplay']:
	    current_netplay_command = ''
	    if iarl_data['settings']['netplay_host_or_client'] == 'Player 1 Host':
	        current_netplay_command = current_netplay_command+'--host '
	        if iarl_data['settings']['netplay_sync_frames'] == 'Enabled':
	            current_netplay_command = current_netplay_command+'--frames '
	        current_netplay_command = current_netplay_command+'--nick "'+str(iarl_data['settings']['netplay_host_nickname'])+'" '
	    elif iarl_data['settings']['netplay_host_or_client'] == 'Player 2 Client':
	        current_netplay_command = current_netplay_command+'--connect '+str(iarl_data['settings']['netplay_host_IP'])+' '
	        current_netplay_command = current_netplay_command+'--port '+str(iarl_data['settings']['netplay_host_port'])+' '
	        if iarl_data['settings']['netplay_sync_frames'] == 'Enabled':
	            current_netplay_command = current_netplay_command+'--frames '
	        current_netplay_command = current_netplay_command+'--nick "'+str(iarl_data['settings']['netplay_client_nickname'])+'" '
	    elif iarl_data['settings']['netplay_host_or_client'] == 'Spectator':
	        current_netplay_command = current_netplay_command+'--spectate '+str(iarl_data['settings']['netplay_host_IP'])+' '
	        current_netplay_command = current_netplay_command+'--port '+str(iarl_data['settings']['netplay_host_port'])+' '
	        if iarl_data['settings']['netplay_sync_frames'] == 'Enabled':
	            current_netplay_command = current_netplay_command+'--frames '
	        current_netplay_command = current_netplay_command+'--nick "'+str(iarl_data['settings']['netplay_spectator_nickname'])+'" '
	    else:
	        current_netplay_command = ''
	else: #Replace any netplay flags with blank space if netplay is not enabled
	    current_netplay_command = ''

	command_out = command_out.replace('%NETPLAY_COMMAND%',current_netplay_command)

	return command_out

def get_xml_header_version(xmlfilename):
	total_lines = 500  #Read up to this many lines looking for the header
	f=open(xmlfilename,'rU')
	f.seek(0)
	header_end=0
	line_num=0
	header_text = ''
	emu_version = list()
	emu_name = list()

	while header_end < 1:
		line=f.readline()    
		header_text+=str(line)
		line_num = line_num+1
		if '</header>' in header_text: #Found the header
			header_end = 1
			header_text = header_text.split('<header>')[1].split('</header>')[0]
			emu_name.append(header_text.split('<emu_name>')[1].split('</emu_name>')[0])
			emu_version.append(header_text.split('<emu_version>')[1].split('</emu_version>')[0])
			f.close()
		if line_num == total_lines:  #Couldn't find the header
			header_end = 1
			f.close()
			xbmc.log(msg='IARL:  Unable to get version in xml header file', level=xbmc.LOGERROR)

	dat_file_table = {
	'emu_name' : emu_name,
	'emu_version' : emu_version,
	}

	return dat_file_table

def define_IARL_theme(archive_name,property_name):
	property_value = None

	if property_name == 'header_color':
		if '32X'.lower() in archive_name.lower():
			property_value = '32x_head.png'
		elif 'SNES'.lower() in archive_name.lower():
			property_value = 'white.png'
		elif 'Genesis'.lower() in archive_name.lower():
			property_value = 'sega_head.png'
		elif 'NES'.lower() in archive_name.lower():
			property_value = 'white.png'
		elif 'Game Gear'.lower() in archive_name.lower():
			property_value = 'sega_head.png'
		elif 'Master System'.lower() in archive_name.lower():
			property_value = 'sega_head.png'
		elif 'N64'.lower() in archive_name.lower():
			property_value = 'n64_head.png'
		elif 'MAME'.lower() in archive_name.lower():
			property_value = 'arcade_head.png'
		elif '2600'.lower() in archive_name.lower():
			property_value = 'atari_head.png'
		elif 'Jaguar'.lower() in archive_name.lower():
			property_value = 'jaguar_head.png'
		elif 'Lynx'.lower() in archive_name.lower():
			property_value = 'lynx_head.png'
		elif 'TurboGrafx'.lower() in archive_name.lower():
			property_value = 'tg16_head.png'
		elif 'Amiga'.lower() in archive_name.lower():
			property_value = 'white.png'
		else:
			property_value = 'white.png'
	elif property_name == 'background_color':
		if '32X'.lower() in archive_name.lower():
			property_value = '32x_bg.png'
		elif 'SNES'.lower() in archive_name.lower():
			property_value = 'nes_dark_bg.png'
		elif 'Genesis'.lower() in archive_name.lower():
			property_value = 'sega_bg.png'
		elif 'NES'.lower() in archive_name.lower():
			property_value = 'nes_dark_bg.png'
		elif 'Game Gear'.lower() in archive_name.lower():
			property_value = 'sega_bg.png'
		elif 'Master System'.lower() in archive_name.lower():
			property_value = 'sega_bg.png'
		elif 'N64'.lower() in archive_name.lower():
			property_value = 'n64_bg.png'
		elif 'MAME'.lower() in archive_name.lower():
			property_value = 'arcade_bg.png'
		elif '2600'.lower() in archive_name.lower():
			property_value = 'atari_bg.png'
		elif 'Jaguar'.lower() in archive_name.lower():
			property_value = 'black.png'
		elif 'Lynx'.lower() in archive_name.lower():
			property_value = 'black.png'
		elif 'TurboGrafx'.lower() in archive_name.lower():
			property_value = 'tg16_bg.png'
		elif 'Amiga'.lower() in archive_name.lower():
			property_value = 'arcade_bg.png'
		else:
			property_value = 'black.png'
	elif property_name == 'button_focus':
		property_value = 'button-highlight1.png'
	elif property_name == 'button_nofocus':
		property_value = 'button-nofocus2.png'
	else:
		xbmc.log(msg='IARL:  Unable to define IARL theme for '+str(property_name), level=xbmc.LOGERROR)

	return property_value

def define_current_archive_data(iarl_data,current_index,page_id):
	archive_current_data = dict()
	archive_current_data['xml_id'] = iarl_data['archive_data']['xml_id'][current_index]
	archive_current_data['category_id'] = iarl_data['archive_data']['category_id'][current_index]
	archive_current_data['page_id'] = page_id
	archive_current_data['emu_name'] = iarl_data['archive_data']['emu_name'][current_index]
	archive_current_data['emu_homepage'] = iarl_data['archive_data']['emu_homepage'][current_index]
	archive_current_data['emu_base_url'] = iarl_data['archive_data']['emu_base_url'][current_index]
	archive_current_data['emu_filepath'] = iarl_data['archive_data']['emu_filepath'][current_index]
	archive_current_data['emu_parser'] = iarl_data['archive_data']['emu_parser'][current_index]
	archive_current_data['emu_category'] = iarl_data['archive_data']['emu_category'][current_index]
	archive_current_data['emu_version'] = iarl_data['archive_data']['emu_version'][current_index]
	archive_current_data['emu_date'] = iarl_data['archive_data']['emu_date'][current_index]
	archive_current_data['emu_author'] = iarl_data['archive_data']['emu_author'][current_index]
	archive_current_data['emu_description'] = iarl_data['archive_data']['emu_description'][current_index]
	archive_current_data['emu_plot'] = iarl_data['archive_data']['emu_plot'][current_index]
	archive_current_data['emu_boxart'] = iarl_data['archive_data']['emu_boxart'][current_index]
	archive_current_data['emu_banner'] = iarl_data['archive_data']['emu_banner'][current_index]
	archive_current_data['emu_fanart'] = iarl_data['archive_data']['emu_fanart'][current_index]
	archive_current_data['emu_logo'] = iarl_data['archive_data']['emu_logo'][current_index]
	archive_current_data['emu_trailer'] = iarl_data['archive_data']['emu_trailer'][current_index]
	archive_current_data['emu_download_path'] = iarl_data['archive_data']['emu_download_path'][current_index]
	archive_current_data['emu_post_download_action'] = iarl_data['archive_data']['emu_post_download_action'][current_index]
	archive_current_data['emu_launcher'] = iarl_data['archive_data']['emu_launcher'][current_index]
	archive_current_data['emu_ext_launch_cmd'] = iarl_data['archive_data']['emu_ext_launch_cmd'][current_index]
	archive_current_data['header_color'] = define_IARL_theme(archive_current_data['emu_name'],'header_color')
	archive_current_data['background_color'] = define_IARL_theme(archive_current_data['emu_name'],'background_color')
	archive_current_data['button_focus'] = define_IARL_theme(archive_current_data['emu_name'],'button_focus')
	archive_current_data['button_nofocus'] = define_IARL_theme(archive_current_data['emu_name'],'button_nofocus')
	archive_current_data['emu_total_num_games'] = None

	return archive_current_data

def parse_xml_romfile(iarl_data,current_index,plugin):
	items = []
	#Define the Parser
	descParser = DescriptionParserFactory.getParser(get_parser_file(iarl_data['archive_data']['emu_parser'][current_index]))
	#Parse results from the archive file
	results = descParser.parseDescription(iarl_data['archive_data']['emu_filepath'][current_index],'xml')

	xx=0
	for entries in results:
		#Define the current rom data

		iarl_data['current_rom_data']['rom_name'] = define_game_listitem('rom_name',None,entries)
		iarl_data['current_rom_data']['rom_icon'] = os.path.join(iarl_data['addon_data']['addon_media_path'],iarl_data['addon_data']['default_icon'])
		iarl_data['current_rom_data']['rom_thumbnail'] = define_game_listitem('rom_thumbnail',None,entries)
		iarl_data['current_rom_data']['rom_title'] = define_game_listitem('rom_title',iarl_data,entries)
		iarl_data['current_rom_data']['rom_studio'] = define_game_listitem('rom_studio',None,entries)
		iarl_data['current_rom_data']['rom_genre'] = define_game_listitem('rom_genre',None,entries)
		iarl_data['current_rom_data']['rom_date'] = define_game_listitem('rom_date',None,entries)
		iarl_data['current_rom_data']['rom_year'] = define_game_listitem('rom_year',None,entries)
		iarl_data['current_rom_data']['rom_plot'] = define_game_listitem('rom_plot',None,entries)
		iarl_data['current_rom_data']['rom_trailer'] = define_game_listitem('rom_trailer',None,entries)
		iarl_data['current_rom_data']['rom_tag'] = define_game_listitem('rom_tag',None,entries)
		iarl_data['current_rom_data']['rom_nplayers'] = define_game_listitem('rom_nplayers',None,entries)
		iarl_data['current_rom_data']['rom_rating'] = define_game_listitem('rom_rating',None,entries)
		iarl_data['current_rom_data']['rom_esrb'] = define_game_listitem('rom_esrb',None,entries)
		iarl_data['current_rom_data']['rom_perspective'] = define_game_listitem('rom_perspective',None,entries)
		iarl_data['current_rom_data']['rom_emu_command'] = define_game_listitem('rom_emu_command',None,entries)
		iarl_data['current_rom_data']['rom_override_cmd'] = define_game_listitem('rom_override_cmd',None,entries)
		iarl_data['current_rom_data']['rom_override_postdl'] = define_game_listitem('rom_override_postdl',None,entries)
		iarl_data['current_rom_data']['rom_override_downloadpath'] = define_game_listitem('rom_override_downloadpath',None,entries)
		iarl_data['current_rom_data']['rom_filenames'] = define_game_listitem('rom_filenames',iarl_data,entries)
		iarl_data['current_rom_data']['rom_supporting_filenames'] = define_game_listitem('rom_supporting_filenames',iarl_data,entries)
		iarl_data['current_rom_data']['rom_save_filenames'] = define_game_listitem('rom_save_filenames',iarl_data,entries)
		iarl_data['current_rom_data']['rom_save_supporting_filenames'] = define_game_listitem('rom_save_supporting_filenames',iarl_data,entries)
		iarl_data['current_rom_data']['rom_size'] = define_game_listitem('rom_size',iarl_data,entries)
		iarl_data['current_rom_data']['rom_label'] = define_game_listitem('rom_label',iarl_data,entries)
		for ii in range(0,total_arts):
			iarl_data['current_rom_data']['rom_fanarts'][ii] = define_game_listitem('rom_fanart'+str(ii+1),None,entries)
			iarl_data['current_rom_data']['rom_boxarts'][ii] = define_game_listitem('rom_boxart'+str(ii+1),None,entries)
			iarl_data['current_rom_data']['rom_banners'][ii] = define_game_listitem('rom_banner'+str(ii+1),None,entries)
			iarl_data['current_rom_data']['rom_snapshots'][ii] = define_game_listitem('rom_snapshot'+str(ii+1),None,entries)
			iarl_data['current_rom_data']['rom_logos'][ii] = define_game_listitem('rom_clearlogo'+str(ii+1),None,entries)

		#Append the current rom data to the list
		# items.append(plugin._listitemify({
		items.append({
	        'label' : iarl_data['current_rom_data']['rom_label'],
	        'label2' : iarl_data['current_rom_data']['rom_name'],
	        'icon': iarl_data['current_rom_data']['rom_icon'],
	        'thumbnail' : iarl_data['current_rom_data']['rom_thumbnail'],
	        'path' : plugin.url_for('get_selected_rom', category_id=iarl_data['current_archive_data']['category_id'], romname=iarl_data['current_rom_data']['rom_name']),
	        'info' : {'title' : iarl_data['current_rom_data']['rom_title'],
	        		  'genre': iarl_data['current_rom_data']['rom_genre'],
	        		  'year': iarl_data['current_rom_data']['rom_year'],
	        		  'studio': iarl_data['current_rom_data']['rom_studio'],
	        		  'date': iarl_data['current_rom_data']['rom_date'],
	        		  'plot': iarl_data['current_rom_data']['rom_plot'],
	        		  'trailer': iarl_data['current_rom_data']['rom_trailer'],
	        		  'rating': iarl_data['current_rom_data']['rom_rating'],
	        		  'mpaa' : iarl_data['current_rom_data']['rom_esrb'],
	        		  'size': sum(map(int,iarl_data['current_rom_data']['rom_size'])) #For display purposes only
	        		  },
	        'properties' : {'fanart_image' : iarl_data['current_rom_data']['rom_fanarts'][0],
							'banner' : iarl_data['current_rom_data']['rom_banners'][0],
							'clearlogo': iarl_data['current_rom_data']['rom_logos'][0],
							'poster': iarl_data['current_rom_data']['rom_thumbnail'],
							'tag': iarl_data['current_rom_data']['rom_tag'],
							'rating': iarl_data['current_rom_data']['rom_rating'],
							'perspective': iarl_data['current_rom_data']['rom_perspective'],
							'esrb': iarl_data['current_rom_data']['rom_esrb'],
							'rom_name': iarl_data['current_rom_data']['rom_name'],
							'rom_icon': iarl_data['current_rom_data']['rom_icon'],
							'rom_thumbnail': iarl_data['current_rom_data']['rom_thumbnail'],
							'rom_title': iarl_data['current_rom_data']['rom_title'],
							'rom_studio': iarl_data['current_rom_data']['rom_studio'],
							'rom_genre': iarl_data['current_rom_data']['rom_genre'],
							'rom_date': iarl_data['current_rom_data']['rom_date'],
							'rom_year': iarl_data['current_rom_data']['rom_year'],
							'rom_plot': iarl_data['current_rom_data']['rom_plot'],
							'rom_trailer': iarl_data['current_rom_data']['rom_trailer'],
							'rom_label': iarl_data['current_rom_data']['rom_label'],
							'fanart1': iarl_data['current_rom_data']['rom_fanarts'][0],
							'fanart2': iarl_data['current_rom_data']['rom_fanarts'][1],
							'fanart3': iarl_data['current_rom_data']['rom_fanarts'][2],
							'fanart4': iarl_data['current_rom_data']['rom_fanarts'][3],
							'fanart5': iarl_data['current_rom_data']['rom_fanarts'][4],
							'fanart6': iarl_data['current_rom_data']['rom_fanarts'][5],
							'fanart7': iarl_data['current_rom_data']['rom_fanarts'][6],
							'fanart8': iarl_data['current_rom_data']['rom_fanarts'][7],
							'fanart9': iarl_data['current_rom_data']['rom_fanarts'][8],
							'fanart10': iarl_data['current_rom_data']['rom_fanarts'][9],
							'banner1': iarl_data['current_rom_data']['rom_banners'][0],
							'banner2': iarl_data['current_rom_data']['rom_banners'][1],
							'banner3': iarl_data['current_rom_data']['rom_banners'][2],
							'banner4': iarl_data['current_rom_data']['rom_banners'][3],
							'banner5': iarl_data['current_rom_data']['rom_banners'][4],
							'banner6': iarl_data['current_rom_data']['rom_banners'][5],
							'banner7': iarl_data['current_rom_data']['rom_banners'][6],
							'banner8': iarl_data['current_rom_data']['rom_banners'][7],
							'banner9': iarl_data['current_rom_data']['rom_banners'][8],
							'banner10': iarl_data['current_rom_data']['rom_banners'][9],
							'snapshot1': iarl_data['current_rom_data']['rom_snapshots'][0],
							'snapshot2': iarl_data['current_rom_data']['rom_snapshots'][1],
							'snapshot3': iarl_data['current_rom_data']['rom_snapshots'][2],
							'snapshot4': iarl_data['current_rom_data']['rom_snapshots'][3],
							'snapshot5': iarl_data['current_rom_data']['rom_snapshots'][4],
							'snapshot6': iarl_data['current_rom_data']['rom_snapshots'][5],
							'snapshot7': iarl_data['current_rom_data']['rom_snapshots'][6],
							'snapshot8': iarl_data['current_rom_data']['rom_snapshots'][7],
							'snapshot9': iarl_data['current_rom_data']['rom_snapshots'][8],
							'snapshot10': iarl_data['current_rom_data']['rom_snapshots'][9],
							'boxart1': iarl_data['current_rom_data']['rom_boxarts'][0],
							'boxart2': iarl_data['current_rom_data']['rom_boxarts'][1],
							'boxart3': iarl_data['current_rom_data']['rom_boxarts'][2],
							'boxart4': iarl_data['current_rom_data']['rom_boxarts'][3],
							'boxart5': iarl_data['current_rom_data']['rom_boxarts'][4],
							'boxart6': iarl_data['current_rom_data']['rom_boxarts'][5],
							'boxart7': iarl_data['current_rom_data']['rom_boxarts'][6],
							'boxart8': iarl_data['current_rom_data']['rom_boxarts'][7],
							'boxart9': iarl_data['current_rom_data']['rom_boxarts'][8],
							'boxart10': iarl_data['current_rom_data']['rom_boxarts'][9],
							'logo1': iarl_data['current_rom_data']['rom_logos'][0],
							'logo2': iarl_data['current_rom_data']['rom_logos'][1],
							'logo3': iarl_data['current_rom_data']['rom_logos'][2],
							'logo4': iarl_data['current_rom_data']['rom_logos'][3],
							'logo5': iarl_data['current_rom_data']['rom_logos'][4],
							'logo6': iarl_data['current_rom_data']['rom_logos'][5],
							'logo7': iarl_data['current_rom_data']['rom_logos'][6],
							'logo8': iarl_data['current_rom_data']['rom_logos'][7],
							'logo9': iarl_data['current_rom_data']['rom_logos'][8],
							'logo10': iarl_data['current_rom_data']['rom_logos'][9],
							'nplayers': iarl_data['current_rom_data']['rom_nplayers'],
							#Need to convert lists into comma seperated strings for listitem properties
							'rom_filenames': ','.join(map(str, iarl_data['current_rom_data']['rom_filenames'])),
							'rom_file_sizes': ','.join(map(str, iarl_data['current_rom_data']['rom_size'])),
							'rom_supporting_filenames': ','.join(map(str, iarl_data['current_rom_data']['rom_supporting_filenames'])),
							'rom_save_filenames': ','.join(map(str, iarl_data['current_rom_data']['rom_save_filenames'])),
							'rom_save_supporting_filenames': ','.join(map(str, iarl_data['current_rom_data']['rom_save_supporting_filenames'])),
							'rom_emu_command': iarl_data['current_rom_data']['rom_emu_command'],
							'rom_override_cmd': iarl_data['current_rom_data']['rom_override_cmd'],
							'rom_override_postdl': iarl_data['current_rom_data']['rom_override_postdl'],
							'rom_override_downloadpath': iarl_data['current_rom_data']['rom_override_downloadpath'],
							'emu_name' : iarl_data['current_archive_data']['emu_name'],
							'category_id' : iarl_data['current_archive_data']['category_id'],
							'emu_parser' : iarl_data['current_archive_data']['emu_parser'],
							'emu_filepath' : iarl_data['current_archive_data']['emu_filepath'],
							'emu_plot' : iarl_data['current_archive_data']['emu_plot'],
							'emu_category' : iarl_data['current_archive_data']['emu_category'],
							'emu_version' : iarl_data['current_archive_data']['emu_version'],
							'emu_date' : iarl_data['current_archive_data']['emu_date'],
							'emu_author' : iarl_data['current_archive_data']['emu_author'],
							'emu_base_url' : iarl_data['current_archive_data']['emu_base_url'],
							'emu_download_path' : iarl_data['current_archive_data']['emu_download_path'],
							'emu_post_download_action' : iarl_data['current_archive_data']['emu_post_download_action'],
							'emu_launcher' : iarl_data['current_archive_data']['emu_launcher'],
							'emu_ext_launch_cmd' : iarl_data['current_archive_data']['emu_ext_launch_cmd'],
							'emu_boxart' : iarl_data['current_archive_data']['emu_boxart'],
							'emu_banner' : iarl_data['current_archive_data']['emu_banner'],
							'emu_fanart' : iarl_data['current_archive_data']['emu_fanart'],
							'emu_logo': iarl_data['current_archive_data']['emu_logo'],
							'emu_trailer': iarl_data['current_archive_data']['emu_trailer']
							},
	        				'context_menu': None
							})

	return items

def define_game_listitem(property_name,iarl_data,rom_info):
	property_value = None
	property_sub_value = None
	label_sep = '  |  '
	xstr = lambda s: s or ''
	try:
		current_rom_info_item_name = xstr(rom_info['rom_name'][0])
	except:
		current_rom_info_item_name = '???'

	try:
		if property_name == 'rom_label':
			if iarl_data['settings']['naming_convention'] == 'Title':
				property_value = iarl_data['current_rom_data']['rom_title']
			elif iarl_data['settings']['naming_convention'] == 'Title, Genre':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre']
			elif iarl_data['settings']['naming_convention'] == 'Title, Date':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_date']
			elif iarl_data['settings']['naming_convention'] == 'Title, Players':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_nplayers']
			elif iarl_data['settings']['naming_convention'] == 'Title, Genre, Date':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre'] + label_sep + iarl_data['current_rom_data']['rom_date']
			elif iarl_data['settings']['naming_convention'] == 'Title, Genre, Players':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre'] + label_sep + iarl_data['current_rom_data']['rom_nplayers']
			elif iarl_data['settings']['naming_convention'] == 'Genre, Title':
				property_value = iarl_data['current_rom_data']['rom_genre'] + label_sep + iarl_data['current_rom_data']['rom_title']
			elif iarl_data['settings']['naming_convention'] == 'Date, Title':
				property_value = iarl_data['current_rom_data']['rom_date'] + label_sep + iarl_data['current_rom_data']['rom_title']
			elif iarl_data['settings']['naming_convention'] == 'Genre, Title, Date':
				property_value = iarl_data['current_rom_data']['rom_genre']+ label_sep + iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_date']
			elif iarl_data['settings']['naming_convention'] == 'Players, Title, Date':
				property_value = iarl_data['current_rom_data']['rom_nplayers']+ label_sep + iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_date']
			elif iarl_data['settings']['naming_convention'] == 'Date, Title, Genre':
				property_value = iarl_data['current_rom_data']['rom_date'] + label_sep + iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre']
			elif iarl_data['settings']['naming_convention'] == 'Players, Title, Genre':
				property_value = iarl_data['current_rom_data']['rom_nplayers'] + label_sep + iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre']
			elif iarl_data['settings']['naming_convention'] == 'Title, Genre, Date, ROM Tag':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre'] + label_sep + iarl_data['current_rom_data']['rom_date'] + label_sep + iarl_data['current_rom_data']['rom_tag']
			elif iarl_data['settings']['naming_convention'] == 'Title, Genre, Date, Players':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre'] + label_sep + iarl_data['current_rom_data']['rom_date'] + label_sep + iarl_data['current_rom_data']['rom_nplayers']
			elif iarl_data['settings']['naming_convention'] == 'Title, Genre, Players, ROM Tag':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre'] + label_sep + iarl_data['current_rom_data']['rom_nplayers'] + label_sep + iarl_data['current_rom_data']['rom_tag']
			elif iarl_data['settings']['naming_convention'] == 'Title, Genre, Size':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre'] + label_sep + bytes_to_string_size(iarl_data['current_rom_data']['rom_size'])
			elif iarl_data['settings']['naming_convention'] == 'Title, Date, Size':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_date'] + label_sep + bytes_to_string_size(iarl_data['current_rom_data']['rom_size'])
			elif iarl_data['settings']['naming_convention'] == 'Title, Date, Players':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_date'] + label_sep + iarl_data['current_rom_data']['rom_nplayers']
			elif iarl_data['settings']['naming_convention'] == 'Title, Genre, Date, Size':
				property_value = iarl_data['current_rom_data']['rom_title'] + label_sep + iarl_data['current_rom_data']['rom_genre'] + label_sep + iarl_data['current_rom_data']['rom_date'] + label_sep + bytes_to_string_size(iarl_data['current_rom_data']['rom_size'])
			else:
				property_value = property_sub_value
		elif property_name == 'rom_title':
			if iarl_data['settings']['clean_list']:
				property_sub_value = xstr(rom_tag_regex.sub('', rom_info['rom_name'][0]).strip()) #Clean rom name
			else:
				property_sub_value = xstr(rom_info['rom_name'][0])
			property_value = property_sub_value
		elif property_name == 'rom_tag':
			if '(' in rom_info['rom_name'][0]:
				property_sub_value = xstr(rom_tag_regex.search(rom_info['rom_name'][0]).group(0).replace('(','').replace(')','').strip()) #Grab value between parens
			else:
				property_sub_value = None
			property_value = property_sub_value
		elif property_name == 'rom_thumbnail':
			for ii in range(0,total_arts):
				if property_sub_value is None:
					if rom_info['rom_boxart'+str(ii+1)]:
						property_sub_value = rom_info['rom_boxart'+str(ii+1)][0] #Search through all the boxarts, make the thumb the first one
				if property_sub_value is None: #If there is no boxart, then make the thumnail a snapshot if avialable
					if rom_info['rom_snapshot'+str(ii+1)]:
						property_sub_value = rom_info['rom_snapshot'+str(ii+1)][0] #Search through all the snapshots, make the thumb the first one
			property_value = html_unescape(xstr(property_sub_value))
		elif property_name == 'rom_date':
			if rom_info['rom_date'] and len(rom_info['rom_date'])>0:
				property_sub_value = date_parser.parse(xstr(rom_info['rom_date'][0])).strftime(addon_date_format)
			else:
				if rom_info['rom_year'] and len(rom_info['rom_year'])>0: #Generate the date based on the year tag if no date tag is present
					property_sub_value = date_parser.parse('1/1/'+xstr(rom_info['rom_year'][0])).strftime(addon_date_format)
				# else:
				# 	property_value = date_parser.parse('1/1/9999').strftime(addon_date_format)
			property_value = property_sub_value
		elif property_name == 'rom_year':
			if rom_info['rom_year'] and len(rom_info['rom_year'])>0:
				property_sub_value = rom_info['rom_year'][0]
			else:
				if rom_info['rom_date'] and len(rom_info['rom_date'])>0: #Generate the year based on the releasedate tag if no year tag is present
					property_sub_value = date_parser.parse(xstr(rom_info['rom_date'][0])).strftime(addon_year_format)
			property_value = property_sub_value
		elif property_name == 'rom_trailer':
			if rom_info['rom_videoid']:
				property_value = get_youtube_plugin_url(rom_info['rom_videoid'][0])
			else:
				property_value = None
		elif property_name == 'rom_size':
			property_value = list()
			if len(iarl_data['current_rom_data']['rom_save_filenames'])>1: #If more than one file is defined
				for rom_file_sizes in rom_info['rom_size']:
					property_value.append(int(rom_file_sizes))
			else: #Only one file is defined, so sum up all the sizes listed to get the total (used for MAME rom DAT files)
				property_value.append(sum(map(int,rom_info['rom_size'])))
		elif property_name == 'rom_filenames':
			property_value = list()
			for rom_file_name in rom_info['rom_filename']:
				if rom_file_name is not None:
					if len(rom_file_name)>0:
						if 'MAME'.lower() in iarl_data['current_archive_data']['emu_parser'].lower():
							if 'zip'.lower() not in rom_file_name:
								rom_file_name = rom_file_name+'.zip' #Sometimes MAME archives dont append the extension, so add it
						property_value.append(html_unescape(iarl_data['current_archive_data']['emu_base_url']+xstr(rom_file_name).replace(',',''))) #Commas removed for zipfiles, they dont like that
		elif property_name == 'rom_save_filenames':
			property_value = list()

			#Determine what the save location should be
			if iarl_data['current_rom_data']['rom_override_downloadpath'] is not None and len(iarl_data['current_rom_data']['rom_override_downloadpath']) > 0:
				download_path = iarl_data['current_rom_data']['rom_override_downloadpath']
			else:
				download_path = iarl_data['current_archive_data']['emu_download_path']
							
			if 'default' in download_path:
				iarl_data['current_archive_data']['emu_download_path'] = iarl_data['addon_data']['addon_temp_dl_path']
			else:
				iarl_data['current_archive_data']['emu_download_path'] = download_path

			for rom_file_name in rom_info['rom_filename']:
				if rom_file_name is not None:
					if len(rom_file_name)>0:
						if 'MAME'.lower() in iarl_data['current_archive_data']['emu_parser'].lower():
							if 'zip'.lower() not in rom_file_name:
								rom_file_name = rom_file_name+'.zip' #Sometimes MAME archives dont append the extension, so add it
						property_value.append(os.path.join(iarl_data['current_archive_data']['emu_download_path'],os.path.split(unquote_text(xstr(rom_file_name)))[-1].replace(',',''))) #Commas removed for zipfiles, they dont like that
		elif property_name == 'rom_supporting_filenames':
			property_value = list()
			for rom_sup_file_name in rom_info['rom_supporting_file']:
				if rom_sup_file_name is not None:
					if len(rom_sup_file_name)>0:
						if 'MAME'.lower() in iarl_data['current_archive_data']['emu_parser'].lower():
							if 'zip'.lower() not in rom_sup_file_name:
								rom_sup_file_name = rom_sup_file_name+'.zip' #Sometimes MAME archives dont append the extension, so add it
						property_value.append(html_unescape(iarl_data['current_archive_data']['emu_base_url']+xstr(rom_sup_file_name).replace(',',''))) #Commas removed for zipfiles, they dont like that
		elif property_name == 'rom_save_supporting_filenames':
			property_value = list()

			#Determine what the save location should be
			if iarl_data['current_rom_data']['rom_override_downloadpath'] is not None and len(iarl_data['current_rom_data']['rom_override_downloadpath']) > 0:
				download_path = iarl_data['current_rom_data']['rom_override_downloadpath']
			else:
				download_path = iarl_data['current_archive_data']['emu_download_path']

			if 'default' in download_path:
				iarl_data['current_archive_data']['emu_download_path'] = iarl_data['addon_data']['addon_temp_dl_path']
			else:
				iarl_data['current_archive_data']['emu_download_path'] = download_path
				
			for rom_sup_file_name in rom_info['rom_supporting_file']:
				if rom_sup_file_name is not None:
					if len(rom_sup_file_name)>0:
						if 'MAME'.lower() in iarl_data['current_archive_data']['emu_parser'].lower():
							if 'zip'.lower() not in rom_sup_file_name:
								rom_sup_file_name = rom_sup_file_name+'.zip' #Sometimes MAME archives dont append the extension, so add it
						property_value.append(os.path.join(iarl_data['current_archive_data']['emu_download_path'],os.path.split(unquote_text(xstr(rom_sup_file_name)))[-1].replace(',',''))) #Commas removed for zipfiles, they dont like that
		else: #By default, set the property value to the same name
			if property_name in rom_info.keys():
				if rom_info[property_name] is not None:
					if len(rom_info[property_name])>0:
						if rom_info[property_name][0] is not None:
							if 'http' in rom_info[property_name][0]: #The property is a URL, so unescape it
								property_value = html_unescape(rom_info[property_name][0])
							else: #The property is a string
								property_value = xstr(rom_info[property_name][0])
	except:
		xbmc.log(msg='IARL:  Unable to define listitem property '+str(property_name)+' for '+str(current_rom_info_item_name), level=xbmc.LOGERROR)

	if property_value is None:
		property_value = ''

	return property_value

def query_favorites_xml(iarl_data):
	favorites_xml_filename = None
	favorite_xmls = dict()
	favorite_xmls['emu_name'] = list()
	favorite_xmls['emu_filepath'] = list()

	#Find all of the available favorites xml files
	for ii in range(0,len(iarl_data['archive_data']['emu_name'])):
		if 'IARL_Favorites'.lower() in iarl_data['archive_data']['emu_description'][ii].lower():
			favorite_xmls['emu_name'].append(iarl_data['archive_data']['emu_name'][ii])
			favorite_xmls['emu_filepath'].append(iarl_data['archive_data']['emu_filepath'][ii])

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
				current_xml_path = current_xml_fileparts[0]
				update_xml_header(current_xml_path,current_xml_filename,'emu_name',ret2)
				favorites_xml_filename = saved_filename
	elif favorite_xmls['emu_name'][ret1] == favorite_xmls['emu_name'][-1]: #Cancel adding favorite
		xbmc.log(msg='IARL:  Adding favorite was cancelled', level=xbmc.LOGDEBUG)
		favorites_xml_filename = None
	else:
		favorites_xml_filename = favorite_xmls['emu_filepath'][ret1]

	return favorites_xml_filename

def create_new_favorites_list(new_filename):
	saved_filename = None
	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Favorites List Emulator Launcher', ['Kodi RetroPlayer','External'])
	if ret1 < 1:
		template_path = get_parser_file('Favorites_Template.xml')
	else:
		template_path = get_parser_file('Favorites_Template_External.xml')
	dat_path = get_XML_files_path()
	new_xml_filename = os.path.join(dat_path,new_filename+'.xml')
	copyFile(template_path, new_xml_filename)
	if os.path.exists(new_xml_filename):
		saved_filename = new_xml_filename
	return saved_filename

def add_favorite_to_xml(iarl_data,favorites_xml_filename):
	add_success = False
	xml_string = ''
	current_rom_command = ''
	strip_base_url_string_1 = 'http://archive.org/download/'
	strip_base_url_string_2 = 'https://archive.org/download/'
	xstr = lambda s: txt_escape(s) or ''

	#Create favorite rom command	
	try: current_rom_command = current_rom_command+xstr(iarl_data['current_rom_data']['emu_post_download_action'])
	except: pass
	try: current_rom_command = current_rom_command+'|'+xstr(iarl_data['current_rom_data']['rom_emu_command'])
	except: pass
	if current_rom_command[0] == '|':
		current_rom_command = current_rom_command[1:]
	if current_rom_command[-1] == '|':
		current_rom_command = current_rom_command[:-1]

	try: xml_string = xml_string+'<game name="%GAME_TITLE%">\r\n'.replace('%GAME_TITLE%',xstr(iarl_data['current_rom_data']['rom_name']))
	except: pass
	try: xml_string = xml_string+'<description>%GAME_TITLE%</description>\r\n'.replace('%GAME_TITLE%',xstr(iarl_data['current_rom_data']['rom_name']))
	except: pass
	for ii in range(0,len(iarl_data['current_rom_data']['rom_filenames'])):
		try:
			xml_string = xml_string+'<rom name="%ROM_URL%" size="%ROM_SIZE%"/>\r\n'.replace('%ROM_URL%',iarl_data['current_rom_data']['rom_filenames'][ii].replace(strip_base_url_string_1,'').replace(strip_base_url_string_2,'')).replace('%ROM_SIZE%',str(iarl_data['current_rom_data']['rom_size'][ii]))
		except:
			try:
				xml_string = xml_string+'<rom name="%ROM_URL%" size="%ROM_SIZE%"/>\r\n'.replace('%ROM_URL%',iarl_data['current_rom_data']['rom_filenames'][ii].replace(strip_base_url_string_1,'').replace(strip_base_url_string_2,'')).replace('%ROM_SIZE%',str(99999))
			except:
				pass
	for ii in range(0,len(iarl_data['current_rom_data']['rom_supporting_filenames'])):
		try: xml_string = xml_string+'<rom name="%ROM_URL%" size="%ROM_SIZE%"/>\r\n'.replace('%ROM_URL%',iarl_data['current_rom_data']['rom_supporting_filenames'][ii].replace(strip_base_url_string_1,'').replace(strip_base_url_string_2,'')).replace('%ROM_SIZE%',str(99999)) #Size of supporting files is unknown, so just make it a big number
		except: pass

	#Provide new launching commands.  If there is an override command already present, we will use that.  Otherwise, we will use the current archives command.
	if iarl_data['settings']['hard_code_favorite_settings']: #Only need to define these settings for hard coded favorites
		if iarl_data['current_rom_data']['rom_override_cmd'] is not None and len(iarl_data['current_rom_data']['rom_override_cmd']) > 0:
			xml_string = xml_string+'<rom_override_cmd>%ROM_OVERRIDE_CMD%</rom_override_cmd>\r\n'.replace('%ROM_OVERRIDE_CMD%',xstr(iarl_data['current_rom_data']['rom_override_cmd']))
			# except: pass
		else:
			xml_string = xml_string+'<rom_override_cmd>%ROM_OVERRIDE_CMD%</rom_override_cmd>\r\n'.replace('%ROM_OVERRIDE_CMD%',xstr(iarl_data['current_rom_data']['emu_ext_launch_cmd']))
			# except: pass
		#Provide new post DL commands.  If there is an override command already present, we will use that.  Otherwise, we will use the current archives command.
		if iarl_data['current_rom_data']['rom_override_postdl'] is not None and len(iarl_data['current_rom_data']['rom_override_postdl']) > 0:
			try: xml_string = xml_string+'<rom_override_postdl>%ROM_OVERRIDE_POSTDL%</rom_override_postdl>\r\n'.replace('%ROM_OVERRIDE_POSTDL%',xstr(iarl_data['current_rom_data']['rom_override_postdl']))
			except: pass
		else:
			try: xml_string = xml_string+'<rom_override_postdl>%ROM_OVERRIDE_POSTDL%</rom_override_postdl>\r\n'.replace('%ROM_OVERRIDE_POSTDL%',xstr(iarl_data['current_rom_data']['emu_post_download_action']))
			except: pass
		#Provide new post DL commands.  If there is an override command already present, we will use that.  Otherwise, we will use the current archives command.
		if iarl_data['current_rom_data']['rom_override_downloadpath'] is not None and len(iarl_data['current_rom_data']['rom_override_downloadpath']) > 0:
			try: xml_string = xml_string+'<rom_override_downloadpath>%ROM_OVERRIDE_DLPATH%</rom_override_downloadpath>\r\n'.replace('%ROM_OVERRIDE_DLPATH%',xstr(iarl_data['current_rom_data']['rom_override_downloadpath']))
			except: pass
		#Provide new DL location.	If there is an override command already present, we will use that.  Otherwise, we will use the current archives location.
		else:
			try:
				if iarl_data['current_rom_data']['emu_download_path'] != iarl_data['addon_data']['addon_temp_dl_path']:
					xml_string = xml_string+'<rom_override_downloadpath>%ROM_OVERRIDE_DLPATH%</rom_override_downloadpath>\r\n'.replace('%ROM_OVERRIDE_DLPATH%',xstr(iarl_data['current_rom_data']['emu_download_path']))
				else:
					xml_string = xml_string+'<rom_override_downloadpath>%ROM_OVERRIDE_DLPATH%</rom_override_downloadpath>\r\n'.replace('%ROM_OVERRIDE_DLPATH%','default')
			except:
				pass
	try: xml_string = xml_string+'<plot>%GAME_PLOT%</plot>\r\n'.replace('%GAME_PLOT%',xstr(iarl_data['current_rom_data']['rom_plot']))
	except: pass
	try: xml_string = xml_string+'<year>%GAME_YEAR%</year>\r\n'.replace('%GAME_YEAR%',xstr(iarl_data['current_rom_data']['rom_year']))
	except: pass
	try: xml_string = xml_string+'<releasedate>%GAME_DATE%</releasedate>\r\n'.replace('%GAME_DATE%',xstr(iarl_data['current_rom_data']['rom_date']))
	except: pass
	try: xml_string = xml_string+'<genre>%GAME_GENRE%</genre>\r\n'.replace('%GAME_GENRE%',xstr(iarl_data['current_rom_data']['rom_genre']))
	except: pass
	try: xml_string = xml_string+'<studio>%GAME_STUDIO%</studio>\r\n'.replace('%GAME_STUDIO%',xstr(iarl_data['current_rom_data']['rom_studio']))
	except: pass
	try: xml_string = xml_string+'<nplayers>%GAME_NPLAYERS%</nplayers>\r\n'.replace('%GAME_NPLAYERS%',xstr(iarl_data['current_rom_data']['rom_nplayers']))
	except: pass
	try: xml_string = xml_string+'<perspective>%GAME_PERSPECTIVE%</perspective>\r\n'.replace('%GAME_PERSPECTIVE%',xstr(iarl_data['current_rom_data']['rom_perspective']))
	except: pass
	try: xml_string = xml_string+'<rating>%GAME_RATING%</rating>\r\n'.replace('%GAME_RATING%',xstr(iarl_data['current_rom_data']['rom_rating']))
	except: pass
	try: xml_string = xml_string+'<ESRB>%GAME_ESRB%</ESRB>\r\n'.replace('%GAME_ESRB%',xstr(iarl_data['current_rom_data']['rom_esrb']))
	except: pass
	try: xml_string = xml_string+'<videoid>%GAME_VIDEOID%</videoid>\r\n'.replace('%GAME_VIDEOID%',xstr(iarl_data['current_rom_data']['rom_trailer']).split('=')[-1]) #Only add the video ID
	except: pass
	try: xml_string = xml_string+'\r\n\r\n<boxart1>%GAME_boxart1%</boxart1>\r\n'.replace('%GAME_boxart1%',xstr(iarl_data['current_rom_data']['rom_boxarts'][0]))
	except: pass
	try: xml_string = xml_string+'<boxart2>%GAME_boxart2%</boxart2>\r\n'.replace('%GAME_boxart2%',xstr(iarl_data['current_rom_data']['rom_boxarts'][1]))
	except: pass
	try: xml_string = xml_string+'<boxart3>%GAME_boxart3%</boxart3>\r\n'.replace('%GAME_boxart3%',xstr(iarl_data['current_rom_data']['rom_boxarts'][2]))
	except: pass
	try: xml_string = xml_string+'<boxart4>%GAME_boxart4%</boxart4>\r\n'.replace('%GAME_boxart4%',xstr(iarl_data['current_rom_data']['rom_boxarts'][3]))
	except: pass
	try: xml_string = xml_string+'<boxart5>%GAME_boxart5%</boxart5>\r\n'.replace('%GAME_boxart5%',xstr(iarl_data['current_rom_data']['rom_boxarts'][4]))
	except: pass
	try: xml_string = xml_string+'<boxart6>%GAME_boxart6%</boxart6>\r\n'.replace('%GAME_boxart6%',xstr(iarl_data['current_rom_data']['rom_boxarts'][5]))
	except: pass
	try: xml_string = xml_string+'<boxart7>%GAME_boxart7%</boxart7>\r\n'.replace('%GAME_boxart7%',xstr(iarl_data['current_rom_data']['rom_boxarts'][6]))
	except: pass
	try: xml_string = xml_string+'<boxart8>%GAME_boxart8%</boxart8>\r\n'.replace('%GAME_boxart8%',xstr(iarl_data['current_rom_data']['rom_boxarts'][7]))
	except: pass
	try: xml_string = xml_string+'<boxart9>%GAME_boxart9%</boxart9>\r\n'.replace('%GAME_boxart9%',xstr(iarl_data['current_rom_data']['rom_boxarts'][8]))
	except: pass
	try: xml_string = xml_string+'<boxart10>%GAME_boxart10%</boxart10>\r\n'.replace('%GAME_boxart10%',xstr(iarl_data['current_rom_data']['rom_boxarts'][9]))
	except: pass
	try: xml_string = xml_string+'\r\n\r\n<snapshot1>%GAME_snapshot1%</snapshot1>\r\n'.replace('%GAME_snapshot1%',xstr(iarl_data['current_rom_data']['rom_snapshots'][0]))
	except: pass
	try: xml_string = xml_string+'<snapshot2>%GAME_snapshot2%</snapshot2>\r\n'.replace('%GAME_snapshot2%',xstr(iarl_data['current_rom_data']['rom_snapshots'][1]))
	except: pass
	try: xml_string = xml_string+'<snapshot3>%GAME_snapshot3%</snapshot3>\r\n'.replace('%GAME_snapshot3%',xstr(iarl_data['current_rom_data']['rom_snapshots'][2]))
	except: pass
	try: xml_string = xml_string+'<snapshot4>%GAME_snapshot4%</snapshot4>\r\n'.replace('%GAME_snapshot4%',xstr(iarl_data['current_rom_data']['rom_snapshots'][3]))
	except: pass
	try: xml_string = xml_string+'<snapshot5>%GAME_snapshot5%</snapshot5>\r\n'.replace('%GAME_snapshot5%',xstr(iarl_data['current_rom_data']['rom_snapshots'][4]))
	except: pass
	try: xml_string = xml_string+'<snapshot6>%GAME_snapshot6%</snapshot6>\r\n'.replace('%GAME_snapshot6%',xstr(iarl_data['current_rom_data']['rom_snapshots'][5]))
	except: pass
	try: xml_string = xml_string+'<snapshot7>%GAME_snapshot7%</snapshot7>\r\n'.replace('%GAME_snapshot7%',xstr(iarl_data['current_rom_data']['rom_snapshots'][6]))
	except: pass
	try: xml_string = xml_string+'<snapshot8>%GAME_snapshot8%</snapshot8>\r\n'.replace('%GAME_snapshot8%',xstr(iarl_data['current_rom_data']['rom_snapshots'][7]))
	except: pass
	try: xml_string = xml_string+'<snapshot9>%GAME_snapshot9%</snapshot9>\r\n'.replace('%GAME_snapshot9%',xstr(iarl_data['current_rom_data']['rom_snapshots'][8]))
	except: pass
	try: xml_string = xml_string+'<snapshot10>%GAME_snapshot10%</snapshot10>\r\n'.replace('%GAME_snapshot10%',xstr(iarl_data['current_rom_data']['rom_snapshots'][9]))
	except: pass
	try: xml_string = xml_string+'\r\n\r\n<fanart1>%GAME_fanart1%</fanart1>\r\n'.replace('%GAME_fanart1%',xstr(iarl_data['current_rom_data']['rom_fanarts'][0]))
	except: pass
	try: xml_string = xml_string+'<fanart2>%GAME_fanart2%</fanart2>\r\n'.replace('%GAME_fanart2%',xstr(iarl_data['current_rom_data']['rom_fanarts'][1]))
	except: pass
	try: xml_string = xml_string+'<fanart3>%GAME_fanart3%</fanart3>\r\n'.replace('%GAME_fanart3%',xstr(iarl_data['current_rom_data']['rom_fanarts'][2]))
	except: pass
	try: xml_string = xml_string+'<fanart4>%GAME_fanart4%</fanart4>\r\n'.replace('%GAME_fanart4%',xstr(iarl_data['current_rom_data']['rom_fanarts'][3]))
	except: pass
	try: xml_string = xml_string+'<fanart5>%GAME_fanart5%</fanart5>\r\n'.replace('%GAME_fanart5%',xstr(iarl_data['current_rom_data']['rom_fanarts'][4]))
	except: pass
	try: xml_string = xml_string+'<fanart6>%GAME_fanart6%</fanart6>\r\n'.replace('%GAME_fanart6%',xstr(iarl_data['current_rom_data']['rom_fanarts'][5]))
	except: pass
	try: xml_string = xml_string+'<fanart7>%GAME_fanart7%</fanart7>\r\n'.replace('%GAME_fanart7%',xstr(iarl_data['current_rom_data']['rom_fanarts'][6]))
	except: pass
	try: xml_string = xml_string+'<fanart8>%GAME_fanart8%</fanart8>\r\n'.replace('%GAME_fanart8%',xstr(iarl_data['current_rom_data']['rom_fanarts'][7]))
	except: pass
	try: xml_string = xml_string+'<fanart9>%GAME_fanart9%</fanart9>\r\n'.replace('%GAME_fanart9%',xstr(iarl_data['current_rom_data']['rom_fanarts'][8]))
	except: pass
	try: xml_string = xml_string+'<fanart10>%GAME_fanart10%</fanart10>\r\n'.replace('%GAME_fanart10%',xstr(iarl_data['current_rom_data']['rom_fanarts'][9]))
	except: pass
	try: xml_string = xml_string+'\r\n\r\n<banner1>%GAME_banner1%</banner1>\r\n'.replace('%GAME_banner1%',xstr(iarl_data['current_rom_data']['rom_banners'][0]))
	except: pass
	try: xml_string = xml_string+'<banner2>%GAME_banner2%</banner2>\r\n'.replace('%GAME_banner2%',xstr(iarl_data['current_rom_data']['rom_banners'][1]))
	except: pass
	try: xml_string = xml_string+'<banner3>%GAME_banner3%</banner3>\r\n'.replace('%GAME_banner3%',xstr(iarl_data['current_rom_data']['rom_banners'][2]))
	except: pass
	try: xml_string = xml_string+'<banner4>%GAME_banner4%</banner4>\r\n'.replace('%GAME_banner4%',xstr(iarl_data['current_rom_data']['rom_banners'][3]))
	except: pass
	try: xml_string = xml_string+'<banner5>%GAME_banner5%</banner5>\r\n'.replace('%GAME_banner5%',xstr(iarl_data['current_rom_data']['rom_banners'][4]))
	except: pass
	try: xml_string = xml_string+'<banner6>%GAME_banner6%</banner6>\r\n'.replace('%GAME_banner6%',xstr(iarl_data['current_rom_data']['rom_banners'][5]))
	except: pass
	try: xml_string = xml_string+'<banner7>%GAME_banner7%</banner7>\r\n'.replace('%GAME_banner7%',xstr(iarl_data['current_rom_data']['rom_banners'][6]))
	except: pass
	try: xml_string = xml_string+'<banner8>%GAME_banner8%</banner8>\r\n'.replace('%GAME_banner8%',xstr(iarl_data['current_rom_data']['rom_banners'][7]))
	except: pass
	try: xml_string = xml_string+'<banner9>%GAME_banner9%</banner9>\r\n'.replace('%GAME_banner9%',xstr(iarl_data['current_rom_data']['rom_banners'][8]))
	except: pass
	try: xml_string = xml_string+'<banner10>%GAME_banner10%</banner10>\r\n'.replace('%GAME_banner10%',xstr(iarl_data['current_rom_data']['rom_banners'][9]))
	except: pass
	try: xml_string = xml_string+'\r\n\r\n<clearlogo1>%GAME_clearlogo1%</clearlogo1>\r\n'.replace('%GAME_clearlogo1%',xstr(iarl_data['current_rom_data']['rom_logos'][0]))
	except: pass
	try: xml_string = xml_string+'<clearlogo2>%GAME_clearlogo2%</clearlogo2>\r\n'.replace('%GAME_clearlogo2%',xstr(iarl_data['current_rom_data']['rom_logos'][1]))
	except: pass
	try: xml_string = xml_string+'<clearlogo3>%GAME_clearlogo3%</clearlogo3>\r\n'.replace('%GAME_clearlogo3%',xstr(iarl_data['current_rom_data']['rom_logos'][2]))
	except: pass
	try: xml_string = xml_string+'<clearlogo4>%GAME_clearlogo4%</clearlogo4>\r\n'.replace('%GAME_clearlogo4%',xstr(iarl_data['current_rom_data']['rom_logos'][3]))
	except: pass
	try: xml_string = xml_string+'<clearlogo5>%GAME_clearlogo5%</clearlogo5>\r\n'.replace('%GAME_clearlogo5%',xstr(iarl_data['current_rom_data']['rom_logos'][4]))
	except: pass
	try: xml_string = xml_string+'<clearlogo6>%GAME_clearlogo6%</clearlogo6>\r\n'.replace('%GAME_clearlogo6%',xstr(iarl_data['current_rom_data']['rom_logos'][5]))
	except: pass
	try: xml_string = xml_string+'<clearlogo7>%GAME_clearlogo7%</clearlogo7>\r\n'.replace('%GAME_clearlogo7%',xstr(iarl_data['current_rom_data']['rom_logos'][6]))
	except: pass
	try: xml_string = xml_string+'<clearlogo8>%GAME_clearlogo8%</clearlogo8>\r\n'.replace('%GAME_clearlogo8%',xstr(iarl_data['current_rom_data']['rom_logos'][7]))
	except: pass
	try: xml_string = xml_string+'<clearlogo9>%GAME_clearlogo9%</clearlogo9>\r\n'.replace('%GAME_clearlogo9%',xstr(iarl_data['current_rom_data']['rom_logos'][8]))
	except: pass
	try: xml_string = xml_string+'<clearlogo10>%GAME_clearlogo10%</clearlogo10>\r\n'.replace('%GAME_clearlogo10%',xstr(iarl_data['current_rom_data']['rom_logos'][9]))
	except: pass
	try: xml_string = xml_string+'\r\n\r\n<emu_command>%GAME_COMMAND%</emu_command>\r\n'.replace('%GAME_COMMAND%',xstr(iarl_data['current_rom_data']['rom_emu_command']))
	except: pass
	# try: xml_string = xml_string+'\r\n\r\n<emu_command>%GAME_COMMAND%</emu_command>\r\n'.replace('%GAME_COMMAND%',current_rom_command)
	# except: pass
	try: xml_string = xml_string+'</game>\r\n'
	except: pass

	#Clean up your hacky xml
	xml_string = xml_string.replace('<plot></plot>','').replace('<releasedate></releasedate>','').replace('<studio></studio>','').replace('<nplayers></nplayers>','').replace('<videoid></videoid>','').replace('<genre></genre>','').replace('<year></year>','').replace('<perspective></perspective>','').replace('<rating></rating>','').replace('<ESRB></ESRB>','')
	xml_string = xml_string.replace('<boxart1></boxart1>','').replace('<boxart2></boxart2>','').replace('<boxart3></boxart3>','').replace('<boxart4></boxart4>','').replace('<boxart5></boxart5>','').replace('<boxart6></boxart6>','').replace('<boxart7></boxart7>','').replace('<boxart8></boxart8>','').replace('<boxart9></boxart9>','').replace('<boxart10></boxart10>','')
	xml_string = xml_string.replace('<snapshot1></snapshot1>','').replace('<snapshot2></snapshot2>','').replace('<snapshot3></snapshot3>','').replace('<snapshot4></snapshot4>','').replace('<snapshot5></snapshot5>','').replace('<snapshot6></snapshot6>','').replace('<snapshot7></snapshot7>','').replace('<snapshot8></snapshot8>','').replace('<snapshot9></snapshot9>','').replace('<snapshot10></snapshot10>','')
	xml_string = xml_string.replace('<fanart1></fanart1>','').replace('<fanart2></fanart2>','').replace('<fanart3></fanart3>','').replace('<fanart4></fanart4>','').replace('<fanart5></fanart5>','').replace('<fanart6></fanart6>','').replace('<fanart7></fanart7>','').replace('<fanart8></fanart8>','').replace('<fanart9></fanart9>','').replace('<fanart10></fanart10>','')
	xml_string = xml_string.replace('<banner1></banner1>','').replace('<banner2></banner2>','').replace('<banner3></banner3>','').replace('<banner4></banner4>','').replace('<banner5></banner5>','').replace('<banner6></banner6>','').replace('<banner7></banner7>','').replace('<banner8></banner8>','').replace('<banner9></banner9>','').replace('<banner10></banner10>','')
	xml_string = xml_string.replace('<clearlogo1></clearlogo1>','').replace('<clearlogo2></clearlogo2>','').replace('<clearlogo3></clearlogo3>','').replace('<clearlogo4></clearlogo4>','').replace('<clearlogo5></clearlogo5>','').replace('<clearlogo6></clearlogo6>','').replace('<clearlogo7></clearlogo7>','').replace('<clearlogo8></clearlogo8>','').replace('<clearlogo9></clearlogo9>','').replace('<clearlogo10></clearlogo10>','')
	xml_string = xml_string.replace('<rom_override_cmd></rom_override_cmd>','').replace('<rom_override_postdl></rom_override_postdl>','').replace('<rom_override_downloadpath></rom_override_downloadpath>','')
	xml_string = xml_string.replace('\r\n\r\n\r\n\r\n','\r\n')
	xml_string = xml_string.replace('\r\n\r\n\r\n','\r\n')
	xml_string = xml_string.replace('\r\n\r\n','\r\n')
	xml_string = xml_string.replace('\r\n\r\n','\r\n')
	xml_string = xml_string.replace('\r\n\r\n','\r\n')

	full_reg_exp = '</datafile>' #Look for this
	fout = open(os.path.join(get_XML_files_path(),'temp.xml'), 'w') # out file
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
		os.rename(os.path.join(get_XML_files_path(),'temp.xml'),favorites_xml_filename) #Rename Temp File
		add_success = True

	return add_success

def get_size_of_folder(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def update_xml_header(current_path,current_filename,reg_exp,new_value):
	full_reg_exp = '</'+reg_exp+'>' #Look for this
	fout = open(os.path.join(current_path,'temp.xml'), 'w') # out file
	full_new_val = '<'+reg_exp+'>'+new_value+'</'+reg_exp+'>' #replacement value
	value_updated = False

	with open(os.path.join(current_path,current_filename), 'rU') as fin:
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
		os.remove(os.path.join(current_path,current_filename)) #Remove Old File
		os.rename(os.path.join(current_path,'temp.xml'),os.path.join(current_path,current_filename)) #Rename Temp File
		xbmc.log(msg='IARL:  XML File Updated: ' +str(current_filename), level=xbmc.LOGDEBUG)

def unzip_file(current_fname):
	zip_success = False
	uz_file_extension = None
	new_fname = None

	if zipfile.is_zipfile(current_fname):
		try:
			current_zip_fileparts = os.path.split(current_fname)
			current_zip_path = current_zip_fileparts[0]
			z_file = zipfile.ZipFile(current_fname)
			uz_file_extension = os.path.splitext(z_file.namelist()[0])[1] #Get rom extension
			#This is a kajillion times faster, but not compatible with python 2.6?
			# zipfile.ZipFile(open(current_fname,'r')).extractall(path=current_zip_path)
			z_file.extractall(current_zip_path)
			z_file.close()
			zip_success = True
			xbmc.log(msg='IARL:  Unzip Successful for ' +str(current_fname), level=xbmc.LOGDEBUG)
		except:
			zip_success = False
			xbmc.log(msg='IARL:  Unzip Failed for ' +str(current_fname), level=xbmc.LOGERROR)
		if zip_success:
			os.remove(current_fname)
	else:
		xbmc.log(msg='IARL:  File was not recognized as a zipfile and not extracted, pointing back to file: ' +str(current_fname), level=xbmc.LOGERROR)
		zip_success = True
		new_fname = current_fname

	if uz_file_extension is not None: #The file was unzipped, change from zip to rom extension
		new_fname = os.path.join(current_zip_fileparts[0],z_file.namelist()[0]) #Updated unzipped filename
	else:
		new_fname = current_fname #Didn't unzip or didn't find a file extension

	return zip_success, new_fname


def unzip_and_rename_file(iarl_data): #This will probably only work when there is one file in the zip
	overall_success = False
	zip_success = list()
	new_fname = None

	for current_fname in iarl_data['current_save_data']['rom_save_filenames']:
		zip_success.append(False)
		uz_file_extension = None

		if zipfile.is_zipfile(current_fname):
			try:
				current_zip_fileparts = os.path.split(current_fname)
				current_file_basename = os.path.splitext(current_zip_fileparts[-1])[0]
				current_zip_path = current_zip_fileparts[0]
				z_file = zipfile.ZipFile(current_fname)
				z_file.extractall(current_zip_path)
				z_file.close()
				zip_success[-1] = True
				xbmc.log(msg='IARL:  Unzip Successful for ' +str(current_fname), level=xbmc.LOGDEBUG)

				for ind_z_file in z_file.namelist():
					try:
						uz_file_extension = os.path.splitext(os.path.split(os.path.join(current_zip_path,ind_z_file))[-1])[-1]
						os.rename(os.path.join(current_zip_path,ind_z_file),os.path.join(current_zip_path,current_file_basename+uz_file_extension)) #Rename file with new extension
						if new_fname is None:
							new_fname = os.path.join(current_zip_path,current_file_basename+uz_file_extension)
						xbmc.log(msg='IARL:  Filename renamed to ' +str(current_file_basename+uz_file_extension), level=xbmc.LOGDEBUG)
					except:
						xbmc.log(msg='IARL:  Unable to rename ' +str(ind_z_file), level=xbmc.LOGDEBUG)
			except:
				zip_success[-1] = False
				xbmc.log(msg='IARL:  Unzip Failed for ' +str(current_fname), level=xbmc.LOGERROR)
			if zip_success:
				os.remove(current_fname)
		else:
			xbmc.log(msg='IARL:  File was not recognized as a zipfile and not extracted, pointing back to file: ' +str(current_fname), level=xbmc.LOGERROR)
			zip_success[-1] = True
			new_fname = current_fname

	if False in zip_success:
		overall_success = False
	else:
		overall_success = True

	return zip_success, new_fname

def unzip_dosbox_file(current_fname,current_rom_emu_command):
	zip_success = False
	new_fname = None

	if zipfile.is_zipfile(current_fname):
		try:
			current_zip_fileparts = os.path.split(current_fname)
			current_zip_path = current_zip_fileparts[0]
			z_file = zipfile.ZipFile(current_fname)
			# uz_file_extension = os.path.splitext(z_file.namelist()[0])[1] #Get rom extension
			#This is a kajillion times faster, but not compatible with python 2.6?
			# zipfile.ZipFile(open(current_fname,'r')).extractall(path=current_zip_path)
			z_file.extractall(current_zip_path)
			z_file.close()
			zip_success = True
			xbmc.log(msg='IARL:  DOSBox Unzip sucessfull for ' +str(current_fname), level=xbmc.LOGDEBUG)
		except:
			zip_success = False
			xbmc.log(msg='IARL:  DOSBox Unzip failed for ' +str(current_fname), level=xbmc.LOGERROR)
		if zip_success:
			os.remove(current_fname)
	else:
		xbmc.log(msg='IARL:  There was an error unzipping files for '+str(current_fname), level=xbmc.LOGERROR)

	if current_rom_emu_command: #The file was unzipped, change from zip to rom extension
		try:
			new_fname = os.path.join(current_zip_path,os.path.join(*current_rom_emu_command.split('/')))
		except:
			new_fname = current_fname #Didn't unzip or didn't find a file extension
	else:
		new_fname = current_fname #Didn't unzip or didn't find a file extension

	return zip_success, new_fname

def unzip_dosbox_update_conf_file(iarl_data):
	zip_success = list()
	overall_success = False
	new_launch_exe = None
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	unzip_folder_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])
	unzip_folder_path = os.path.join(current_save_path,unzip_folder_name)
	conf_filename = os.path.join(unzip_folder_path,str(unzip_folder_name)+'.conf')
	current_dialog = xbmcgui.Dialog()
	current_dialog.notification('Please Wait','Converting DOSBox Archive...', xbmcgui.NOTIFICATION_INFO, 500000)

	if not os.path.isdir(unzip_folder_path): #If the directory doesnt already exist
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				try:
					z_file = zipfile.ZipFile(iarl_data['current_save_data']['rom_save_filenames'][ii])
					z_file.extractall(unzip_folder_path)
					z_file.close()
					zip_success.append(True)
					xbmc.log(msg='IARL:  DOSBOX archive unzip successful', level=xbmc.LOGDEBUG)
				except:
					zip_success.append(False)
					xbmc.log(msg='IARL:  DOSBOX archive unzip failed', level=xbmc.LOGERROR)
					current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
		if False in zip_success:
			overall_success = False
			conf_filename = None
		else: #Make the conf file
			try:
				archive_conf_file = [s for s in z_file.namelist() if s.endswith('.conf')][0]
			except:
				try:
					available_exe_files = [s for s in z_file.namelist() if s.endswith('.exe') or s.endswith('.EXE') or s.endswith('.com') or s.endswith('.COM')]
					xbmc.log(msg='IARL:  DOSBOX archive conf file could not be found, looking for a suitable executable', level=xbmc.LOGDEBUG)
					guess_launch_file = [s for s in available_exe_files if 'install' not in s.lower()][0]
					new_launch_exe = os.path.join(unzip_folder_path,os.path.join(*guess_launch_file.split('/')))
					archive_conf_file = None
				except:
					xbmc.log(msg='IARL:  DOSBOX archive conf file could not be found', level=xbmc.LOGDEBUG)
					archive_conf_file = None
					new_launch_exe = None
			if archive_conf_file is not None:
				old_conf_file = os.path.join(unzip_folder_path,archive_conf_file)
				fout = open(conf_filename, 'w') # out file
				with open(old_conf_file, 'rU') as fin:
					while True:
						line = fin.readline()
						if 'mount c ' in line.lower():
							try:
								my_new_line = 'mount c "'+unzip_folder_path+'"\r'
								fout.write(my_new_line)
							except:
								fout.write(line)
						elif 'exit' in line.lower(): #Comment out any exit calls in the configuration file
							my_new_line = '#exit\r'
							fout.write(my_new_line)
						else:
							fout.write(line)
						if not line:
							break
							pass
				fout.close()
				current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
				xbmc.log(msg='IARL:  DOSBOX conf conversion successful', level=xbmc.LOGDEBUG)
				overall_success = True
			else:
				current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
				xbmc.log(msg='IARL:  DOSBOX conf conversion failed', level=xbmc.LOGDEBUG)
				overall_success = False
	else: #Folder already exists
		if os.path.isfile(conf_filename): #The conf file already exists
			current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
			xbmc.log(msg='IARL:  DOSBOX conf file already exists', level=xbmc.LOGDEBUG)
			overall_success = True
		else: #Make the conf file
			try:
				z_file = zipfile.ZipFile(iarl_data['current_save_data']['rom_save_filenames'][0])
				z_file.close()
				archive_conf_file = [s for s in z_file.namelist() if s.endswith('.conf')][0]
			except:
				try:
					z_file = zipfile.ZipFile(iarl_data['current_save_data']['rom_save_filenames'][0])
					z_file.close()
					available_exe_files = [s for s in z_file.namelist() if s.endswith('.exe') or s.endswith('.EXE') or s.endswith('.com') or s.endswith('.COM')]
					xbmc.log(msg='IARL:  DOSBOX archive conf file could not be found, looking for a suitable executable', level=xbmc.LOGDEBUG)
					guess_launch_file = [s for s in available_exe_files if 'install' not in s.lower()][0]
					new_launch_exe = os.path.join(unzip_folder_path,os.path.join(*guess_launch_file.split('/')))
					archive_conf_file = None
				except:
					xbmc.log(msg='IARL:  DOSBOX archive conf file could not be found', level=xbmc.LOGDEBUG)
					archive_conf_file = None
					new_launch_exe = None
			if archive_conf_file is not None:
				old_conf_file = os.path.join(unzip_folder_path,archive_conf_file)
				fout = open(conf_filename, 'w') # out file
				with open(old_conf_file, 'rU') as fin:
					while True:
						line = fin.readline()
						if 'mount c ' in line.lower():
							try:
								my_new_line = 'mount c "'+unzip_folder_path+'"\r'
								fout.write(my_new_line)
							except:
								fout.write(line)
						elif 'exit' in line.lower(): #Comment out any exit calls in the configuration file
							my_new_line = '#exit\r'
							fout.write(my_new_line)
						else:
							fout.write(line)
						if not line:
							break
							pass
				fout.close()
				current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
				xbmc.log(msg='IARL:  DOSBOX conf conversion successful', level=xbmc.LOGDEBUG)
				overall_success = True
			else:
				current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
				xbmc.log(msg='IARL:  DOSBOX conf conversion failed', level=xbmc.LOGDEBUG)
				overall_success = False

	if new_launch_exe is not None: #Found a suitable exe to try and launch
		overall_success = True
		conf_filename = new_launch_exe
		xbmc.log(msg='IARL:  DOSBOX archive conf file could not be found, attempting to launch game with '+str(os.path.split(conf_filename)[-1]), level=xbmc.LOGDEBUG)

	return overall_success, conf_filename

def generate_uae_conf_file(iarl_data):
	conf_file = None
	conf_success = False
	uae_config_template = os.path.join(iarl_data['addon_data']['addon_install_path'],'resources','data','UAE_config_template.fs-uae')
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	file_base_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])
	new_filename = os.path.join(current_save_path,str(file_base_name)+'.fs-uae')

	if not os.path.isfile(new_filename):
		show_busy_dialog()
		with open(uae_config_template, 'r') as content_file:
			uae_config_template_content = content_file.read()

		try:
			uae_config_template_content = uae_config_template_content.replace('%AMIGA_MODEL%',iarl_data['current_rom_data']['rom_emu_command'])
		except:
			pass
		uae_config_template_content = uae_config_template_content.replace('%AMIGA_MODEL%','A4000') #Default Amiga model if one is not available
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if iarl_data['current_save_data']['rom_save_filenames'][ii] is not None:
				if len(iarl_data['current_save_data']['rom_save_filenames'][ii])>0:
					uae_config_template_content = uae_config_template_content.replace('%INCLUDE_AMIGA_DISK'+str(ii)+'%','')
					uae_config_template_content = uae_config_template_content.replace('%AMIGA_DISK'+str(ii)+'%',iarl_data['current_save_data']['rom_save_filenames'][ii])

		#Replace any remaining disk outliers with the correct value
		for ii in range(0,21):
			uae_config_template_content = uae_config_template_content.replace('%INCLUDE_AMIGA_DISK'+str(ii)+'%','#')

		with open(new_filename, 'w') as fout:
			fout.write(uae_config_template_content)
		hide_busy_dialog()
		
	if os.path.isfile(new_filename):
		conf_success = True
		conf_file = new_filename

	return conf_success, conf_file

def generate_uae_cd32_conf_file(iarl_data):
	conf_file = None
	conf_success = False
	uae_config_template = os.path.join(iarl_data['addon_data']['addon_install_path'],'resources','data','UAE_cd32_config_template.fs-uae')
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	file_base_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])
	new_filename = os.path.join(current_save_path,str(file_base_name)+'.fs-uae')
	current_dialog = xbmcgui.Dialog()
	current_dialog.notification('Please Wait','Processing Archive...', xbmcgui.NOTIFICATION_INFO, 500000)

	if not os.path.isfile(new_filename):
		with open(uae_config_template, 'r') as content_file:
			uae_config_template_content = content_file.read()
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				try:
					current_zip_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][ii])
					current_zip_path = os.path.join(current_zip_fileparts[0],file_base_name) #Unzip the files to a folder with the game title
					z_file = zipfile.ZipFile(iarl_data['current_save_data']['rom_save_filenames'][ii])
					# uz_file_extension = os.path.splitext(z_file.namelist()[0])[1] #Get rom extension
					#This is a kajillion times faster, but not compatible with python 2.6?
					# zipfile.ZipFile(open(current_fname,'r')).extractall(path=current_zip_path)
					z_file.extractall(current_zip_path)
					z_file.close()
					zip_success = True
					# #This is a kajillion times faster!
					# zipfile.ZipFile(open(iarl_data['current_save_data']['rom_save_filenames'][ii],'r')).extractall(path=current_zip_path)
					# zip_success = True
					xbmc.log(msg='IARL:  UAE CD32 Unzip successful for ' +str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
				except:
					zip_success = False
					xbmc.log(msg='IARL:  UAE CD32 Unzip failed for ' +str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGERROR)
				cue_found = False
				iso_found = False
				iso_list = list()
				#Look for a cue file, and if it's present, then use that to launch, otherwise list the iso/img files
				if zip_success:
					for uz_files in os.listdir(current_zip_path):
						if not cue_found:
							if '.cue' in uz_files:
								uae_config_template_content = uae_config_template_content.replace('%AMIGA_DISK0%',os.path.join(current_zip_path,uz_files))
								cue_found = True
					for uz_files in os.listdir(current_zip_path):
						if not cue_found:
							if '.iso' in uz_files:
								iso_list.append(os.path.join(current_zip_path,uz_files))
								iso_found = True
							if '.img' in uz_files:
								iso_list.append(os.path.join(current_zip_path,uz_files))
								iso_found = True
					for uz_files in os.listdir(current_zip_path):
						if not cue_found:
							if not iso_found:
								if '.bin' in uz_files:
									iso_list.append(os.path.join(current_zip_path,uz_files))

					if not cue_found: #No cue available, so list the first ISO as disk 0, then repeat through
						for jj in range(0,len(iso_list)):
							if len(iso_list[jj])>0:
								uae_config_template_content = uae_config_template_content.replace('%INCLUDE_AMIGA_DISK'+str(jj)+'%','')
								uae_config_template_content = uae_config_template_content.replace('%AMIGA_DISK'+str(ii)+'%',iso_list[jj])

					#Replace any remaining disk outliers with the correct value
					for ii in range(0,21):
						uae_config_template_content = uae_config_template_content.replace('%INCLUDE_AMIGA_DISK'+str(ii)+'%','#')
					
					with open(new_filename, 'w') as fout:
						fout.write(uae_config_template_content)

	if os.path.isfile(new_filename):
		current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		conf_success = True
		conf_file = new_filename
	else:
		current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)

	return conf_success, conf_file


def convert_adf_folder(iarl_data,point_to_file_type):

	if not point_to_file_type:
		point_to_file_type = 'adf' #Default to point to amiga file

	converted_success = list()
	overall_success = False
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	unzip_folder_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])

	if unzip_folder_name == os.path.split(current_save_path)[-1]: #GDI game folder is already present on system
		unzip_folder_path = current_save_path #Change the unzip folder to the existing folder at a minimum, then check if the gdi file is already present
	else:
		unzip_folder_path = os.path.join(current_save_path,unzip_folder_name)

	output_filename = None
	current_dialog = xbmcgui.Dialog()
	current_dialog.notification('Please Wait','Converting Files...', xbmcgui.NOTIFICATION_INFO, 500000)

	if not os.path.isdir(unzip_folder_path): #If the directory doesnt already exist
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				try:
					z_file = zipfile.ZipFile(iarl_data['current_save_data']['rom_save_filenames'][ii])
					z_file.extractall(unzip_folder_path)
					z_file.close()
					zip_success = True
					xbmc.log(msg='IARL:  Unzip Successful for ' +str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
					converted_success.append(True)
				except:
					xbmc.log(msg='IARL:  Unzip Failed for ' +str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
					converted_success.append(False)
			elif '.adf' in iarl_data['current_save_data']['rom_save_filenames'][ii].lower():
				copyFile(iarl_data['current_save_data']['rom_save_filenames'][ii],os.path.join(unzip_folder_path,os.path.split(iarl_data['current_save_data']['rom_save_filenames'][ii])[-1]))
				if os.path.isfile(os.path.join(unzip_folder_path,os.path.split(iarl_data['current_save_data']['rom_save_filenames'][ii])[-1])): #Copy was successful, delete addondata file
					os.remove(iarl_data['current_save_data']['rom_save_filenames'][ii]) #Remove the original file since its been copied
					converted_success.append(True)
				else:
					converted_success.append(False)
					xbmc.log(msg='IARL:  Copying the ADF file '+str(iarl_data['current_save_data']['rom_save_filenames'][ii])+' failed.', level=xbmc.LOGERROR)
		if False in converted_success:
			overall_success = False
		else:
			if 'adf' in point_to_file_type.lower():
				found_file = False
				for ffiles in os.listdir(unzip_folder_path):
					if 'disk1' in ffiles.lower() or 'disk 1' in ffiles.lower() or 'disc1' in ffiles.lower() or 'disc 1' in ffiles.lower():
						if not found_file:
							output_filename = os.path.join(unzip_folder_path,ffiles)
							found_files = True
							overall_success = True
			else: #Just look for the selected file extension (cue/gdi/etc), point to the first one
				found_file = False
				for ffiles in os.listdir(unzip_folder_path):
					if ffiles.endswith(point_to_file_type):
						if not found_file:
							output_filename = os.path.join(unzip_folder_path,ffiles)
							found_files = True
							overall_success = True
		# hide_busy_dialog()
	else: #Folder already exists
		if 'adf' in point_to_file_type.lower():
			found_file = False
			for ffiles in os.listdir(unzip_folder_path):
				if 'disk1' in ffiles.lower() or 'disk 1' in ffiles.lower() or 'disc1' in ffiles.lower() or 'disc 1' in ffiles.lower():
					if not found_file:
						output_filename = os.path.join(unzip_folder_path,ffiles)
						found_files = True
						overall_success = True
		else: #Just look for the selected file extension (cue/gdi/etc), point to the first one
			found_file = False
			for ffiles in os.listdir(unzip_folder_path):
				if ffiles.endswith(point_to_file_type):
					if not found_file:
						output_filename = os.path.join(unzip_folder_path,ffiles)
						found_files = True
						overall_success = True
	if overall_success:
		current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				os.remove(iarl_data['current_save_data']['rom_save_filenames'][ii]) #Remove ZIP File, leave only decrompressed files
	else:
		current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)

	return overall_success, output_filename

def generate_uae4arm_conf_file(iarl_data):
	conf_file = None
	conf_success = False
	continue_launch = False

	if len(iarl_data['current_save_data']['rom_save_filenames'])>4:
		current_dialog = xbmcgui.Dialog()
		ret1 = current_dialog.select('There are more than 4 disks for this game, launch anyway?', ['Yes','No'])
		if ret1 == 0:
			continue_launch = False
		else:
			continue_launch = True
	else:
		continue_launch = True

	if continue_launch:	
		uae_config_template = os.path.join(iarl_data['addon_data']['addon_install_path'],'resources','data','UAE4ARM_config_template.uae')
		current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
		current_save_path = current_save_fileparts[0]
		file_base_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])
		new_filename = os.path.join(current_save_path,str(file_base_name)+'.uae')

		if not os.path.isfile(new_filename):
			show_busy_dialog()
			with open(uae_config_template, 'r') as content_file:
				uae_config_template_content = content_file.read()

			# try:
			# 	uae_config_template_content = uae_config_template_content.replace('%AMIGA_MODEL%',iarl_data['current_rom_data']['rom_emu_command'])
			# except:
			# 	pass
			# uae_config_template_content = uae_config_template_content.replace('%AMIGA_MODEL%','A4000') #Default Amiga model if one is not available
			uae_config_template_content = uae_config_template_content.replace('%AMIGA_TITLE%',iarl_data['current_rom_data']['rom_title'])
			uae_config_template_content = uae_config_template_content.replace('%AMIGA_NDISKS%',str(len(iarl_data['current_save_data']['rom_save_filenames'])))
			
			for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
				if iarl_data['current_save_data']['rom_save_filenames'][ii] is not None:
					if len(iarl_data['current_save_data']['rom_save_filenames'][ii])>0:
						uae_config_template_content = uae_config_template_content.replace('%INCLUDE_AMIGA_DISK'+str(ii)+'%','')
						uae_config_template_content = uae_config_template_content.replace('%AMIGA_DISK'+str(ii)+'%',iarl_data['current_save_data']['rom_save_filenames'][ii])

			#Replace any remaining disk outliers with the correct value (comment out the non used disks)
			for ii in range(0,21):
				uae_config_template_content = uae_config_template_content.replace('%INCLUDE_AMIGA_DISK'+str(ii)+'%','; ')

			with open(new_filename, 'w') as fout:
				fout.write(uae_config_template_content)
			hide_busy_dialog()
			
		if os.path.isfile(new_filename):
			conf_success = True
			conf_file = new_filename

	return conf_success, conf_file

def setup_mame_softlist_game(iarl_data,softlist_type):
	overall_success = False
	converted_success = list()
	new_fname = None
	continue_launch = False
	check_and_download_hash = False

	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	containing_folder = os.path.split(os.path.dirname(iarl_data['current_save_data']['rom_save_filenames'][0]))[-1]
	file_base_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])

	current_sys_path = iarl_data['settings']['path_to_retroarch_system_dir']

	if current_sys_path is not None: #If the setting for retroarch system directory is defined, then check for/download hash file
		if len(current_sys_path)>0:
			continue_launch = True
			check_and_download_hash = True

	if not continue_launch:
		if 'true' in __addon__.getSetting(id='iarl_setting_warn_retroarch_sys_dir').lower():
			current_dialog = xbmcgui.Dialog()
			ret1 = current_dialog.select('System Directory setting undefined, try launch anyway?', ['Yes','No','Yes, stop warning me!'])
			if ret1==0:
				continue_launch = True
			elif ret1==1:
				continue_launch = False
			else:
				__addon__.setSetting(id='iarl_setting_warn_retroarch_sys_dir',value='false') #No longer show the warning
				continue_launch = True
		else:
			continue_launch = True


	if continue_launch:
		if len(softlist_type)>0:
			#1 Check for and download hash file if needed
			parserfile = get_parser_file('mame_softlist_parser.xml')
			softlistfile = get_parser_file('mame_softlist_database.xml')
			descParser = DescriptionParserFactory.getParser(parserfile)
			results = descParser.parseDescription(softlistfile,'xml')
			softlist_info = [x for x in results if str(softlist_type) in x['system']][0]
			# print 'ztest'
			# print softlist_info
			if check_and_download_hash:
				current_hash_path = os.path.join(current_sys_path,'mame','hash')
				save_hash_filename = os.path.join(current_hash_path,os.path.split(softlist_info['web_url'][0])[-1])
				if not os.path.exists(current_hash_path):
					try:
						os.makedirs(current_hash_path)
					except:
						xbmc.log(msg='IARL:  Error creating MAME hash path: ' +str(current_hash_path), level=xbmc.LOGERROR)
				if not os.path.isfile(save_hash_filename): #Download the hash file if it's not already present
					# from resources.lib.webutils import *
					hash_dl_success = download_tools().Downloader(softlist_info['web_url'][0],save_hash_filename,False,'','',99999,str(os.path.split(softlist_info['web_url'][0])),'Downloading hash file, please wait...') #No login required for github raw files
					if not hash_dl_success:
						xbmc.log(msg='IARL:  Error downloading MAME hash file: ' +str(softlist_info['web_url'][0]), level=xbmc.LOGERROR)
				else:
					xbmc.log(msg='IARL:  MAME Softlist hash file was found for '+str(softlist_type), level=xbmc.LOGDEBUG)
			#2 Check for correct folder and create if needed, then move all files to the folder
			if containing_folder == softlist_info['folder_name'][0]: #Save location already correctly named
				xbmc.log(msg='IARL:  MAME folder already defined for '+str(softlist_type), level=xbmc.LOGDEBUG)
			else: #Make the correct folder
				if not os.path.exists(os.path.join(current_save_path,softlist_info['folder_name'][0])):
					try:
						os.makedirs(os.path.join(current_save_path,softlist_info['folder_name'][0]))
					except:
						xbmc.log(msg='IARL:  Error creating mame folder path for ' +str(softlist_type), level=xbmc.LOGERROR)
				for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
					if os.path.isfile(iarl_data['current_save_data']['rom_save_filenames'][ii]): #Copy files to new location
						new_save_file_location = os.path.join(current_save_path,softlist_info['folder_name'][0],os.path.split(iarl_data['current_save_data']['rom_save_filenames'][ii])[-1])
						if not os.path.isfile(new_save_file_location):
							copyFile(iarl_data['current_save_data']['rom_save_filenames'][ii],new_save_file_location)
						if os.path.isfile(new_save_file_location): #Copy was successful
							try:
								if new_save_file_location != iarl_data['current_save_data']['rom_save_filenames'][ii]: #Only remove the old file if the new save location is different
									os.remove(iarl_data['current_save_data']['rom_save_filenames'][ii]) #Remove the old file
									xbmc.log(msg='IARL:  File deleted '+str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
								else:
									xbmc.log(msg='IARL:  File already exists and will not be deleted '+str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
							except:
								xbmc.log(msg='IARL:  Old file was not found and could not be deleted '+str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
							iarl_data['current_save_data']['rom_save_filenames'][ii] = new_save_file_location
							converted_success.append(True)
						else:
							converted_success.append(False)
							xbmc.log(msg='IARL:  Copying the XML file '+str(new_save_file_location)+' failed.', level=xbmc.LOGERROR)
					else:
						xbmc.log(msg='IARL:  Skipped copy of '+str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
			#3 Define new launch filename
			if False in converted_success:
				overall_success = False
			else:
				overall_success = True
				new_fname = iarl_data['current_save_data']['rom_save_filenames'][0]

	return overall_success, new_fname

def setup_mess2014_softlist_game(iarl_data,softlist_type):
	overall_success = False
	converted_success = list()
	new_fname = None
	continue_launch = False
	check_and_download_hash = False

	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	containing_folder = os.path.split(os.path.dirname(iarl_data['current_save_data']['rom_save_filenames'][0]))[-1]
	file_base_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])

	current_sys_path = iarl_data['settings']['path_to_retroarch_system_dir']

	if current_sys_path is not None: #If the setting for retroarch system directory is defined, then check for/download hash file
		if len(current_sys_path)>0:
			continue_launch = True
			check_and_download_hash = True

	if not continue_launch:
		if 'true' in __addon__.getSetting(id='iarl_setting_warn_retroarch_sys_dir').lower():
			current_dialog = xbmcgui.Dialog()
			ret1 = current_dialog.select('System Directory setting undefined, try launch anyway?', ['Yes','No','Yes, stop warning me!'])
			if ret1==0:
				continue_launch = True
			elif ret1==1:
				continue_launch = False
			else:
				__addon__.setSetting(id='iarl_setting_warn_retroarch_sys_dir',value='false') #No longer show the warning
				continue_launch = True
		else:
			continue_launch = True


	if continue_launch:
		if len(softlist_type)>0:
			#1 Check for and download hash file if needed
			parserfile = get_parser_file('mame_softlist_parser.xml')
			softlistfile = get_parser_file('mame_softlist_database.xml')
			descParser = DescriptionParserFactory.getParser(parserfile)
			results = descParser.parseDescription(softlistfile,'xml')
			softlist_info = [x for x in results if str(softlist_type) in x['system']][0]
			# print 'ztest'
			# print softlist_info
			if check_and_download_hash:
				current_hash_path = os.path.join(current_sys_path,'mess2014','hash')
				save_hash_filename = os.path.join(current_hash_path,os.path.split(softlist_info['web_url'][0])[-1])
				if not os.path.exists(current_hash_path):
					try:
						os.makedirs(current_hash_path)
					except:
						xbmc.log(msg='IARL:  Error creating MESS2014 hash path: ' +str(current_hash_path), level=xbmc.LOGERROR)
				if not os.path.isfile(save_hash_filename): #Download the hash file if it's not already present
					# from resources.lib.webutils import *
					hash_dl_success = download_tools().Downloader(softlist_info['web_url'][0],save_hash_filename,False,'','',99999,str(os.path.split(softlist_info['web_url'][0])),'Downloading hash file, please wait...') #No login required for github raw files
					if not hash_dl_success:
						xbmc.log(msg='IARL:  Error downloading MESS2014 hash file: ' +str(softlist_info['web_url'][0]), level=xbmc.LOGERROR)
				else:
					xbmc.log(msg='IARL:  MESS2014 Softlist hash file was found for '+str(softlist_type), level=xbmc.LOGDEBUG)
			#2 Check for correct folder and create if needed, then move all files to the folder
			if containing_folder == softlist_info['folder_name'][0]: #Save location already correctly named
				xbmc.log(msg='IARL:  MESS2014 folder already defined for '+str(softlist_type), level=xbmc.LOGDEBUG)
			else: #Make the correct folder
				if not os.path.exists(os.path.join(current_save_path,softlist_info['folder_name'][0])):
					try:
						os.makedirs(os.path.join(current_save_path,softlist_info['folder_name'][0]))
					except:
						xbmc.log(msg='IARL:  Error creating MESS2014 folder path for ' +str(softlist_type), level=xbmc.LOGERROR)
				for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
					if os.path.isfile(iarl_data['current_save_data']['rom_save_filenames'][ii]): #Copy files to new location
						new_save_file_location = os.path.join(current_save_path,softlist_info['folder_name'][0],os.path.split(iarl_data['current_save_data']['rom_save_filenames'][ii])[-1])
						if not os.path.isfile(new_save_file_location):
							copyFile(iarl_data['current_save_data']['rom_save_filenames'][ii],new_save_file_location)
						if os.path.isfile(new_save_file_location): #Copy was successful
							try:
								if new_save_file_location != iarl_data['current_save_data']['rom_save_filenames'][ii]: #Only remove the old file if the new save location is different
									os.remove(iarl_data['current_save_data']['rom_save_filenames'][ii]) #Remove the old file
									xbmc.log(msg='IARL:  File deleted '+str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
								else:
									xbmc.log(msg='IARL:  File already exists and will not be deleted '+str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
							except:
								xbmc.log(msg='IARL:  Old file was not found and could not be deleted '+str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
							iarl_data['current_save_data']['rom_save_filenames'][ii] = new_save_file_location
							converted_success.append(True)
						else:
							converted_success.append(False)
							xbmc.log(msg='IARL:  Copying the XML file '+str(new_save_file_location)+' failed.', level=xbmc.LOGERROR)
					else:
						xbmc.log(msg='IARL:  Skipped copy of '+str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
			#3 Define new launch filename
			if False in converted_success:
				overall_success = False
			else:
				overall_success = True
				new_fname = iarl_data['current_save_data']['rom_save_filenames'][0]

	return overall_success, new_fname

def unzip_scummvm_update_conf_file(iarl_data):
	zip_success = list()
	overall_success = False
	new_launch_exe = None
	scummvm_config_template = os.path.join(iarl_data['addon_data']['addon_install_path'],'resources','data','scummvm_template.scummvm')
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	unzip_folder_name = str(iarl_data['current_rom_data']['rom_emu_command'])
	unzip_folder_path = os.path.join(current_save_path,unzip_folder_name)
	scummvm_config_template = os.path.join(iarl_data['addon_data']['addon_install_path'],'resources','data','scummvm_template.scummvm')
	conf_filename = os.path.join(unzip_folder_path,str(iarl_data['current_rom_data']['rom_emu_command'])+'.scummvm')
	current_dialog = xbmcgui.Dialog()
	current_dialog.notification('Please Wait','Converting ScummVM Archive...', xbmcgui.NOTIFICATION_INFO, 500000)

	if not os.path.isdir(unzip_folder_path): #If the directory doesnt already exist
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				try:
					z_file = zipfile.ZipFile(iarl_data['current_save_data']['rom_save_filenames'][ii])
					z_file.extractall(unzip_folder_path)
					z_file.close()
					zip_success.append(True)
					xbmc.log(msg='IARL:  ScummVM archive unzip successful', level=xbmc.LOGDEBUG)
				except:
					zip_success.append(False)
					xbmc.log(msg='IARL:  ScummVM archive unzip failed', level=xbmc.LOGERROR)
					current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
		if False in zip_success:
			overall_success = False
			conf_filename = None
		else: #Make the conf file
			if not os.path.isfile(conf_filename): #If the conf file doesnt exist yet, make it
				with open(scummvm_config_template, 'r') as content_file:
					scummvm_config_content = content_file.read()
				scummvm_config_content = scummvm_config_content.replace('%GAME_PATH%',unzip_folder_path)
				scummvm_config_content = scummvm_config_content.replace('%GAME_ID%',str(iarl_data['current_rom_data']['rom_emu_command']))	
				with open(conf_filename, 'w') as fout:
					fout.write(scummvm_config_content)

				current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
				xbmc.log(msg='IARL:  ScummVM conversion successful', level=xbmc.LOGDEBUG)
				overall_success = True
	else: #Folder already exists
		if os.path.isfile(conf_filename): #The conf file already exists
			current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
			xbmc.log(msg='IARL:  ScummVM conf file already exists', level=xbmc.LOGDEBUG)
			overall_success = True
		else: #Make the conf file
			with open(scummvm_config_template, 'r') as content_file:
				scummvm_config_content = content_file.read()
			scummvm_config_content = scummvm_config_content.replace('%GAME_PATH%',unzip_folder_path)
			scummvm_config_content = scummvm_config_content.replace('%GAME_ID%',str(iarl_data['current_rom_data']['rom_emu_command']))	
			with open(conf_filename, 'w') as fout:
				fout.write(scummvm_config_content)

			current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
			xbmc.log(msg='IARL:  ScummVM conversion successful', level=xbmc.LOGDEBUG)
			overall_success = True

	return overall_success, conf_filename

def convert_chd_bin(current_fname,iarl_setting_chdman_path,point_to_file_type):

	if not point_to_file_type:
		point_to_file_type = 'bin' #Default to point to bin file
	chd_success = False
	new_file_extension = None
	new_fname = None
	current_dialog = xbmcgui.Dialog()

	if iarl_setting_chdman_path is None: #Check if there's a CHDMAN available
		ok_ret = current_dialog.ok('Error','No CHDMAN binary is available for your system')
		xbmc.log(msg='IARL:  CHDMAN binary is not defined for your system: '+str(os.uname()), level=xbmc.LOGERROR)
		return chd_success, new_fname

	current_dialog.notification('Please Wait','Converting CHD...', xbmcgui.NOTIFICATION_INFO, 500000)

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
		xbmc.log(msg='IARL:  Attempting CHD Conversion: '+str(command), level=xbmc.LOGDEBUG)
		failed_text = 'Unhandled exception'
		already_exists_text = 'file already exists'
		success_text = 'Extraction complete'
		conversion_process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) #Convert CHD to BIN/CUE
		results1 = conversion_process.stdout.read().replace('\n', '')
		conversion_process.kill() #End the process after its completed

		if success_text.lower() in results1.lower():
			xbmc.log(msg='IARL:  CHDMAN conversion successful', level=xbmc.LOGDEBUG)
			if 'cue' in point_to_file_type:
				new_fname = output_cue
			else:
				new_fname = output_bin
			chd_success = True
		elif already_exists_text.lower() in results1.lower():
			xbmc.log(msg='IARL:  CHDMAN converted files already exists, conversion not required', level=xbmc.LOGDEBUG)
			if 'cue' in point_to_file_type:
				new_fname = output_cue
			else:
				new_fname = output_bin
			chd_success = True
		elif failed_text.lower() in results1.lower():
			chd_success = False
			xbmc.log(msg='IARL:  CHDMAN conversion failed: '+str(results1), level=xbmc.LOGERROR)
		else:
			chd_success = False
			xbmc.log(msg='IARL:  CHDMAN conversion failed', level=xbmc.LOGERROR)

		if chd_success:
			os.remove(current_fname) #Delete the CHD and leave the new BIN/CUE if the conversion was a success
			current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		else:
			current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
	else:
		xbmc.log(msg='IARL:  File '+str(current_fname)+' does not appear to be a CHD and was not converted', level=xbmc.LOGERROR)
		current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)

	return chd_success, new_fname


def convert_7z_bin_cue_gdi(iarl_data,point_to_file_type):

	if not point_to_file_type:
		point_to_file_type = 'bin' #Default to point to bin file

	converted_success = list()
	overall_success = False
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	un7zip_folder_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])

	if un7zip_folder_name == os.path.split(current_save_path)[-1]: #GDI game folder is already present on system
		un7zip_folder_path = current_save_path #Change the unzip folder to the existing folder at a minimum, then check if the gdi file is already present
	else:
		un7zip_folder_path = os.path.join(current_save_path,un7zip_folder_name)

	output_filename = None
	current_dialog = xbmcgui.Dialog()
	current_dialog.notification('Please Wait','Converting 7z File...', xbmcgui.NOTIFICATION_INFO, 500000)

	if not os.path.isdir(un7zip_folder_path): #If the directory doesnt already exist
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if iarl_data['addon_data']['7za_path'] is not None:
				if '7z' in iarl_data['current_save_data']['rom_save_filenames'][ii] or 'zip' in iarl_data['current_save_data']['rom_save_filenames'][ii]:
					command = '"%7ZA_APP_PATH%" -aoa -o"%OUTPUT_DIR%" e "%INPUT_7Z%"' #May need to provide other OS options here
					command = command.replace('%7ZA_APP_PATH%',iarl_data['addon_data']['7za_path'])
					command = command.replace('%INPUT_7Z%',iarl_data['current_save_data']['rom_save_filenames'][ii])
					command = command.replace('%OUTPUT_DIR%',un7zip_folder_path)
					xbmc.log(msg='IARL:  Attempting 7ZA Conversion: '+str(command), level=xbmc.LOGDEBUG)
					success_text = 'everything is ok'
					conversion_process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) #Uncompress the 7z
					results1 = conversion_process.stdout.read().replace('\n', '')
					conversion_process.kill() #End the process after its completed

					if success_text.lower() in results1.lower():
						xbmc.log(msg='IARL:  7Z conversion successful', level=xbmc.LOGDEBUG)
						current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
						converted_success.append(True)
					else:
						xbmc.log(msg='IARL:  7Z conversion failed: '+str(results1), level=xbmc.LOGDEBUG)
						current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
						converted_success.append(False)
			else:
				xbmc.log(msg='IARL:  7z binary is not defined for your system: '+str(os.uname()), level=xbmc.LOGERROR)
				current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
				converted_success.append(False)

		if False in converted_success:
			overall_success = False
		else:
			if 'track 1' in point_to_file_type.lower():
				found_file = False
				for ffiles in os.listdir(un7zip_folder_path):
					if 'track 1' in ffiles.lower():
						if not found_file:
							output_filename = os.path.join(un7zip_folder_path,ffiles)
							found_files = True
							overall_success = True
			else: #Just look for the selected file extension (cue/gdi/etc), point to the first one
				found_file = False
				for ffiles in os.listdir(un7zip_folder_path):
					if ffiles.endswith(point_to_file_type):
						if not found_file:
							output_filename = os.path.join(un7zip_folder_path,ffiles)
							found_files = True
							overall_success = True
		# hide_busy_dialog()
	else: #Folder already exists
		if 'track 1' in point_to_file_type.lower():
			found_file = False
			for ffiles in os.listdir(un7zip_folder_path):
				if 'track 1' in ffiles.lower():
					if not found_file:
						output_filename = os.path.join(un7zip_folder_path,ffiles)
						found_files = True
						overall_success = True
		else: #Just look for the selected file extension (cue/gdi/etc), point to the first one
			found_file = False
			for ffiles in os.listdir(un7zip_folder_path):
				if ffiles.endswith(point_to_file_type):
					if not found_file:
						output_filename = os.path.join(un7zip_folder_path,ffiles)
						found_files = True
						overall_success = True
		current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
				
	return overall_success, output_filename


def convert_zip_bin_cue_gdi(iarl_data,point_to_file_type):

	if not point_to_file_type:
		point_to_file_type = 'bin' #Default to point to bin file

	converted_success = list()
	overall_success = False
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	unzip_folder_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])

	if unzip_folder_name == os.path.split(current_save_path)[-1]: #GDI game folder is already present on system
		unzip_folder_path = current_save_path #Change the unzip folder to the existing folder at a minimum, then check if the gdi file is already present
	else:
		unzip_folder_path = os.path.join(current_save_path,unzip_folder_name)

	output_filename = None
	current_dialog = xbmcgui.Dialog()
	current_dialog.notification('Please Wait','Converting zip File...', xbmcgui.NOTIFICATION_INFO, 500000)

	if not os.path.isdir(unzip_folder_path): #If the directory doesnt already exist
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				try:
					z_file = zipfile.ZipFile(iarl_data['current_save_data']['rom_save_filenames'][ii])
					z_file.extractall(unzip_folder_path)
					z_file.close()
					zip_success = True
					xbmc.log(msg='IARL:  Unzip Successful for ' +str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
					converted_success.append(True)
				except:
					xbmc.log(msg='IARL:  Unzip Failed for ' +str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
					converted_success.append(False)

		if False in converted_success:
			overall_success = False
		else:
			if 'track 1' in point_to_file_type.lower():
				found_file = False
				for ffiles in os.listdir(unzip_folder_path):
					if 'track 1' in ffiles.lower():
						if not found_file:
							output_filename = os.path.join(unzip_folder_path,ffiles)
							found_files = True
							overall_success = True
			else: #Just look for the selected file extension (cue/gdi/etc), point to the first one
				found_file = False
				for ffiles in os.listdir(unzip_folder_path):
					if ffiles.endswith(point_to_file_type):
						if not found_file:
							output_filename = os.path.join(unzip_folder_path,ffiles)
							found_files = True
							overall_success = True
		# hide_busy_dialog()
	else: #Folder already exists
		if 'track 1' in point_to_file_type.lower():
			found_file = False
			for ffiles in os.listdir(unzip_folder_path):
				if 'track 1' in ffiles.lower():
					if not found_file:
						output_filename = os.path.join(unzip_folder_path,ffiles)
						found_files = True
						overall_success = True
		else: #Just look for the selected file extension (cue/gdi/etc), point to the first one
			found_file = False
			for ffiles in os.listdir(unzip_folder_path):
				if ffiles.endswith(point_to_file_type):
					if not found_file:
						output_filename = os.path.join(unzip_folder_path,ffiles)
						found_files = True
						overall_success = True
	if overall_success:
		current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				os.remove(iarl_data['current_save_data']['rom_save_filenames'][ii]) #Remove ZIP File, leave only decrompressed files
	else:
		current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
				
	return overall_success, output_filename

def convert_7z_m3u(iarl_data):

	converted_success = list()
	overall_success = False
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	un7zip_folder_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])

	if un7zip_folder_name == os.path.split(current_save_path)[-1]: #M3U game folder is already present on system
		un7zip_folder_path = current_save_path #Change the unzip folder to the existing folder at a minimum, then check if the gdi file is already present
	else:
		un7zip_folder_path = os.path.join(current_save_path,un7zip_folder_name)


	m3u_filename = os.path.join(un7zip_folder_path,str(un7zip_folder_name)+'.m3u')
	current_dialog = xbmcgui.Dialog()
	current_dialog.notification('Please Wait','Converting 7z File...', xbmcgui.NOTIFICATION_INFO, 500000)

	if not os.path.isdir(un7zip_folder_path): #If the directory doesnt already exist
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if iarl_data['addon_data']['7za_path'] is not None:
				if '7z' in iarl_data['current_save_data']['rom_save_filenames'][ii]:
					command = '"%7ZA_APP_PATH%" -aoa -o"%OUTPUT_DIR%" e "%INPUT_7Z%"' #May need to provide other OS options here
					command = command.replace('%7ZA_APP_PATH%',iarl_data['addon_data']['7za_path'])
					command = command.replace('%INPUT_7Z%',iarl_data['current_save_data']['rom_save_filenames'][ii])
					command = command.replace('%OUTPUT_DIR%',un7zip_folder_path)
					xbmc.log(msg='IARL:  Attempting 7ZA Conversion: '+str(command), level=xbmc.LOGDEBUG)
					success_text = 'everything is ok'
					conversion_process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) #Uncompress the 7z
					results1 = conversion_process.stdout.read().replace('\n', '')
					conversion_process.kill() #End the process after its completed

					if success_text.lower() in results1.lower():
						xbmc.log(msg='IARL:  7Z conversion successful', level=xbmc.LOGDEBUG)
						# current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
						converted_success.append(True)
					else:
						xbmc.log(msg='IARL:  7Z conversion failed: '+str(results1), level=xbmc.LOGDEBUG)
						# current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
						converted_success.append(False)
			else:
				xbmc.log(msg='IARL:  7z binary is not defined for your system: '+str(os.uname()), level=xbmc.LOGERROR)
				# current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
				converted_success.append(False)

		if False in converted_success:
			overall_success = False
			m3u_filename = None
			current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
		else:
			if '.cue' in [os.path.splitext(x)[-1] for x in os.listdir(un7zip_folder_path)]:
				m3u_content = '\r\n'.join([x for x in os.listdir(un7zip_folder_path) if 'cue' in x])
				fout = open(m3u_filename, 'w') # out file
				fout.write(m3u_content)
				fout.close()
				overall_success = True
				current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		# hide_busy_dialog()
	else: #Folder already exists
		if os.path.isfile(m3u_filename): #The m3u file already exists
			overall_success = True
			current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		else: #Make the m3u file
			if '.cue' in [os.path.splitext(x)[-1] for x in os.listdir(un7zip_folder_path)]:
				m3u_content = '\r\n'.join([x for x in os.listdir(un7zip_folder_path) if 'cue' in x])
				fout = open(m3u_filename, 'w') # out file
				fout.write(m3u_content)
				fout.close()
				overall_success = True
		current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
				
	return overall_success, m3u_filename


def convert_zip_m3u(iarl_data):

	converted_success = list()
	overall_success = False
	current_save_fileparts = os.path.split(iarl_data['current_save_data']['rom_save_filenames'][0])
	current_save_path = current_save_fileparts[0]
	unzip_folder_name = clean_file_folder_name(iarl_data['current_rom_data']['rom_title'])

	if unzip_folder_name == os.path.split(current_save_path)[-1]: #M3U game folder is already present on system
		unzip_folder_path = current_save_path #Change the unzip folder to the existing folder at a minimum, then check if the gdi file is already present
	else:
		unzip_folder_path = os.path.join(current_save_path,unzip_folder_name)


	m3u_filename = os.path.join(unzip_folder_path,str(unzip_folder_name)+'.m3u')
	current_dialog = xbmcgui.Dialog()
	current_dialog.notification('Please Wait','Converting zip File...', xbmcgui.NOTIFICATION_INFO, 500000)

	if not os.path.isdir(unzip_folder_path): #If the directory doesnt already exist
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				try:
					z_file = zipfile.ZipFile(iarl_data['current_save_data']['rom_save_filenames'][ii])
					z_file.extractall(unzip_folder_path)
					z_file.close()
					zip_success = True
					xbmc.log(msg='IARL:  Unzip Successful for ' +str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
					converted_success.append(True)
				except:
					xbmc.log(msg='IARL:  Unzip Failed for ' +str(iarl_data['current_save_data']['rom_save_filenames'][ii]), level=xbmc.LOGDEBUG)
					converted_success.append(False)

		if False in converted_success:
			overall_success = False
			m3u_filename = None
			current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)
		else:
			if '.cue' in [os.path.splitext(x)[-1] for x in os.listdir(unzip_folder_path)]:
				m3u_content = '\r\n'.join([x for x in os.listdir(unzip_folder_path) if 'cue' in x])
				fout = open(m3u_filename, 'w') # out file
				fout.write(m3u_content)
				fout.close()
				overall_success = True
	else: #Folder already exists
		if os.path.isfile(m3u_filename): #The m3u file already exists
			overall_success = True
		else: #Make the m3u file
			if '.cue' in [os.path.splitext(x)[-1] for x in os.listdir(unzip_folder_path)]:
				m3u_content = '\r\n'.join([x for x in os.listdir(unzip_folder_path) if 'cue' in x])
				fout = open(m3u_filename, 'w') # out file
				fout.write(m3u_content)
				fout.close()
				overall_success = True

	if overall_success:
		current_dialog.notification('Complete', 'Conversion Successful', xbmcgui.NOTIFICATION_INFO, 1000)
		for ii in range(0,len(iarl_data['current_save_data']['rom_save_filenames'])):
			if zipfile.is_zipfile(iarl_data['current_save_data']['rom_save_filenames'][ii]):
				os.remove(iarl_data['current_save_data']['rom_save_filenames'][ii]) #Remove ZIP File, leave only decrompressed files
	else:
		current_dialog.notification('Error', 'Error Converting, please see log', xbmcgui.NOTIFICATION_INFO, 1000)

	return overall_success, m3u_filename


def rename_rom_postdl(current_fname,new_extension):
	rename_success = False
	new_fname = None

	if os.path.exists(current_fname):
		if len(new_extension)>0:
			file_basename_no_ext = os.path.splitext(current_fname)
			new_fname = file_basename_no_ext[0]+'.'+new_extension.replace('.','').replace("'",'') #Clean extension
			os.rename(current_fname,new_fname) #Rename file with new extension
			xbmc.log(msg='IARL:  Filename extension renamed to ' +str(new_fname), level=xbmc.LOGDEBUG)
			rename_success = True
		else:
			xbmc.log(msg='IARL:  New filename extension is not defined', level=xbmc.LOGERROR)
	else:
		xbmc.log(msg='IARL:  Unable to find the file for renaming', level=xbmc.LOGERROR)

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
				if use_header in old.read():
					xbmc.log(msg='IARL:  Lynx ROM already appears to have the expected header.', level=xbmc.LOGDEBUG)
					update_file_with_header = False
				else:
					xbmc.log(msg='IARL:  Lynx ROM does not appear to have the expected header.  Attempting to update', level=xbmc.LOGDEBUG)
					update_file_with_header = True

			if update_file_with_header:
				with open(new_rom_fname, 'rb') as old:
					with open(temp_filename, 'wb') as new:
					    new.write(use_header)
					    new.write(old.read())
				os.remove(new_rom_fname) #Remove Old File
				os.rename(temp_filename,new_rom_fname) #Rename Temp File
				xbmc.log(msg='IARL:  Lynx ROM updated with '+str(header_text)+' bytes.', level=xbmc.LOGDEBUG)

			new_fname = new_rom_fname
			success = True

	return success, new_fname

def set_new_dl_path(xml_id,plugin):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0]

	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Select Download Path Type', ['Default','Custom'])

	if ret1 == 0:
		ret2 = current_dialog.select('Are you sure you want to update the current Download Path for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_downloadpath','default')
			ok_ret = current_dialog.ok('Complete','Download Path was updated to default[CR]Cache was cleared for new settings')
			delete_userdata_list_cache_file(current_xml_filename.split('.')[0])
	elif ret1 == 1:
		new_path = current_dialog.browse(0,'Update Download Path','files')
		ret2 = current_dialog.select('Are you sure you want to update the current Download Path for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_downloadpath',new_path)
			ok_ret = current_dialog.ok('Complete','Download Path was updated to your custom folder[CR]Cache was cleared for new settings')
			delete_userdata_list_cache_file(current_xml_filename.split('.')[0])
	else:
		pass

def hide_selected_archive(iarl_data,xml_id,plugin):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0]

	current_emu_category = iarl_data['archive_data']['emu_category'][iarl_data['archive_data']['emu_filepath'].index(xml_id)]
	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Are you sure you want to Hide '+current_xml_filename, ['Yes','Cancel'])
	iarl_data
	if ret1 == 0:
		new_xml_category = current_emu_category + ', hidden'
		update_xml_header(current_xml_path,current_xml_filename,'emu_category',new_xml_category)
		ok_ret = current_dialog.ok('Complete','Archive will be hidden after IARL restart[CR]Cache was cleared for new settings')
		delete_userdata_list_cache_file(current_xml_filename.split('.')[0])
	else:
		pass

def set_new_post_dl_action(xml_id,plugin):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0]
	current_dialog = xbmcgui.Dialog()

	post_dl_actions_list = ['None',
							'UnZIP Archive',
							'UnZIP Archive and Rename',
							'UnZIP DOSBox, Run Command',
							'UnZIP DOSBox, Launch Conf',
							'UnZIP SCUMMVm, Generate Conf',
							'Convert CHD, Launch bin',
							'Convert CHD, Launch cue',
							'Convert Lynx Headerless Rom',
							'Update downloaded file extension',
							'Unzip Archive, Generate FS-UAE Conf',
							'UnZIP Archive, Generate UAE4ARM Conf',
							'UnZIP Archive, Generate FS-UAE CD32 Conf',
							'Un7Z Archive, Generate M3U',
							'Un7Z Archive, Launch track1.bin',
							'Un7Z Archive, Launch gdi',
							'Un7Z Archive, Launch cue',
							'Un7Z Archive, Launch iso',
							'UnZIP Archive, Generate M3U',
							'UnZIP Archive, Launch track1.bin',
							'UnZIP Archive, Launch gdi',
							'UnZIP Archive, Launch cue',
							'UnZIP Archive, Launch iso',
							'UnZIP Archive, Launch disk1.adf',
							'Generate MAME Softlist Command',
							'Generate MESS2014 Softlist Command',
							'Cancel']
	post_dl_commands_list = ['none',
							'unzip_rom',
							'unzip_and_rename_file',
							'unzip_update_rom_path_dosbox',
							'unzip_dosbox_update_conf_file',
							'unzip_scummvm_update_conf_file',
							'convert_chd_bin',
							'convert_chd_cue',
							'lynx_header_fix',
							'rename_rom_postdl',
							'generate_uae_conf_file',
							'generate_uae4arm_conf_file',
							'generate_uae_cd32_conf_file',
							'convert_7z_m3u',
							'convert_7z_track1_bin',
							'convert_7z_gdi',
							'convert_7z_cue',
							'convert_7z_iso',
							'convert_zip_m3u',
							'convert_zip_track1_bin',
							'convert_zip_gdi',
							'convert_zip_cue',
							'convert_zip_iso',
							'convert_adf_folder',
							'convert_mame_softlist',
							'convert_mess2014_softlist',
							'Cancel']

	ret1 = current_dialog.select('Select New Post Download Action',post_dl_actions_list)

	try:
		print 'ztest'
		print ret1
		selected_action = post_dl_actions_list[ret1]
		selected_command = post_dl_commands_list[ret1]
		print 'ztest'
		print selected_action
		print selected_command
	except:
		selected_action = 'Cancel'
		selected_command = None
		xbmc.log(msg='IARL:  An unknown post DL action was selected, defaulting to Cancel', level=xbmc.LOGDEBUG)

	new_command_append = None
	if selected_action != 'Cancel': #Attempt to update post DL command if Cancel was not selected
		if selected_command is not None:
			ret2 = current_dialog.select('Are you sure you want to set the post DL action to '+selected_action+' for '+current_xml_filename, ['Yes','Cancel'])
			if ret2<1: #If the user selected YES, then keep going
				if selected_command == 'rename_rom_postdl': #Ask user for new extension
					new_command_append = current_dialog.input('Enter the new file extension:')
				elif selected_command == 'convert_mame_softlist': #Ask user for mame softlist type
					new_command_append = current_dialog.input('Enter the softlist type:')
				elif selected_command == 'convert_mess2014_softlist': #Ask user for mess2014 softlist type
					new_command_append = current_dialog.input('Enter the softlist type:')

				if new_command_append is not None:
					selected_command = selected_command+"('"+new_command_append+"')"
					selected_action = selected_action+" ("+new_command_append+")"
				xbmc.log(msg='IARL:  POSTDL Update: '+str(selected_command), level=xbmc.LOGDEBUG)
				update_xml_header(current_xml_path,current_xml_filename,'emu_postdlaction',selected_command)
				ok_ret = current_dialog.ok('Complete','Post Download Action Updated to '+selected_action+'[CR]Cache was cleared for new settings')
				delete_userdata_list_cache_file(current_xml_filename.split('.')[0])
		else:
			xbmc.log(msg='IARL:  An unknown post DL action was selected, no changes were made', level=xbmc.LOGDEBUG)
	else:
		xbmc.log(msg='IARL:  The post DL action was canceled, no changes were made', level=xbmc.LOGDEBUG)

def set_new_emu_launcher(xml_id,plugin):
	current_xml_fileparts = os.path.split(xml_id)
	current_xml_filename = current_xml_fileparts[1]
	current_xml_path = current_xml_fileparts[0]

	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Select New Emulator Launcher', ['Kodi RetroPlayer','External','Cancel'])
	if ret1 == 0:
		ret2 = current_dialog.select('Are you sure you want to set the Emulator to Kodi Retroplayer for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_launcher','retroplayer')
			ok_ret = current_dialog.ok('Complete','Emulator updated to Kodi Retroplayer[CR]Cache was cleared for new settings')
			delete_userdata_list_cache_file(current_xml_filename.split('.')[0])
	elif ret1 == 1:
		ret2 = current_dialog.select('Are you sure you want to set the Emulator to External Program for '+current_xml_filename, ['Yes','Cancel'])
		if ret2<1:
			update_xml_header(current_xml_path,current_xml_filename,'emu_launcher','external')
			ok_ret = current_dialog.ok('Complete','Emulator updated to External Program[CR]Cache was cleared for new settings')
			delete_userdata_list_cache_file(current_xml_filename.split('.')[0])
	else:
		pass

def check_file_exists_wildcard(file_path,file_name_2,exact_match_req):
	#A more robust file exists check.  This will check for any file or folder with the same base filename (replacing spaces with wildcard and file extension with wildcard) that is trying to be launched
	#It will not match retroarch save filetypes like srm, sav, etc
	xbmc.log(msg='IARL:  Looking for matches for '+str(file_path)+' - Exact Matching: '+str(exact_match_req),level=xbmc.LOGDEBUG)
	file_found = False #Default to not found
	idx = None
	try:
		file_path_base = os.path.split(file_path)[0]
		file_path_name = os.path.splitext(os.path.split(file_path)[-1])[0].replace('][','*').replace('[','*').replace(']','*') #glob doesnt like literal brackets in filenames
		if len(os.path.splitext(file_name_2)[-1]) == 4:
			file_path_name2 = os.path.splitext(file_name_2)[0] #Remove extension if present
		else:
			file_path_name2 = file_name_2
		for ii in range(1,101): #Remove numbers 1. - 100. from filename
			if file_path_name2.startswith(str(ii)+'.'):
				file_path_name2 = file_path_name2.replace(str(ii)+'.','').strip()
		matching_files = glob.glob(os.path.join(file_path_base,file_path_name.replace(' ','*')+'*')) #Search for the filename with a different extension or folder with same name
		matching_files = matching_files+glob.glob(os.path.join(file_path_base,'*',file_path_name.replace(' ','*')+'*')) #Add recursive search one folder down for MESS type setups
		matching_files = matching_files+glob.glob(os.path.join(file_path_base,clean_file_folder_name(file_path_name.split('(')[0])+'*')) #Add search for processed filenames used in IARL
		#Search again for files without commas in the filename	
		matching_files = matching_files+glob.glob(os.path.join(file_path_base,file_path_name.replace(',','*').replace(' ','*')+'*')) #Search for the filename with a different extension or folder with same name
		matching_files = matching_files+glob.glob(os.path.join(file_path_base,'*',file_path_name.replace(',','*').replace(' ','*')+'*')) #Add recursive search one folder down for MESS type setups
		matching_files = matching_files+glob.glob(os.path.join(file_path_base,clean_file_folder_name(file_path_name.replace(',','*').split('(')[0])+'*')) #Add search for processed filenames used in IARL
		if file_path_name != file_path_name2: #if the save filename is not the same as the rom name, search for that too unzipped files may be named per rom name rather than save filename
			matching_files = matching_files+glob.glob(os.path.join(file_path_base,file_path_name2.replace(' ','*')+'*')) #Search for the filename with a different extension or folder with same name
			matching_files = matching_files+glob.glob(os.path.join(file_path_base,'*',file_path_name2.replace(' ','*')+'*')) #Add recursive search one folder down for MESS type setups
			matching_files = matching_files+glob.glob(os.path.join(file_path_base,clean_file_folder_name(file_path_name2.split('(')[0])+'*')) #Add search for processed filenames used in IARL
			#Search again for files without commas in the filename	
			matching_files = matching_files+glob.glob(os.path.join(file_path_base,file_path_name2.replace(',','*').replace(' ','*')+'*')) #Search for the filename with a different extension or folder with same name
			matching_files = matching_files+glob.glob(os.path.join(file_path_base,'*',file_path_name2.replace(',','*').replace(' ','*')+'*')) #Add recursive search one folder down for MESS type setups
			matching_files = matching_files+glob.glob(os.path.join(file_path_base,clean_file_folder_name(file_path_name2.replace(',','*').split('(')[0])+'*')) #Add search for processed filenames used in IARL
		remove_these_filetypes = ['srm','sav','fs','state','auto','xml'] #Save filetypes
		matching_files = list(set([x for x in matching_files if x.split('.')[-1].lower() not in remove_these_filetypes])) #Remove duplicates and save filetypes
		if len(matching_files)>0: #Matches were found, look for an exact match first
			xbmc.log(msg='IARL:  Matching files found for '+str(file_path)+': '+str(', '.join(matching_files)), level=xbmc.LOGDEBUG)
			try:
				idx = matching_files.index(file_path)
				xbmc.log(msg='IARL:  Exact match found for '+str(file_path), level=xbmc.LOGDEBUG)
				file_path = matching_files[idx]
				file_found = True
			except:
				idx = None
				xbmc.log(msg='IARL:  Exact match not found.', level=xbmc.LOGDEBUG)
				file_found = False
			if not exact_match_req: #If an exact match is not required for launching
				if idx is None: #And an exact match wasnt found, search for the best match
					try:
						xbmc.log(msg='IARL:  Best match '+str(file_path)+': '+str(difflib.get_close_matches(str(file_path),matching_files,1)[0]), level=xbmc.LOGDEBUG)
						file_path = difflib.get_close_matches(str(file_path),matching_files,1)[0]
						file_found = True
					except:
						xbmc.log(msg='IARL:  2nd best match '+str(file_path)+': '+str(matching_files[0]), level=xbmc.LOGDEBUG)
						file_path = str(matching_files[0]) #Return the first file found?  Not sure if this will work in all cases, maybe prompt the user?
						file_found = True
		else:
			xbmc.log(msg='IARL:  No matching file found for '+str(file_path), level=xbmc.LOGDEBUG)
	except:
		xbmc.log(msg='IARL:  The file '+str(file_path)+' couldnt be searched', level=xbmc.LOGDEBUG)

	return file_found, file_path

def check_downloaded_file(file_path):
	bad_file_found = False
	st = os.stat(file_path)
	# print st
	if st.st_size < 1: #Zero Byte File
		current_dialog = xbmcgui.Dialog()
		ok_ret = current_dialog.ok('Error','The selected file was not available in the Archive.')
		xbmc.log(msg='IARL:  The file '+str(file_path)+' was 0 bytes in size.', level=xbmc.LOGERROR)
		os.remove(file_path) #Remove Zero Byte File
		bad_file_found = True
	if st.st_size > 1 and st.st_size < 40000: #Small file, check if archive.org returned 'item not found'
		try:
			with open(file_path, 'r') as content_file:
				file_contents = content_file.read().replace('\n', '')
			if '<title>item not available' in file_contents.lower() or '<title>internet archive' in file_contents.lower() or '<title>archive.org' in file_contents.lower():
				current_dialog = xbmcgui.Dialog()
				ok_ret = current_dialog.ok('Error','Archive returned no file or requires login in settings.')
				xbmc.log(msg='IARL:  Archive.org returned a bad file for '+str(file_path)+'.  The archive may require login to download this file.', level=xbmc.LOGERROR)
				os.remove(file_path) #Remove bad file.
				bad_file_found = True	
		except:
			xbmc.log(msg='IARL:  The file '+str(file_path)+' couldnt be read for validity.', level=xbmc.LOGDEBUG)

	return bad_file_found