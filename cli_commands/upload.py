#!/usr/bin/env python

__author__ = "Jim Cassidy"
__copyright__ = "Copyright 2020, SpiderPig Project"
__credits__ = ["Jim Cassidy"]
__license__ = "???"
__version__ = "0.1.0"
__maintainer__ = "Jim Cassidy, "
__email__ = "jim@ion8.net"
__status__ = "Dev"

from click import command
import typer
from os import path
import os
import sys
from google.cloud import storage
from google.api_core import exceptions
from dotenv import load_dotenv
import yaml 
import json
from genson import SchemaBuilder
from enum import Enum

load_dotenv("./config/.env")

BUCKET_NAME = os.getenv("BUCKET_NAME")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
CLIENT_NAME = os.getenv("CLIENT_NAME")
MAP_DIRECTORY  = "integrations"
CONFIG_DIRECTORY  ="config"
EVENT_DIRECTORY  ="events"
integration_files = ['data_out_schema.json', 'transform.jsonata', "url"]

print(BUCKET_NAME, "Bucket")

class FileDoesNotExist(Exception):
    """Error is a file does not exist"""
    pass

class StorageBucketDoesNotExist(Exception):
    """Error is a storage buck does not exist"""
    pass

class SPTransformBucket:
    """
    This provides some methods to interface with Google Clood Storage buckets.
    Specifically buckets that contain information about SpiderPig Integrations and events.
    """
    def __init__(self):
        pass
    
    def list(self):
        """Lists all of the integrations for the current client"""
        pass
    
    def gett(self, integration_name: str, file_name: str):
        """
        Gets any of the files that are part of a integrations for the current client
        from Google storage 
        """
        bucket = None
        storage_client = storage.Client()
        try:
            bucket = storage_client.get_bucket(BUCKET_NAME)
        except exceptions.NotFound:
            raise StorageBucketDoesNotExist(f"The bucket called {BUCKET_NAME} does not exist.") # wrong
        except Exception as e:
            print(e, type(e))
            sys.exit()
 
        blob_name = CLIENT_NAME +"/" + integration_name + "/" + file_name
        bucket = storage_client.get_bucket(BUCKET_NAME)
        blob = storage.Blob(blob_name, bucket)

        return blob.download_as_string()


    def upload_event(self, event_name:str):
            """
            Uploads a integration to Google Storage.
            This command expects the name of an event.
            
            The event directory must contain a properly formatted files that corresponds to the event_name:
            """
            bucket = None
            storage_client = storage.Client()
            try:
                bucket = storage_client.get_bucket(BUCKET_NAME)
            except exceptions.NotFound:
                print(f"Creating storge bucket: {BUCKET_NAME}.")
                bucket=storage_client.create_bucket(BUCKET_NAME)  
            except Exception as e:
                print(e, type(e))
                sys.exit()
            blob_name = CLIENT_NAME +f"/{EVENT_DIRECTORY}/" + event_name
            file_path = f"./{EVENT_DIRECTORY}/" + event_name +".json"
            blob = bucket.blob(blob_name)
            try:
                blob.upload_from_filename(file_path)
                print(f"Uploading {file_path}"
                
                )
            except Exception as err:
                print(err)

            typer.echo(f"Uploaded {event_name}")

    def upload_integration(self, integration_name: str, directory_path: str, file_name: str):
            """
            Uploads a integration to Google Storage.
            This command expects the name of a directory, the name of the client, and the name of the trnasform.
            
            The integration directory must contain properly formatted files with the following names:
            
            1. data_in.json
            2. data_out.json
            3. transform.jsonata
            4. url
            """
            bucket = None
            storage_client = storage.Client()
            try:
                bucket = storage_client.get_bucket(BUCKET_NAME)
            except exceptions.NotFound:
                print(f"Creating storge bucket: {BUCKET_NAME}.")
                bucket=storage_client.create_bucket(BUCKET_NAME)  
            except Exception as e:
                print(e, type(e))
                sys.exit()
 
            # This creates a dependency on the naming convention: s1_event_s2
            integration_name_parts = integration_name.split("_")
            event_name = f"{integration_name_parts[0]}_{integration_name_parts[1]}"

            blob_name = CLIENT_NAME +f"/events/{event_name}_files/" + integration_name + "/" + file_name

            file_path = directory_path +'/'+file_name
            blob = bucket.blob(blob_name)
            if(path.exists(file_path)==False):
                typer.echo(f"The file {file_name} does not exist.")
                return
            try:
                blob.upload_from_filename(file_path)
                print(f"Uploading {file_path}")
            except Exception as err:
                if(not file_name == "functions.py"):
                    print(err)
        
app = typer.Typer(help="Awesome SpiderPig CLI")

@app.command()
def integration(name: str= typer.Option(..., prompt=True)):
    pass

@app.command()
def event(event: str= typer.Option(..., prompt=True)):
    """Loads the integration and event files to the cloud"""
    if(GOOGLE_APPLICATION_CREDENTIALS == None):
        typer.echo(f"\n" + typer.style(f"Please initialize your project by using the <pig init> command and by defining an integration.\n", fg=typer.colors.RED, bold=True))
        raise typer.Exit()
        
    sp_TransformBucket = SPTransformBucket()
    file_name = f"./{EVENT_DIRECTORY}/{event}.json"

    if not path.exists(file_name):
        typer.echo(f"\n" + typer.style(f"No such event file: {file_name}\n", fg=typer.colors.RED, bold=True))
        raise typer.Exit()

    try:
        sp_TransformBucket.upload_event(event)
    except Exception as err:
        typer.echo(err)
        raise typer.Exit()

    # Upload all of the integrations that are part of the event - can't leave them behind.
    for integration in os.listdir(f"./{MAP_DIRECTORY}"):
        upload_integration(integration)

    typer.echo("\n")

def upload_integration(name:str):
    directory_path = f"./{MAP_DIRECTORY}/{name}"
    sp_TransformBucket = SPTransformBucket()
    if not path.isdir(directory_path):
        typer.echo(f"\n" + typer.style(f"{directory_path} : no such integration. Run the <sp integration create> command to create a trasnform.\n", fg=typer.colors.RED, bold=True))
        raise typer.Exit()
    t= typer.style(f"{name}", fg=typer.colors.YELLOW, bold=True) 
    b= typer.style(f"{BUCKET_NAME}", fg=typer.colors.YELLOW, bold=True) 
    c= typer.style(f"{CLIENT_NAME}", fg=typer.colors.YELLOW, bold=True) 
    typer.echo(f"\nuploading integration {t} for {c} to {b}\n")

    try:
        for file_name in integration_files:
            sp_TransformBucket.upload_integration(name, directory_path, file_name)
    except Exception as err:
        typer.echo(err)
        raise typer.Exit()

    # typer.echo("\n")

if __name__ == "__main__":
    app()



