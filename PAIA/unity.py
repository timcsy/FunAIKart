from datetime import datetime
import os
import platform
from typing import Dict, Union

from config import ENV, bool_ENV, int_ENV
from utils import get_dir_fileprefix

def get_unity_app(auto=None, basedir: str=None, windows: str=None, linux: str=None, macos: str=None, other: str=None, editor=False) -> Union[str, None]:
    if auto is None:
        # Choose the OS automatically, if is false, then use other path (with basedir)
        auto = bool_ENV('UNITY_APP_AUTO', True)
    if basedir is None:
        basedir = ENV.get('UNITY_APP_BASE_DIR', 'kart')
    if windows is None:
        windows = ENV.get('UNITY_APP_WINDOWS', 'Windows/kart.exe')
    if linux is None:
        linux = ENV.get('UNITY_APP_LINUX', 'Linux/kart.x86_64')
    if macos is None:
        macos = ENV.get('UNITY_APP_MACOS', 'macOS/kart.app')
    if other is None:
        other = ENV.get('UNITY_APP_OTHER', '')
    if editor is None:
        editor = bool_ENV('UNITY_USE_EDITOR', False)
    
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
        company = ENV.get('UNITY_CONFIG_COMPANY', 'PAIA')
    if product is None:
        product = ENV.get('UNITY_CONFIG_PRODUCT', 'kart')
    if basedir is None:
        basedir = ENV.get('UNITY_CONFIG_BASE_DIR', 'kart')
    
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

def prepare_recording(episode: int=None, enable: bool=None, recording_dir=None, filename=None, file_suffix='.mp4', width=None, height=None):
    # Assume episode starts from 0
    is_recording = False
    if enable is None:
        enable = bool_ENV('RECORDING_ENABLE', False)
    if enable:
        dirname, file_prefix = get_dir_fileprefix('RECORDING', base_dir_default='records', use_dir_default=True)
        if recording_dir is None:
            recording_dir = dirname
        if not os.path.isabs(recording_dir):
            recording_dir = os.path.join(os.getcwd(), recording_dir)
        if episode is None:
            is_recording = True
        else:
            period = int_ENV('RECORDING_PERIOD', 0)
            if period > 0:
                is_recording = episode % period == 0
            elif period == 0:
                expr = eval(ENV.get('RECORDING_EXPRESSION', ''))
                is_recording = expr(episode)
    if is_recording:
        if not filename is None:
            file_prefix, file_suffix = os.path.splitext(os.path.basename(filename))
        if not episode is None:
            file_prefix = f'{file_prefix}_{episode}'
        filename = file_prefix + file_suffix

        tmp_dir = os.path.join(get_unity_dir(), 'Records', datetime.now().strftime("%Y%m%d%H%M%S"))
        set_config('Records', tmp_dir)
        output_video_path = os.path.join(recording_dir, filename)

        if width is None:
            width = int_ENV('RECORDING_WIDTH', 960)
        if height is None:
            height = int_ENV('RECORDING_HEIGHT', 540)
        set_config('Screen', f'{width}x{height}')

        return tmp_dir, recording_dir, output_video_path
    else:
        set_config('Records', False)
        return None, None, None

def prepare_demo(episode: int=None, purename=None, enable: bool=None):
    # Assume episode starts from 0
    is_demo = False
    if enable is None:
        enable = bool_ENV('DEMO_ENABLE', False)
    if enable:
        if episode is None:
            is_demo = True
        else:
            period = int_ENV('DEMO_PERIOD', 0)
            if period > 0:
                is_demo = episode % period == 0
            elif period == 0:
                expr = eval(ENV.get('DEMO_EXPRESSION', ''))
                is_demo = expr(episode)
    if is_demo:
        if purename is None:
            purename = datetime.now().strftime("%Y%m%d%H%M%S")
        if not episode is None:
            purename = f'{purename}{episode}'
        
        set_config('Demo', purename)
        return purename
    else:
        set_config('Demo', False)
        return None


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
                size = f'{config["width"]}x{config["height"]}'
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