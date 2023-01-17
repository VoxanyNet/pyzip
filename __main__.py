import os
import zipapp
import sys
import shutil
import uuid
import subprocess
import logging
import argparse

import tomlkit as toml
import pipreqs

parser = argparse.ArgumentParser(
    prog = "PyZip",
    description = "Easily package python applications to .pyz archive",
)

parser.add_argument("-o", "--output-dir", dest="output_dir", default=".")
parser.add_argument("-p", "--package-dir", dest="package_dir", default=".")

if not os.path.exists("/tmp/pyzip"):
    os.mkdir("/tmp/pyzip")

output_directory = parser.output_dir
package_name = paser.package_dir

# load local config file if exists
with open(".pyzip", "r") as file:
    

print(f"Generating archive for {package_directory}\n")

# make a temporary copy of the package so that we don't pollute
# the user's actual package with requirements.txt packages
temp_directory = shutil.copytree(package_directory, f"/tmp/pyzip/{str(uuid.uuid4())}")

# we dont want to include the "pyzip" directory in the archive, so we delete it from the temp directory
if os.path.exists(f"{temp_directory}/pyzip"):
    shutil.rmtree(f"{temp_directory}/pyzip")

bundle_packages_resp = input("Bundle requirements.txt packages? (Y/n) ")

match bundle_packages_resp.lower():
    
    # DO bundle pip packages
    case "y" | "yes" | "":
        
        autogen_resp = input("Generate requirements.txt? (Y/n) ")

        match autogen_resp.lower():

            # DO autogen requirements
            case "y" | "yes" | "":

                # overwrite existing requirements.txt
                subprocess.run("pipreqs --force", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            
            # DONT autogen requirements
            case "n" | "no":

                pass 

            case _:
                print(f"Invalid response '{autogen_resp}'")

                sys.exit()

        if not os.path.exists("requirements.txt"):
            
            print("Missing requirements.txt file")

            sys.exit()

        subprocess.run(f"pip install -r requirements.txt --target {temp_directory}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    case "n" | "no":

        pass

    case _:
        print(f"Invalid response '{bundle_packages_resp}'")

        sys.exit()

if not os.path.exists("pyzip"):
    os.mkdir("pyzip")

zipapp.create_archive(temp_directory, f"{package_directory}/pyzip/{package_name}.pyz", "/usr/bin/env python3")

shutil.rmtree(temp_directory)

print(f"Succesfully packaged '{package_name}' to 'pyzip/{package_name}.pyz'")

        
        


    
            