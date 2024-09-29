from urllib.request import urlretrieve
import requests
import traceback
import os
import sys

class PaparDownloader:
    
    baseURL="https://api.papermc.io/v2/projects/paper/"

    def __init__(self, ver):
        if not ver:
            url = self.getLatestBuild()
        else:
            url = self.getBuild(ver)
        if url:
            self.downloadFile(url)

    def getLatestBuild(self):
        print("[INFO] Getting latest build.")
        try:
            response = requests.get(self.baseURL).json()
            return self.getBuild(response["versions"][-1])
        except:
            self.display_error("[ERROR] API Call Failed, Download Aborted.")
            return None

    def getBuild(self, ver):
        versions_prefix="versions/"
        builds_prefix = "/builds/"
        downloads_prefix = "/downloads/"
        package_URL = self.baseURL + versions_prefix + ver
        try:
            response = requests.get(package_URL).json()
            print("[INFO] Connected to API.")
            package_URL += builds_prefix
            package_URL += str(response["builds"][-1])
            response = requests.get(package_URL).json()
            package_URL += downloads_prefix
            package_URL += response["downloads"]["application"]["name"]
            return package_URL
        except:
            self.display_error("[ERROR] API Call Failed, Download Aborted.")
            return None

    def downloadFile(self, url):
        filename = os.path.basename(url)
        current_directory = os.getcwd()
        file_path = os.path.join(current_directory, filename)
        try:
            urlretrieve(url, file_path)
            print("[INFO] Downloaded Package.")
            return True
        except:
            self.display_error("[ERROR] Download Failed, Download Aborted.")
            return False

    def display_error(self, context):
        print("\n====================================================================================")
        print(context)
        print("Ah shit, here we go again.")
        print(traceback.format_exc())
        print("Hello User, you found a bug!")
        print("Please Report the error above: https://github.com/YourBoyRory/PaparMC-Downloader/issues")
        print("====================================================================================\n")


if __name__ == "__main__":
    try:
        ver = sys.argv[1]
    except:
        ver = None
    PaparDownloader(ver)
