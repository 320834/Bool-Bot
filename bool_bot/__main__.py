import platform
import sys

from settings import DISCORD_DEV_KEY, DISCORD_PROD_KEY, DISCORD_CUSTOM_KEY


if platform.system() == "Windows":
    sys.path.append("C:\Python38\Lib\site-packages")



import index

if len(sys.argv) == 1:
    index.main(DISCORD_DEV_KEY)

if len(sys.argv) == 2:

    if(sys.argv[1] == "dev"):
        print("Using dev")
        index.main(DISCORD_DEV_KEY)
    elif(sys.argv[1] == "prod"):
        index.main(DISCORD_PROD_KEY)
    elif(sys.argv[1] == "custom"):
        print("Using custom")
        index.main(DISCORD_CUSTOM_KEY)
    else:
        print("Error: Please enter either dev, prod, or custom")
