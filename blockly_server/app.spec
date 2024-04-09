# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Function to recursively get all python files in a directory
def get_python_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                yield os.path.join(root, file)

# List of directories to include all Python files from
directories_to_include = ['app'] # Add your directories here

# Start with your specific Python files
python_files = ['run.py','config.py','extensions.py']

# Add all Python files from the specified directories
for directory in directories_to_include:
    python_files.extend(get_python_files(directory))



a = Analysis(
    python_files,
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('assets', 'assets'), ('static', 'static'),('translations', 'translations'), ('../lib', 'lib'),('app.ico','app.ico')],
    hiddenimports=[
        'engineio.async_drivers.threading',
                'pyzmq',
                'zmq',
                'coppeliasim_zmqremoteapi_client',
                'eventlet.hubs.epolls',
                'eventlet.hubs.kqueue',
                'eventlet.hubs.selects',
                'eventlet',
                'dns.dnssec',
                'dns.asyncbackend',
                'dns.asyncquery',
                'dns.asyncresolver',
                'dns.versioned',
                'dns.e164',
                'dns.namedict',
                'dns.tsigkeyring',
                'robot.roboclass',
                'pystray'
                 ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)



pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fossbot-app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='app.app',
    icon="app.ico",
    bundle_identifier=None,
)
