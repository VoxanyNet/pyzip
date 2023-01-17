import os
import zipapp
import sys
import shutil
import uuid
import subprocess
import logging
import argparse
import pathlib

import tomlkit as toml
import pipreqs

parser = argparse.ArgumentParser(
    prog = "pyzip",
    description = "Easily package python applications to .pyz archive",
)

parser.add_argument("-p", "--package-dir", dest="package_dir", help="Directory that contains __main__.py file")
parser.add_argument("-o", "--output-path", dest="output_path", help="Path for .pyz file to saved to")
parser.add_argument("-c", "--gen-config", dest="gen_config", help="Generate local configuration file for directory", action="store_true")

args = parser.parse_args()

if not os.path.exists("/tmp/pyzip"):
    os.mkdir("/tmp/pyzip")

# generate user config file
if not os.path.exists(f"{pathlib.Path.home()}/.pyzip"):
    with open("/etc/pyzip.conf", "r") as file:
        default_config = file.read()
    
    with open(f"{pathlib.Path.home()}/.pyzip", "w") as file:
        file.write(default_config) 

# generate local configuration file for this directory
if args.gen_config:
    
    print("Generating configuration file '.pyzip' in this directory", end = "\n\n")
    
    with open(f"{pathlib.Path.home()}/.pyzip", "r") as file:
        user_config = toml.parse(file.read())

    # use /src folder as package directory if we can find one
    if os.path.exists("src/__main__.py"):
        use_src_resp = input("Found 'src' directory containing '__main__.py', set as package directory? (Y/n) ")
        
        match use_src_resp.lower():
            case "y" | "yes" | "":
                user_config["package_directory"] = "./src"

            case "n" | "no":
                print("Using working directory instead", end="\n\n")
            
            case _:
                print(f"Invalid response {use_src_resp}")

                sys.exit()

    with open(".pyzip", "w") as file:
        file.write(toml.dumps(user_config))

    print("Generated local config file")

    sys.exit()

# load local config file if it exists
if os.path.exists(".pyzip"):
    with open(".pyzip", "r") as file:
        config = toml.parse(file.read())

# use user config file if it doesnt exist
else: 
    with open(f"{pathlib.Path.home()}/.pyzip", "r") as file:
        config = toml.parse(file.read())

package_directory = config["package_directory"]

output_path = config["output_path"]

if args.package_dir:
    package_directory = args.package_dir

if args.output_path:
    output_path = args.output_path

if not os.path.exists(f"{package_directory}/__main__.py"):
    print("Cannot find entry point file '__main__.py' in package")
    
    sys.exit()

print(f"Generating archive for {os.path.abspath(package_directory)}\n")

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
                subprocess.run(f"pipreqs {package_directory} --force", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            
            # DONT autogen requirements
            case "n" | "no":

                pass 

            case _:
                print(f"Invalid response '{autogen_resp}'")

                sys.exit()

        if not os.path.exists(f"{package_directory}/requirements.txt"):
            
            print("Missing requirements.txt file")

            sys.exit()

        subprocess.run(f"pip install -r {package_directory}/requirements.txt --target {temp_directory}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    case "n" | "no":

        pass

    case _:
        print(f"Invalid response '{bundle_packages_resp}'")

        sys.exit()

if not os.path.exists("pyzip"):
    os.mkdir("pyzip")

try:
    zipapp.create_archive(temp_directory, output_path, "/usr/bin/env python3")

except FileNotFoundError:
    print(f"Could not find output directory {os.path.dirname(output_path)}")
    sys.exit()

shutil.rmtree(temp_directory)

print(f"Succesfully packaged to '{os.path.abspath(output_path)}'")

        
        


    
            