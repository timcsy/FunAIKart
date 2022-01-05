import config

def debug_print(*args, depth: int=2, **kwargs):
    if config.LOG >= depth or config.LOG < 0:
        print(*args, **kwargs)