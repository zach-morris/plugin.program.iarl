import xbmcaddon, xbmcgui

addon = xbmcaddon.Addon(id='plugin.program.iarl')
current_setting = addon.getSetting('iarl_setting_clear_hidden_archives')

if 'false'.lower() in current_setting.lower():
	current_dialog = xbmcgui.Dialog()
	ret1 = current_dialog.select('Are you sure you want to unhide all IARL Archives?', ['No','Yes'])

	if ret1 == 0:
		pass
	else:
		addon.setSetting(id='iarl_setting_clear_hidden_archives',value='true')
		ok_ret = current_dialog.ok('Complete','All Archives will be set to Visible.')
		print 'IARL:  Unhide All Archives set to true'