#Internet Archive ROM Launcher
#Zach Morris
#https://github.com/zach-morris/plugin.program.iarl

from resources.lib.xbmcswift2b import Plugin
from resources.lib.xbmcswift2b import actions
from resources.lib.xbmcswift2b import ListItem as LI
import os, sys, subprocess, xbmc, xbmcgui, xbmcaddon
from resources.lib.util import *
from resources.lib.webutils import *
import resources.lib.paginate as paginate

xbmc.log(msg='IARL:  Lets Play!', level=xbmc.LOGNOTICE)

#Initialize Stuff
plugin = Plugin()

iarl_data = {
            'settings' : {  'cache_list' : plugin.get_setting('iarl_setting_cache_list',bool),
                            'clean_list' : plugin.get_setting('iarl_setting_clean_list',bool),
                            'listing_convention' : plugin.get_setting('iarl_setting_listing',unicode),
                            'naming_convention' : plugin.get_setting('iarl_setting_naming',unicode),
                            'items_per_page_setting' : None, #Initialize variable and set later
                            'local_file_action' : plugin.get_setting('iarl_setting_localfile_action',unicode),
                            'game_select_action' : plugin.get_setting('iarl_setting_default_action',unicode),
                            'window_theme' : plugin.get_setting('iarl_setting_rom_window_theme',unicode),
                            'download_cache' : None, #Initialize variable and set later
                            'ia_enable_login' : None, #Initialize variable and set later
                            'ia_username' : plugin.get_setting('iarl_setting_ia_username',unicode),
                            'ia_password' : plugin.get_setting('iarl_setting_ia_password',unicode),
                            'external_launch_env' : plugin.get_setting('iarl_external_user_external_env',unicode),
                            'external_launch_close_kodi' : plugin.get_setting('iarl_external_launch_close_kodi',unicode),
                            'path_to_retroarch' : plugin.get_setting('iarl_path_to_retroarch',unicode),
                            'path_to_retroarch_system_dir' : plugin.get_setting('iarl_path_to_retroarch_system_dir',unicode),
                            'path_to_retroarch_cfg' : plugin.get_setting('iarl_path_to_retroarch_cfg',unicode),
                            'enable_additional_emulators' : [plugin.get_setting('iarl_additional_emulator_1_type',unicode),plugin.get_setting('iarl_additional_emulator_2_type',unicode),plugin.get_setting('iarl_additional_emulator_3_type',unicode)],
                            'path_to_additional_emulators' : [plugin.get_setting('iarl_additional_emulator_1_path',unicode),plugin.get_setting('iarl_additional_emulator_2_path',unicode),plugin.get_setting('iarl_additional_emulator_3_path',unicode)],
                            'enable_netplay' : None, #Initialize variable and set later
                            'netplay_host_or_client' : plugin.get_setting('iarl_netplay_hostclient',unicode),
                            'netplay_host_nickname' : plugin.get_setting('iarl_netplay_nickname1',unicode),
                            'netplay_client_nickname' : plugin.get_setting('iarl_netplay_nickname2',unicode),
                            'netplay_spectator_nickname' : plugin.get_setting('iarl_netplay_nickname3',unicode),
                            'netplay_host_IP' : plugin.get_setting('iarl_netplay_IP',unicode),
                            'netplay_host_port' : plugin.get_setting('iarl_netplay_port',unicode),
                            'netplay_sync_frames' : None, #Initialize variable and set later
                            'hidden_setting_clear_cache_value' : plugin.get_setting('iarl_setting_clear_cache_value',bool),
                            'hidden_setting_clear_hidden_archives' : plugin.get_setting('iarl_setting_clear_hidden_archives',bool),
                            'hidden_setting_warn_chd' : plugin.get_setting('iarl_setting_warn_chd',bool),
                            'hidden_setting_warn_iso' : plugin.get_setting('iarl_setting_warn_iso',bool),
                            'hard_coded_include_back_link' : False,
                        },
            'addon_data':{  'plugin_name' : 'plugin.program.iarl',
                            'log_level' : 'LOG_LEVEL_INFO',
                            'operating_system' : get_operating_system(),
                            'addon_media_path' : get_media_files_path(),
                            'addon_skin_path' : get_skin_files_path(),
                            'addon_dat_path' : get_XML_files_path(),
                            'addon_temp_dl_path' : get_userdata_temp_dir(),
                            'addon_list_cache_path' : get_userdata_list_cache_dir(),
                            'addon_install_path' : get_addon_install_path(),
                            'addon_bin_path' : get_addondata_bindir(),
                            '7za_path' : None,
                            'chdman_path' : None,
                            'default_icon' : 'arcade_default_box.jpg',
                            'default_header_color' : 'white.png',
                            'default_bg_color' : 'black.png',
                            'default_buttonfocustheme' : 'button-highlight1.png',
                            'default_buttonnofocustheme' : 'button-nofocus2.png',
            },
            'archive_data': None,
            'current_archive_data':{'xml_id' : None,
                            'page_id' : None,
                            'emu_name' : None,
                            'emu_base_url' : None,
                            'emu_homepage' : None,
                            'emu_filepath' : None,
                            'emu_parser' : None,
                            'emu_category' : None,
                            'emu_version' : None,
                            'emu_date' : None,
                            'emu_author' : None,
                            'emu_description' : None,
                            'emu_plot' : None,
                            'emu_boxart' : None,
                            'emu_banner' : None,
                            'emu_fanart' : None,
                            'emu_logo' : None,
                            'emu_trailer' : None,
                            'emu_download_path' : None,
                            'emu_post_download_action' : None,
                            'emu_launcher' : None,
                            'emu_ext_launch_cmd' : None,
                            'total_num_archives' : None,
                            'emu_total_num_games' : None,
                            'category_id' : None,
                            'header_color' : None,
                            'background_color' : None,
                            'button_focus' : None,
                            'button_nofocus' : None,
                            },
            'current_rom_data':{'rom_label' : None,
                            'rom_name' : None,
                            'rom_icon' : None,
                            'rom_thumbnail' : None,
                            'rom_title' : None,
                            'rom_filenames' : list(),
                            'rom_save_filenames' : list(),
                            'rom_supporting_filenames' : list(),
                            'rom_save_supporting_filenames' : list(),
                            'rom_emu_command' : None,
                            'rom_size' : list(),
                            'rom_plot' : None,
                            'rom_date' : None,
                            'rom_year' : None,
                            'rom_studio' : None,
                            'rom_genre' : None,
                            'rom_nplayers' : None,
                            'rom_tag' : None,
                            'rom_rating' : None,
                            'rom_perspective' : None,
                            'rom_esrb' : None,
                            'rom_trailer' : None,
                            'rom_boxarts' : [None,None,None,None,None,None,None,None,None,None],
                            'rom_snapshots' : [None,None,None,None,None,None,None,None,None,None],
                            'rom_fanarts' : [None,None,None,None,None,None,None,None,None,None],
                            'rom_banners' : [None,None,None,None,None,None,None,None,None,None],
                            'rom_logos' : [None,None,None,None,None,None,None,None,None,None],
                            },
            'current_save_data':{'rom_save_filenames' : list(),
                            'rom_save_filenames_exist' : list(),
                            'rom_save_filenames_success' : list(),
                            'rom_supporting_filenames' : list(),
                            'rom_save_supporting_filenames' : list(),
                            'rom_save_supporting_filenames_exist' : list(),
                            'rom_save_supporting_filenames_success' : list(),
                            'rom_converted_filenames' : list(),
                            'rom_converted_filenames_success' : list(),
                            'rom_converted_supporting_filenames' : list(),
                            'rom_converted_supporting_filenames_success' : list(),
                            'overall_download_success' : True,
                            'overall_conversion_success' : True,
                            'overwrite_existing_files' : False,
                            'launch_filename' : None,
                            },
}

#Define number of items to display per page
items_pp_options = {'10':10,'25':25,'50':50,'100':100,'150':150,'200':200,'250':250,'300':300,'350':350,'400':400,'450':450,'500':500,'List All':99999}
try:
    iarl_data['settings']['items_per_page_setting'] = items_pp_options[plugin.get_setting('iarl_setting_items_pp',unicode)]
except ValueError:
    iarl_data['settings']['items_per_page_setting'] = 99999 #Default to All if not initialized correctly

if iarl_data['settings']['items_per_page_setting'] is None:
    iarl_data['settings']['items_per_page_setting'] = 99999 #Default to All if not initialized correctly

#Define temp download cache size
cache_options = {'Zero (One ROM and Supporting Files Only)':0,'10 MB':10*1e6,'25MB':25*1e6,'50MB':50*1e6,'100MB':100*1e6,'150MB':150*1e6,'200MB':200*1e6,'250MB':250*1e6,'300MB':300*1e6,'350MB':350*1e6,'400MB':400*1e6,'450MB':450*1e6,'500MB':500*1e6,'1GB':1000*1e6,'2GB':2000*1e6,'5GB':5000*1e6,'10GB':10000*1e6,'20GB':20000*1e6}
try:
    iarl_data['settings']['download_cache'] = cache_options[plugin.get_setting('iarl_setting_dl_cache',unicode)]
except ValueError:
    iarl_data['settings']['download_cache'] = 0 #Default to 0 if not initialized correctly

if iarl_data['settings']['download_cache'] is None:
    iarl_data['settings']['download_cache'] = 0 #Default to 0 if not initialized correctly

#Convert Enabled/Disabled to True/False
enabled_disabled_options = {'Enabled':True,'Disabled':False}
try:
    iarl_data['settings']['enable_netplay'] = enabled_disabled_options[plugin.get_setting('iarl_enable_netplay',unicode)]
except ValueError:
    iarl_data['settings']['enable_netplay'] = False #Default to False if not initialized correctly

if iarl_data['settings']['enable_netplay'] is None:
    iarl_data['settings']['enable_netplay'] = False #Default to False if not initialized correctly

try:
    iarl_data['settings']['netplay_sync_frames'] = enabled_disabled_options[plugin.get_setting('iarl_netplay_frames',unicode)]
except ValueError:
    iarl_data['settings']['netplay_sync_frames'] = False #Default to False if not initialized correctly

if iarl_data['settings']['netplay_sync_frames'] is None:
    iarl_data['settings']['netplay_sync_frames'] = False #Default to False if not initialized correctly

try:
    iarl_data['settings']['ia_enable_login'] = enabled_disabled_options[plugin.get_setting('iarl_enable_login',unicode)]
except ValueError:
    iarl_data['settings']['ia_enable_login'] = False #Default to False if not initialized correctly

if iarl_data['settings']['ia_enable_login'] is None:
    iarl_data['settings']['ia_enable_login'] = False #Default to False if not initialized correctly

#Define path to 7za binary
if 'OSX' in iarl_data['addon_data']['operating_system']:
    iarl_data['addon_data']['7za_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'7za','7za.OSX')
elif 'Windows' in iarl_data['addon_data']['operating_system']:
    iarl_data['addon_data']['7za_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'7za','7za.exe')
elif 'Nix' in iarl_data['addon_data']['operating_system']:
    iarl_data['addon_data']['7za_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'7za','7za.Nix')
elif 'OpenElec RPi' in iarl_data['addon_data']['operating_system'] or 'Android' in iarl_data['addon_data']['operating_system'] or 'LibreElec RPi' in iarl_data['addon_data']['operating_system']:
    try:
        if 'v7' in os.uname()[4]:
            iarl_data['addon_data']['7za_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'7za','7za.armv7l')
        else:
            iarl_data['addon_data']['7za_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'7za','7za.armv6l')
    except:
        iarl_data['addon_data']['7za_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'7za','7za.armv6l')
elif 'OpenElec x86' in iarl_data['addon_data']['operating_system'] or 'LibreElec x86' in iarl_data['addon_data']['operating_system']:
    iarl_data['addon_data']['7za_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'7za','7za.x86_64')
else:
    iarl_data['addon_data']['7za_path'] = None
    xbmc.log(msg='IARL:  7ZA Path could not be defined', level=xbmc.LOGDEBUG)

#Define path to CHDMAN binary
if 'OSX' in iarl_data['addon_data']['operating_system']:
    iarl_data['addon_data']['chdman_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'chdman','chdman.OSX')
elif 'Windows' in iarl_data['addon_data']['operating_system']:
    iarl_data['addon_data']['chdman_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'chdman','chdman.exe')
elif 'Nix' in iarl_data['addon_data']['operating_system']:
    iarl_data['addon_data']['chdman_path'] = os.path.join(iarl_data['addon_data']['addon_bin_path'],'chdman','chdman.Nix')
else:
    iarl_data['addon_data']['chdman'] = None
    xbmc.log(msg='IARL:  CHDMAN Path could not be defined', level=xbmc.LOGDEBUG)

#If cache list is false, then clear the listed cache every time the addon is run
if not iarl_data['settings']['cache_list']:
    try:
        plugin.clear_function_cache()
    except:
        pass

#If the advanced setting action 'Clear Addon Cache' was set, then run this one time clear cache function
if iarl_data['settings']['hidden_setting_clear_cache_value']:
    advanced_setting_action_clear_cache(plugin)

#If the advanced setting action 'Unhide All Archives' was set, then run this one time clear hidden archives function
if iarl_data['settings']['hidden_setting_clear_hidden_archives']:
    unhide_all_archives(plugin)
    xbmcaddon.Addon(id='plugin.program.iarl').setSetting(id='iarl_setting_clear_hidden_archives',value='false')
    xbmc.log(msg='IARL:  Unhide All Archives set back to false', level=xbmc.LOGDEBUG)

#When addon is initialized, get all available archive infos
iarl_data['archive_data'] = get_archive_info()

##Start of Addon Routes
#Update XML Value (Context Menu Item)
@plugin.route('/update_xml/<xml_id>')
def update_xml_value(xml_id):
    args_in = plugin.request.args
    try:
        tag_value = args_in['tag_value'][0]
    except:
        tag_value = None

    if tag_value == 'emu_downloadpath':
        xbmc.log(msg='IARL:  Updating archive download path for: '+str(xml_id), level=xbmc.LOGDEBUG)
        set_new_dl_path(xml_id,plugin)

    elif tag_value == 'emu_postdlaction':
        xbmc.log(msg='IARL:  Updating archive post download action for: '+str(xml_id), level=xbmc.LOGDEBUG)
        set_new_post_dl_action(xml_id,plugin)

    elif tag_value == 'emu_launcher':
        xbmc.log(msg='IARL:  Updating internal/external emulator launcher for: '+str(xml_id), level=xbmc.LOGDEBUG)
        set_new_emu_launcher(xml_id,plugin)

    elif tag_value == 'emu_ext_launch_cmd':
        xbmc.log(msg='IARL:  Updating external launch command for: '+str(xml_id), level=xbmc.LOGDEBUG)
        update_external_launch_commands(iarl_data,xml_id,plugin)

    elif tag_value == 'hide_archive':
        xbmc.log(msg='IARL:  Updating archive visibility for: '+str(xml_id), level=xbmc.LOGDEBUG)
        hide_selected_archive(iarl_data,xml_id,plugin)

    elif tag_value == 'refresh_archive_cache':
        xbmc.log(msg='IARL:  Refreshing list_cache for: '+str(xml_id), level=xbmc.LOGDEBUG)
        if iarl_data['archive_data'] is None:
            iarl_data['archive_data'] = get_archive_info()
        try:
            cache_category_id = iarl_data['archive_data']['category_id'][iarl_data['archive_data']['emu_filepath'].index(xml_id)]
            clear_cache_success = delete_userdata_list_cache_file(cache_category_id)
        except:
            xbmc.log(msg='IARL:  Unable to clear list_cache for: '+str(xml_id), level=xbmc.LOGERROR)
        if clear_cache_success:
            current_dialog = xbmcgui.Dialog()
            ok_ret = current_dialog.ok('Complete','Archive Listing Refreshed')
    else:
        xbmc.log(msg='IARL:  Context menu selection is not defined', level=xbmc.LOGERROR)
        pass #Do Nothing

def update_context(xml_id_in,tag_value_in,context_label):
    new_url = plugin.url_for('update_xml_value', xml_id=xml_id_in, tag_value = tag_value_in)
    return (context_label, actions.background(new_url))

#Add Favorite (Context Menu Item)
@plugin.route('/update_favorites/<item_string>')
def update_favorite_items(item_string):
    ystr = lambda s: s if len(s) > 0 else None

    if iarl_data['archive_data'] is None:
        iarl_data['archive_data'] = get_archive_info()

    iarl_data['current_rom_data']['rom_name'] = ystr(xbmc.getInfoLabel('ListItem.Property(rom_name)'))
    iarl_data['current_rom_data']['rom_icon'] = ystr(xbmc.getInfoLabel('ListItem.Icon'))
    iarl_data['current_rom_data']['rom_thumbnail'] = ystr(xbmc.getInfoLabel('ListItem.Thumb'))
    iarl_data['current_rom_data']['rom_title'] = ystr(xbmc.getInfoLabel('ListItem.Title'))
    iarl_data['current_rom_data']['rom_studio'] = ystr(xbmc.getInfoLabel('ListItem.Studio'))
    iarl_data['current_rom_data']['rom_genre'] = ystr(xbmc.getInfoLabel('ListItem.Genre'))
    iarl_data['current_rom_data']['rom_date'] = ystr(xbmc.getInfoLabel('ListItem.Date'))
    iarl_data['current_rom_data']['rom_year'] = ystr(xbmc.getInfoLabel('ListItem.Year'))
    iarl_data['current_rom_data']['rom_plot'] = ystr(xbmc.getInfoLabel('ListItem.Plot'))
    iarl_data['current_rom_data']['rom_trailer'] = ystr(xbmc.getInfoLabel('ListItem.Trailer'))
    iarl_data['current_rom_data']['rom_tag'] = ystr(xbmc.getInfoLabel('ListItem.Property(tag)'))
    iarl_data['current_rom_data']['rom_nplayers'] = ystr(xbmc.getInfoLabel('ListItem.Property(nplayers)'))
    iarl_data['current_rom_data']['rom_rating'] = ystr(xbmc.getInfoLabel('ListItem.Property(rating)'))
    iarl_data['current_rom_data']['rom_esrb'] = ystr(xbmc.getInfoLabel('ListItem.Property(esrb)'))
    iarl_data['current_rom_data']['rom_perspective'] = ystr(xbmc.getInfoLabel('ListItem.Property(perspective)'))
    iarl_data['current_rom_data']['rom_emu_command'] = ystr(xbmc.getInfoLabel('ListItem.Property(rom_emu_command)'))
    iarl_data['current_rom_data']['rom_label'] = ystr(xbmc.getInfoLabel('ListItem.Label'))
    iarl_data['current_rom_data']['emu_post_download_action'] = ystr(xbmc.getInfoLabel('ListItem.Property(emu_post_download_action)')) #Needed to add this for xml favorites
    iarl_data['current_rom_data']['rom_filenames'] = [ystr(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_filenames)').split(',')] #Split into list
    iarl_data['current_rom_data']['rom_supporting_filenames'] = [ystr(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_supporting_filenames)').split(',')] #Split into list
    iarl_data['current_rom_data']['rom_save_filenames'] = [ystr(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_save_filenames)').split(',')] #Split into list
    iarl_data['current_rom_data']['rom_save_supporting_filenames'] = [ystr(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_save_supporting_filenames)').split(',')] #Split into list
    iarl_data['current_rom_data']['rom_size'] = [int(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_file_sizes)').split(',')] #Split into list, convert to int
    for ii in range(0,total_arts):
        iarl_data['current_rom_data']['rom_fanarts'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(fanart'+str(ii+1)+')'))
        iarl_data['current_rom_data']['rom_boxarts'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(boxart'+str(ii+1)+')'))
        iarl_data['current_rom_data']['rom_banners'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(banner'+str(ii+1)+')'))
        iarl_data['current_rom_data']['rom_snapshots'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(snapshot'+str(ii+1)+')'))
        iarl_data['current_rom_data']['rom_logos'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(logo'+str(ii+1)+')'))

    favorites_xml_filename = query_favorites_xml(iarl_data) #Find all the current favorite xml files, prompt for which to use, or make a new one

    if favorites_xml_filename is not None:
        try:
            add_success = add_favorite_to_xml(iarl_data,favorites_xml_filename)
            if add_success:
                current_dialog = xbmcgui.Dialog()
                ok_ret = current_dialog.ok('Complete','Favorite Added:[CR]'+str(iarl_data['current_rom_data']['rom_name']))   
                xbmc.log(msg='IARL:  Favorite was added: '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGNOTICE)
        except:
            xbmc.log(msg='IARL:  There was an error adding the favorite '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)
        
        if add_success:
            try:
                cache_category_id = iarl_data['archive_data']['category_id'][iarl_data['archive_data']['emu_filepath'].index(favorites_xml_filename)]
                clear_cache_success = delete_userdata_list_cache_file(cache_category_id)
            except:
                xbmc.log(msg='IARL:  Unable to clear list_cache for the favorite list', level=xbmc.LOGERROR)

def update_context_favorite(item_in,context_label):
    new_url = plugin.url_for('update_favorite_items', item_string=item_in)
    return (context_label, actions.background(new_url))

## Main Start/Index Page of Addon
@plugin.route('/')
def index():
    items = []
    initialize_userdata()
    if iarl_data['archive_data'] is None:
        iarl_data['archive_data'] = get_archive_info()
    if len(iarl_data['archive_data']['emu_name'])<1: #This is a first run issue, check archive_data
        iarl_data['archive_data'] = get_archive_info()

    for ii in range(0,iarl_data['archive_data']['total_num_archives']):
        #Generate the context menu
        context_menus = [update_context(iarl_data['archive_data']['emu_filepath'][ii],'emu_downloadpath','Update Download Path'),
                        #update_context(iarl_data['archive_data']['emu_filepath'][ii],'emu_postdlaction','Update Post DL Action'), #Hidden now since users shouldnt change this
                        update_context(iarl_data['archive_data']['emu_filepath'][ii],'emu_launcher','Update Launcher'),
                        update_context(iarl_data['archive_data']['emu_filepath'][ii],'emu_ext_launch_cmd','Update Ext Launcher Command'),
                        update_context(iarl_data['archive_data']['emu_filepath'][ii],'hide_archive','Hide This Archive'),
                        update_context(iarl_data['archive_data']['emu_filepath'][ii],'refresh_archive_cache','Refresh Archive Listing'),]

        if 'hidden' not in iarl_data['archive_data']['emu_category'][ii]: #Don't include the archive if it's tagged hidden
            if 'alphabetical' in iarl_data['settings']['listing_convention'].lower(): #List alphabetically
                current_plugin_path = plugin.url_for('get_rom_starting_letter_page', category_id=iarl_data['archive_data']['category_id'][ii])
            else:
                current_plugin_path = plugin.url_for('get_rom_page', category_id=iarl_data['archive_data']['category_id'][ii],page_id='1')

            items.append(plugin._listitemify({ 
                'label' : iarl_data['archive_data']['emu_name'][ii],
                'path': current_plugin_path,
                'icon': iarl_data['archive_data']['emu_logo'][ii],
                'thumbnail' : iarl_data['archive_data']['emu_boxart'][ii],
                'info' : {'genre': iarl_data['archive_data']['emu_category'][ii],
                          'credits': iarl_data['archive_data']['emu_author'][ii],
                          'date': iarl_data['archive_data']['emu_date'][ii],
                          'plot': iarl_data['archive_data']['emu_plot'][ii],
                          'trailer': get_youtube_plugin_url(iarl_data['archive_data']['emu_trailer'][ii]),
                          'FolderPath': iarl_data['archive_data']['emu_base_url'][ii]},
                'properties' : {'fanart_image' : iarl_data['archive_data']['emu_fanart'][ii],
                                'banner' : iarl_data['archive_data']['emu_banner'][ii],
                                'clearlogo': iarl_data['archive_data']['emu_logo'][ii],
                                'poster': iarl_data['archive_data']['emu_boxart'][ii]},
                'context_menu' : context_menus
                }))
            items[-1].set_banner(items[-1].get_property('banner'))
            items[-1].set_landscape(items[-1].get_property('banner'))
            items[-1].set_poster(items[-1].get_property('poster'))
            items[-1].set_clearlogo(items[-1].get_property('clearlogo'))
            items[-1].set_clearart(items[-1].get_property('clearlogo'))

    #Append Search Function
    items.append(plugin._listitemify({ 
        'label' : '\xc2\xa0Search',
        'path' :  plugin.url_for('search_roms_window'),
        'icon': os.path.join(iarl_data['addon_data']['addon_media_path'],'search.jpg'),
        'thumbnail' : os.path.join(iarl_data['addon_data']['addon_media_path'],'search.jpg'),
        'info' : {'genre': '\xc2\xa0',
                  'date': '01/01/2999',
                  'plot' : 'Search for a particular game.'},
        'properties' : {'fanart_image' : os.path.join(iarl_data['addon_data']['addon_media_path'],'fanart.jpg'),
                        'banner' : os.path.join(iarl_data['addon_data']['addon_media_path'],'search_banner.jpg')}
        }))
    items[-1].set_banner(items[-1].get_property('banner'))
    items[-1].set_landscape(items[-1].get_property('banner'))
    items[-1].set_poster(items[-1].get_property('poster'))
    items[-1].set_clearlogo(items[-1].get_property('clearlogo'))
    items[-1].set_clearart(items[-1].get_property('clearlogo'))

    #Append Random Play Function
    items.append(plugin._listitemify({ 
        'label' : '\xc2\xa0\xc2\xa0Random Play',
        'path' :  plugin.url_for('random_play'),
        'icon': os.path.join(iarl_data['addon_data']['addon_media_path'],'lucky.jpg'),
        'thumbnail' : os.path.join(iarl_data['addon_data']['addon_media_path'],'lucky.jpg'),
        'info' : {'genre': '\xc2\xa0\xc2\xa0', 'date': '01/01/2999', 'plot' : 'Play a random game from the archive.'},
        'properties' : {'fanart_image' : os.path.join(iarl_data['addon_data']['addon_media_path'],'fanart.jpg'),
                        'banner' : os.path.join(iarl_data['addon_data']['addon_media_path'],'lucky_banner.jpg')}
        }))
    items[-1].set_banner(items[-1].get_property('banner'))
    items[-1].set_landscape(items[-1].get_property('banner'))
    items[-1].set_poster(items[-1].get_property('poster'))
    items[-1].set_clearlogo(items[-1].get_property('clearlogo'))
    items[-1].set_clearart(items[-1].get_property('clearlogo'))

    return plugin.finish(items, update_listing=True, sort_methods=[xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_GENRE])

@plugin.route('/Emulator/<category_id>/<page_id>')
def get_rom_page(category_id,page_id):

    #Re-scrape the current archive data if the index was not first visited
    if iarl_data['archive_data'] is None:
        iarl_data['archive_data'] = get_archive_info()
    #Define current archive data based on the route category_id
    try:
        current_index = iarl_data['archive_data']['category_id'].index(category_id)
    except:
        xbmc.log(msg='IARL:  The archive '+str(category_id)+' could not be found.', level=xbmc.LOGERROR)
        current_index = None
    if current_index is not None:
        iarl_data['current_archive_data'] = define_current_archive_data(iarl_data,current_index,page_id)

    if ',' in page_id: #If the list was requested alphabetically, define the page and alpha ID
        alpha_id = page_id.split(',')[0]
        page_id = page_id.split(',')[-1]
    else:
        alpha_id = None

    #Parse XML ROM List
    try:
        if alpha_id is None: #No Alpha ID = One Big List
            rom_list = [plugin._listitemify(x) for x in get_rom_list(iarl_data,current_index)]
        else: #Only games that start with the selected letter
            if '#' in alpha_id: #List everything that doesnt start with a letter
                rom_list = [plugin._listitemify(list_item) for list_item in get_rom_list(iarl_data,current_index) if not list_item['label'].lower().isalpha()]
            else: #List everything that starts with the selected letter
                rom_list = [plugin._listitemify(list_item) for list_item in get_rom_list(iarl_data,current_index) if (alpha_id.lower() in list_item['label'].lower()[0])]
    except:
        xbmc.log(msg='IARL:  Unable to get ROM List: %s'%str(sys.exc_info()[0]), level=xbmc.LOGERROR)
        rom_list = None
    items = list()
    for ii in range(0,len(rom_list)):
        # items.append(plugin._listitemify(roms))
        rom_list[ii].set_banner(rom_list[ii].get_property('banner'))
        rom_list[ii].set_landscape(rom_list[ii].get_property('banner'))
        rom_list[ii].set_poster(rom_list[ii].get_property('poster'))
        rom_list[ii].set_clearlogo(rom_list[ii].get_property('clearlogo'))
        rom_list[ii].set_clearart(rom_list[ii].get_property('clearlogo'))
    #Paginate results
    page = paginate.Page(rom_list, page=page_id, items_per_page=iarl_data['settings']['items_per_page_setting'])

    #Create Page Controls
    next_page = []
    prev_page = []

    if alpha_id is None: #One Big List
        prev_page_str = str(page.previous_page)
        next_page_str = str(page.next_page)
    else:
        prev_page_str = alpha_id+','+str(page.previous_page)
        next_page_str = alpha_id+','+str(page.next_page)

    prev_page.append(plugin._listitemify({ 
        'label' : '\xc2\xa0Prev <<',
        'path' :  plugin.url_for('get_rom_page', category_id=category_id,page_id=prev_page_str),
        'icon': os.path.join(iarl_data['addon_data']['addon_media_path'],'Previous.png'),
        'thumbnail' : os.path.join(iarl_data['addon_data']['addon_media_path'],'Previous.png'),
        'info' : {'genre': '\xc2\xa0',
                  'date': '01/01/2999',
                  'plot' : 'Page ' + str(page.page) + ' of ' + str(page.page_count) + '.  Prev page is ' + str(page.previous_page) + '.  Total of ' + str(page.item_count) + ' games in this archive.'}
        }))
    next_page.append(plugin._listitemify({ 
        'label' : '\xc2\xa0Next >>',
        'path' :  plugin.url_for('get_rom_page', category_id=category_id,page_id=next_page_str),
        'icon': os.path.join(iarl_data['addon_data']['addon_media_path'],'Next.png'),
        'thumbnail' : os.path.join(iarl_data['addon_data']['addon_media_path'],'Next.png'),
        'info' : {'genre': '\xc2\xa0',
                  'date': '01/01/2999',
                  'plot' : 'Page ' + str(page.page) + ' of ' + str(page.page_count) + '.  Next page is ' + str(page.next_page) + '.  Total of ' + str(page.item_count) + ' games in this archive.'}
        }))

    #Define the listitems to display
    current_page = page.items

    #Add next and prev page listitems
    if iarl_data['settings']['hard_coded_include_back_link']:
        if page.previous_page:
            current_page.extend(prev_page)

    if page.next_page:
        current_page.extend(next_page)

    # # plugin.finish(succeeded=True, update_listing=True,sort_methods=[xbmcplugin.SORT_METHOD_NONE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_GENRE, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE])
    return plugin.finish(current_page, sort_methods=[xbmcplugin.SORT_METHOD_NONE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_GENRE, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE])

@plugin.route('/Emulator_Alpha/<category_id>')
def get_rom_starting_letter_page(category_id):
    items = []
    alpha_pages = ['#','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

    for alpha_page in alpha_pages:
        if '#' in alpha_page:
            alpha_image_id = 'Numeric'
        else:
            alpha_image_id = alpha_page
        items.append(plugin._listitemify({ 
        'label' : alpha_page,
        'path': plugin.url_for('get_rom_page', category_id=category_id,page_id=alpha_page+',1'),
        'icon': os.path.join(iarl_data['addon_data']['addon_media_path'],alpha_image_id+'.png'),
        'thumbnail' : os.path.join(iarl_data['addon_data']['addon_media_path'],alpha_image_id+'.png'),
        'properties' : {'fanart_image' : os.path.join(iarl_data['addon_data']['addon_media_path'],'fanart.jpg'),
        'banner' : os.path.join(iarl_data['addon_data']['addon_media_path'],alpha_image_id+'_banner.png')}
        }))
        items[-1].set_banner(items[-1].get_property('banner'))
        items[-1].set_landscape(items[-1].get_property('banner'))
        items[-1].set_poster(items[-1].get_property('poster'))

    return plugin.finish(items, sort_methods=[xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE])

# @plugin.cached(TTL=24*60*30) #Using custom cache saving functions now
def get_rom_list(iarl_data,current_index):
    
    if iarl_data['settings']['cache_list']: #Try to load a cached list, otherwise parse and save it
        if os.path.isfile(os.path.join(iarl_data['addon_data']['addon_list_cache_path'],iarl_data['archive_data']['category_id'][current_index]+'.pickle')): #Cached list exists
            load_success, rom_list = load_userdata_list_cache_file(iarl_data['archive_data']['category_id'][current_index])
            if not load_success:
                xbmc.log(msg='IARL:  Error loading cached list, re-parsing list instead', level=xbmc.LOGDEBUG)
                rom_list = parse_xml_romfile(iarl_data,current_index,plugin)
                for ii in range(0,len(rom_list)):
                    rom_list[ii]['context_menu'] = [update_context_favorite('%s'%str(rom_list[ii]['label2']),'Add to IARL Favorites')]
        else:
            rom_list = parse_xml_romfile(iarl_data,current_index,plugin)
            for ii in range(0,len(rom_list)):
                rom_list[ii]['context_menu'] = [update_context_favorite('%s'%str(rom_list[ii]['label2']),'Add to IARL Favorites')]
            save_success = save_userdata_list_cache_file(rom_list,iarl_data['archive_data']['category_id'][current_index])
    else: #Cached lists is not selected
        rom_list = parse_xml_romfile(iarl_data,current_index,plugin)
        for ii in range(0,len(rom_list)):
            rom_list[ii]['context_menu'] = [update_context_favorite('%s'%str(rom_list[ii]['label2']),'Add to IARL Favorites')]
    return rom_list

@plugin.route('/Emulator/<category_id>/Game/<romname>')
def get_selected_rom(category_id,romname):

    ystr = lambda s: s if len(s) > 0 else None
    list_item_available = False

    try:
        current_index = iarl_data['archive_data']['category_id'].index(category_id)
    except:
        xbmc.log(msg='IARL:  The archive '+str(category_id)+' could not be found.', level=xbmc.LOGERROR)
        current_index = None
    if current_index is not None:
        iarl_data['current_archive_data'] = define_current_archive_data(iarl_data,current_index,None)

    if len(xbmc.getInfoLabel('Listitem.Title'))>0:
        if len(xbmc.getInfoLabel('ListItem.Property(rom_filenames)'))>0:
            list_item_available = True

    if not list_item_available:
        #The listitem is not defined, so we'll need to rescrape the xml for the game (most likely a favorite or other URL route)
        if iarl_data['archive_data'] is None:
                iarl_data['archive_data'] = get_archive_info()
        #Define current archive data based on the route category_id
        rom_list = get_rom_list(iarl_data,current_index)
        try:
            rom_idx = [romnames['label2'] for romnames in rom_list].index(romname)
        except:
            xbmc.log(msg='IARL:  Unable to find the requested game '+str(romname), level=xbmc.LOGERROR)
            rom_idx = None
        #Define current_data by the rescraped rom_idx
        if rom_idx is not None:
            iarl_data['current_rom_data']['rom_name'] = rom_list[rom_idx]['properties']['rom_name']
            iarl_data['current_rom_data']['rom_icon'] = rom_list[rom_idx]['properties']['rom_icon']
            iarl_data['current_rom_data']['rom_thumbnail'] = rom_list[rom_idx]['properties']['rom_thumbnail']
            iarl_data['current_rom_data']['rom_title'] = rom_list[rom_idx]['properties']['rom_title']
            iarl_data['current_rom_data']['rom_studio'] = rom_list[rom_idx]['properties']['rom_studio']
            iarl_data['current_rom_data']['rom_genre'] = rom_list[rom_idx]['properties']['rom_genre']
            iarl_data['current_rom_data']['rom_date'] = rom_list[rom_idx]['properties']['rom_date']
            iarl_data['current_rom_data']['rom_year'] = rom_list[rom_idx]['properties']['rom_year']
            iarl_data['current_rom_data']['rom_plot'] = rom_list[rom_idx]['properties']['rom_plot']
            iarl_data['current_rom_data']['rom_trailer'] = rom_list[rom_idx]['properties']['rom_trailer']
            iarl_data['current_rom_data']['rom_tag'] = rom_list[rom_idx]['properties']['tag']
            iarl_data['current_rom_data']['rom_nplayers'] = rom_list[rom_idx]['properties']['nplayers']
            iarl_data['current_rom_data']['rom_rating'] = rom_list[rom_idx]['properties']['rating']
            iarl_data['current_rom_data']['rom_esrb'] = rom_list[rom_idx]['properties']['esrb']
            iarl_data['current_rom_data']['rom_perspective'] = rom_list[rom_idx]['properties']['perspective']
            iarl_data['current_rom_data']['rom_emu_command'] = ystr(rom_list[rom_idx]['properties']['rom_emu_command'])
            iarl_data['current_rom_data']['rom_label'] = rom_list[rom_idx]['properties']['rom_label']
            iarl_data['current_rom_data']['rom_filenames'] = [ystr(x) for x in rom_list[rom_idx]['properties']['rom_filenames'].split(',')] #Split into list
            iarl_data['current_rom_data']['rom_supporting_filenames'] = [ystr(x) for x in rom_list[rom_idx]['properties']['rom_supporting_filenames'].split(',')] #Split into list
            iarl_data['current_rom_data']['rom_save_filenames'] = [ystr(x) for x in rom_list[rom_idx]['properties']['rom_save_filenames'].split(',')] #Split into list
            iarl_data['current_rom_data']['rom_save_supporting_filenames'] = [ystr(x) for x in rom_list[rom_idx]['properties']['rom_save_supporting_filenames'].split(',')] #Split into list
            iarl_data['current_rom_data']['rom_size'] = [int(x) for x in rom_list[rom_idx]['properties']['rom_file_sizes'].split(',')] #Split into list, convert to int
            for ii in range(0,total_arts):
                iarl_data['current_rom_data']['rom_fanarts'][ii] = ystr(rom_list[rom_idx]['properties']['fanart'+str(ii+1)])
                iarl_data['current_rom_data']['rom_boxarts'][ii] = ystr(rom_list[rom_idx]['properties']['boxart'+str(ii+1)])
                iarl_data['current_rom_data']['rom_banners'][ii] = ystr(rom_list[rom_idx]['properties']['banner'+str(ii+1)])
                iarl_data['current_rom_data']['rom_snapshots'][ii] = ystr(rom_list[rom_idx]['properties']['snapshot'+str(ii+1)])
                iarl_data['current_rom_data']['rom_logos'][ii] = ystr(rom_list[rom_idx]['properties']['logo'+str(ii+1)])
    else:
        #Define current_data by the selected list item
        iarl_data['current_rom_data']['rom_name'] = ystr(xbmc.getInfoLabel('ListItem.Property(rom_name)'))
        iarl_data['current_rom_data']['rom_icon'] = ystr(xbmc.getInfoLabel('ListItem.Icon'))
        iarl_data['current_rom_data']['rom_thumbnail'] = ystr(xbmc.getInfoLabel('ListItem.Thumb'))
        iarl_data['current_rom_data']['rom_title'] = ystr(xbmc.getInfoLabel('ListItem.Title'))
        iarl_data['current_rom_data']['rom_studio'] = ystr(xbmc.getInfoLabel('ListItem.Studio'))
        iarl_data['current_rom_data']['rom_genre'] = ystr(xbmc.getInfoLabel('ListItem.Genre'))
        iarl_data['current_rom_data']['rom_date'] = ystr(xbmc.getInfoLabel('ListItem.Date'))
        iarl_data['current_rom_data']['rom_year'] = ystr(xbmc.getInfoLabel('ListItem.Year'))
        iarl_data['current_rom_data']['rom_plot'] = ystr(xbmc.getInfoLabel('ListItem.Plot'))
        iarl_data['current_rom_data']['rom_trailer'] = ystr(xbmc.getInfoLabel('ListItem.Trailer'))
        iarl_data['current_rom_data']['rom_tag'] = ystr(xbmc.getInfoLabel('ListItem.Property(tag)'))
        iarl_data['current_rom_data']['rom_nplayers'] = ystr(xbmc.getInfoLabel('ListItem.Property(nplayers)'))
        iarl_data['current_rom_data']['rom_rating'] = ystr(xbmc.getInfoLabel('ListItem.Property(rating)'))
        iarl_data['current_rom_data']['rom_esrb'] = ystr(xbmc.getInfoLabel('ListItem.Property(esrb)'))
        iarl_data['current_rom_data']['rom_perspective'] = ystr(xbmc.getInfoLabel('ListItem.Property(perspective)'))
        iarl_data['current_rom_data']['rom_emu_command'] = ystr(xbmc.getInfoLabel('ListItem.Property(rom_emu_command)'))
        iarl_data['current_rom_data']['rom_label'] = ystr(xbmc.getInfoLabel('ListItem.Label'))
        iarl_data['current_rom_data']['rom_filenames'] = [ystr(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_filenames)').split(',')] #Split into list
        iarl_data['current_rom_data']['rom_supporting_filenames'] = [ystr(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_supporting_filenames)').split(',')] #Split into list
        iarl_data['current_rom_data']['rom_save_filenames'] = [ystr(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_save_filenames)').split(',')] #Split into list
        iarl_data['current_rom_data']['rom_save_supporting_filenames'] = [ystr(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_save_supporting_filenames)').split(',')] #Split into list
        iarl_data['current_rom_data']['rom_size'] = [int(x) for x in xbmc.getInfoLabel('ListItem.Property(rom_file_sizes)').split(',')] #Split into list, convert to int
        for ii in range(0,total_arts):
            iarl_data['current_rom_data']['rom_fanarts'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(fanart'+str(ii+1)+')'))
            iarl_data['current_rom_data']['rom_boxarts'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(boxart'+str(ii+1)+')'))
            iarl_data['current_rom_data']['rom_banners'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(banner'+str(ii+1)+')'))
            iarl_data['current_rom_data']['rom_snapshots'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(snapshot'+str(ii+1)+')'))
            iarl_data['current_rom_data']['rom_logos'][ii] = ystr(xbmc.getInfoLabel('ListItem.Property(logo'+str(ii+1)+')'))

    check_for_warn(iarl_data['current_rom_data']['rom_size']) #Added warning for file sizes over 100MB

    #Show ROM Info window selected in settings
    if 'ROM Info Page'.lower() in iarl_data['settings']['game_select_action'].lower():
        if 'IARL Classic Window'.lower() in iarl_data['settings']['window_theme'].lower():
            MyROMWindow = ROMWindow('default.xml',iarl_data['addon_data']['addon_install_path'],'Default','720p',iarl_data=iarl_data)
            MyROMWindow.doModal()
        # elif: #Not yet implemented
        #     print xbmc.getSkinDir()
        #     print get_skin_install_path(xbmc.getSkinDir())
        #     MyROMWindow = ROMWindow('Confluence.xml',iarl_data['addon_data']['addon_install_path'],'Default','720p',iarl_data=iarl_data)
        #     MyROMWindow.doModal()
        else: #Default to classic
            MyROMWindow = ROMWindow('default.xml',iarl_data['addon_data']['addon_install_path'],'Default','720p',iarl_data=iarl_data)
            MyROMWindow.doModal()

    #Download and launch selected in settings
    elif 'Download and Launch'.lower() in iarl_data['settings']['game_select_action'].lower():
        download_and_launch_rom(None,iarl_data)
    #Download only selected in settings
    elif 'Download Only'.lower() in iarl_data['settings']['game_select_action'].lower():
        iarl_data['current_save_data'] = download_rom_only(iarl_data)
        if iarl_data['current_save_data']['overall_download_success']:
            current_dialog = xbmcgui.Dialog()
            ok_ret = current_dialog.ok('Complete',iarl_data['current_rom_data']['rom_name']+' was successfully downloaded')          
    else:
        xbmc.log(msg='IARL:  Selected game action is unknown', level=xbmc.LOGERROR)
        pass #Shouldn't ever see this

    pass

@plugin.route('/Search_Results/<search_term>') #Not sure why normal routing with extra kwargs isn't working for this route...
def search_roms_results(search_term,**kwargs):
    search_results = []

    current_search_term = search_term.lower().strip()
    # args_in = plugin.request.args #This doesn't work in this intance when using urlfor?

    try:
        current_includes = kwargs['include_archives'].split(',')
    except:
        current_includes = 'all'
    try:
        current_adv_search = kwargs['adv_search']
    except:
        current_adv_search = 'False'
    try:
        current_region = kwargs['region'].lower().strip()
    except:
        current_region = 'any'
    try:
        current_genre = kwargs['genre'].lower().strip()
    except:
        current_genre = 'any'
    try:
        current_studio = kwargs['studio'].lower().strip()
    except:
        current_studio = 'any'
    try:
        current_nplayers = kwargs['nplayers'].lower().strip()
    except:
        current_nplayers = 'any'
    try:
        current_datefrom = kwargs['datefrom'].lower().strip()
    except:
        current_datefrom = 'any'
    try:
        current_dateto = kwargs['dateto'].lower().strip()
    except:
        current_dateto = 'any'

    if current_datefrom == 'any':
        datefrom_num = 1950 #Random year well before any game was invented
    else:
        try:
            datefrom_num = int(current_datefrom.lower().strip().split('/')[-1]) #No checking... yet
        except:
            xbmc.log(msg='IARL:  Search start date is badly formatted, default year used', level=xbmc.LOGERROR)
            datefrom_num = 1950 #Bad formatted date

    if current_dateto == 'any':
        dateto_num = 2999 #Random year that this code will obviously be dead and gone when reached
    else:
        try:
            dateto_num = int(current_dateto.lower().strip().split('/')[-1])+1
        except:
            xbmc.log(msg='IARL:  Search end date is badly formatted, default year used', level=xbmc.LOGERROR)
            dateto_num = 2999 #Bad formatted date

    date_list = range(datefrom_num,dateto_num) #List of years to look for

    if iarl_data['archive_data'] is None:
        iarl_data['archive_data'] = get_archive_info()

    progress_dialog = xbmcgui.DialogProgress()
    progress_dialog.create('IARL', 'Searching...')

    #This probably isnt a very efficient method for filtering.  Need to look into lambda dict filtering
    if current_adv_search == 'False':
        for ii in range(0,len(current_includes)):
            progress_dialog.update(max(1,int(100*ii/len(current_includes))-10), 'Looking in '+iarl_data['archive_data']['emu_name'][ii])
            if current_includes[ii] == '1':
                iarl_data['current_archive_data'] = define_current_archive_data(iarl_data,ii,None)
                if current_search_term == 'any':
                    for roms_in_list in get_rom_list(iarl_data,ii):
                        if (progress_dialog.iscanceled()):
                            xbmc.log(msg='IARL:  Search was cancelled by the user', level=xbmc.LOGDEBUG)
                            return
                        search_results.append(roms_in_list)
                else:
                    for roms_in_list in get_rom_list(iarl_data,ii):
                        if (progress_dialog.iscanceled()):
                            xbmc.log(msg='IARL:  Search was cancelled by the user', level=xbmc.LOGDEBUG)
                            return
                        if current_search_term in roms_in_list['label'].lower().strip(): #search term is in label
                            search_results.append(roms_in_list)
    else:
        for ii in range(0,len(current_includes)):
            progress_dialog.update(max(1,int(100*ii/len(current_includes))-10), 'Looking in '+iarl_data['archive_data']['emu_name'][ii])
            if current_includes[ii] == '1':
                iarl_data['current_archive_data'] = define_current_archive_data(iarl_data,ii,None)
                for roms_in_list in get_rom_list(iarl_data,ii):
                    if (progress_dialog.iscanceled()):
                        xbmc.log(msg='IARL:  Search was cancelled by the user', level=xbmc.LOGDEBUG)
                        return
                    include_this_rom = True #Default to include rom
                    try:
                        if (current_search_term not in roms_in_list['label'].lower().strip()) & (current_search_term != 'any'):
                            include_this_rom = False #Filter out rom if the search term is not in the label and the search term isn't "any"
                    except:
                        pass
                        # include_this_rom = False
                    try:
                        if (current_genre not in roms_in_list['info']['genre'].lower().strip()) & (current_genre != 'any'):
                            include_this_rom = False
                    except:
                        pass
                        # include_this_rom = False
                    try:
                        if (current_studio not in roms_in_list['info']['studio'].lower().strip()) & (current_studio != 'any'):
                            include_this_rom = False
                    except:
                        pass
                        # include_this_rom = False
                    try:
                        if (current_nplayers not in roms_in_list['properties']['nplayers'].lower().strip()) & (current_nplayers != 'any'):
                            include_this_rom = False
                    except:
                        pass
                        # include_this_rom = False
                    try:
                        if (current_region not in roms_in_list['properties']['rom_tag'].lower().strip()) & (current_region != 'any'):
                            include_this_rom = False
                    except:
                        pass
                        # include_this_rom = False
                    try:
                        if (int(roms_in_list['info']['date'][-4:]) not in date_list):
                            include_this_rom = False
                    except:
                        pass
                        # include_this_rom = False

                    if include_this_rom: #Append to the list if include tag is still true
                        search_results.append(roms_in_list)

    progress_dialog.update(95, 'Compiling Results...')
    xbmc.log(msg='IARL:  Search found '+str(len(search_results))+' matches', level=xbmc.LOGDEBUG)
    return plugin.finish(search_results,cache_to_disc=True,sort_methods=[xbmcplugin.SORT_METHOD_NONE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_GENRE, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE])
    progress_dialog.close()

@plugin.route('/Search')
def search_roms_window():
    MySearchWindow = SearchWindow('search.xml',iarl_data['addon_data']['addon_install_path'],'Default','720p')
    MySearchWindow.doModal()
    pass

@plugin.route('/Random')
def random_play():
    import random

    if iarl_data['archive_data'] is None:
        iarl_data['archive_data'] = get_archive_info()

    iarl_data_2 = { #Create temp dict to populate non-hidden archives into
        'emu_filepath' : list(),
        }

    for ii in range(0,len(iarl_data['archive_data']['emu_name'])):
        if 'hidden' not in iarl_data['archive_data']['emu_category'][ii]: #Don't include the archive if it's tagged hidden
            iarl_data_2['emu_filepath'].append(iarl_data['archive_data']['emu_filepath'][ii])

    rand_int_1 = random.randint(0,len(iarl_data_2['emu_filepath']))
    # rand_int_1 = 0 #For testing
    try:
        current_index = iarl_data['archive_data']['emu_filepath'].index(iarl_data_2['emu_filepath'][rand_int_1])
    except:
        try:
            rand_int_1 = random.randint(0,len(iarl_data_2['emu_filepath']))
            current_index = iarl_data['archive_data']['emu_filepath'].index(iarl_data_2['emu_filepath'][rand_int_1])
        except:
            xbmc.log(msg='IARL:  Unable to generate a random archive for some unknown reason, try again', level=xbmc.LOGERROR)
            current_index = None

    if current_index is not None:
        iarl_data['current_archive_data'] = define_current_archive_data(iarl_data,current_index,None)
        try:
            rom_list = get_rom_list(iarl_data,current_index)
        except:
            rom_list = None

        try:
            rand_int_2 = random.randint(0,len(rom_list))
            page = paginate.Page(rom_list, page=rand_int_2, items_per_page=1)
        except:
            page = None
        try:
            xbmc.log(msg='IARL:  Random play archive: '+str(page.items[0]['properties']['emu_name'])+', game: '+str(page.items[0]['properties']['rom_title']), level=xbmc.LOGDEBUG)
        except:
            pass
        return plugin.finish(page.items,update_listing=False)
    else:
        return plugin.finish([],update_listing=False)
    # pass

def download_rom_only(iarl_data):
    xbmc.log(msg='IARL:  Download started for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGNOTICE)

    #Initialize current save data dict since it may have been populated with the last selected game
    iarl_data['current_save_data']['rom_save_filenames'] = list()
    iarl_data['current_save_data']['rom_save_filenames_exist'] = list()
    iarl_data['current_save_data']['rom_save_filenames_success'] = list()
    iarl_data['current_save_data']['rom_supporting_filenames'] = list()
    iarl_data['current_save_data']['rom_save_supporting_filenames'] = list()
    iarl_data['current_save_data']['rom_save_supporting_filenames_exist'] = list()
    iarl_data['current_save_data']['rom_save_supporting_filenames_success'] = list()
    iarl_data['current_save_data']['rom_converted_filenames'] = list()
    iarl_data['current_save_data']['rom_converted_filenames_success'] = list()
    iarl_data['current_save_data']['rom_converted_supporting_filenames'] = list()
    iarl_data['current_save_data']['rom_converted_supporting_filenames_success'] = list()
    iarl_data['current_save_data']['overwrite_existing_files'] = False #Default to not overwrite existing files, then check
    iarl_data['current_save_data']['overall_download_success'] = True #Default to a good download, then check afterward
    iarl_data['current_save_data']['overall_conversion_success'] = True #Default to a good conversion, then check afterward
    iarl_data['current_save_data']['launch_filename'] = None #Default to no launch filename (will be populated by post_download_action)

    #1.  Check temp folder and clean if necessary
    if 'default' in iarl_data['current_archive_data']['emu_download_path']:
        check_temp_folder_and_clean(iarl_data['settings']['download_cache'])

    #2.  Check if filename(s) already exist
    for filenames in iarl_data['current_rom_data']['rom_save_filenames']:
        if filenames:
            iarl_data['current_save_data']['rom_save_filenames'].append(filenames)
            if os.path.exists(filenames):
                iarl_data['current_save_data']['rom_save_filenames_exist'].append(True)
                iarl_data['current_save_data']['rom_save_filenames_success'].append(True)
            else:
                iarl_data['current_save_data']['rom_save_filenames_exist'].append(False)
                iarl_data['current_save_data']['rom_save_filenames_success'].append(False)
    for filenames in iarl_data['current_rom_data']['rom_save_supporting_filenames']:
        if filenames:
            iarl_data['current_save_data']['rom_save_supporting_filenames'].append(filenames)
            if os.path.exists(filenames):
                iarl_data['current_save_data']['rom_save_supporting_filenames_exist'].append(True)
                iarl_data['current_save_data']['rom_save_supporting_filenames_success'].append(True)
            else:
                iarl_data['current_save_data']['rom_save_supporting_filenames_exist'].append(False)
                iarl_data['current_save_data']['rom_save_supporting_filenames_success'].append(False)

    #3.  Determine action if file already exists
    if (True in iarl_data['current_save_data']['rom_save_filenames_exist']) or (True in iarl_data['current_save_data']['rom_save_supporting_filenames_exist']):
        if 'Prompt'.lower() in iarl_data['settings']['local_file_action'].lower():
            current_dialog = xbmcgui.Dialog()
            ret1 = current_dialog.select('Download and overwrite local files?', ['No','Yes'])
            if ret1 == 0:
                iarl_data['current_save_data']['overwrite_existing_files'] = False
                xbmc.log(msg='IARL:  File was found to exist locally, no overwrite option selected', level=xbmc.LOGDEBUG)
            else:
                iarl_data['current_save_data']['overwrite_existing_files'] = True
                xbmc.log(msg='IARL:  File was found to exist locally, overwrite option selected', level=xbmc.LOGDEBUG)
        elif 'Do Not ReDownload'.lower() in iarl_data['settings']['local_file_action'].lower():
            iarl_data['current_save_data']['overwrite_existing_files'] = False
            xbmc.log(msg='IARL:  File was found to exist locally, no overwrite option selected', level=xbmc.LOGDEBUG)
        else:
            iarl_data['current_save_data']['overwrite_existing_files'] = True
            xbmc.log(msg='IARL:  File was found to exist locally, overwrite option selected', level=xbmc.LOGDEBUG)
    
    #4.  Download the files, check the file downloaded
    for ii in range (0,len(iarl_data['current_rom_data']['rom_save_filenames'])):
        download_filename = False
        if iarl_data['current_rom_data']['rom_save_filenames'][ii]:
            if iarl_data['current_save_data']['rom_save_filenames_exist'][ii]:
                if iarl_data['current_save_data']['overwrite_existing_files']:
                    download_filename = True #Download the file if the file exists and overwrite was selected
            else:
                download_filename = True #Download the file if the file does not exist
        if download_filename:
            iarl_data['current_save_data']['rom_save_filenames_success'][ii] = download_tools().Downloader(quote_url(iarl_data['current_rom_data']['rom_filenames'][ii]),iarl_data['current_rom_data']['rom_save_filenames'][ii],iarl_data['settings']['ia_enable_login'],iarl_data['settings']['ia_username'],iarl_data['settings']['ia_password'],iarl_data['current_rom_data']['rom_size'][ii],iarl_data['current_rom_data']['rom_title'],'Downloading, please wait...')
            if iarl_data['current_save_data']['rom_save_filenames_success'][ii]:
                if not check_downloaded_file(iarl_data['current_rom_data']['rom_save_filenames'][ii]): #Check the file, if its 0 bytes, then archive.org couldnt find the file
                    iarl_data['current_save_data']['rom_save_filenames_exist'][ii] = True
                else: #File was 0 bytes, delete it and call it a fail
                    iarl_data['current_save_data']['rom_save_filenames_success'][ii] = False
                    iarl_data['current_save_data']['rom_save_filenames_exist'][ii] = False
    for ii in range (0,len(iarl_data['current_rom_data']['rom_save_supporting_filenames'])):
        download_filename = False
        if iarl_data['current_rom_data']['rom_save_supporting_filenames'][ii]:
            if iarl_data['current_save_data']['rom_save_supporting_filenames_exist'][ii]:
                if iarl_data['current_save_data']['overwrite_existing_files']:
                    download_filename = True #Download the file if the file exists and overwrite was selected
            else:
                download_filename = True #Download the file if the file does not exist
        if download_filename:
            iarl_data['current_save_data']['rom_save_supporting_filenames_success'][ii] = download_tools().Downloader(quote_url(iarl_data['current_rom_data']['rom_supporting_filenames'][ii]),iarl_data['current_rom_data']['rom_save_supporting_filenames'][ii],iarl_data['settings']['ia_enable_login'],iarl_data['settings']['ia_username'],iarl_data['settings']['ia_password'],9999999,iarl_data['current_rom_data']['rom_supporting_filenames'][ii],'Downloading, please wait...')
            if iarl_data['current_save_data']['rom_save_supporting_filenames_success'][ii]:
                if not check_downloaded_file(iarl_data['current_rom_data']['rom_save_supporting_filenames'][ii]):
                    iarl_data['current_save_data']['rom_save_supporting_filenames_exist'][ii] = True
                else:
                    iarl_data['current_save_data']['rom_save_supporting_filenames_success'][ii] = False
                    iarl_data['current_save_data']['rom_save_supporting_filenames_exist'][ii] = False
    
    #5.  Check to ensure each file was a success
    for check in iarl_data['current_save_data']['rom_save_filenames_success']:
        if not check:
            iarl_data['current_save_data']['overall_download_success'] = False
    for check in iarl_data['current_save_data']['rom_save_supporting_filenames_success']:
        if not check:
            iarl_data['current_save_data']['overall_download_success'] = False

    #5.  Post-download process the files if necessary
    if iarl_data['current_save_data']['overall_download_success']:
        iarl_data['current_save_data']['launch_filename'], post_download_action_success = post_download_action(iarl_data,iarl_data['current_archive_data']['emu_post_download_action'],None)
    else:
        xbmc.log(msg='IARL:  There was a download error for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)
    return iarl_data['current_save_data']

def post_download_action(iarl_data,option,option2):
    post_download_action_success = False

    if option == 'none':
        iarl_data['current_save_data']['overall_conversion_success'] = True
        iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_save_filenames'][0] #Define the launch filename as the first one
    elif option == 'unzip_rom':
        if iarl_data['current_save_data']['rom_save_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_filenames']:
                conversion_success, converted_filename = unzip_file(filenames)
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        if iarl_data['current_save_data']['rom_save_supporting_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_supporting_filenames']:
                conversion_success, converted_filename = unzip_file(filenames)
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error unzipping files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)
    elif option == 'unzip_update_rom_path_dosbox':
        if iarl_data['current_save_data']['rom_save_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_filenames']:
                if option2 is None:
                    option2 = iarl_data['current_rom_data']['rom_emu_command']
                conversion_success, converted_filename = unzip_dosbox_file(filenames,option2)
                # conversion_success, converted_filename = unzip_dosbox_file(filenames,iarl_data['current_rom_data']['rom_emu_command'])
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        if iarl_data['current_save_data']['rom_save_supporting_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_supporting_filenames']:
                if option2 is None:
                    option2 = iarl_data['current_rom_data']['rom_emu_command']
                conversion_success, converted_filename = unzip_dosbox_file(filenames,option2)
                # conversion_success, converted_filename = unzip_dosbox_file(filenames,iarl_data['current_rom_data']['rom_emu_command'])
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting DOSBox files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)
    elif 'unzip_dosbox_update_conf_file' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = unzip_dosbox_update_conf_file(iarl_data)
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting the DOSBox archive for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)  
    elif 'unzip_scummvm_update_conf_file' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = unzip_scummvm_update_conf_file(iarl_data)
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting the ScummVM archive for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)  
    elif option == 'convert_chd_bin':
        if iarl_data['current_save_data']['rom_save_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_filenames']:
                conversion_success, converted_filename = convert_chd_bin(filenames,iarl_data['addon_data']['chdman_path'],'bin')
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        if iarl_data['current_save_data']['rom_save_supporting_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_supporting_filenames']:
                conversion_success, converted_filename = convert_chd_bin(filenames,iarl_data['addon_data']['chdman_path'],'bin')
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting CHD to BIN/CUE for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)    
    elif option == 'convert_chd_cue':
        if iarl_data['current_save_data']['rom_save_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_filenames']:
                conversion_success, converted_filename = convert_chd_bin(filenames,iarl_data['addon_data']['chdman_path'],'cue')
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        if iarl_data['current_save_data']['rom_save_supporting_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_supporting_filenames']:
                conversion_success, converted_filename = convert_chd_bin(filenames,iarl_data['addon_data']['chdman_path'],'cue')
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting CHD to CUE/BIN for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)  
    elif option == 'lynx_header_fix':
        if iarl_data['current_save_data']['rom_save_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_filenames']:
                conversion_success, converted_filename = lynx_header_fix(filenames)
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        if iarl_data['current_save_data']['rom_save_supporting_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_supporting_filenames']:
                conversion_success, converted_filename = lynx_header_fix(filenames)
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error attempting to fix Lynx ROM Header for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)
    elif 'rename_rom_postdl' in option:
        try:
            new_extension = re.search(r'\([^)]*\)',option).group(0).replace('(','').replace(')','').strip()
        except:
            new_extension = ''
            xbmc.log(msg='IARL:  Rename ROM option extension could not be defined', level=xbmc.LOGERROR)
        if iarl_data['current_save_data']['rom_save_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_filenames']:
                conversion_success, converted_filename = rename_rom_postdl(filenames,new_extension)
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        if iarl_data['current_save_data']['rom_save_supporting_filenames']:
            for filenames in iarl_data['current_save_data']['rom_save_supporting_filenames']:
                conversion_success, converted_filename = rename_rom_postdl(filenames,new_extension)
                iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
                iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error attempting to rename the file extension for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)        
    elif 'generate_uae_conf_file' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = generate_uae_conf_file(iarl_data)
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error creating the FS-UAE conf files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)  
    elif 'generate_uae4arm_conf_file' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = generate_uae4arm_conf_file(iarl_data)
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error creating the UAE4ARM conf files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)  
    elif 'generate_uae_cd32_conf_file' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = generate_uae_cd32_conf_file(iarl_data)
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error creating the FS-UAE CD32 conf files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR) 
    elif 'convert_7z_m3u' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = convert_7z_m3u(iarl_data)
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting the 7z files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR)  
    elif 'convert_7z_track1_bin' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = convert_7z_bin_cue_gdi(iarl_data,'track 1')
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting the 7z track 1 files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR) 
    elif 'convert_7z_gdi' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = convert_7z_bin_cue_gdi(iarl_data,'gdi')
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting the 7z track 1 files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR) 
    elif 'convert_7z_cue' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = convert_7z_bin_cue_gdi(iarl_data,'cue')
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting the 7z track 1 files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR) 
    elif 'convert_7z_iso' in option:
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = convert_7z_bin_cue_gdi(iarl_data,'iso')
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error converting the 7z iso files for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR) 
    elif 'convert_mame_softlist' in option:
        try:
            softlist_type = re.search(r'\([^)]*\)',option).group(0).replace('(','').replace(')','').replace("'",'').strip()
        except:
            softlist_type = ''
            xbmc.log(msg='IARL:  MAME softlist type could not be defined', level=xbmc.LOGERROR)
        if iarl_data['current_save_data']['rom_save_filenames']:
            conversion_success, converted_filename = setup_mame_softlist_game(iarl_data,softlist_type)
            iarl_data['current_save_data']['rom_converted_filenames'].append(converted_filename)
            iarl_data['current_save_data']['rom_converted_filenames_success'].append(conversion_success)
        for check in iarl_data['current_save_data']['rom_converted_filenames_success']:
            if not check:
                iarl_data['current_save_data']['overall_conversion_success'] = False
        if iarl_data['current_save_data']['overall_conversion_success']:
            iarl_data['current_save_data']['launch_filename'] = iarl_data['current_save_data']['rom_converted_filenames'][0] #Define the launch filename as the first one
        else:
            xbmc.log(msg='IARL:  There was an error setting up the MAME softlist game '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGERROR) 
    elif 'favorites_post_action' in option:
        if '|' in option:
            option_1 = rom_emu_command.split('|')[0]
            option_2 = rom_emu_command.split('|')[-1]
        else:
            option_1 = option
            option_2 = None
        #Call post_download_action again with new arguments
        new_launch_filename, overall_conversion_success_2 = post_download_action(iarl_data,option_1,option_2)
        if overall_conversion_success_2:
            iarl_data['current_save_data']['launch_filename'] = new_launch_filename
            iarl_data['current_save_data']['overall_conversion_success'] = True
    else:
        iarl_data['current_save_data']['launch_filename'] = None
        post_download_action_success = False
        xbmc.log(msg='IARL:  The post download action '+str(option)+' is unknown', level=xbmc.LOGERROR)

    return iarl_data['current_save_data']['launch_filename'], iarl_data['current_save_data']['overall_conversion_success']

def download_and_launch_rom(romwindow,iarl_data):
    xbmc.log(msg='IARL:  Download and Launch started for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGNOTICE)

    #Use External Launcher
    if iarl_data['current_archive_data']['emu_launcher'] == 'external':
        if 'Select'.lower() in iarl_data['settings']['external_launch_env'].lower():
            current_dialog = xbmcgui.Dialog()
            ok_ret = current_dialog.ok('Error','External launching is not setup in addon settings')
            xbmc.log(msg='IARL:  External launching is not setup in dddon settings yet!', level=xbmc.LOGERROR)
        else:
            if iarl_data['current_archive_data']['emu_ext_launch_cmd'] != 'none':
                #Download the required files, and process them if needed
                iarl_data['current_save_data'] = download_rom_only(iarl_data)
                if iarl_data['current_save_data']['overall_download_success']:
                    current_external_command = replace_external_launch_variables(iarl_data) #Function replaces command line variables

                    if '%' not in current_external_command:
                        #Close the Info Window if it's open
                        if romwindow is not None:
                            romwindow.closeDialog()
                        if 'Android' in iarl_data['addon_data']['operating_system']:
                            #Suspend audio for HDMI audio purposes on some systems
                            xbmc.log(msg='IARL:  Android external command: '+str(current_external_command), level=xbmc.LOGNOTICE)
                            xbmc.audioSuspend()
                            xbmc.enableNavSounds(False) 
                            xbmc.sleep(500) #This pause seems to help... I'm not really sure why
                            # execute_subprocess_command(current_external_command.encode('utf-8'))
                            os.system(current_external_command.encode('utf-8')) #Android is frustrating...
                            #Resume audio after external command is complete
                            xbmc.audioResume()
                            xbmc.enableNavSounds(True)
                        else:
                            xbmc.log(msg='IARL:  External launch command sent: '+str(current_external_command), level=xbmc.LOGNOTICE)
                            #Suspend audio for HDMI audio purposes on some systems
                            xbmc.audioSuspend()
                            xbmc.enableNavSounds(False) 
                            xbmc.sleep(500) #This pause seems to help... I'm not really sure why
                            # execute_subprocess_command(current_external_command)
                            external_command = subprocess.call(current_external_command,shell=True)
                            #Resume audio after external command is complete
                            xbmc.audioResume()
                            xbmc.enableNavSounds(True)
                    else:
                        xbmc.log(msg='IARL:  There is an undefined value in the external launch command: '+str(current_external_command.split('%')[1]), level=xbmc.LOGERROR)
                #Error downloading, so the game will not be launched
                else:
                    xbmc.log(msg='IARL:  There was an error downloading the requested files, so the game will not be launched.', level=xbmc.LOGERROR)
            else:
                current_dialog = xbmcgui.Dialog()
                ok_ret = current_dialog.ok('Error','External launch command not defined.')
                xbmc.log(msg='IARL:  External Launch Command is not defined for: '+str(iarl_data['current_archive_data']['emu_name']), level=xbmc.LOGERROR)
    #Use Retroplayer
    else:
        iarl_data['current_save_data'] = download_rom_only(iarl_data)
        if iarl_data['current_save_data']['overall_download_success']:
            launch_game_listitem = xbmcgui.ListItem(iarl_data['current_save_data']['launch_filename'], "0", "", "")
            parameters = {'title': iarl_data['current_rom_data']['rom_title'], 'url': iarl_data['current_save_data']['launch_filename']}
            launch_game_listitem.setInfo(type='game', infoLabels=parameters)
            if iarl_data['current_rom_data']['rom_boxarts'][0] is not None:
                launch_game_listitem.setArt({'thumb': iarl_data['current_rom_data']['rom_boxarts'][0]})
                launch_game_listitem.setThumbnailImage(iarl_data['current_rom_data']['rom_boxarts'][0])
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)
            #Close the Info Window if it's open
            if romwindow is not None:
                romwindow.closeDialog()
            xbmc.sleep(500) #This pause seems to help... I'm not really sure why
            xbmc.log(msg='IARL:  Retroplayer launch for: '+str(iarl_data['current_save_data']['launch_filename']), level=xbmc.LOGNOTICE)
            xbmc.Player().play(iarl_data['current_save_data']['launch_filename'],launch_game_listitem)
        else:
            xbmc.log(msg='IARL:  There was an error downloading the requested files, so the game will not be launched.', level=xbmc.LOGERROR)
 
class ROMWindow(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback, *args, **kwargs):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.iarl_data = kwargs
        xbmc.log(msg='IARL:  ROMWindow Opened for '+str(iarl_data['current_rom_data']['rom_name']), level=xbmc.LOGDEBUG)
        pass

    def onInit(self):
        self.please_wait = self.getControl(3012) #Number of players
        self.please_wait.setVisible(False)
        #Define theme for ROM Window
        xbmcgui.Window(10000).setProperty('iarl.current_theme',str(iarl_data['current_archive_data']['emu_name']))
        xbmcgui.Window(10000).setProperty('iarl.default_thumb',str(iarl_data['current_archive_data']['emu_boxart']))
        xbmcgui.Window(10000).setProperty('iarl.header_color',str(iarl_data['current_archive_data']['header_color']))
        xbmcgui.Window(10000).setProperty('iarl.bg_color',str(iarl_data['current_archive_data']['background_color']))
        xbmcgui.Window(10000).setProperty('iarl.buttonfocustheme',str(iarl_data['current_archive_data']['button_focus']))
        xbmcgui.Window(10000).setProperty('iarl.buttonnofocustheme',str(iarl_data['current_archive_data']['button_nofocus']))

        self.action_exitkeys_id = [10, 13]
        self.logo_art = self.getControl(103) #Logo
        self.plot_box = self.getControl(104) #Plot
        self.left_art2 = self.getControl(111) #Left Art List
        self.right_art2 = self.getControl(112) #Right Art List
        self.play_button = self.getControl(3005) #Play Trailer
        self.stop_button = self.getControl(3006) #Top Trailer
        self.right_art2.setVisible(True) #Default Fanart visible for trailer control

        self.title_box = self.getControl(3007) #Title - Game Name
        self.genre_box = self.getControl(3008) #Genre
        self.players_box = self.getControl(3009) #Number of players
        self.studio_box = self.getControl(3010) #Number of players
        

        # get control ids
        self.control_id_button_action1 = 3001 #Download Only
        self.control_id_button_action2 = 3002 #Download and Launch
        self.control_id_button_action3 = 3005 #Play Trailer
        self.control_id_button_action4 = 3006 #Stop Trailer
        self.control_id_button_exit = 3003
        self.control_id_label_action = 3011

        if iarl_data['current_rom_data']['rom_trailer'] is not None: #If the trailer exists make the play button available
            self.play_button.setVisible(True)
            self.stop_button.setVisible(False)
        else:
            self.play_button.setVisible(False)
            self.stop_button.setVisible(False)

        # translation ids - I don't currently translate
        self.translation_id_action1 = 3101
        self.translation_id_action2 = 3102
        self.translation_id_exit = 3103
        self.translation_id_demotext = 3120
        
        # set actions
        self.button_action1 = self.getControl(self.control_id_button_action1)
        self.button_action2 = self.getControl(self.control_id_button_action2)
        self.button_action3 = self.getControl(self.control_id_button_action3)
        self.button_action4 = self.getControl(self.control_id_button_action4)
        self.button_exit = self.getControl(self.control_id_button_exit)
        
        # translate buttons
        self.button_action1.setLabel('Download')
        self.button_action2.setLabel('Launch')
        self.button_exit.setLabel('Close')

        self.plot_box.setText(iarl_data['current_rom_data']['rom_plot']) #Enter the plot if its available
        self.logo_art.setImage(iarl_data['current_archive_data']['emu_logo']) #Place the emu logo

        self.title_box.setText(iarl_data['current_rom_data']['rom_title'])
        if iarl_data['current_rom_data']['rom_genre'] is not None:
            genre_box_text = str(iarl_data['current_rom_data']['rom_genre'])
        else:
            genre_box_text = ''
        if iarl_data['current_rom_data']['rom_perspective'] is not None:
            if len(genre_box_text)>0:
                genre_box_text = genre_box_text+'[CR]'+str(iarl_data['current_rom_data']['rom_perspective'])
            else:
                genre_box_text = str(iarl_data['current_rom_data']['rom_perspective'])
        self.genre_box.setText(genre_box_text)
        if iarl_data['current_rom_data']['rom_nplayers'] is not None:
            player_box_text = 'Players[CR]'+str(iarl_data['current_rom_data']['rom_nplayers'])
        else:
            player_box_text = ''
        self.players_box.setText(player_box_text)
        if iarl_data['current_rom_data']['rom_date'] is not None:
            studio_box_text = 'Released: '+str(iarl_data['current_rom_data']['rom_date'])
        else:
            studio_box_text = ''
        if iarl_data['current_rom_data']['rom_studio'] is not None:
            if len(studio_box_text)>0:
                studio_box_text = studio_box_text+'[CR]'+str(iarl_data['current_rom_data']['rom_studio'])
            else:
                studio_box_text = str(iarl_data['current_rom_data']['rom_studio'])
        self.studio_box.setText(studio_box_text)
 
        #Populate the image spots
        left_art_found = False
        right_art_found = False
        for rom_boxarts in filter(bool,iarl_data['current_rom_data']['rom_boxarts']):
            left_art_found = True
            self.left_art2.addItem(xbmcgui.ListItem(label2=str(iarl_data['current_rom_data']['rom_name']), thumbnailImage=rom_boxarts)) #Add boxart to the left image slideshow

        for rom_fanarts in filter(bool,iarl_data['current_rom_data']['rom_fanarts']):
            right_art_found = True
            self.right_art2.addItem(xbmcgui.ListItem(label2=str(iarl_data['current_rom_data']['rom_name']), thumbnailImage=rom_fanarts)) #Add fanart to the right image slideshow

        for rom_snapshots in filter(bool,iarl_data['current_rom_data']['rom_snapshots']):
            right_art_found = True
            self.right_art2.addItem(xbmcgui.ListItem(label2=str(iarl_data['current_rom_data']['rom_name']), thumbnailImage=rom_snapshots)) #Add snapshots to the right image slideshow

        if not right_art_found:
            self.right_art2.addItem(xbmcgui.ListItem(label2=str(iarl_data['current_rom_data']['rom_name']), thumbnailImage=iarl_data['current_archive_data']['emu_fanart'])) #If no fanart is found, make it the current emulator fanart

        if not left_art_found:
            self.left_art2.addItem(xbmcgui.ListItem(label2=str(iarl_data['current_rom_data']['rom_name']), thumbnailImage=iarl_data['current_rom_data']['rom_icon'])) #If no boxart is found, make it the default box


    def onAction(self, action):
        # Same as normal python Windows.
        if action in self.action_exitkeys_id:
            self.closeDialog()

    def onFocus(self, controlId):
        pass

    def onClick(self, controlId):
        #Download Only
        if controlId == self.control_id_button_action1:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)

            iarl_data['current_save_data'] = download_rom_only(iarl_data)

            if iarl_data['current_save_data']['overall_download_success']:
                current_dialog = xbmcgui.Dialog()
                ok_ret = current_dialog.ok('Complete',iarl_data['current_rom_data']['rom_name']+' was successfully downloaded')

        #Download and Launch
        if controlId == self.control_id_button_action2:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)
            # self.please_wait.setVisible(True)
            download_and_launch_rom(self,iarl_data)
            # self.please_wait.setVisible(False)

        #Play the Trailer
        if controlId == self.control_id_button_action3: #Play the trailer if it exists
            if iarl_data['current_rom_data']['rom_trailer']:
                self.right_art2.setVisible(False) #Get Fanart out of the way
                xbmc.sleep(100)
                xbmc.Player().play(iarl_data['current_rom_data']['rom_trailer'], windowed=True)
                self.play_button.setVisible(False)
                self.stop_button.setVisible(True)
                self.setFocus(self.stop_button)
        #Stop the Trailer
        if controlId == self.control_id_button_action4:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)
                self.right_art2.setVisible(True) #Turn the fanart back on
                self.play_button.setVisible(True)
                self.stop_button.setVisible(False)
                self.setFocus(self.play_button)
        #Exit the window
        elif controlId == self.control_id_button_exit:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)
            self.closeDialog()

    def doAction(self, controlId):
        # print controlId
        pass

    def closeDialog(self):
        self.close()


class SearchWindow(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback, *args, **kwargs):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.iarl_data = kwargs
        self.available_as_options = ['Genre','Release Date','Region','Num Players','Studio'] #Not currently used

    def onInit(self):
        # Put your List Populating code/ and GUI startup stuff here
        # get control ids
        self.action_exitkeys_id = [10, 13]
        self.archive_list = self.getControl(101) #Archive List
        self.search_box = self.getControl(102) #Search Box
        self.genre_id = self.getControl(104) #Genre
        self.nplayers_id = self.getControl(106) #Players
        self.date_from_id = self.getControl(108) #Date From
        self.date_to_id = self.getControl(109) #Date To
        self.studio_id = self.getControl(111) #Studio
        self.region_id = self.getControl(113) #Studio

        self.control_id_button_1 = self.getControl(3001)  #Add all archives button
        self.control_id_button_2 = self.getControl(3002)  #Remove all archives button
        self.control_id_button_3 = self.getControl(3003)  #Advanced search on button
        self.control_id_button_4 = self.getControl(3004)  #Advanced search off button
        self.as_group_control = self.getControl(3005)  #Advanced search on button
        self.control_id_button_5 = self.getControl(3006)  #Search Button
        self.control_id_button_6 = self.getControl(3008)  #Search Button
        
        #Set initial vis
        self.as_group_control.setVisible(False)
        self.control_id_button_3.setVisible(False)
        self.control_id_button_4.setVisible(True)
        xbmcgui.Window(10000).setProperty('iarl.advanced_search','False') #Turn off AS by default

        # translate buttons
        self.control_id_button_1.setLabel('Select All')
        self.control_id_button_2.setLabel('Select None')
        self.control_id_button_5.setLabel('Search')
        self.control_id_button_6.setLabel('Close')

        #Populate Lists
        for ii in range(0,len(iarl_data['archive_data']['emu_name'])):
            if 'hidden' not in iarl_data['archive_data']['emu_category'][ii]: #Don't include the archive if it's tagged hidden
                current_listitem = xbmcgui.ListItem(label=iarl_data['archive_data']['emu_name'][ii])
                current_listitem.setIconImage(iarl_data['archive_data']['emu_boxart'][ii])
                current_listitem.setProperty('include_in_search','0') #Default to not include in search
                self.archive_list.addItem(current_listitem) #Add item to the filter list

    def onAction(self, action):
        # Same as normal python Windows.
        if action in self.action_exitkeys_id:
            self.closeDialog()

    # def onFocus(self, controlId):
    #     pass

    def onClick(self, controlId):
        if controlId == 101:
            current_item = self.archive_list.getSelectedItem()
            if current_item.getProperty('include_in_search') == '0':
                current_item.setProperty('include_in_search','1') #It wasnt included, and now should be included
            else:
                current_item.setProperty('include_in_search','0') #It was included, and now shouldnt be included

        if controlId == 3001:
            for ii in range(0,self.archive_list.size()):
                current_listitem = self.archive_list.getListItem(ii)
                current_listitem.setProperty('include_in_search','1') #Select All

        if controlId == 3002:
            for ii in range(0,self.archive_list.size()):
                current_listitem = self.archive_list.getListItem(ii)
                current_listitem.setProperty('include_in_search','0') #Select None

        if controlId == 3003:
            self.as_group_control.setVisible(False)
            self.control_id_button_3.setVisible(False)
            self.control_id_button_4.setVisible(True)
            xbmcgui.Window(10000).setProperty('iarl.advanced_search','False') #Turn off AS

        if controlId == 3004:
            self.as_group_control.setVisible(True)
            self.control_id_button_3.setVisible(True)
            self.control_id_button_4.setVisible(False)
            xbmcgui.Window(10000).setProperty('iarl.advanced_search','True') #Turn off AS

        if controlId == 3008:
            self.closeDialog()

        if controlId == 3006:
            #Define search criteria
            include_text_arg = ''
            at_least_one = False
            for ii in range(0,self.archive_list.size()):
                if self.archive_list.getListItem(ii).getProperty('include_in_search') == '1':
                    include_text_arg = include_text_arg+',1'
                    at_least_one = True
                else:
                    include_text_arg = include_text_arg+',0'
            include_text_arg = include_text_arg[1:] #Remove that first comma

            current_search_term = 'any'
            current_genre = 'any'
            current_nplayers = 'any'
            current_date_from = 'any'
            current_date_to = 'any'
            current_studio = 'any'
            current_region = 'any'

            if len(self.search_box.getText())>0:
                current_search_term = self.search_box.getText()

            if xbmcgui.Window(10000).getProperty('iarl.advanced_search') == 'True':
                if len(self.genre_id.getText())>0:
                    current_genre = self.genre_id.getText()
                if len(self.nplayers_id.getText())>0:
                    current_nplayers = self.nplayers_id.getText()
                if len(self.date_from_id.getText())>0:
                    current_date_from = self.date_from_id.getText()
                if len(self.date_to_id.getText())>0:
                    current_date_to = self.date_to_id.getText()
                if len(self.studio_id.getText())>0:
                    current_studio = self.studio_id.getText()
                if len(self.region_id.getText())>0:
                    current_region = self.region_id.getText()

            current_dialog = xbmcgui.Dialog()

            if not at_least_one:
                current_dialog.ok('Wah Waaah','You must select at least one archive!')
                ret1=1
            else:
                # ret1 = current_dialog.select('Start Search?', ['Yes','No']) #Removing redundant search dialog
                ret1 = 0

            if ret1 == 0:
                xbmc.log(msg='IARL:  Starting Search...', level=xbmc.LOGDEBUG)
                #Not sure why plugin.redirect doesnt work here.  It for some reason will not pass kwargs?
                # search_url = plugin.url_for('search_roms_results', search_term=current_search_term,include_archives=include_text_arg, adv_search=xbmcgui.Window(10000).getProperty('iarl.advanced_search'),genre=current_genre,nplayers=current_nplayers,datefrom=current_date_from,dateto=current_date_to,studio=current_studio,region=current_region)
                self.closeDialog()
                search_roms_results(current_search_term,include_archives=include_text_arg,adv_search=xbmcgui.Window(10000).getProperty('iarl.advanced_search'),genre=current_genre,nplayers=current_nplayers,datefrom=current_date_from,dateto=current_date_to,studio=current_studio,region=current_region)
                # plugin.redirect(search_url)
            else:
                pass

    def closeDialog(self):
        self.close()

if __name__ == '__main__':
    plugin.run()