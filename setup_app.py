"""
py2app setup for Consistency Tracker
"""
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,
    'plist': {
        'CFBundleName': 'Consistency Tracker',
        'CFBundleDisplayName': 'Consistency Tracker',
        'CFBundleIdentifier': 'com.consistency.tracker',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSUIElement': False,
    },
    'packages': ['PyQt6'],
    'includes': [
        'PyQt6.QtWidgets',
        'PyQt6.QtCore', 
        'PyQt6.QtGui',
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
