import sys
import unity
import os
import webbrowser

if __name__ == '__main__':
    print(unity.get_unity_dir())
    webbrowser.open('file:///' + unity.get_unity_dir())

    if sys.argv[1] == 'on':
        unity.set_config('Records', True)
        unity.set_config('Demo', True)
        unity.set_config('PickUps', True)
        unity.set_config('Screen', '960x540')
    else:
        unity.set_config('Records', False)
        unity.set_config('Demo', False)
        unity.set_config('PickUps', False)
        unity.set_config('Screen', False)