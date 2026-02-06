"""
Setup script to build ConsistencyTracker.app
Run: python setup.py py2app
"""

from setuptools import setup

APP = ['ConsistencyApp.py']
DATA_FILES = []

OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,  # Add icon file path here if you have one
    'plist': {
        'CFBundleName': 'Consistency Tracker',
        'CFBundleDisplayName': 'Consistency Tracker',
        'CFBundleIdentifier': 'com.consistency.tracker',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # Makes it a menu bar app (no dock icon)
        'LSMinimumSystemVersion': '10.15',
        'NSHighResolutionCapable': True,
        'NSUserNotificationAlertStyle': 'alert',
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    name='Consistency Tracker',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
