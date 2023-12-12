from setuptools import setup, find_packages

setup(
    name='TagMate',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4~=4.12.2',
        'rapidfuzz~=3.5.2',
        'Unidecode~=1.3.7',
        'customtkinter~=5.2.1',
        'tkhtmlview~=0.2.0',
        'PyYAML~=6.0.1',
        'tqdm~=4.66.1',
        'pandas~=2.1.4',
        'spotipy~=2.23.0',
        'python-dotenv~=1.0.0',
        'music-tag~=0.4.3',
        'packaging~=23.2'
    ],
    entry_points={
        'console_scripts': [
            'tagmate=TagMate.module:main',
        ],
    },
)
