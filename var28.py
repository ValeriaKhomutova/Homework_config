import os
import xml.etree.ElementTree as ET
import zipfile
from calendar import TextCalendar
from datetime import datetime, timedelta
import io
import toml
import time


class ShellEmulator:
    def __init__(self, config_path):
        """
        Initializes the ShellEmulator object from a configuration file.
        :param config_path: Path to the configuration file
        :type config_path: str
        """
        self.config = self.load_config(config_path)
        self.username = self.config["user"]["name"]
        self.computer_name = self.config["user"]["computer"]
        self.fs_zip_path = self.config["paths"]["vfs"]
        self.log_file = self.config["paths"]["log"]
        self.start_script = self.config["paths"]["start_script"]
        self.parametr = self.config["user"]["parametr"]
        self.current_path = "/"
        self.vfs = {}
        self.hist = []
        self.start = time.time()
        self.start_ = datetime.now()
        self.load_vfs()
        self.create_log_file()
        self.run_start_script()

    def load_config(self, config_path: str) -> dict:
        """
        Loads the configuration from the given file path.

        :param config_path: Path to the configuration file
        :type config_path: str
        :return: The loaded configuration
        :rtype: dict
        """
        with open(config_path, "r") as f:
            return toml.load(f)

    def load_vfs(self):
        """
        Loads the virtual file system from the zip file at the given path.

        :raises UnicodeDecodeError: If a file cannot be decoded as UTF-8
        """
        with zipfile.ZipFile(self.fs_zip_path, "r") as zip_ref:
            for file in zip_ref.namelist():
                normalized_path = os.path.join("/", file)  # Ensure paths start with '/'
                try:
                    # Try to decode as UTF-8
                    self.vfs[normalized_path] = zip_ref.read(file).decode("utf-8")
                except UnicodeDecodeError:
                    # If decoding fails, store the raw binary data or skip the file
                    print(f"Warning: Unable to decode {file}. Storing as binary.")
                    self.vfs[normalized_path] = zip_ref.read(
                        file
                    )  # Store binary data without decoding

    def create_log_file(self):
        """
        Initializes the log file. Creates an XML file with a root 'session' element.
        Then logs the 'session_start' action.
        """
        root = ET.Element("session")
        self.log_tree = ET.ElementTree(root)
        self.log_action("session_start")

    def log_action(self, action, user=None):
        """
        Logs an action in the log file.

        :param action: The action to log
        :type action: str
        :param user: The user who performed the action, defaults to self.username
        :type user: str, optional
        """
        if user is None:
            user = self.username
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        root = self.log_tree.getroot()
        entry = ET.SubElement(root, "action")
        ET.SubElement(entry, "user").text = user
        ET.SubElement(entry, "timestamp").text = timestamp
        ET.SubElement(entry, "command").text = action

    def save_log(self):
        """
        Saves the log to the file specified in the configuration.
        This method writes the XML log tree to the file specified in the
        configuration. The log tree is an ElementTree object containing all
        logged actions.
        :return: None
        """
        self.log_tree.write(self.log_file)

    def run_start_script(self):
        if os.path.exists(self.start_script) and self.start_script.endswith(".sh"):
            print(f"Running start script: {self.start_script}")
            with open(self.start_script, "r") as f:
                commands = f.readlines()
            for command in commands:
                command = command.strip()
                if command and not command.startswith("#"):  # Skip comments
                    print(f"Executing command from script: {command}")
                    self.execute(command)

    def prompt(self):
        return f"{self.username}@{self.computer_name}:{self.current_path}$ "

    def execute(self, command):
        if command.startswith("cd "):
            self.cd(command[3:])
            self.hist.append(command)
        elif command.startswith("ls"): # 1
            if len(command) == 2:
                self.ls()
            else:
                self.ls_args(command[3:])
            self.hist.append(command)
        elif len(command) > 3 and command[2:] == "ls":
            self.ls()
        elif command == "exit":
            self.exit_shell()
            self.hist.append(command)
        elif command == "whoami":
            self.whoami()
            self.hist.append(command)
        elif command == "tree":
            self.tree(self.current_path)
            self.hist.append(command) 
        elif command =="pwd":
            self.pwd()
            self.hist.append(command)
        elif command == "history":
            self.history()
            self.hist.append(command)
        elif command == "uptime":
            self.uptime()
            self.hist.append(command)
        else:
            print(f"Command not found: {command}")
        self.log_action(command)

    def history(self):
        for command in self.hist:
            print(command)
            
    def pwd(self):
        print(self.current_path)

    def uptime(self): 
        print(datetime.now().strftime("%H:%M:%S"))
        end = time.time() - self.start
        time_format = time.strftime("%H:%M:%S", time.gmtime(end))
        print(time_format)
        print("1 user")
        '''#22:20:33 up 620 days, 22:37,  1 user,  load average: 0.03, 0.10, 0.10
        #22:20:33 — Текущее системное время.
        #up 620 days, 22:37 — Продолжительность работы системы.
        #1 user — количество вошедших в систему пользователей.
        #load average: 0.03, 0.10, 0.10 — load average: 0.03, 0.10, 0.10 системы за последние 1, 5 и 15 минут.
'''
    def cd(self, path):
        #print(self.vfs)    
        if path == "..":
            if self.current_path != '/':
                # os.path.dirname - возвращает имя директории по указанному пути
                self.current_path = os.path.dirname(self.current_path.rstrip('/'))
                print(f"Перешли на уровень выше: '{self.current_path}'")
        else:
            path_prefix = (
            path
            if path.endswith("/")
            else "/" + path + "/"
            )
            if path_prefix in self.vfs and self.current_path + path + "/" in self.vfs:
                self.current_path = self.current_path + path + "/"
            else:
                print(f"No such directory: {path}")

    def ls(self):
        contents = set()
        path_prefix = (
            self.current_path
            if self.current_path.endswith("/")
            else self.current_path + "/"
        )

        # Gather all files and directories that are within the current directory
        for file in self.vfs:
            if file.startswith(path_prefix):
                sub_path = file[len(path_prefix) :].split("/")[
                    0
                ]  # Get the first directory level
                contents.add(sub_path)

        # Print unique entries (files/directories)
        print("\n".join(sorted(contents)))


    def cd_l(self):
        if self.current_path != '/':
                # os.path.dirname - возвращает имя директории по указанному пути
                self.current_path = os.path.dirname(self.current_path.rstrip('/'))

    def ls_args(self,path):
            contents = set()
            self.cd(path)
            path_prefix = (
                self.current_path
                if self.current_path.endswith("/")
                else self.current_path + "/"
            )
            for file in self.vfs:
                if file.startswith(path_prefix):
                    sub_path = file[len(path_prefix) :].split("/")[
                        0
                    ]  # Get the first directory level
                    contents.add(sub_path)

            # Print unique entries (files/directories)
            self.cd_l()
            print("\n".join(sorted(contents)))


    def tree(self, path, indent=""):
        # Ensure the current path ends with a '/'
        path_prefix = path if path.endswith("/") else path + "/"
        printed_dirs = set()

        for file in sorted(self.vfs):
            if file.startswith(path_prefix):
                relative_path = file[len(path_prefix) :]
                if "/" in relative_path:
                    # This means it's a directory
                    first_dir = relative_path.split("/")[0]
                    if first_dir not in printed_dirs:
                        print(f"{indent}{first_dir}/")
                        printed_dirs.add(first_dir)
                        # Recursively call tree for the subdirectory
                        self.tree(os.path.join(path, first_dir), indent + "  ")
                else:
                    # It's a file, print it
                    print(f"{indent}{relative_path}")

    def whoami(self):
        print(self.username)
    

    def exit_shell(self):
        self.log_action("session_end")
        self.save_log()
        print("Exiting...")
        exit()

    def run(self):
        """
        Runs the shell emulator in an infinite loop.

        This method repeatedly prompts the user with a shell prompt and
        executes the entered command. The loop continues until the user
        manually exits the shell.
        """
        while True:
            command = input(self.prompt())
            self.execute(command)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python shell_emulator.py <config.toml>")
        sys.exit(1)

    config_path = sys.argv[1]
    shell = ShellEmulator(config_path)
    shell.run()
