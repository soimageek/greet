from cli_commands import upload
from cli_commands import init
from cli_commands import generate

import typer

app = typer.Typer(help="Awesome SpiderPig CLI")

app.add_typer(init.app, name="init", help="Create a new integration project")
app.add_typer(generate.app, name="generate", help="Generate files and configurations.")
app.add_typer(upload.app, name="upload", help="Upload events and integrations.")

@app.command()
def sayhi():
    """
    Just say hi!
    """
    typer.echo("Hi Jim")
