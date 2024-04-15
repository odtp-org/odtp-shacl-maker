# odtp-shacl-maker
SHACL schema maker for odtp compatible components.

SHACL Maker is a command-line tool written in Python that uses the pyshacl and typer libraries to convert CSV files into SHACL (Shapes Constraint Language) graphs.

## Installation
This project uses Poetry for dependency management. If you haven't installed Poetry yet, you can do so by following the instructions on their official documentation.

Once you have Poetry installed, you can install the dependencies for this project by navigating to the project's root directory and running:

```
poetry install
```

This will create a virtual environment and install the necessary dependencies.

## Usage
The tool provides a command-line interface. You can run the tool with the following command:

```
poetry run python shacl-maker.py make_shacl <csv_file>
```

Replace <csv_file> with the path to your CSV file.