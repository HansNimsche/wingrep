"""Wingrep is a simple grep Linux-like program written for windows. You can use it to 
search for a given regex in files by specifying the extension and location, 
additionally you can scan folders recursively.

This project is written for educational purposes
"""

# /------------------------ IMPORTS ------------------------/
# /------ STANDART LIBS ------/
import os
import re
import sys
import codecs
from argparse import ArgumentParser
# /------ INTERNAL LIBS ------/
from colorama import Fore as Color

# /------------------------ CODE ------------------------/
class Wingrep:
    """This class contains all used functions"""
    def __init__(self, regex, dir, files, extensions, recursive=False, colored=False):
        """Class initial function"""
        self.regex = regex
        self.folder = dir
        self.files = files
        self.extensions = extensions
        self.recursive = recursive
        self.colored = colored
    
    def highlight_phrase(self, result_s):
        """Highlight sought phrase inside of result string"""
        # escape from all regex special characters
        forbidden_chars = ["\\", "$", "(", ")", ".", "?", "|", "{", "}", "[",
                            "]", "+", "*", "^"]
        sought_phrase = self.regex 
        for forb_c in forbidden_chars:
            sought_phrase = sought_phrase.replace(forb_c, "")
        highlighted = Color.GREEN + sought_phrase + Color.RESET # make phrase green
        result_s = result_s.replace(sought_phrase, highlighted)
        return result_s
            
    def list_appro_files(self, root_path, files):
        """List all appropriate files from given folder. If extensions are 
        given list only file which has one of those extensions"""
        listed_files = [os.path.join(root_path, f) for f in os.listdir(root_path) 
                        if os.path.isfile(os.path.join(root_path, f))]
        if self.extensions:
            listed_files = [f for f in listed_files 
                            if f.split(".")[-1] in self.extensions]
        return listed_files
    
    def open_files(self, listed_files):
        """Open the files and yield its object to prepare it for the next 
        searching function"""
        for file_ in listed_files:
            try: 
                with codecs.open(file_, "r", encoding="utf-8", errors="ignore") as f:
                    yield f
            except Exception as error:
                print(error, file=sys.stderr)
                exit(0)
                
    def search_in(self, file_object):
        """Search for the specified regex in the file and print result if found"""
        for line_num, line in enumerate(file_object.readlines()):
            line = line.replace("\n", "").replace("\r", "") # remove new line char
            if re.match(self.regex, line):
                result = f"~{os.path.abspath(file_object.name)}: {line} (line {line_num})"
                if self.colored:
                    result = self.highlight_phrase(result)
                print(result, file=sys.stdout)
                
    def walk(self):
        """Walk throught all folders starting in passed dir and yield files and 
        root path"""
        if os.path.exists(self.folder):
            for root_path, _, f_files in os.walk(self.folder):
                yield root_path, f_files
                if not self.recursive:
                    break
        else:
            print(f"[!e] Passed folder doesn't exist. Path: {self.folder}",
                  file=sys.stdout)
            exit(0)
                
    def wingrep(self):
        """Main function. In this function all behaviours are described"""
        for folder, files_ in self.walk():
            listed_files = self.list_appro_files(folder, files_)
            for file_o in self.open_files(listed_files=listed_files):
                self.search_in(file_o)

def parseArgs():
    """Parse passed arguments and return dictionary containing them"""
    parser = ArgumentParser()
    parser.add_argument("regex", type=str, help="Regular expression searched")
    parser.add_argument("-f", "--files", type=str, nargs="+",
                        help="Files for review")
    parser.add_argument("-e", "--extensions", type=str,
                        help="File extensions to review", default=[])
    parser.add_argument("-d", "--dir", type=str, help="Folder to be viewed",
                        default=".")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Search the folder recursively")
    parser.add_argument("-c", "--colored", action="store_true",
                        help="Highlight sought regex(!Don't use with pipe)")
    args = parser.parse_args()
    
    return vars(args)


if __name__ == "__main__":
    try:
        wingrep = Wingrep(**parseArgs())
        wingrep.wingrep()
    except InterruptedError:
        print("Program stopped...")
        exit(0)