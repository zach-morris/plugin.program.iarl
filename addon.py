from xbmcswift2 import Plugin
from xbmcswift2 import actions
import os, sys, subprocess, xbmc, xbmcgui
from resources.lib.util import *
from resources.lib.webutils import *
import resources.lib.paginate as paginate

plugin = Plugin()

iarl_setting_cache_list = plugin.get_setting('iarl_setting_cache_list',bool)
iarl_setting_clean_list = plugin.get_setting('iarl_setting_clean_list',bool)
iarl_setting_clear_cache_value  = plugin.get_setting('iarl_setting_clear_cache_value',bool)

items_pp_options = {'10':10,'25':25,'50':50,'100':100,'150':150,'200':200,'250':250,'300':300,'350':350,'400':400,'450':450,'500':500,'List All':99999}
try:
    iarl_setting_items_pp = items_pp_options[plugin.get_setting('iarl_setting_items_pp',unicode)]
except ValueError:
    iarl_setting_items_pp = 99999

cache_options = {'Zero (One ROM and Supporting Files Only)':0,'10 MB':10*1e6,'25MB':25*1e6,'50MB':50*1e6,'100MB':100*1e6,'150MB':150*1e6,'200MB':200*1e6,'250MB':250*1e6,'300MB':300*1e6,'350MB':350*1e6,'400MB':400*1e6,'450MB':450*1e6,'500MB':500*1e6}
try:
    iarl_setting_dl_cache = cache_options[plugin.get_setting('iarl_setting_dl_cache',unicode)]
except ValueError:
    iarl_setting_dl_cache = 0

if not iarl_setting_cache_list:
    plugin.clear_function_cache() #Clear the cache every run

if iarl_setting_clear_cache_value:
    advanced_setting_action_clear_cache(plugin)

iarl_setting_default_action = plugin.get_setting('iarl_setting_default_action')
iarl_setting_retroarch_path = plugin.get_setting('iarl_path_to_retroarch')
iarl_setting_operating_system = get_Operating_System()

@plugin.route('/update_xml/<xml_id>')
def update_xml_value(xml_id):
    args_in = plugin.request.args
    try:
        tag_value = args_in['tag_value'][0]
    except:
        tag_value = None

    if tag_value == 'emu_downloadpath':
        print 'Updating Download Path for '+xml_id
        set_new_dl_path(xml_id,plugin)

    elif tag_value == 'emu_postdlaction':
        print 'Updating Post DL Action for '+xml_id
        set_new_post_dl_action(xml_id,plugin)

    elif tag_value == 'emu_launcher':
        print 'Updating Emu Laucher for '+xml_id
        set_new_emu_launcher(xml_id,plugin)

    elif tag_value == 'emu_ext_launch_cmd':
        print 'Updating External Launch Command'
        update_external_launch_commands(iarl_setting_operating_system,iarl_setting_retroarch_path,xml_id,plugin)

    else:
        pass #Do Nothing

def update_context(xml_id_in,tag_value_in,context_label):
    new_url = plugin.url_for('update_xml_value', xml_id=xml_id_in, tag_value = tag_value_in)
    return (context_label, actions.background(new_url))

@plugin.route('/') #Start Page
def index():
    items = []
    emu_info = scape_xml_headers() #Find all xml dat files and get the header info
    icon_filepath = getMediaFilePath()

    for ii in range(0,len(emu_info['emu_name'])):
        
        #Generate the context menu
        context_menus = [update_context(emu_info['emu_location'][ii],'emu_downloadpath','Update Download Path'),
                        update_context(emu_info['emu_location'][ii],'emu_postdlaction','Update Post DL Action'),
                        update_context(emu_info['emu_location'][ii],'emu_launcher','Update Launcher'),
                        update_context(emu_info['emu_location'][ii],'emu_ext_launch_cmd','Update Ext Launcher Command'),]

        items.append({ 
        'label' : emu_info['emu_name'][ii], 'path': plugin.url_for('get_rom_page', category_id=emu_info['emu_name'][ii],page_id='1',parser_id=emu_info['emu_parser'][ii],xml_id=emu_info['emu_location'][ii]), 'icon': emu_info['emu_logo'][ii],
        'thumbnail' : emu_info['emu_thumb'][ii],
        'info' : {'genre': emu_info['emu_category'][ii], 'credits': emu_info['emu_author'][ii], 'date': emu_info['emu_date'][ii], 'plot': emu_info['emu_comment'][ii], 'trailer': getYouTubePluginurl(emu_info['emu_trailer'][ii]), 'FolderPath': emu_info['emu_baseurl'][ii]},
        'properties' : {'fanart_image' : emu_info['emu_fanart'][ii], 'banner' : emu_info['emu_banner'][ii], 'clearlogo': emu_info['emu_logo'][ii]},
        'context_menu' : context_menus
        })
    
    items.append({ 
        'label' : '\xc2\xa0Search', 'path' :  plugin.url_for('search_roms_window'), 'icon': icon_filepath + 'search.jpg',
        'thumbnail' : icon_filepath + 'search.jpg',
        'info' : {'genre': '\xc2\xa0', 'date': '01/01/2999', 'plot' : 'Search for a particular game.'},
        'properties' : {'fanart_image' : icon_filepath + 'fanart.jpg'}
        })

    items.append({ 
        'label' : '\xc2\xa0\xc2\xa0Random Play', 'path' :  plugin.url_for('random_play'), 'icon': icon_filepath + 'lucky.jpg',
        'thumbnail' : icon_filepath + 'lucky.jpg',
        'info' : {'genre': '\xc2\xa0\xc2\xa0', 'date': '01/01/2999', 'plot' : 'Play a random game from the archive.'},
        'properties' : {'fanart_image' : icon_filepath + 'fanart.jpg'}
        })

    return plugin.finish(items, sort_methods=[xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_GENRE])
    # return items

@plugin.route('/Emulator/<category_id>/<page_id>')
def get_rom_page(category_id,page_id):
    
    include_pp_link = 0 #Just use the standard list back buton

    #Define Parser
    args_in = plugin.request.args
    try:
        parserpath = args_in['parser_id'][0]
    except:
        parserpath = None
    try:
        xmlpath = args_in['xml_id'][0]
    except:
        xmlpath = None
    try:
        rom_list = get_rom_list(xmlpath,parserpath)
    except:
        rom_list = None
    

    page = paginate.Page(rom_list, page=page_id, items_per_page=iarl_setting_items_pp)
    # print page.items
    #Create Page Controls
    next_page = []
    prev_page = []
    icon_filepath = getMediaFilePath()
    # next_page.append({'label': 'Next >>', 'path': plugin.url_for('get_rom_list', category_id=category_id,page_id=str(int(float(page_id))+1),parser_id=parserpath,xml_id=rom_list)})
    prev_page.append({ 
        'label' : '\xc2\xa0Prev <<', 'path' :  plugin.url_for('get_rom_page', category_id=category_id,page_id=str(page.previous_page),parser_id=parserpath,xml_id=xmlpath), 'icon': icon_filepath + 'Previous.png',
        'thumbnail' : icon_filepath + 'Previous.png',
        'info' : {'genre': '\xc2\xa0', 'date': '01/01/2999', 'plot' : 'Page ' + str(page.page) + ' of ' + str(page.page_count) + '.  Prev page is ' + str(page.previous_page) + '.  Total of ' + str(page.item_count) + ' games in this archive.'}
        })
    next_page.append({ 
        'label' : '\xc2\xa0Next >>', 'path' :  plugin.url_for('get_rom_page', category_id=category_id,page_id=str(page.next_page),parser_id=parserpath,xml_id=xmlpath), 'icon': icon_filepath + 'Next.png',
        'thumbnail' : icon_filepath + 'Next.png',
        'info' : {'genre': '\xc2\xa0', 'date': '01/01/2999', 'plot' : 'Page ' + str(page.page) + ' of ' + str(page.page_count) + '.  Next page is ' + str(page.next_page) + '.  Total of ' + str(page.item_count) + ' games in this archive.'}
        })

    current_page = page.items #Grab the current page requested

    #Add next and prev page URL routes
    if include_pp_link:
        if page.previous_page:
            current_page.extend(prev_page)

    if page.next_page:
        current_page.extend(next_page)

    return plugin.finish(current_page, sort_methods=[xbmcplugin.SORT_METHOD_NONE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_GENRE, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE])
    # return current_page

@plugin.cached(TTL=24*60*30)
def get_rom_list(xmlpath,parserpath):
    parserpath = getParserFilePath(parserpath)
    rom_list = parse_xml_romfile(xmlpath,parserpath,iarl_setting_clean_list,plugin) #List doesn't exist, so get the romlist
    return rom_list

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
            datefrom_num = int(current_datefrom.lower().strip()) #No checking... yet
        except:
            print 'IARL Error:  Date from is badly formatted, default year used'
            datefrom_num = 1950 #Bad formatted date

    if current_dateto == 'any':
        dateto_num = 2999 #Random year that this code will obviously be dead and gone when reached
    else:
        try:
            dateto_num = int(current_dateto.lower().strip())
        except:
            print 'IARL Error:  Date to is badly formatted, default year used'
            dateto_num = 2999 #Bad formatted date

    date_list = range(datefrom_num,dateto_num) #List of years to look for

    emu_info = scape_xml_headers() #Find all xml dat files and get the header info
    progress_dialog = xbmcgui.DialogProgress()
    progress_dialog.create('IARL', 'Searching...')

    #This probably isnt a very efficient method for filtering.  Need to look into lambda dict filtering
    if current_adv_search == 'False':
        for ii in range(0,len(current_includes)):
            progress_dialog.update(max(1,int(100*ii/len(current_includes))-10), 'Looking in '+emu_info['emu_name'][ii])
            if current_includes[ii] == '1':
                if current_search_term == 'any':
                    for roms_in_list in get_rom_list(emu_info['emu_location'][ii],emu_info['emu_parser'][ii]):
                        if (progress_dialog.iscanceled()):
                            print 'IARL:  Search Cancelled'
                            return
                        search_results.append(roms_in_list)
                else:
                    for roms_in_list in get_rom_list(emu_info['emu_location'][ii],emu_info['emu_parser'][ii]):
                        if (progress_dialog.iscanceled()):
                            print 'IARL:  Search Cancelled'
                            return
                        if current_search_term in roms_in_list['label'].lower().strip(): #search term is in label
                            search_results.append(roms_in_list)
    else:
        for ii in range(0,len(current_includes)):
            progress_dialog.update(max(1,int(100*ii/len(current_includes))-10), 'Looking in '+emu_info['emu_name'][ii])
            if current_includes[ii] == '1':
                for roms_in_list in get_rom_list(emu_info['emu_location'][ii],emu_info['emu_parser'][ii]):
                    if (progress_dialog.iscanceled()):
                        print 'IARL:  Search Cancelled'
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
    print 'IARL:  Found ' + str(len(search_results)) + ' matches'
    return plugin.finish(search_results,cache_to_disc=False,sort_methods=[xbmcplugin.SORT_METHOD_NONE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_GENRE, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE])
    progress_dialog.close()

@plugin.route('/Search')
def search_roms_window():
    MySearchWindow = SearchWindow('search.xml',getAddonInstallPath(),'Default','720p')
    MySearchWindow.doModal()
    pass

@plugin.route('/Random')
def random_play():
    print 'IARL:  Random play not yet implemented :-('
    pass


@plugin.route('/Emulator/<romname>')
def get_selected_rom(romname):

    args_in = plugin.request.args
    
    current_fanart = list()
    current_banner = list()
    current_snapshot = list()
    current_boxart = list()
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart1)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart2)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart3)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart4)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart5)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart6)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart7)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart8)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart9)'))
    current_fanart.append(xbmc.getInfoLabel('ListItem.Property(fanart10)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner1)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner2)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner3)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner4)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner5)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner6)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner7)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner8)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner9)'))
    current_banner.append(xbmc.getInfoLabel('ListItem.Property(banner10)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot1)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot2)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot3)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot4)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot5)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot6)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot7)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot8)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot9)'))
    current_snapshot.append(xbmc.getInfoLabel('ListItem.Property(snapshot10)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart1)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart2)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart3)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart4)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart5)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart6)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart7)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart8)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart9)'))
    current_boxart.append(xbmc.getInfoLabel('ListItem.Property(boxart10)'))
    current_title= xbmc.getInfoLabel('Listitem.Label')
    current_studio= xbmc.getInfoLabel('Listitem.Studio')
    current_rom_tag = xbmc.getInfoLabel('ListItem.Property(rom_tag)')
    current_nplayers = xbmc.getInfoLabel('ListItem.Property(nplayers)')
    current_emu_logo = xbmc.getInfoLabel('ListItem.Property(emu_logo)')
    current_emu_fanart = xbmc.getInfoLabel('ListItem.Property(emu_fanart)')
    current_emu_name = xbmc.getInfoLabel('ListItem.Property(emu_name)')
    current_rom_fname = xbmc.getInfoLabel('ListItem.Property(rom_fname)') #Full URL of ROM
    current_rom_sfname = xbmc.getInfoLabel('ListItem.Property(rom_sfname)') #Full URL of supporting ROMs
    # current_rom_save_fname = xbmc.getInfoLabel('ListItem.Property(rom_save_fname)') #Filename to save for ROM
    current_rom_save_fname = os.path.split(unquote_name(xbmc.getInfoLabel('ListItem.Property(rom_save_fname)')))[-1].strip() #Filename to save for ROM
    # current_rom_save_sfname = xbmc.getInfoLabel('ListItem.Property(rom_save_sfname)') #Filename to save for supporting ROMs
    current_rom_save_sfname = os.path.split(unquote_name(xbmc.getInfoLabel('ListItem.Property(rom_save_sfname)')))[-1].strip() #Filename to save for ROM
    current_genre = xbmc.getInfoLabel('ListItem.Genre')
    current_release_date = xbmc.getInfoLabel('ListItem.Date')
    current_plot = xbmc.getInfoLabel('ListItem.Plot')
    current_trailer = xbmc.getInfoLabel('ListItem.Trailer')
    current_emu_downloadpath = xbmc.getInfoLabel('ListItem.Property(emu_downloadpath)')
    current_emu_postdlaction = xbmc.getInfoLabel('ListItem.Property(emu_postdlaction)')
    current_emu_launcher = xbmc.getInfoLabel('ListItem.Property(emu_launcher)')
    current_emu_ext_launch_cmd = xbmc.getInfoLabel('ListItem.Property(emu_ext_launch_cmd)')
    current_rom_emu_command = xbmc.getInfoLabel('ListItem.Property(rom_emu_command)')

    if 'ROM Info Page'.lower() in iarl_setting_default_action.lower():
        MyROMWindow = ROMWindow('default.xml',getAddonInstallPath(),'Default','720p',rom_fname=current_rom_fname, rom_sfname=current_rom_sfname, rom_save_fname=current_rom_save_fname, rom_save_sfname=current_rom_save_sfname, emu_name=current_emu_name, logo=current_emu_logo, emu_fanart=current_emu_fanart, title=current_title, plot=current_plot, fanart=filter(bool, current_fanart), boxart=filter(bool, current_boxart), snapshot=filter(bool, current_snapshot), banner=filter(bool, current_banner), trailer=current_trailer, nplayers=current_nplayers, studio=current_studio, genre=current_genre, release_date=current_release_date, emu_downloadpath=current_emu_downloadpath, emu_postdlaction=current_emu_postdlaction, emu_launcher=current_emu_launcher, emu_ext_launch_cmd=current_emu_ext_launch_cmd, rom_emu_command=current_rom_emu_command)
        MyROMWindow.doModal()
    elif 'Download and Launch'.lower() in iarl_setting_default_action.lower():
        download_and_launch_rom(None,current_rom_fname,current_rom_sfname, current_rom_save_fname, current_rom_save_sfname, current_emu_downloadpath, current_emu_postdlaction, current_emu_launcher, current_emu_ext_launch_cmd, current_rom_emu_command)
    elif 'Download Only'.lower() in iarl_setting_default_action.lower():
        current_dialog = xbmcgui.Dialog()
        download_success, new_rom_fname, new_rom_sfname = download_rom_only(current_rom_fname,current_rom_sfname, current_rom_save_fname, current_rom_save_sfname, current_emu_downloadpath, current_emu_postdlaction, current_rom_emu_command)
        if download_success:
            ok_ret = current_dialog.ok('Complete',current_rom_save_fname + ' was successfully downloaded')            
    else:
        print 'IARL Error:  Unknown Option'
        pass #Shouldn't ever see this

    pass

def download_rom_only(rom_fname,rom_sfname, rom_save_fname, rom_save_sfname, rom_dl_path, rom_postdlaction, rom_emu_command):
    download_success = False
    new_rom_fname = None
    new_rom_sfname = None

    if rom_dl_path == 'default':
        current_path = getTempDir()
    else:
        current_path = rom_dl_path

    #Clean the savefilenames so it's only the last thing listed in the ROM argument (no folders)
    # cleaned_save_fname = rom_save_fname.split('/')[-1:][0]
    # cleaned_save_fname = cleaned_save_fname.split('%2F')[-1:][0]
    # cleaned_save_fname = unquote_name(cleaned_save_fname) #Added 082415, issue with launching if the filename is quoted
    # cleaned_save_sfname = rom_save_sfname.split('/')[-1:][0]
    # cleaned_save_sfname = cleaned_save_sfname.split('%2F')[-1:][0]
    # cleaned_save_sfname = unquote_name(cleaned_save_sfname) #Added 082415, issue with launching if the filename is quoted
    current_save_fname = current_path+'/'+rom_save_fname
    current_save_sfname = current_path+'/'+rom_save_sfname

    fname_found, do_not_download_flag = check_if_rom_exits(current_save_fname,current_path)

    if not do_not_download_flag: #File already is downloaded, no need to do anything else
        if rom_dl_path == 'default':
            check_temp_folder_and_clean(iarl_setting_dl_cache) #Check temp folder cache size and clean if needed

        print 'Downloading Selected ROM'
        # print 'test'
        # print rom_emu_command
        
        if rom_save_fname:
            download_tools().Downloader(quote_url(rom_fname),current_save_fname,rom_save_fname,'Downloading, please wait...')
            bad_file_found1 = check_downloaded_file(current_save_fname)

            if not bad_file_found1:
                download_success = True

                if rom_postdlaction == 'unzip_rom':
                    print 'Unzipping ' + current_save_fname
                    zip_success1, new_rom_fname = unzip_file(current_save_fname)
                elif rom_postdlaction == 'unzip_update_rom_path_dosbox':
                    zip_success1, new_rom_fname = unzip_dosbox_file(current_save_fname,rom_emu_command)
            else:
                download_success = False

        if rom_save_sfname:
            if rom_save_sfname != 'None':
                download_tools().Downloader(rom_sfname,current_save_sfname,rom_save_sfname,'Downloading additional, please wait...')
                bad_file_found2 = check_downloaded_file(current_save_sfname)

            if not bad_file_found2:
                download_success = True

                if rom_postdlaction == 'unzip_rom':
                    print 'Unzipping ' + current_save_sfname
                    zip_success2, new_rom_sfname = unzip_file(current_save_sfname)
            else:
                download_success = False
    else:
        if fname_found is not None:
            new_rom_fname = current_path+'/'+fname_found #Ensure the filename has the correct extension (could potentially have been unzipped)

    return download_success, new_rom_fname, new_rom_sfname

def download_and_launch_rom(romwindow,rom_fname,rom_sfname, rom_save_fname, rom_save_sfname, rom_dl_path, rom_postdlaction, emu_launcher, emu_ext_launch_cmd, rom_emu_command):
    print 'Download and Launch Selected'

    if emu_launcher == 'external': #Use external launcher
        if emu_ext_launch_cmd != 'none':
            external_command = None
            download_success, new_rom_fname, new_rom_sfname = download_rom_only(rom_fname,rom_sfname, rom_save_fname, rom_save_sfname, rom_dl_path, rom_postdlaction, rom_emu_command)
            current_path = getTempDir()
            current_save_fname = current_path+'/'+rom_save_fname
            current_save_sfname = current_path+'/'+rom_save_sfname

            if new_rom_fname is not None: #The file was unzipped, change from zip to the correct rom extension
                current_save_fname = new_rom_fname

            if new_rom_sfname is not None: #The file was unzipped, change from zip to the correct rom extension
                current_save_sfname = new_rom_sfname

            current_external_command = emu_ext_launch_cmd.replace('%ROM_PATH%',current_save_fname) 
            print 'External Command: '+ current_external_command
            if romwindow is not None:
                romwindow.closeDialog()
            external_command = subprocess.call(current_external_command,shell=True)

        else:
            print 'IARL Error:  No external launch command is defined'

    else: #Otherwise use retroplayer
        download_success, new_rom_fname, new_rom_sfname = download_rom_only(rom_fname,rom_sfname, rom_save_fname, rom_save_sfname, rom_dl_path, rom_postdlaction, rom_emu_command)
        current_path = getTempDir()
        current_save_fname = current_path+'/'+rom_save_fname
        current_save_sfname = current_path+'/'+rom_save_sfname

        if new_rom_fname is not None: #The file was unzipped, change from zip to the correct rom extension
            current_save_fname = new_rom_fname

        if new_rom_sfname is not None: #The file was unzipped, change from zip to the correct rom extension
            current_save_sfname = new_rom_sfname

        launch_game_listitem = xbmcgui.ListItem(current_save_fname, "0", "", "")
        parameters = { }
        launch_game_listitem.setInfo( type="game", infoLabels=parameters)

        if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)

        if romwindow is not None:
            romwindow.closeDialog() #Need to close the dialog window for the game window to be in the front
        
        xbmc.sleep(500) #This pause seems to help... I'm not really sure why
        xbmc.Player().play(current_save_fname,launch_game_listitem)

class ROMWindow(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback, *args, **kwargs):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        self.rom_fname = kwargs['rom_fname']
        self.rom_sfname = kwargs['rom_sfname']
        self.rom_save_fname = kwargs['rom_save_fname']
        self.rom_save_sfname = kwargs['rom_save_sfname']
        self.emu_name = kwargs['emu_name']
        self.logo = kwargs['logo']
        self.fanart = kwargs['fanart']
        self.boxart = kwargs['boxart']
        self.snapshot = kwargs['snapshot']
        self.banner = kwargs['banner']
        self.title = kwargs['title']
        self.plot = kwargs['plot']
        self.trailer = kwargs['trailer']
        self.emu_fanart = kwargs['emu_fanart']
        self.nplayers = kwargs['nplayers']
        self.studio = kwargs['studio']
        self.genre = kwargs['genre']
        self.release_date = kwargs['release_date']
        self.emu_downloadpath = kwargs['emu_downloadpath']
        self.emu_postdlaction = kwargs['emu_postdlaction']
        self.emu_launcher = kwargs['emu_launcher']
        self.emu_ext_launch_cmd = kwargs['emu_ext_launch_cmd']
        self.rom_emu_command = kwargs['rom_emu_command']
        pass

    def onInit(self):
        # Put your List Populating code/ and GUI startup stuff here

        set_iarl_window_properties(self.emu_name) #Set these properties again in case the list was cached

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

        self.action_exitkeys_id = [10, 13]
        
        # get control ids
        self.control_id_button_action1 = 3001 #Download Only
        self.control_id_button_action2 = 3002 #Download and Launch
        self.control_id_button_action3 = 3005 #Play Trailer
        self.control_id_button_action4 = 3006 #Stop Trailer
        self.control_id_button_exit = 3003
        self.control_id_label_action = 3011
        
        if self.trailer: #If the trailer exists make the play button available
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

        self.plot_box.setText(self.plot) #Enter the plot if its available
        self.logo_art.setImage(self.logo) #Place the emu logo

        self.title_box.setText(self.title)
        self.genre_box.setText(self.genre)
        self.players_box.setText('Players[CR]'+self.nplayers)
        self.studio_box.setText('Released: '+self.release_date+'[CR]'+self.studio)
 
        #Populate the image spots
        left_art_found = False
        right_art_found = False
        for entries in self.boxart:
            left_art_found = True
            self.left_art2.addItem(xbmcgui.ListItem(label2=xbmcgui.Window(10000).getProperty('iarl.current_theme'), thumbnailImage=entries)) #Add boxart to the left image slideshow

        for entries in self.fanart:
            right_art_found = True
            self.right_art2.addItem(xbmcgui.ListItem(label2=xbmcgui.Window(10000).getProperty('iarl.current_theme'), thumbnailImage=entries)) #Add fanart to the right image slideshow

        for entries in self.snapshot:
            right_art_found = True
            self.right_art2.addItem(xbmcgui.ListItem(label2=xbmcgui.Window(10000).getProperty('iarl.current_theme'), thumbnailImage=entries)) #Add snapshots to the right image slideshow

        if not right_art_found:
            self.right_art2.addItem(xbmcgui.ListItem(label2=xbmcgui.Window(10000).getProperty('iarl.current_theme'), thumbnailImage=self.emu_fanart)) #If no fanart is found, make it the current emulator fanart

        if not left_art_found:
            self.left_art2.addItem(xbmcgui.ListItem(label2=xbmcgui.Window(10000).getProperty('iarl.current_theme'), thumbnailImage=getMediaFilePath() + xbmcgui.Window(10000).getProperty('iarl.default_thumb'))) #If no boxart is found, make it the default box


    def onAction(self, action):
        # Same as normal python Windows.
        if action in self.action_exitkeys_id:
            self.closeDialog()

    def onFocus(self, controlId):
        pass

    def onClick(self, controlId):
        if controlId == self.control_id_button_action1:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)

            current_dialog = xbmcgui.Dialog()
            download_success, uz_file_extension1, uz_file_extension2 = download_rom_only(self.rom_fname, self.rom_sfname, self.rom_save_fname, self.rom_save_sfname, self.emu_downloadpath, self.emu_postdlaction, self.rom_emu_command)

            if download_success:
                ok_ret = current_dialog.ok('Complete',self.rom_save_fname + ' was successfully downloaded')

        if controlId == self.control_id_button_action2:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)

            download_and_launch_rom(self,self.rom_fname, self.rom_sfname, self.rom_save_fname, self.rom_save_sfname, self.emu_downloadpath, self.emu_postdlaction, self.emu_launcher, self.emu_ext_launch_cmd, self.rom_emu_command)

        if controlId == self.control_id_button_action3: #Play the trailer if it exists
            if self.trailer:
                self.right_art2.setVisible(False) #Get Fanart out of the way
                xbmc.sleep(100)
                xbmc.Player().play(self.trailer, windowed=True)
                self.play_button.setVisible(False)
                self.stop_button.setVisible(True)
                self.setFocus(self.stop_button)

        if controlId == self.control_id_button_action4: #Stop the trailer
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)
                self.right_art2.setVisible(True) #Turn the fanart back on
                self.play_button.setVisible(True)
                self.stop_button.setVisible(False)
                self.setFocus(self.play_button)


        elif controlId == self.control_id_button_exit:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)

            self.closeDialog()

    def doAction(self, controlId):
        # print 'test'
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
        self.available_as_options = ['Genre','Release Date','Region','Num Players','Studio'] #Not currently used

    def onInit(self):
        # Put your List Populating code/ and GUI startup stuff here
        emu_info = scape_xml_headers() #Find all xml dat files and get the header info
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
        
        #Set initial vis
        self.as_group_control.setVisible(False)
        self.control_id_button_3.setVisible(False)
        self.control_id_button_4.setVisible(True)
        xbmcgui.Window(10000).setProperty('iarl.advanced_search','False') #Turn off AS by default

        # translate buttons
        self.control_id_button_1.setLabel('Select All')
        self.control_id_button_2.setLabel('Select None')
        self.control_id_button_5.setLabel('Search')

        #Populate Lists
        for ii in range(0,len(emu_info['emu_name'])):    
            current_listitem = xbmcgui.ListItem(label=emu_info['emu_name'][ii])
            current_listitem.setIconImage(emu_info['emu_thumb'][ii])
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
                ret1 = current_dialog.select('Start Search?', ['Yes','No'])

            if ret1 == 0:
                print 'IARL:  Starting Search'
                #Not sure why plugin.redirect doesnt work here.  It for some reason will not pass kwargs?
                # search_url = plugin.url_for('search_roms_results', search_term=current_search_term,include_archives=include_text_arg, adv_search=xbmcgui.Window(10000).getProperty('iarl.advanced_search'),genre=current_genre,nplayers=current_nplayers,datefrom=current_date_from,dateto=current_date_to,studio=current_studio,region=current_region)
                self.closeDialog()
                search_roms_results(current_search_term,include_archives=include_text_arg, adv_search=xbmcgui.Window(10000).getProperty('iarl.advanced_search'),genre=current_genre,nplayers=current_nplayers,datefrom=current_date_from,dateto=current_date_to,studio=current_studio,region=current_region)
                # plugin.redirect(search_url)
            else:
                pass

    def closeDialog(self):
        self.close()

if __name__ == '__main__':
    plugin.run()