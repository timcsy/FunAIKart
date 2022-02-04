import os
import platform
from typing import Dict, Union

from config import ENV, to_bool

def get_unity_app(auto=None, basedir: str=None, windows: str=None, linux: str=None, macos: str=None, other: str=None, editor=False) -> Union[str, None]:
    if auto is None:
        auto = to_bool(ENV.get('UNITY_APP_AUTO'))
        if auto is None:
            auto = True
    if basedir is None:
        basedir = ENV.get('UNITY_APP_BASE_DIR') or 'kart'
    if windows is None:
        windows = ENV.get('UNITY_APP_WINDOWS') or 'Windows/kart.exe'
    if linux is None:
        linux = ENV.get('UNITY_APP_LINUX') or 'Linux/kart.x86_64'
    if macos is None:
        macos = ENV.get('UNITY_APP_MACOS') or 'macOS/kart.app'
    if other is None:
        other = ENV.get('UNITY_APP_OTHER') or ''
    if editor is None:
        editor = to_bool(ENV.get('UNITY_USE_EDITOR')) or False
    
    if editor:
        return None
    
    operating_system = platform.system()
    if not auto:
        file_relpath = other
    elif operating_system == 'Windows':
        file_relpath = windows
    elif operating_system == 'Linux':
        file_relpath = linux
    elif operating_system == 'Darwin':
        file_relpath = macos
    else:
        file_relpath = other
    
    if os.path.isabs(file_relpath):
        filepath = file_relpath
    else:
        filepath = os.path.abspath(os.path.join(basedir, file_relpath))
    return filepath

def get_unity_dir(company: str=None, product: str=None, basedir: str=None) -> str:
    if company is None:
        company = ENV.get('UNITY_CONFIG_COMPANY') or 'PAIA'
    if product is None:
        product = ENV.get('UNITY_CONFIG_PRODUCT') or 'kart'
    if basedir is None:
        basedir = ENV.get('UNITY_CONFIG_BASE_DIR') or 'kart'
    
    persistentDataPath = '.'

    operating_system = platform.system()
    if operating_system == 'Windows':
        persistentDataPath = os.path.join(os.path.expanduser("~"), 'AppData\LocalLow', company, product)
    elif operating_system == 'Linux':
        persistentDataPath = os.path.join(os.path.expanduser("~"), '.config/unity3d', company, product)
    elif operating_system == 'Darwin':
        persistentDataPath = os.path.join(os.path.expanduser("~"), 'Library/Application Support', company, product)

    dirpath = os.path.join(persistentDataPath, basedir)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath

def set_config(name: str, config=True, dirname: str=None) -> None:
    '''
    Call this function before running Unity
    '''
    if dirname is None:
        dirname = get_unity_dir()

    remove_config(name, dirname)

    disable = False
    default = False
    if config is None or config is False:
        disable = True
    elif not config or config is True:
        # For True, zero of any numeric type, or empty sequences and collections
        default = True
    
    # Cases for different config names
    if name == 'Demo':
        if default:
            config = '' # Using timestamp: <kart dir>/Demo/yyyymmddHHMMSS.demo as demo path
        if not disable and isinstance(config, str):
            write_config(name, config, dirname)
    elif name == 'Records':
        if default:
            config = '' # Using timestamp: <kart dir>/Records/yyyymmddHHMMSS as img audio folder path
        if not disable and isinstance(config, str):
            write_config(name, config, dirname)
    elif name == 'PickUps':
        # If is disable, then PickUps are disabled
        if default:
            config = '' # Do not set the random seed
        config = str(config) # Set the random seed for integers
        if not disable:
            write_config(name, config, dirname)
    elif name == 'Screen':
        if default:
            config = '' # Using default screen size (last time or 1024x768)
        if not disable:
            if isinstance(config, str):
                size = config
            if isinstance(config, Dict) and 'width' in config and isinstance(config['width'], int) and 'height' in config and isinstance(config['height'], int):
                size = str(config['width']) + 'x' + str(config['height'])
            if size:
                write_config(name, size, dirname)

def write_config(name: str, config: str, dirname: str=None) -> None:
    if dirname is None:
        dirname = get_unity_dir()
    
    config_file = os.path.join(dirname, name + '.config')
    with open(config_file, 'w') as fout:
        fout.write(config)

def remove_config(name: str, dirname: str=None) -> None:
    if dirname is None:
        dirname = get_unity_dir()
    
    try:
        os.remove(os.path.join(dirname, name + '.config'))
    except:
        pass