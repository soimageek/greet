#!/usr/bin/env python

__author__ = "Jim Cassidy"
__copyright__ = "Copyright 2020, SpiderPig Project"
__credits__ = ["Jim Cassidy"]
__license__ = "???"
__version__ = "0.1.0"
__maintainer__ = "Jim Cassidy, "
__email__ = "jim@ion8.net"
__status__ = "Dev"

from ast import And, Not
import re
import typer
from os import path
import os
from google.cloud import storage
from google.api_core import exceptions
from dotenv import load_dotenv
import json
from genson import SchemaBuilder
from enum import Enum
import pprint

load_dotenv("./config/.env")
CLIENT_NAME = os.getenv("CLIENT_NAME")

map_directory = "integrations"

app = typer.Typer(help="Awesome SpiderPig CLI")

class Direction(str, Enum):
    incoming = "in"
    outgoing = "out"

class AuthMethods(str, Enum):
    APIKey ="APIKey"
    OAuth2 = "OAuth2"

def fetch_data_schema(direction: Direction):
    prompt = "sample for incoming data (file path)" if direction.value == Direction.incoming else "sample for outgoing data (file path)"
    datafile: str = typer.prompt(prompt)

    if not os.path.exists(datafile):
        typer.echo(f"\nERROR: {datafile} does not exist\n")
        os.abort()
    # Build JSON Scema from sample of data
    with open(datafile, 'r') as f:
        sample_json = f.read()
        builder = SchemaBuilder()
        builder.add_object(json.loads(sample_json))
        data_schema = json.dumps(builder.to_schema(),  indent=2) 
    return data_schema
 
@app.command()
def integration(integration_name: str = typer.Option(..., prompt=True),
            auth: AuthMethods = typer.Option(AuthMethods.OAuth2)):
    data_schema = fetch_data_schema(Direction.outgoing)
    
    if not os.path.exists(f"./{map_directory}"):
        os.mkdir(f"./{map_directory}")

    integration_directory = f"./{map_directory}/{integration_name}"
    integration_directory_exists = os.path.exists(integration_directory)

    if not integration_directory_exists:
        typer.echo(f"\nCreating the integration directory: {integration_directory}\n")
        os.mkdir(integration_directory)

    add_integration_to_event(integration_name)

    create_system_files(integration_name, auth)
    # integration_name_parts = integration_name.split("_")
    # system_name =  integration_name_parts[2]
    # create_directory_if_not_exists("systems")
    # if not os.path.exists(f"./systems/{system_name}"):
    #     url = add_service_file(integration_name, auth)
    #     url_file_name = f"./{map_directory}/{integration_name}/url"
    #     with open(url_file_name , 'w+') as f:
    #         f.write(url)
    create_integration_files(integration_name, data_schema)
    # transform_file = f"./{map_directory}/{integration_name}/transform.jsonata"

    # if not os.path.exists(transform_file):
    #     typer.echo(f"\nCreating the transform file: {transform_file}\n")
    #     # The default transform just passes back the data it received in a node.
    #     with open(transform_file , 'w+') as f:
    #         typer.echo(f"\nCreating the tranform: {transform_file}\n")
    #         transform_def ="""(\n  {\n   "data": * \n  }\n)"""
    #         f.write(transform_def)

    # with open(integration_directory +schema_file_name , 'w+') as f:
    #     typer.echo(f"\nCreating the schema: {integration_directory}{schema_file_name}\n")
    #     f.write(data_schema)

# @app.command()
# def event(name:str = typer.Option(..., prompt=True),
#     help = " Help creating event"):

#     event_directory = create_directory_if_not_exists(f"./events")
#     events = {"integrations": []}

#     schema_file_name = "/data_in_schema.json"
#     data_schema = json.loads(fetch_data_schema(Direction.incoming))

#     events = {"integrations": [], "validation": data_schema}
#     with open(event_directory + f"/{name}.json" , 'w+') as f:
#         f.write(json.dumps(events))

# @app.command()
# def integration(integration_name: str = typer.Option(..., prompt=True), 
#     auth: AuthMethods = typer.Option(AuthMethods.OAuth2, case_sensitive=False ),
#     help =" Help with init" ):

#     add_integration_to_event(integration_name)
#     create_directory_if_not_exists(f"{map_directory}")
   
#     # create_directory_if_not_exists(f"{map_directory})
#     integration_directory = create_directory_if_not_exists(f"{map_directory}/{integration_name}")
#     # add_service_file(integration_name, auth)

#     match auth:
#         case AuthMethods.OAuth2:
#             """
#             Get:
#                 authorization_url
#                 client_id
#                 redirect_uri
#                 whatver

#             save in the transfor directory - alter the upload command to upload these files
#             to Google Storage.
#             """
#             pass

#     typer.echo("\nThe integration and event directories has been created. Edit the documents to finish defining the integration")

def create_system_files (integration_name, auth):
    integration_name_parts = integration_name.split("_")
    system_name = integration_name_parts[2]
    create_directory_if_not_exists("systems")
    if not os.path.exists(f"./systems/{system_name}"):
        url = add_service_file(integration_name, auth)
        url_file_name = f"./{map_directory}/{integration_name}/url"
        with open(url_file_name , 'w+') as f:
            f.write(url)
            
def create_integration_files(integration_name, data_schema):
    schema_file_name = "/data_out_schema.json"
    transform_file = f"./{map_directory}/{integration_name}/transform.jsonata"

    if not os.path.exists(transform_file):
        typer.echo(f"\nCreating the transform file: {transform_file}\n")
        # The default transform just passes back the data it received in a node.
        with open(transform_file , 'w+') as f:
            typer.echo(f"\nCreating the tranform: {transform_file}\n")
            transform_def ="""(\n  {\n   "data": * \n  }\n)"""
            f.write(transform_def)

    integration_directory = create_directory_if_not_exists(f"{map_directory}/{integration_name}")
    with open(integration_directory +schema_file_name , 'w+') as f:
        typer.echo(f"\nCreating the schema: {integration_directory}{schema_file_name}\n")
        f.write(data_schema)
            
def create_directory_if_not_exists(directory_name):
    directory_exists = os.path.exists(directory_name)

    if not directory_exists:
        typer.echo(f"\nCreating the directory: {directory_name}\n")
        os.mkdir(directory_name)
    return directory_name

def add_service_file(integration_name:str, auth:AuthMethods):
    # We have to enforce the naming convention for this to work.
    integration_name_parts = integration_name.split("_")
    system_name =  integration_name_parts[2]

    # if not os.path.exists(""):
    os.mkdir(f"./systems/{system_name}")
    url: str = typer.prompt(f"What is the URL for the {system_name} service? ")

    auth_info = get_auth_info(auth)
    
    with open(f"./systems/{system_name}/settings.json" , 'w+', encoding='utf-8') as f:

        f.write(f"{{\n  \"authenticationMethod\": \"{auth.value}\",\n" )
        f.write(f"  \"integration_name\": \"{CLIENT_NAME}_{system_name}\",\n")
        f.write(f"  \"method\": \"POST\",\n" )
        f.write("  \"sp_secrets\": {\n" )

        for key in auth_info:
            if(key == "url"):
                f.write(f"    \"{key}\":\"{url}\",\n")
            elif(key not in ["url", "auth prefix"]):
                f.write(f"    \"{key}\":\"\",\n")
            else:
                # no comma for last item - it's json not a python list
                f.write(f"    \"{key}\":\"\"\n")
        f.write("  }\n")
        f.write("}")
    return url


def get_auth_info(auth: AuthMethods):
    """
    Given an auth method, this function returns
    a template that can be used to set the key
    values for sp_secrets.
    """
    match auth:
        case AuthMethods.OAuth2:
            return  {
                        "type": "oauth2 refresh",
                        "refresh token": "",
                        "auth url": "",
                        "client id": "",
                        "client secret": "",
                        "url": "",
                        "auth prefix": ""
            }
        case AuthMethods.APIKey:
            return {
                        "apiKey": ""
            }

def add_integration_to_event(integration_name):
    event_directory = create_directory_if_not_exists(f"./events/")
    existing_events = os.listdir(event_directory)
    event_name_parts = integration_name.split("_")
    event_name = f"{event_name_parts[0]}_{event_name_parts[1]}"

    if not f"{event_name}.json" in existing_events:
        if typer.confirm(f"There is no event called {event_name} - cteate it "):

            data_schema = json.loads(fetch_data_schema(Direction.incoming))

            events = {"integrations": [], "validation": data_schema}
            with open(event_directory + f"/{event_name}.json" , 'w+') as f:
                f.write(json.dumps(events))

        else:
            os.abort()

    with open(f"./events/{event_name}.json", "r") as f:
        integration_events = json.loads(f.read())
        if not integration_name in integration_events["integrations"]:
            integration_events["integrations"].append(integration_name)
        
            with open(f"./events/{event_name}.json" , 'w+') as f:
                f.write(json.dumps(integration_events))

if __name__ == "__main__":
    app()