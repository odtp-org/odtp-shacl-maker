import typer 
import pandas as pd
import csv
from rdflib import (
    Graph,
    Literal,
    RDF,
    XSD,
    URIRef,
    Namespace,
    SH,
    RDFS,
)
import os
import yaml
from urllib.parse import quote
import itertools

"""
Module Name: SHACL-Maker
Author: [Your Name Here]
Description: This module provides functionality to generate RDF (Resource Description Framework) data using SHACL (Shapes Constraint Language) shapes based on structured information provided in CSV or YAML format.

Dependencies:
- typer: For creating command-line interfaces in Python.
- pandas: For data manipulation and analysis.
- rdflib: For working with RDF data.
- csv: For reading CSV files.
- os: For interacting with the operating system.
- yaml: For reading YAML files.
- urllib: For URL encoding.
- Set: For working with sets.

Usage:
This module can be used to generate RDF data by providing structured information in a CSV or YAML file format. It defines the following functions:

1. convert_to_variables(filename: str) -> dict[str, Set[str]]:
   Reads the CSV or YAML file and processes the data, returning a dictionary containing file paths as keys and sets of variable names as values.

2. create_triples(file_relative_path: str, file_description: str, variable_name: str, variable_alternative_labels: str, variable_description: str, variable_value_example: str, variable_type: str) -> None:
   Creates triples for file and variable metadata based on the provided parameters.

3. and_builder(variables: dict[str, set[str]]) -> list[str]:
   Constructs AND statements for the property shapes based on the provided dictionary of variables.

4. main(input_filename: str) -> None:
   Orchestrates the RDF generation process, taking the relative path to the input file containing structured information (either CSV or YAML).

Command-Line Interface:
This module also defines a command-line interface using Typer. It provides a command 'make_shacl' to generate SHACL shapes based on structured data provided in a CSV file.

Example Usage:
To generate SHACL shapes, run the module with the 'make_shacl' command followed by the path to the CSV file:
    python RDFGenerator.py make_shacl example_data.csv

Note: Ensure that all dependencies are installed before running the module.

For more details, refer to the function docstrings and the module implementation.
"""

shapes_graph = Graph()

# Prefixes used throughout the script
ODTP = Namespace("https://odtp.example.org/components/data/")
shapes_graph.bind("odtp", ODTP)

SD = Namespace("https://w3id.org/okn/o/sd#")
shapes_graph.bind("SD", SD)

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
shapes_graph.bind("skos", SKOS)

def figure_out_if_input_or_output(filename: str = "File") -> str:
    """Determines if the file is an input or output file based on the file path. 
    Only gets called on the non-yaml files (as those contain both).

    Parameters
    ----------
    file_path : str
        The relative path of the file.

    Returns
    -------
    str
        The type of the file (input or output).
    """
    if "input" in filename:
        return "InputFile"
    elif "output" in filename:
        return "OutputFile"
    else:
        return "File"
    
def convert_to_variables(filename: str) -> dict[str, set[str]]:
    """Takes a CSV or YAML structured file containing metadata about the required inputs of a ODTP component and converts each row/entry into variables to be used by create_triples function.

    Parameters
    ----------
    filename : str
        The name of the input file.

    Returns
    -------
    Dict[str, Set[str]]
        A dictionary containing file paths as keys and sets of variable names as values.
    """    
    with open(filename, "r") as file:
        file_extension = os.path.splitext(file.name)[1]
        
        if file_extension == ".csv":
            reader = csv.DictReader(file)
            files_variables = {}
            for row in reader:
                file_relative_path = row["file_relative_path"]
                file_description = row["file_description"]
                variable_name = row["variable_name"]
                variable_alternative_labels = row["variable_alternative_labels"].split(",") if row["variable_alternative_labels"] else []
                variable_description = row["variable_description"]
                variable_value_example = row["variable_value_example"]
                variable_type = row["variable_type"]

                if file_relative_path not in files_variables:
                    files_variables[file_relative_path] = set()
                files_variables[file_relative_path].add(variable_name)

                create_triples(file_relative_path, file_description, variable_name, variable_alternative_labels, variable_description, variable_value_example, variable_type)
        
        elif file_extension == ".yml":
            data = yaml.safe_load(file)
            files_variables = {}
            data_input = data.get("data-input", [])
            data_output = data.get("data-output", [])
            for entry in itertools.chain(data_input, data_output):
                file_relative_path = entry["file_relative_path"]
                file_description = entry["file_description"]
                
                if file_relative_path not in files_variables:
                    files_variables[file_relative_path] = set()
                
                for variable in entry.get("variables", []):
                    variable_name = variable["variable_name"]
                    variable_alternative_labels = variable["variable_alternative_labels"]
                    variable_description = variable["variable_description"]
                    variable_value_example = variable["variable_value_example"]
                    variable_type = variable["variable_type"]
                    
                    files_variables[file_relative_path].add(variable_name)

                    create_triples(file_relative_path, file_description, variable_name, variable_alternative_labels, variable_description, variable_value_example, variable_type)

        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    return files_variables


def create_triples(file_relative_path: str, file_description: str, variable_name: str, variable_alternative_labels: str, variable_description: str, variable_value_example: str, variable_type: str) -> None:
    """Creates triples for file and variable metadata.

    Parameters
    ----------
    file_relative_path : str
        Relative path of the file.
    file_description : str
        Description of the file.
    variable_name : str
        Name of the variable.
    variable_alternative_labels : str
        Alternative labels for the variable.
    variable_description : str
        Description of the variable.
    variable_value_example : str
        Example value of the variable.
    variable_type : str
        Type of the variable.
    """
    file_uri = ODTP[quote(file_relative_path)]

    variable_uri = URIRef(ODTP + variable_name + "Shape")
    # nodeshapes (for restricting files)
    shapes_graph.add((file_uri, RDF.type, SH.NodeShape))
    shapes_graph.add((file_uri, RDFS.subClassOf, ODTP.File))
    shapes_graph.add((file_uri, SH.targetNode, file_uri))
    shapes_graph.add((file_uri, SH.description, Literal(file_description, datatype=XSD.string)))
    
    # propertyshapes (for restricting variables)
    shapes_graph.add((variable_uri, RDF.type, SH.PropertyShape))
    shapes_graph.add((variable_uri, SH.datatype, URIRef(variable_type)))
    shapes_graph.add((variable_uri, SH.description, Literal(variable_description, datatype=XSD.string)))
    shapes_graph.add((variable_uri, SH.name, Literal(variable_name)))
    shapes_graph.add((variable_uri, SH.path, URIRef(ODTP + variable_name)))
    shapes_graph.add((variable_uri, SKOS.example, Literal(variable_value_example)))
    if type(variable_alternative_labels) == list:
        for label in variable_alternative_labels:
            shapes_graph.add((variable_uri, SKOS.altLabel, Literal(label)))
    else:
        shapes_graph.add((variable_uri, SKOS.altLabel, Literal(variable_alternative_labels)))


def and_builder(variables: dict[str, set[str]]) -> list[str]:
    """Constructs AND statements for the property shapes.

    Parameters
    ----------
    variables : Dict[str, Set[str]]
        Mapping from file paths to sets of variable names

    Returns
    -------
    List[str]
        template for ttl syntax nodeshapes with an sh:and to be filled.
    """
    prop_string_list = []
    for var in variables:
        prop_string = ""
        and_string = ""
        file_uri = URIRef(ODTP + var)

        for item in variables[var]:
            blank_node_item = f"[sh:path <https://w3id.org/okn/o/sd#hasParameter> ; sh:hasValue <https://odtp.example.org/components/data/{item}>]"
            and_string += f" {blank_node_item}"

        prop_string = f"<{file_uri}> sh:and ({and_string}) ."
        prop_string_list.append(prop_string)
    return prop_string_list


def main(input_filename: str) -> None:
    """Main function to orchestrate the RDF generation process.

    Parameters
    ----------
    input_filename : str
        The relative path to the file containing structured information (either csv or yml).
    """
    files_variables = convert_to_variables(input_filename)
    shapes_graph.serialize(destination="shapeswithoutand.ttl", format="turtle")
    with open("shapeswithoutand.ttl", "a") as file:
        for and_statement in and_builder(files_variables):
            file.write(and_statement + "\n")

    final_graph = Graph()
    final_graph.parse("shapeswithoutand.ttl", format="turtle")
    filename_without_extension = os.path.splitext(input_filename)[0]
    final_graph.serialize(destination=f"{filename_without_extension}.ttl", format="turtle")
    os.remove("shapeswithoutand.ttl")

app = typer.Typer()
@app.command()
def make_shacl(csv_file: str):
    main(csv_file)

if __name__ == "__main__":
    app()