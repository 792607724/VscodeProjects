# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['temp.py'],
             pathex=['/Users/cgt/VscodeProjects/Gooey_Python_GUI'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='temp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='sat_tool_icon.icns')
app = BUNDLE(exe,
             name='temp.app',
             icon='sat_tool_icon.icns',
             bundle_identifier=None)
