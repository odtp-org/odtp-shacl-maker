import pyshacl
import typer 

app = typer.Typer()

def shaclifyer(csv_file: str):
    pass

@app.command()
def make_shacl(csv_file: str):
    # Call your function here and pass the csv_file as input
    shaclifyer(csv_file)

if __name__ == "__main__":
    app()