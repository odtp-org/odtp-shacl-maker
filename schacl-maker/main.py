from typing import Dict, Set, List

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

shapes_graph = Graph()

# Prefixes used throughout the script
ODTP = Namespace("https://odtp.example.org/components/data/")
shapes_graph.bind("odtp", ODTP)

SD = Namespace("https://w3id.org/okn/o/sd#")
shapes_graph.bind("SD", SD)

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
shapes_graph.bind("skos", SKOS)


def read_and_process_file(filename: str) -> Dict[str, Set[str]]:
    """Reads the CSV or YAML file and processes the data.

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
        elif file_extension == ".yml":
            reader = yaml.safe_load(file)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        files_variables = {}

        for row in reader:
            file_relative_path = row["file_relative_path"]
            file_description = row["file_description"]
            variable_name = row["variable_name"]
            variable_alternative_labels = row["variable_alternative_labels"]
            variable_description = row["variable_description"]
            variable_value_example = row["variable_value_example"]
            variable_type = row["variable_type"]

            if file_relative_path not in files_variables:
                files_variables[file_relative_path] = set()
            files_variables[file_relative_path].add(variable_name)

            create_triples(file_relative_path, file_description, variable_name, variable_alternative_labels, variable_description, variable_value_example, variable_type)

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
    shapes_graph.add((file_uri, RDFS.subClassOf, ODTP.InputFile))
    shapes_graph.add((file_uri, SH.targetNode, file_uri))
    shapes_graph.add((file_uri, SH.description, Literal(file_description, datatype=XSD.string)))
    
    # propertyshapes (for restricting variables)
    shapes_graph.add((variable_uri, RDF.type, SH.PropertyShape))
    shapes_graph.add((variable_uri, SH.datatype, URIRef(variable_type)))
    shapes_graph.add((variable_uri, SH.description, Literal(variable_description, datatype=XSD.string)))
    shapes_graph.add((variable_uri, SH.name, Literal(variable_name)))
    shapes_graph.add((variable_uri, SH.path, URIRef(ODTP + variable_name)))
    shapes_graph.add((variable_uri, SKOS.example, Literal(variable_value_example)))
    shapes_graph.add((variable_uri, SKOS.altLabel, Literal(variable_alternative_labels)))


def and_builder(variables: Dict[str, Set[str]]) -> List[str]:
    """Constructs AND statements for the property shapes.

    Parameters
    ----------
    variables : Dict[str, Set[str]]
        Dictionary containing file paths as keys and sets of variable names as values.

    Returns
    -------
    List[str]
        List strings containing ttl syntax nodeshapes with an sh:and.
    """
    propstringlist = []
    for var in variables:
        propstring = ""
        andstring = ""
        file_uri = URIRef(ODTP + var)

        for item in variables[var]:
            blanknodeitem = f"[sh:path <https://w3id.org/okn/o/sd#hasParameter> ; sh:hasValue <https://odtp.example.org/components/data/{item}>]"
            andstring += f" {blanknodeitem}"

        propstring = f"<{file_uri}> sh:and ({andstring}) ."
        propstringlist.append(propstring)
    return propstringlist


def main(input_filename: str) -> None:
    """Main function to orchestrate the RDF generation process.

    Parameters
    ----------
    input_filename : str
        The relative path to the file containing structured information (either csv or yml).
    """
    files_variables = read_and_process_file(input_filename)
    shapes_graph.serialize(destination="shapeswithoutand.ttl", format="turtle")
    with open("shapeswithoutand.ttl", "a") as file:
        for andstatement in and_builder(files_variables):
            file.write(andstatement + "\n")

    final_graph = Graph()
    final_graph.parse("shapeswithoutand.ttl", format="turtle")
    final_graph.serialize(destination="finalShapes.ttl", format="turtle")
    os.remove("shapeswithoutand.ttl")


if __name__ == "__main__":
    input_filename = input("Enter the relative path to the file containing structured information: ")
    main(input_filename)