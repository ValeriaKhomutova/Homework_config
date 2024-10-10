import os
import shutil
import tempfile
import zipfile
from datetime import datetime
import pytest
import toml
from var37 import ShellEmulator


@pytest.fixture
def temp_fs_zip():
    """Fixture to create a temporary zip file simulating a virtual file system."""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "vfs.zip")

    # Create some directories and files inside the zip
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr("1/1.txt", "File 1 content")
        zip_file.writestr("2/2.txt", "File 2 content")
        zip_file.writestr("/3/", "File 3 content")
        zip_file.writestr("4.txt", "text ready")
        zip_file.writestr("start.sh", "echo 'Start script'")

    yield zip_path

    shutil.rmtree(temp_dir)


@pytest.fixture
def config_file(temp_fs_zip):
    """Fixture to create a temporary config file."""
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, "config.toml")

    config = {
        "user": {"name": "admin", "computer": "admin", "parametr": "some_param"},
        "paths": {
            "vfs": temp_fs_zip,
            "log": os.path.join(temp_dir, "log.xml"),
            "start_script": os.path.join(temp_dir, "start.sh"),
        },
    }

    with open(config_path, "w") as config_file:
        toml.dump(config, config_file)

    yield config_path

    shutil.rmtree(temp_dir)


@pytest.fixture
def shell_emulator(config_file):
    """Fixture to initialize the shell emulator."""
    return ShellEmulator(config_file)


def test_ls(shell_emulator, capsys):
    """Test the 'ls' command."""
    shell_emulator.execute("ls")
    captured = capsys.readouterr()
    assert "1\n2\n3\n4.txt\nstart.sh\n" in captured.out


def test_tree(shell_emulator, capsys):
    """Test the 'tree' command."""
    shell_emulator.execute("tree")
    captured = capsys.readouterr()
    expected_output = """1/
  1.txt
2/
  2.txt
3/
  
4.txt
start.sh
"""

    assert expected_output in captured.out
def test_whoami(shell_emulator, capsys):
    """Test the 'whoami' command."""
    shell_emulator.execute("whoami")
    captured = capsys.readouterr()
    assert "admin" in captured.out


def test_exit(shell_emulator):
    """Test the 'exit' command."""
    with pytest.raises(SystemExit):
        shell_emulator.execute("exit")


def test_history(shell_emulator,capsys):
    shell_emulator.execute("history")
    captured = capsys.readouterr()
    assert "" in captured.out


def test_cd(shell_emulator,capsys):
    shell_emulator.load_vfs()
    shell_emulator.execute("cd 3")
    shell_emulator.execute("cd ..")
    captured = capsys.readouterr()
    assert "/3/" + '\n'+f"Перешли на уровень выше: '/'"+ '\n' == captured.out
    

def test_pwd(shell_emulator,capsys):
    shell_emulator.execute("pwd")
    captured = capsys.readouterr()
    assert "/" + '\n' == captured.out


def test_uptime(shell_emulator,capsys):
    dt1 =  datetime.now().strftime("%H:%M:%S") + "\n"
    shell_emulator.execute("uptime")
    captured = capsys.readouterr()
    assert dt1 +'00:00:00' + "\n" + "1 user" + '\n' == captured.out