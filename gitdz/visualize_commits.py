import os
import subprocess
from datetime import datetime
from typing import List, Tuple

import yaml
import xml.etree.ElementTree as ET
from graphviz import Digraph
from plantuml import PlantUML


def load_config_from_xml(config_file: str) -> dict:
    """
    Load configuration from an XML file.

    Args:
        config_file (str): Path to the XML configuration file.

    Returns:
        dict: Parsed configuration data as a dictionary.
    """
    tree = ET.parse(config_file)
    root = tree.getroot()
    
    # Преобразуем XML-данные в словарь
    config = {
        "repository_path": root.find("repository_path").text,
        "graph_output_path": root.find("graph_output_path").text,
        "since_date": root.find("since_date").text
    }
    
    return config

'''def load_config(config_file: str) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_file (str): Path to the YAML configuration file.

    Returns:
        dict: Parsed configuration data as a dictionary.
    """
    with open(config_file, "r") as file:
        return yaml.safe_load(file)'''


def get_commits(repo_path: str, since_date: str) -> List[Tuple[str, str]]:
    """
    Get a list of commits from the repository since the given date.

    Args:
        repo_path (str): Path to the git repository.
        since_date (str): Date string in a format accepted by 'git log --since', e.g., '2023-01-01'.

    Returns:
        List[Tuple[str, str]]: List of tuples where each tuple contains the commit hash and the commit date.

    Raises:
        Exception: If the git command fails.
    """
    git_command = [
        "git",
        "-C",
        repo_path,
        "log",
        "--pretty=format:%H %ct",
        "--since",
        since_date,
    ]
    result = subprocess.run(git_command, stdout=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Error running git command: {result.stderr}")

    commits = result.stdout.splitlines()
    commit_data = [
        (
            c.split()[0],
            datetime.utcfromtimestamp(int(c.split()[1])).strftime("%Y-%m-%d %H:%M:%S"),
        )
        for c in commits
    ]
    return commit_data[::-1]  # Reverse to have chronological order


def build_dependency_graph(commits: List[Tuple[str, str]]) -> Digraph:
    """
    Build a dependency graph for commits using Graphviz.

    Args:
        commits (List[Tuple[str, str]]): List of commit hashes and dates in chronological order.

    Returns:
        Digraph: A Graphviz Digraph object representing the commit dependencies.
    """
    dot = Digraph(comment="Git Commit Dependencies")

    for i, (commit, date) in enumerate(commits):
        dot.node(str(i), f"Commit: {commit}\nDate: {date}")
        if i > 0:
            dot.edge(str(i - 1), str(i))  # Connect commits in chronological order

    return dot


'''def save_graph(graph: Digraph, output_file: str) -> None:
    """
    Save the graph to a PNG file.

    Args:
        graph (Digraph): A Graphviz Digraph object to be saved.
        output_file (str): Path to the output PNG file without extension.

    Prints:
        Success message after saving the file.
    """
    graph.render(output_file, format="png")
    print(f"Success! The graph has been saved to {output_file}.png")'''
def save_graph(graph: Digraph, output_file: str) -> None:
    """
    Save the dependency graph in PlantUML format and generate the diagram.

    Args:
        graph (Digraph): The dependency graph to be saved.
        output_file (str): Path to the output file without extension.
    """
    plantuml_code = "@startuml\n"

    # Сохраняем узлы
    node_names = {}  # Для хранения отображения узлов
    '''for line in graph.body:
        if 'Commit' in line:
            # Извлекаем имя узла из строки вида 'node "Commit: abc123"'
            node_name = line.split('"')[1]  # Имя узла
            node_id = line.split(' ')[-1]  # ID узла (например, i)
            node_names[node_id] = node_name
            plantuml_code += f'node "{node_name}" as {node_id}\n'''
    # Сохраняем связи
    for line in graph.body:
        if 'Commit' in line:
            # Извлекаем имя узла из строки вида 'node "Commit: abc123"'
            node_name = line.split('"')[1]  # Имя узла
            node_id = line.split(' ')[-1][:-2]  # ID узла (например, i)
            node_names[node_id] = node_name
            #pl_code += f'node "{node_name}" as {node_id}\n'
            #plantuml_code += f'node "{node_name}" as {node_id}\n'
        if '->' in line:
            parts = line.split('->')
            tail = parts[0].strip()
            head = parts[1].strip()
            plantuml_code += f"{tail} --> {head} : {node_name}\n"
    plantuml_code += "@enduml"

    # Запись в файл
    with open(f"{output_file}.puml", "w") as f:
        f.write(plantuml_code)
    print(f"Graph saved in PlantUML format to {output_file}.puml")

    # Генерация диаграммы с использованием PlantUML
    plantuml_server = PlantUML(url='http://localhost:8080/img/')
    try:
        result = plantuml_server.processes(f"{output_file}.puml")
        print(f"Diagram generated from {output_file}.puml")
    except Exception as e:
        print(f"Failed to generate diagram: {str(e)}")
        if hasattr(e, 'content'):
            print(f"Response content: {e.content}")  # выводим содержимое ответа, если оно доступно
        else:
            print("Error without response content.")


def main(config_file: str) -> None:
    """
    Main function to generate the commit dependency graph.

    Args:
        config_file (str): Path to the YAML configuration file.
    """
    config_file = "config.xml"
    config = load_config_from_xml(config_file)
    repo_path = config["repository_path"]
    graph_output_path = config["graph_output_path"]
    since_date = config["since_date"]
    if not os.path.exists(repo_path):
        print(f"Error: Repository path '{repo_path}' does not exist.")
        return

    commits = get_commits(repo_path, since_date)

    if not commits:
        print(f"No commits found since {since_date}")
        return

    graph = build_dependency_graph(commits)
    save_graph(graph, graph_output_path)


if __name__ == "__main__":
    #config_file = "config.yaml"  # Path to your YAML configuration file

    config_file = "config.xml"
    main(config_file)