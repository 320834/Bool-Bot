import platform
import sys

if platform.system() == "Windows":
    sys.path.append("C:\Python38\Lib\site-packages")

import index

index.main()
