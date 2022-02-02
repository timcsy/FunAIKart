import os
import platform
from typing import Dict, Tuple

def get_unity(basedir: str='kart', windows: str='Windows/kart.exe', linux: str='Linux/kart.x86_64', macos: str='macOS/kart.app', other: str=None, editor=False) -> Tuple[str, str]:
    if editor:
        return None, os.path.abspath('..')
    
    operating_system = platform.system()
    if operating_system == 'Windows':
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
    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return filepath, dirname

def set_config(name: str, config=True, dirname: str=None) -> None:
    '''
    Call this function before running Unity
    '''
    if dirname is None:
        _, dirname = get_unity()

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
        _, dirname = get_unity()
    
    config_file = os.path.join(dirname, name + '.config')
    with open(config_file, 'w') as fout:
        fout.write(config)

def remove_config(name: str, dirname: str=None) -> None:
    if dirname is None:
        _, dirname = get_unity()
    
    try:
        os.remove(os.path.join(dirname, name + '.config'))
    except:
        pass