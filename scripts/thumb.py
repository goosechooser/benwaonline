import os
import sys
import subprocess
import platform
from benwaonline.util import make_thumbnail

if __name__ == '__main__':
    img = sys.argv[1]
    thumb_path = sys.argv[2]

    make_thumbnail(img, thumb_path)
    exit(0)
