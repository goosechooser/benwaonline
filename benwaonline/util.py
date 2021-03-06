"""
Contains any utility functions used by processors or the benwaonline frontend.
"""
import os
import subprocess
import platform

def make_thumbnail(img, thumb_path, thumb_size="150x150"):
    head, tail = os.path.split(img)
    thumb_path = os.path.join(thumb_path, tail)

    cmd = ['convert', img, '-strip', '-resize', thumb_size, thumb_path]
    if platform.system() == 'Windows':
        cmd[0] = 'magick'
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(e)
        exit(1)

    return