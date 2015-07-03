from xbmcswift2 import Plugin
import os, sys, xbmc, xbmcgui, xbmcvfs, textwrap
# import pyxbmct.addonwindow as pyxbmct
from resources.lib.util import *
from resources.lib.webutils import *
import resources.lib.paginate as paginate
from random import randint
# from resources.lib.descriptionparserfactory import *
# from PIL import Image
# import requests
# from io import BytesIO

plugin = Plugin()

iarl_setting_cache_list = plugin.get_setting('iarl_setting_cache_list',bool)
iarl_setting_clean_list = plugin.get_setting('iarl_setting_clean_list',bool)
iarl_options_items_pp = [10, 25, 50, 100, 150 ,200, 250, 300, 350, 400, 450, 500, 99999]
iarl_setting_items_pp = iarl_options_items_pp[plugin.get_setting('iarl_setting_items_pp',int)]
iarl_options_dl_cache = [0, 10*1e6, 25*1e6, 50*1e6, 100*1e6, 150*1e6, 200*1e6, 250*1e6, 300*1e6, 350*1e6, 400*1e6, 450*1e6, 500*1e6]
iarl_setting_dl_cache = iarl_options_dl_cache[plugin.get_setting('iarl_setting_dl_cache',int)]

if not iarl_setting_cache_list:
    plugin.clear_function_cache() #Clear the cache every run

@plugin.route('/') #Start Page
def index():
    items = []

    emu_info = scape_xml_headers() #Find all xml dat files and get the header info

    for ii in range(0,len(emu_info['emu_name'])):
        items.append({ 
        'label' : emu_info['emu_name'][ii], 'path': plugin.url_for('get_rom_list', category_id=emu_info['emu_name'][ii],page_id='1',parser_id=emu_info['emu_parser'][ii],xml_id=emu_info['emu_location'][ii]), 'icon': emu_info['emu_logo'][ii],
        'thumbnail' : emu_info['emu_thumb'][ii],
        'info' : {'genre': emu_info['emu_category'][ii], 'credits': emu_info['emu_author'][ii], 'date': emu_info['emu_date'][ii], 'plot': emu_info['emu_comment'][ii], 'trailer': getYouTubePluginurl(emu_info['emu_trailer'][ii]), 'FolderPath': emu_info['emu_baseurl'][ii]},
        'properties' : {'fanart_image' : emu_info['emu_fanart'][ii], 'banner' : emu_info['emu_banner'][ii], 'clearlogo': emu_info['emu_logo'][ii]}
        })
    
    return items

@plugin.route('/Emulator/<category_id>/<page_id>')
def get_rom_list(category_id,page_id):
    
    include_pp_link = 0

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
        'label' : '<< Prev', 'path' :  plugin.url_for('get_rom_list', category_id=category_id,page_id=str(page.previous_page),parser_id=parserpath,xml_id=xmlpath), 'icon': icon_filepath + 'Previous.png',
        'thumbnail' : icon_filepath + 'Previous.png',
        'info' : { 'plot' : 'Page ' + str(page.page) + ' of ' + str(page.page_count) + '.  Prev page is ' + str(page.previous_page) + '.  Total of ' + str(page.item_count) + ' games in this archive.'}
        })
    next_page.append({ 
        'label' : 'Next >>', 'path' :  plugin.url_for('get_rom_list', category_id=category_id,page_id=str(page.next_page),parser_id=parserpath,xml_id=xmlpath), 'icon': icon_filepath + 'Next.png',
        'thumbnail' : icon_filepath + 'Next.png',
        'info' : { 'plot' : 'Page ' + str(page.page) + ' of ' + str(page.page_count) + '.  Next page is ' + str(page.next_page) + '.  Total of ' + str(page.item_count) + ' games in this archive.'}
        })

    current_page = page.items #Grab the current page requested

    #Add next and prev page URL routes
    if include_pp_link:
        if page.previous_page:
            current_page.extend(prev_page)

    if page.next_page:
        current_page.extend(next_page)

    return current_page

@plugin.cached(TTL=24*60*30)
def get_rom_list(xmlpath,parserpath):
    parserpath = getParserFilePath(parserpath)
    rom_list = parse_xml_romfile(xmlpath,parserpath,iarl_setting_clean_list,plugin) #List doesn't exist, so get the romlist
    return rom_list


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
    current_nplayers = xbmc.getInfoLabel('ListItem.Property(nplayers)')
    current_emu_logo = xbmc.getInfoLabel('ListItem.Property(emu_logo)')
    current_emu_fanart = xbmc.getInfoLabel('ListItem.Property(emu_fanart)')
    current_emu_name = xbmc.getInfoLabel('ListItem.Property(emu_name)')
    current_rom_fname = xbmc.getInfoLabel('ListItem.Property(rom_fname)') #Full URL of ROM
    current_rom_sfname = xbmc.getInfoLabel('ListItem.Property(rom_sfname)') #Full URL of supporting ROMs
    current_rom_save_fname = xbmc.getInfoLabel('ListItem.Property(rom_save_fname)') #Filename to save for ROM
    current_rom_save_sfname = xbmc.getInfoLabel('ListItem.Property(rom_save_sfname)') #Filename to save for supporting ROMs
    current_emu_name = xbmc.getInfoLabel('ListItem.Property(emu_name)')
    current_genre = xbmc.getInfoLabel('ListItem.Genre')
    current_release_date = xbmc.getInfoLabel('ListItem.Date')
    current_plot = xbmc.getInfoLabel('ListItem.Plot')
    current_trailer = xbmc.getInfoLabel('ListItem.Trailer')
    MyROMWindow = ROMWindow('default.xml',getAddonInstallPath(),'Default','720p',rom_fname=current_rom_fname, rom_sfname=current_rom_sfname, rom_save_fname=current_rom_save_fname, rom_save_sfname=current_rom_save_sfname, emu_name=current_emu_name, logo=current_emu_logo, emu_fanart=current_emu_fanart, title=current_title, plot=current_plot, fanart=filter(bool, current_fanart), boxart=filter(bool, current_boxart), snapshot=filter(bool, current_snapshot), banner=filter(bool, current_banner), trailer=current_trailer, nplayers=current_nplayers, studio=current_studio, genre=current_genre, release_date=current_release_date)
    MyROMWindow.doModal()

def download_rom_only(rom_fname,rom_sfname, rom_save_fname, rom_save_sfname):
    print 'Download Only Selected'
    current_path = getTempDir()
    check_temp_folder_and_clean(iarl_setting_dl_cache)
    current_save_fname = current_path+'/'+rom_save_fname
    current_save_sfname = current_path+'/'+rom_save_sfname

    print rom_save_fname
    print rom_save_sfname

    if rom_save_fname:
        download_tools().Downloader(rom_fname,current_save_fname,rom_save_fname,'Downloading, please wait...')

    if rom_save_sfname:
        if rom_save_sfname != 'None':
            download_tools().Downloader(rom_sfname,current_save_sfname,rom_save_sfname,'Downloading additional, please wait...')

def download_and_launch_rom(romwindow,rom_fname,rom_sfname, rom_save_fname, rom_save_sfname):
    print 'Download and Launch Selected'
    
    success, selectedcore = selectlibretrocore()

    if selectedcore:
        download_rom_only(rom_fname,rom_sfname, rom_save_fname, rom_save_sfname)
        current_path = getTempDir()
        current_save_fname = current_path+'/'+rom_save_fname
        launch_game_listitem = xbmcgui.ListItem(current_save_fname, "0", "", "")
        parameters = { "gameclient": selectedcore }
        print selectedcore
        launch_game_listitem.setInfo( type="game", infoLabels=parameters)

        if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)

        romwindow.closeDialog() #Need to close the dialog window for the game window to be in the front
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

            download_rom_only(self.rom_fname, self.rom_sfname, self.rom_save_fname, self.rom_save_sfname)

        if controlId == self.control_id_button_action2:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                xbmc.sleep(100)

            download_and_launch_rom(self,self.rom_fname, self.rom_sfname, self.rom_save_fname, self.rom_save_sfname)

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

if __name__ == '__main__':
    plugin.run()