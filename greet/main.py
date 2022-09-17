import typer

app = typer.Typer()

@app.command()
def sayhi():
    """
    Just say hi!
    """
    typer.echo("Hi")
    
@app.command()
def saybye():
    """
    Just say bye!
    """
    typer.echo("bye")