from urllib.request import urlretrieve
import argparse
import requests
import traceback
import glob
import re
import os

class PaparDownloader:

    baseURL="https://api.papermc.io/v2/projects/paper/"
    backup_dir = './backups/server_jars'
    max_backups = 10

    def __init__(self, ver, update):
        if not ver:
            url, build_str = self.getLatestBuild()
        else:
            url, build_str = self.getBuild(ver)
        if url:
            if update:
                updateNeeded, old_build_str = self.checkForUpdate(build_str)
                if updateNeeded:
                    if self.downloadFile(url):
                        print(f"[INFO] Updated PaperMC! - {old_build_str} -> {build_str}")
                        self.manageBackups(old_build_str)
                elif old_build_str != "":
                    print(f"[INFO] PaperMC Up to date! - {build_str}")
            else:
                self.downloadFile(url)

    def manageBackups(self, old_build_str):
        max_backups = self.max_backups
        backup_dir = self.backup_dir
        os.rename(f"paper-{old_build_str}.jar", f"./backups/server_jars/paper-{old_build_str}.jar.bak")
        backup_pattern = os.path.join(backup_dir, 'paper-*.jar.bak')
        backup_files = glob.glob(backup_pattern)
        backup_files.sort(key=os.path.getmtime)
        if len(backup_files) > max_backups:
            to_delete = backup_files[:-max_backups]
            for file_path in to_delete:
                os.remove(file_path)
                print(f"[INFO] Deleted old backup: {file_path}")

    def checkForUpdate(self, build_str):
        old_build_str = ""
        try:
            pattern = re.compile(r'^paper-(\d+\.\d+\.\d+-\d+)\.jar$')
            for filename in os.listdir('.'):
                match = pattern.match(filename)
                if match:
                    old_build_str = match.group(1)
            if old_build_str == "":
                print("[WARN] No old version found!")
                return False, old_build_str
        except:
            display_error(self, "[WARN] No old version found!")
            return False, old_build_str

        def parse_version(v):
            main, build = v.split('-')
            parts = list(map(int, main.split('.')))
            parts.append(int(build))
            return parts

        return parse_version(old_build_str) < parse_version(build_str), old_build_str

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
            build_number = str(response["builds"][-1])
            build_str = f"{ver}-{build_number}"
            package_URL += build_number
            response = requests.get(package_URL).json()
            package_URL += downloads_prefix
            package_URL += response["downloads"]["application"]["name"]
            return package_URL, build_str
        except:
            self.display_error("[ERROR] API Call Failed, Download Aborted.")
            return None, ""

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
    parser = argparse.ArgumentParser(description="Download PaperMC Server")
    parser.add_argument("--ver", type=str, help="Version to download.")
    parser.add_argument("--update", action='store_true', help="skip download if already up to date.")
    args = parser.parse_args()

    if args.update:
        update = True
    else:
        update = True

    if args.ver:
        ver = args.ver
    else:
        ver = None
    PaparDownloader(ver, update)
