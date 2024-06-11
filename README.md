# odtp-shacl-maker

Module Name: SHACL-Maker
Author: SDSC
Description: This module provides functionality to generate RDF (Resource Description Framework) data using SHACL (Shapes Constraint Language) shapes based on structured information provided in CSV or YAML format.

Dependencies:
- typer: For creating command-line interfaces in Python.
- pandas: For data manipulation and analysis.
- rdflib: For working with RDF data.
- csv: For reading CSV files.
- os: For interacting with the operating system.
- yaml: For reading YAML files.
- urllib: For URL encoding.
- itertools: For iterating over data structures.

Usage:
This module can be used to generate RDF data by providing structured information in a CSV or YAML file format. It defines the following functions:

1. convert_to_variables(filename: str) -> dict[str, Set[str]]:
   Reads the CSV or YAML file and processes the data, returning a dictionary containing file paths as keys and sets of variable names as values.

2. create_triples(file_relative_path: str, file_description: str, variable_name: str, variable_alternative_labels: str, variable_description: str, variable_value_example: str, variable_type: str) -> None:
   Creates triples for file and variable metadata based on the provided parameters.

3. and_builder(variables: dict[str, set[str]]) -> list[str]:
   Constructs AND statements for the property shapes based on the provided dictionary of variables.

4. main(input_filename: str) -> None:
   Orchestrates the RDF generation process, taking the relative path to the input files containing structured information (either CSV or YAML).

Command-Line Interface:
This module also defines a command-line interface using Typer. It provides a command 'make_shacl' to generate SHACL shapes based on structured data provided in a CSV file.

Example Usage:
To generate SHACL shapes, run the module with the 'make_shacl' command followed by the path to the folder containing your structured data files. For example, to generate SHACL shapes for the files in a relative folder called "data", you can run the following command:
    python shacl-maker.py ./data/

Note: Ensure that all dependencies are installed before running the module.

For more details, refer to the function docstrings and the module implementation.

## How to run this tool?

```
docker build -t odtp-shacl-maker .

docker run -it -t odtp-shacl-maker bash

docker run -it -p 8499:8501  -t odtp-shacl-maker
```