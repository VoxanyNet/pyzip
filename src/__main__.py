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

DEFAULT_CONFIG = """
#directory that contains __main__.py file
package_directory = "."

# path for archive to be saved to
output_path = "./pyzip/archive.pyz"

# bundle requirements.txt packages into archive
bundle_requirements = false

# attempt to generate requirements.txt automatically
generate_requirements = false
"""

if not os.path.exists(".pyzip"):
    with open(".pyzip", "w") as file:
        file.write(DEFAULT_CONFIG)

with open(".pyzip", "r") as file:
    config = toml.parse(file.read())

parser = argparse.ArgumentParser(
    prog = "pyzip",
    description = "Easily package python applications to .pyz archive"
)

parser.add_argument(
    "-p", 
    "--package-directory", 
    dest="package_directory", 
    help="directory that contains __main__.py file",
    default=config["package_directory"]
)
parser.add_argument(
    "-o", 
    "--output-path", 
    dest="output_path", 
    help="path for archive to be saved to",
    default=config["output_path"]
)
parser.add_argument(
    "-b", 
    "--bundle-requirements", 
    dest="bundle_requirements", 
    help="bundle requirements.txt packages into archive", 
    action="store_true", 
    default=config["bundle_requirements"]
)
parser.add_argument(
    "-g", 
    "--generate-requirements", 
    dest="generate_requirements", 
    help="attempt to generate requirements.txt automatically", 
    action="store_true", 
    default=config["generate_requirements"]
)

args = parser.parse_args()

if not os.path.exists(f"{args.package_directory}/__main__.py"):
    print("Cannot find entry point file '__main__.py' in package")
    
    sys.exit()

print(f"Generating archive for {os.path.abspath(args.package_directory)}\n")

if not os.path.exists("/tmp/pyzip"):
    os.mkdir("/tmp/pyzip")
    
# make a temporary copy of the package so that we don't pollute
# the user's actual package with requirements.txt packages
temp_directory = shutil.copytree(args.package_directory, f"/tmp/pyzip/{str(uuid.uuid4())}")

# we dont want to include the "pyzip" directory in the archive, so we delete it from the temp directory
if os.path.exists(f"{temp_directory}/pyzip"):
    shutil.rmtree(f"{temp_directory}/pyzip")

if args.generate_requirements:

    # overwrite existing requirements.txt
    subprocess.run(
        f"pipreqs {args.package_directory} --force", 
        shell=True, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.STDOUT
    )

if args.bundle_requirements:

    if not os.path.exists(f"{args.package_directory}/requirements.txt"):
        
        print("Missing requirements.txt file")

        sys.exit(1)

    subprocess.run(
        f"pip install -r {args.package_directory}/requirements.txt --target {temp_directory}", 
        shell=True, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.STDOUT
    )

try:
    zipapp.create_archive(temp_directory, args.output_path, "/usr/bin/env python3")

except FileNotFoundError:
    print(f"Could not find output directory {os.path.dirname(args.output_path)}")

    sys.exit(1)

shutil.rmtree(temp_directory)

print(f"Succesfully packaged to '{os.path.abspath(args.output_path)}'")

        
        


    
            