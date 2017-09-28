import xbmc, xbmcaddon, xbmcgui, os
from descriptionparserfactory import *
from util import *

#Create dialog right away so user knows something is happening
dp = xbmcgui.DialogProgress()
dp.create('IARL Wizard','Please Wait...','')
dp.update(0)

addon = xbmcaddon.Addon(id='plugin.program.iarl')
archive_data = get_archive_info()

wizard_data = {
			'settings' : {  'iarl_external_user_external_env' : addon.getSetting('iarl_external_user_external_env'),
							'iarl_external_launch_close_kodi' : addon.getSetting('iarl_external_launch_close_kodi'),
							'iarl_path_to_retroarch' : addon.getSetting('iarl_path_to_retroarch'),
							'iarl_path_to_retroarch_cfg' : addon.getSetting('iarl_path_to_retroarch_cfg'),
							'iarl_additional_emulator_1_type' : addon.getSetting('iarl_additional_emulator_1_type'),
							'iarl_additional_emulator_1_path' : addon.getSetting('iarl_additional_emulator_1_path'),
							'iarl_additional_emulator_2_type' : addon.getSetting('iarl_additional_emulator_2_type'),
							'iarl_additional_emulator_2_path' : addon.getSetting('iarl_additional_emulator_2_path'),
							'iarl_wizard_launcher_group' : addon.getSetting('iarl_wizard_launcher_group'),
						},
										#Most Playable, Balanced, Accurate
			'OSX' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['RetroArch 4DO (3DO)','RetroArch 4DO (3DO)','RetroArch 4DO (3DO)'],
							'Amiga_CD32_Full' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Full_ZRL' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Bestof' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)'],
							'Atari_Jaguar_ZachMorris' : ['RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)'],
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'Atari_ST_ZachMorris' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'Atari_ST_ZachMorris_Full' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Colecovision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Colecovision_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_Bestof_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_2003_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2014_ZachMorris' : ['RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)'],
							'MAME_AKNF_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'NES_Bestof_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							# 'PS1_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris_Full' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris' : ['hidden','hidden','hidden'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							# 'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'ZX_Spectrum_ZachMorris' : ['hidden','hidden','hidden'],
							'x68000_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'x68000_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Intellivision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_800_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_5200_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Vectrex_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_CHD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							# 'MAME_2010_ZachMorris' : ['RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)'],
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							},
			'Windows' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['RetroArch 4DO (3DO)','RetroArch 4DO (3DO)','RetroArch 4DO (3DO)'],
							'Amiga_CD32_Full' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Full_ZRL' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Bestof' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)'],
							'Atari_Jaguar_ZachMorris' : ['RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)'],
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'Atari_ST_ZachMorris' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'Atari_ST_ZachMorris_Full' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Colecovision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Colecovision_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_Bestof_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_2003_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2014_ZachMorris' : ['RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)'],
							'MAME_AKNF_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'NES_Bestof_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							# 'PS1_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris_Full' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris' : ['hidden','hidden','hidden'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'x68000_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'x68000_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Intellivision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_800_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_5200_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Vectrex_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_CHD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							# 'MAME_2010_ZachMorris' : ['RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)'],
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							},
			'Linux/Kodibuntu' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['RetroArch 4DO (3DO)','RetroArch 4DO (3DO)','RetroArch 4DO (3DO)'],
							'Amiga_CD32_Full' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Full_ZRL' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Bestof' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)'],
							'Atari_Jaguar_ZachMorris' : ['RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)'],
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'Atari_ST_ZachMorris' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'Atari_ST_ZachMorris_Full' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Colecovision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Colecovision_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_Bestof_ZachMorris' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'MAME_ZachMorris' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'MAME_2003_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2014_ZachMorris' : ['RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)'],
							'MAME_AKNF_Full' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'NES_Bestof_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							# 'PS1_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris_Full' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris' : ['hidden','hidden','hidden'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'x68000_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'x68000_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Intellivision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_800_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_5200_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Vectrex_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_CHD_ZachMorris' : ['hidden','hidden','hidden'], #Superceded with MAME2014
							# 'MAME_2010_ZachMorris' : ['RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)'],
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							},
			'OpenElec x86 (tssemek Addon)' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['RetroArch 4DO (3DO)','RetroArch 4DO (3DO)','RetroArch 4DO (3DO)'],
							'Amiga_CD32_Full' : ['FS-UAE OpenElec Addon (Amiga)','FS-UAE OpenElec Addon (Amiga)','FS-UAE OpenElec Addon (Amiga)'],
							'Amiga_Full_ZRL' : ['FS-UAE OpenElec Addon (Amiga)','FS-UAE OpenElec Addon (Amiga)','FS-UAE OpenElec Addon (Amiga)'],
							'Amiga_Bestof' : ['FS-UAE OpenElec Addon (Amiga)','FS-UAE OpenElec Addon (Amiga)','FS-UAE OpenElec Addon (Amiga)'],
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)'],
							'Atari_Jaguar_ZachMorris' : ['RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)'],
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'Atari_ST_ZachMorris' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'Atari_ST_ZachMorris_Full' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Colecovision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Colecovision_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_Bestof_ZachMorris' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'MAME_ZachMorris' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'MAME_2003_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2014_ZachMorris' : ['RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)'],
							'MAME_AKNF_Full' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'NES_Bestof_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							# 'PS1_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris_Full' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris' : ['hidden','hidden','hidden'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'x68000_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'x68000_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Intellivision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_800_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_5200_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Vectrex_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_CHD_ZachMorris' : ['hidden','hidden','hidden'], #Superceded with MAME2014
							# 'MAME_2010_ZachMorris' : ['RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)'],
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							},
			'LibreElec x86' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['RetroArch 4DO (3DO)','RetroArch 4DO (3DO)','RetroArch 4DO (3DO)'],
							'Amiga_CD32_Full' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Full_ZRL' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Bestof' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)'],
							'Atari_Jaguar_ZachMorris' : ['RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)'],
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'Atari_ST_ZachMorris' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'Atari_ST_ZachMorris_Full' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Colecovision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Colecovision_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_Bestof_ZachMorris' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'MAME_ZachMorris' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'MAME_2003_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2014_ZachMorris' : ['RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)'],
							'MAME_AKNF_Full' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'NES_Bestof_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							# 'PS1_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris_Full' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris' : ['hidden','hidden','hidden'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'x68000_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'x68000_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Intellivision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_800_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_5200_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Vectrex_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_CHD_ZachMorris' : ['hidden','hidden','hidden'], #Superceded with MAME2014
							# 'MAME_2010_ZachMorris' : ['RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)'],
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							},
			'LibreElec SX05' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['RetroArch 4DO (3DO)','RetroArch 4DO (3DO)','RetroArch 4DO (3DO)'],
							'Amiga_CD32_Full' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Full_ZRL' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Amiga_Bestof' : ['FS-UAE Launcher','FS-UAE Launcher','FS-UAE Launcher'],
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)'],
							'Atari_Jaguar_ZachMorris' : ['RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)'],
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'Atari_ST_ZachMorris' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'Atari_ST_ZachMorris_Full' : ['RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)','RetroArch Hatari (Atari ST/STE/TT/Falcon)'],
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Colecovision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Colecovision_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_Bestof_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_2003_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2014_ZachMorris' : ['RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)'],
							'MAME_AKNF_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'NES_Bestof_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							# 'PS1_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris_Full' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris' : ['hidden','hidden','hidden'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'x68000_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'x68000_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Intellivision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_800_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_5200_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Vectrex_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_CHD_ZachMorris' : ['hidden','hidden','hidden'], #Superceded with MAME2014
							# 'MAME_2010_ZachMorris' : ['RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)'],
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							},
			'RPi Gamestarter Addon' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['hidden','hidden','hidden'], #4DO core not available
							'Amiga_CD32_Full' : ['hidden','hidden','hidden'],
							'Amiga_Full_ZRL' : ['hidden','hidden','hidden'],
							'Amiga_Bestof' : ['hidden','hidden','hidden'],
							'Apple2GS_ZachMorris' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'Apple2GS_ZachMorris_Full' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'Atari_800_ZachMorris' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'Atari_5200_ZachMorris' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['hidden','hidden','hidden'], #Prosystem currently crashes with Gamestarter
							'Atari_Jaguar_ZachMorris' : ['hidden','hidden','hidden'], #Virtual Jaguar core not available
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'Atari_ST_ZachMorris' : ['hidden','hidden','hidden'], #Hatari core not available
							'Atari_ST_ZachMorris_Full' : ['hidden','hidden','hidden'], #Hatari core not available
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Colecovision_ZachMorris' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'Colecovision_ZachMorris_Full' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Intellivision_ZachMorris' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_CHD_ZachMorris' : ['hidden','hidden','hidden'],  #RPi MAME is limited to 2003 / 2010
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],  #Need to rescrape 2010
							'MAME_Bestof_ZachMorris' : ['hidden','hidden','hidden'], #RPi MAME is limited to 2003 / 2010
							'MAME_2003_Bestof_ZachMorris' : ['RetroArch MAME 2003 (Arcade 0.78)','RetroArch MAME 2003 (Arcade 0.78)','RetroArch MAME 2003 (Arcade 0.78)'],
							'MAME_2014_ZachMorris' : ['hidden','hidden','hidden'], #RPi MAME is limited to 2003 / 2010
							'MAME_AKNF_Full' : ['hidden','hidden','hidden'], #RPi MAME is limited to 2003 / 2010
							'MAME_ZachMorris' : ['hidden','hidden','hidden'], #RPi MAME is limited to 2003 / 2010
							'MAME_2003_ZachMorris' : ['RetroArch MAME 2003 (Arcade 0.78)','RetroArch MAME 2003 (Arcade 0.78)','RetroArch MAME 2003 (Arcade 0.78)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch fMSX (MSX)','RetroArch fMSX (MSX)','RetroArch fMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Glupen64 (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Glupen64 (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Glupen64 (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'NES_Bestof_ZachMorris' : ['RetroArch QuickNES (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch QuickNES (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch QuickNES (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Dreamcast_ZachMorris' : ['hidden','hidden','hidden'], #Core not available
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9xNext (SNES)','RetroArch SNES9xNext (SNES)','RetroArch SNES9xNext (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9x 2005 (SNES)','RetroArch SNES9x 2005 (SNES)','RetroArch SNES9x (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9x 2005 (SNES)','RetroArch SNES9x 2005 (SNES)','RetroArch SNES9x (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Vectrex_ZachMorris' : ['RetroArch VECX (Vectrex)','RetroArch VECX (Vectrex)','RetroArch VECX (Vectrex)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'x68000_ZachMorris' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'x68000_ZachMorris_Full' : ['hidden','hidden','hidden'], #MAME/MESS core not available
							'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'ZX_Spectrum_ZachMorris_Full' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							},
			'OpenElec RPi (Mezo/lollo78 Addon)' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['RetroArch 4DO (3DO)','RetroArch 4DO (3DO)','RetroArch 4DO (3DO)'],
							'Amiga_CD32_Full' : ['RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)'],
							'Amiga_Full_ZRL' : ['RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)'],
							'Amiga_Bestof' : ['RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)'],
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)'],
							'Atari_Jaguar_ZachMorris' : ['RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)'],
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Colecovision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Colecovision_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch gpSP (GBA)','RetroArch gpSP (GBA)','RetroArch gpSP (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch gpSP (GBA)','RetroArch gpSP (GBA)','RetroArch gpSP (GBA)'],
							'GBA_ZachMorris' : ['RetroArch gpSP (GBA)','RetroArch gpSP (GBA)','RetroArch gpSP (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_Bestof_ZachMorris' : ['RetroArch MAME 2003 (Arcade 0.78)','RetroArch MAME 2003 (Arcade 0.78)','RetroArch MAME 2003 (Arcade 0.78)'],
							'MAME_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_ZachMorris' : ['RetroArch MAME 2003 (Arcade 0.78)','RetroArch MAME 2003 (Arcade 0.78)','RetroArch MAME 2003 (Arcade 0.78)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['RetroArch iMAME4All (Arcade)','RetroArch iMAME4All (Arcade)','RetroArch iMAME4All (Arcade)'],
							'NES_Bestof_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							# 'PS1_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris_Full' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris' : ['hidden','hidden','hidden'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9xNext (SNES)','RetroArch SNES9xNext (SNES)','RetroArch SNES9xNext (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9xNext (SNES)','RetroArch SNES9xNext (SNES)','RetroArch SNES9xNext (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9xNext (SNES)','RetroArch SNES9xNext (SNES)','RetroArch SNES9xNext (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'x68000_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'x68000_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Intellivision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_800_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_5200_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Vectrex_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_CHD_ZachMorris' : ['hidden','hidden','hidden'],
							# 'MAME_2010_ZachMorris' : ['RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)'],
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							},
			'Android' : { '32X_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'3DO_ZachMorris' : ['RetroArch 4DO (3DO)','RetroArch 4DO (3DO)','RetroArch 4DO (3DO)'],
							'Amiga_CD32_Full' : ['RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)'],
							'Amiga_Full_ZRL' : ['RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)'],
							'Amiga_Bestof' : ['RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)','RetroArch PUAE (Amiga)'],
							'Atari_2600_Bestof_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris_Full' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_2600_ZachMorris' : ['RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)','RetroArch Stella (Atari 2600)'],
							'Atari_7800_ZachMorris' : ['RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)','RetroArch ProSystem (Atari 7800)'],
							'Atari_Jaguar_ZachMorris' : ['RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)','RetroArch Virtual Jaguar (Jaguar)'],
							'Atari_Lynx_ZachMorris' : ['RetroArch Handy (Lynx)','RetroArch Handy (Lynx)','RetroArch Mednafen Lynx (Lynx)'],
							'C64_ZachMorris' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'C64_ZachMorris_Full' : ['RetroArch VICE (C64)','RetroArch VICE (C64)','RetroArch VICE (C64)'],
							'Colecovision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Colecovision_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Game_Gear_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Game_Gear_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'GB_Classic_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GB_Classic_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBA_Bestof_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris_Full' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBA_ZachMorris' : ['RetroArch mGBA (GBA)','RetroArch mGBA (GBA)','RetroArch mGBA (GBA)'],
							'GBC_ZachMorris_Full' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'GBC_ZachMorris' : ['RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)','RetroArch Gambatte (GB/GBC)'],
							'Genesis_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Genesis_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'IA_MSDOS_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'Magnavox_O2_ZachMorris' : ['RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)','RetroArch O2EM (Odyssey2/Videopac)'],
							'MAME_Bestof_ZachMorris' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'MAME_ZachMorris' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'MAME_2003_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2003_ZachMorris' : ['hidden','hidden','hidden'],
							'MAME_2014_ZachMorris' : ['RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)','RetroArch MAME 2014 (Arcade 0.159)'],
							'MAME_AKNF_Full' : ['RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)','RetroArch MAME 2016 (Arcade 0.174)'],
							'Master_System_Bestof_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Master_System_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'MSX_ZachMorris' : ['RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)','RetroArch BlueMSX (MSX)'],
							'N64_Bestof_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'N64_ZachMorris_Full' : ['RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)','RetroArch Mupen64Plus (N64)'],
							'Neo_Geo_CD_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'NES_Bestof_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NES_ZachMorris_Full' : ['RetroArch Nestopia (NES)','RetroArch Nestopia (NES)','RetroArch Nestopia (NES)'],
							'NGPC_ZachMorris' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'NGPC_ZachMorris_Full' : ['RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)','RetroArch Mednafen NeoPop (NGP/NGPC)'],
							'PCE_CD_ZachMorris': ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'Point_and_Click_Bestof_ZachMorris' : ['RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)','RetroArch DOSBox (DOS)'],
							'PS1_Bestof_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris_Full' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							'PS1_ZachMorris' : ['RetroArch PCSX ReArmed (PS1)','RetroArch PCSX ReArmed (PS1)','RetroArch Mednafen PSX (PS1)'],
							# 'PS1_Bestof_ZachMorris' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris_Full' : ['hidden','hidden','hidden'],
							# 'PS1_ZachMorris' : ['hidden','hidden','hidden'],
							'Sega_CD_ZachMorris' : ['RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)','RetroArch PicoDrive (SMS/Gen/Sega CD/32X)'],
							'Sega_Saturn_ZachMorris' : ['RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)','RetroArch Yabuse (Saturn)'],
							'Sega_SG1000_ZachMorris' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'Sega_SG1000_ZachMorris_Full' : ['RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)','RetroArch Genesis Plus GX (GG/SMS/Gen/PICO/SG-1000)'],
							'SNES_Bestof_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'SNES_ZachMorris_Full' : ['RetroArch SNES9x (SNES)','RetroArch BSNES Mercury Balanced (SNES)','RetroArch BSNES Mercury Accuracy (SNES)'],
							'TG16_Bestof_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris_Full' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'TG16_ZachMorris' : ['RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)','RetroArch Mednafen PCE FAST (PCE/TG16)'],
							'ZX_Spectrum_ZachMorris' : ['RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)','RetroArch FUSE (Spectrum)'],
							'x68000_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'x68000_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Apple2GS_ZachMorris_Full' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Intellivision_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_800_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Atari_5200_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'Vectrex_ZachMorris' : ['RetroArch MAME (Arcade)','RetroArch MAME (Arcade)','RetroArch MAME (Arcade)'],
							'MAME_CHD_ZachMorris' : ['hidden','hidden','hidden'], #Superceded with MAME2014
							# 'MAME_2010_ZachMorris' : ['RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)','RetroArch MAME 2010 (Arcade 0.139)'],
							'MAME_2010_ZachMorris' : ['hidden','hidden','hidden'],
							'FBA_ZachMorris' : ['RetroArch FBA (Arcade)','RetroArch FBA (Arcade)','RetroArch FBA (Arcade)'],
							'SCUMMVM_ZachMorris' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'SCUMMVM_ZachMorris_Full' : ['RetroArch ScummVM (Various)','RetroArch ScummVM (Various)','RetroArch ScummVM (Various)'],
							'Wonderswan_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Wonderswan_Color_ZachMorris' : ['RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)','RetroArch Mednafen Cygne (WonderSwan/WonderSwan Color)'],
							'Quake_Lefty420' : ['RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)','RetroArch TyrQuake (Other)'],
							'Doom_Lefty420' : ['RetroArch PrBoom (Other)','RetroArch PrBoom (Other)','RetroArch PrBoom (Other)'],
							'Cavestory_Lefty420' : ['RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)','RetroArch CaveStory (NXEngine)'],
							'Dinothawr_Lefty420' : ['RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)','RetroArch Dinothawr (Other)'],
							},
            }

try:
	parserfile = os.path.join(addon.getAddonInfo('path'),'resources','data','external_launcher_parser.xml')
	launchersfile = os.path.join(addon.getAddonInfo('path'),'resources','data','external_command_database.xml')
	descParser = DescriptionParserFactory.getParser(parserfile)
	results = descParser.parseDescription(launchersfile,'xml')
except:
	xbmc.log(msg='IARL:  Wizard could not find the external launch database.', level=xbmc.LOGDEBUG)
# print results[0]

current_dialog = xbmcgui.Dialog()
not_ready = False
not_ready_reason = 'See Debug Log.'

if 'Select' in wizard_data['settings']['iarl_wizard_launcher_group']:
	# ok_ret = current_dialog.ok('Setup not ready','Please select a setup type[CR]Then hit OK to save your settings and try again.')
	not_ready_reason = 'Please select (Playable/Accurate/Balanced)[CR]Then hit OK to close & save addon settings and try again.'
	not_ready = True

# Select|OSX|Windows|Linux/Kodibuntu|OpenElec x86 (tssemek Addon)|RPi Gamestarter Addon|Android
if not not_ready:
	if 'Select' in wizard_data['settings']['iarl_external_user_external_env']:
		# ok_ret = current_dialog.ok('Setup not ready','Please select your system type[CR]Then hit OK to save your settings and try again.')
		not_ready_reason = 'Please select your system type[CR]Then hit OK to close & save addon settings and try again.'
		not_ready = True

if not not_ready:
	if 'OSX' in wizard_data['settings']['iarl_external_user_external_env'] or 'Windows' in wizard_data['settings']['iarl_external_user_external_env'] or 'Linux/Kodibuntu' in wizard_data['settings']['iarl_external_user_external_env']:
		if len(wizard_data['settings']['iarl_path_to_retroarch'])<1 and 'RetroPlayer' not in wizard_data['settings']['iarl_wizard_launcher_group']:
			# ok_ret = current_dialog.ok('External Program Warning','Path to retroarch must be set first.[CR]Then hit OK to save your settings and try again.')
			not_ready_reason = 'Path to retroarch must be set first.[CR]Then hit OK to close & save addon settings and try again.'
			not_ready = True
		if 'Disabled' in wizard_data['settings']['iarl_additional_emulator_1_type'] and 'Disabled' in wizard_data['settings']['iarl_additional_emulator_2_type']:
			dp.close()
			ret2 = current_dialog.select('Additional emulators for some archives are not setup, continue?', ['Yes','Cancel'])
			if ret2>0:
				not_ready = True
				not_ready_reason = 'Additional Emulators arent setup.[CR]User cancelled wizard.'

if not not_ready:
	try:
		group_index = 'Select|Most Playable (Least CPU Intensive)|Balanced|Most Accurate|RetroPlayer'.split('|').index(wizard_data['settings']['iarl_wizard_launcher_group'])
	except:
		group_index = None
		not_ready = True
		xbmc.log(msg='IARL:  Wizard group could not be defined', level=xbmc.LOGDEBUG)
		not_ready_reason = 'Please select (Playable/Accurate/Balanced)[CR]Then hit OK to close & save addon settings and try again.'

#Main script start
if not not_ready:
	xbmc.log(msg='IARL:  Wizard attempting to initialize userdata', level=xbmc.LOGDEBUG)
	try:
		initialize_userdata()
	except:
		xbmc.log(msg='IARL:  Unable to initialize userdata', level=xbmc.LOGERROR)
	if group_index < 4: #External Launching selected
		user_options = list()
		launch_command = list()
		new_launch_command = None
		xbmc.log(msg='IARL:  Wizard Script Started for external launching', level=xbmc.LOGNOTICE)
		if 'enabled' in wizard_data['settings']['iarl_external_launch_close_kodi'].lower():
			external_launch_database_os = wizard_data['settings']['iarl_external_user_external_env'] + ' Close_Kodi' #Look for launch commands to close Kodi
		else:
			external_launch_database_os = wizard_data['settings']['iarl_external_user_external_env']
		if wizard_data['settings']['iarl_external_user_external_env'] in 'OpenElec x86 (tssemek Addon)|RPi Gamestarter Addon|OpenElec RPi (Mezo/lollo78 Addon)|Android'.split('|'):
			external_launch_database_os = external_launch_database_os.replace(' Close_Kodi','') #By default, the above setups auto close Kodi, so there's only one list of launchers to choose from
		
		for entries in results:
			#Define the list of commands from the external database corresponding to the current environment
			if entries['operating_system'][0] == external_launch_database_os:
				user_options.append(entries['launcher'][0])
				launch_command.append(entries['launcher_command'][0])

		# initialize_userdata()
		userdata_xmldir = get_userdata_xmldir()
		userdata_subfolders, userdata_files = xbmcvfs.listdir(userdata_xmldir)

		dp = xbmcgui.DialogProgress()
		dp.create('IARL Wizard','Updating Settings','')
		dp.update(0)
		for ffiles in userdata_files:
			try:
				current_name = os.path.splitext(os.path.split(ffiles)[-1])[0]
			except:
				current_name = None
				xbmc.log(msg='IARL:  '+str(current_name)+' could not be found', level=xbmc.LOGDEBUG)
			try:
				current_key = wizard_data[wizard_data['settings']['iarl_external_user_external_env']][current_name][group_index-1]
			except:
				current_key = None
				xbmc.log(msg='IARL:  Wizard setting for '+str(current_name)+' could not be found', level=xbmc.LOGDEBUG)

			if current_key is not None:
				# print launch_command[user_options.index(current_key)]
				percent_complete = int((int(userdata_files.index(ffiles))*100)/int(len(userdata_files)))
				dp.update(percent_complete)
				xbmc.sleep(100)
				if dp.iscanceled():
					dp.close()
					raise
				if 'hidden' in current_key:
					try:
						arch_idx = archive_data['category_id'].index(current_name)
						current_emu_category = archive_data['emu_category'][arch_idx]
						if 'hidden' not in current_emu_category:
							new_xml_category = current_emu_category + ', hidden'
							update_xml_header(userdata_xmldir,ffiles,'emu_category',new_xml_category)
							xbmc.log(msg='IARL:  The listing for '+str(ffiles)+' was hidden with the Wizard', level=xbmc.LOGDEBUG)
						else:
							xbmc.log(msg='IARL:  The listing for '+str(ffiles)+' is already hidden', level=xbmc.LOGDEBUG)
					except:
						xbmc.log(msg='IARL:  The listing for '+str(ffiles)+' could not be hidden with the Wizard', level=xbmc.LOGDEBUG)
				else:
					try:
						update_xml_header(userdata_xmldir,ffiles,'emu_launcher','external')
					except:
						xbmc.log(msg='IARL:  emu_launcher command for '+str(ffiles)+' could not be set in Wizard', level=xbmc.LOGDEBUG)
					try:
						update_xml_header(userdata_xmldir,ffiles,'emu_ext_launch_cmd',launch_command[user_options.index(current_key)])
						xbmc.log(msg='IARL:  '+str(ffiles)+' new command: '+str(launch_command[user_options.index(current_key)]), level=xbmc.LOGDEBUG)
					except:
						xbmc.log(msg='IARL:  emu_ext_launch_cmd for '+str(ffiles)+' could not be set in Wizard', level=xbmc.LOGDEBUG)
	else: #Retroplayer Launching selected
		xbmc.log(msg='IARL:  Wizard Script Started for RetroPlayer launching', level=xbmc.LOGNOTICE)

		# initialize_userdata()
		userdata_xmldir = get_userdata_xmldir()
		userdata_subfolders, userdata_files = xbmcvfs.listdir(userdata_xmldir)

		dp = xbmcgui.DialogProgress()
		dp.create('IARL Wizard','Updating Settings','')
		dp.update(0)
		for ffiles in userdata_files:
			percent_complete = int((int(userdata_files.index(ffiles))*100)/int(len(userdata_files)))
			dp.update(percent_complete)
			xbmc.sleep(100)
			if dp.iscanceled():
				dp.close()
				raise
			try:
				update_xml_header(userdata_xmldir,ffiles,'emu_launcher','retroplayer')
			except:
				xbmc.log(msg='IARL:  emu_launcher command for '+str(ffiles)+' could not be set in Wizard', level=xbmc.LOGDEBUG)

	clear_userdata_list_cache_dir()
	dp.close()
	ok_ret = current_dialog.ok('Complete','Wizard run completed!')
	xbmc.log(msg='IARL:  Wizard Script Completed', level=xbmc.LOGNOTICE)
else:
	xbmc.log(msg='IARL:  Wizard Script Cancelled or Setup Not Ready', level=xbmc.LOGNOTICE)
	xbmc.log(msg='IARL:  W_Setting Ext Env:  '+str(wizard_data['settings']['iarl_external_user_external_env']), level=xbmc.LOGDEBUG)
	xbmc.log(msg='IARL:  W_Setting Close Kodi:  '+str(wizard_data['settings']['iarl_external_launch_close_kodi']), level=xbmc.LOGDEBUG)
	xbmc.log(msg='IARL:  W_Setting RA Path:  '+str(wizard_data['settings']['iarl_path_to_retroarch']), level=xbmc.LOGDEBUG)
	xbmc.log(msg='IARL:  W_Setting RA CFG Path:  '+str(wizard_data['settings']['iarl_path_to_retroarch_cfg']), level=xbmc.LOGDEBUG)
	xbmc.log(msg='IARL:  W_Setting Launch Group:  '+str(wizard_data['settings']['iarl_wizard_launcher_group']), level=xbmc.LOGDEBUG)
	dp.close()
	ok_ret = current_dialog.ok('Setup not ready',not_ready_reason)