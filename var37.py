import os
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime

import toml


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
        elif command == "ls":
            self.ls()
        elif command == "exit":
            self.exit_shell()
        elif command == "whoami":
            self.whoami()
        elif command == "tree":
            self.tree(self.current_path)
        else:
            print(f"Command not found: {command}")
        self.log_action(command)

    def cd(self, path):
        if path in self.vfs:
            self.current_path = path
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

    def tree(self, path, indent=""):
        # Ensure the current path ends with a '/'
        path_prefix = path if path.endswith("/") else path + "/"

        # Track already printed directories to avoid recursion issues
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
