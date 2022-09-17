#!/usr/bin/env python

__author__ = "Jim Cassidy"
__copyright__ = "Copyright 2020, SpiderPig Project"
__credits__ = ["Jim Cassidy"]
__license__ = "???"
__version__ = "0.1.0"
__maintainer__ = "Jim Cassidy, "
__email__ = "jim@ion8.net"
__status__ = "Dev"

import typer
import os

map_directory = "integrations"
config_directory ="config"
event_directory ="events"
systems_directory = "systems"
service_account_file_name = "service-account-file.json"

app = typer.Typer(help="Awesome SpiderPig CLI")
 
@app.command()
def project(client: str = typer.Option(..., prompt=True),
    help =" Help with init" ):
    """Initializes a project, creates the map directory with template files and creates a .env file"""

    if not os.path.exists(map_directory):
        os.mkdir(map_directory)
    
    if not os.path.exists(config_directory):
        os.mkdir(config_directory)

    if not os.path.exists(event_directory):
        os.mkdir(event_directory)
    
    if not os.path.exists(systems_directory):
        os.mkdir(systems_directory)

    else:
       delete_previous_config = typer.prompt("\nDo you want to overwrite the previous configuration? Y/N")
       if(delete_previous_config.upper() != "Y"):
           typer.echo("Exiting\n")
           raise typer.Exit()

    # This has to come from the secrets manager or something secure - can't be in GIT.
    service_account = '{\n' \
        '    "type": "service_account",\n' \
        '    "project_id": "spiderpig-348518",\n' \
        '    "private_key_id": "7356eb466cc824cfa02387db0dc908fbe747f80d",\n' \
        '    "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDR+07/EGqXAHs6\\n1KZk2Ef7F6txHXjtHgCUOxpjLQer4Futm0OZt3bjF3eR7WwKcXr0ESSKmAkrbbmY\\nY76Vn2AA2CrMYuo2zHDrglReyBzGhQJhS9OyBhd9RvPfMy4R+qBlpFdQ2gvJmfxB\\ncgMTHERE2p93CVa36dIqLZ3Cu8OAUZ4J8rq0Ux86OSFc0hhr1yh0a2mPDS8Tv16y\\nq0fMv8MlRpEO84ev4NgQy9HaqKnDpvdOBYdH9Val4t9Ul5j9nbo97PI9YgV6s4Ox\\nJryWQH/fSHDNY8Be2ttKiobnUIIHS+Fr4qaytg+VrFqAKO0fgxAC+C1hzekYFwo3\\nUrSGzPm1AgMBAAECggEAKQfYSdLlYRhA/B/tW6s/dXsMjw/ZP0wrhMt/vn1gEF/I\\nykWakgDdhEZjoOopwGioQ+TNpR9MO2Y3a+Whqg74bXHP+xwg9BBCyGIxJkwoA0qe\\nSnDMru6tzFb+9FBF4lF84h+YyD2zK/Og7RDgNO3DEUk++72halKQNJmxSAn0i7AM\\ncaJ7z3wzLGiEnxMD4Yqp3da/hIW1T92dizqfiGjzefC2iVhVAetJ1WIYRuGhVRwt\\nxCQpazvtJlZ5DmMh/7rIbBU2VpT6QV6btscfAeZ8CBI8v5vOcdqHsECRBaPZ+a1v\\nEgrgrgXZxxbneQ40KjGLb8GELLG4F3ALhkiJNlWlgQKBgQDuuiCL7M812+I1ous4\\nzLsAWZgIttKorHtzH2Ac2pzz+OgD7+YClVlNLNW5PSJrh+kZ6ixazGFcbQnp69HJ\\nWVJXU/wL24r3AsGqBcC54hYQ4Er+g2XN5pUd70uvAyKlJL2xwj31yt6uFvnaCIaJ\\nAUX8uP1hsHgss6C5QzfdEB5PZQKBgQDhLL0p5vr2biNnhCyfKR1JuA9IeH0tVWpG\\nJ/DLfWvG/9ORHkabKxNm5NejIYEfCH7WOhv9wbffeCU3CpK1E7Tk1ervLqNDmMCI\\nHrpLm/KAS/0R+i2kywOerNeWE/qxy2sHF5fDPTDSqb5TNZd95ekpfhifglvq09jk\\nCbvGu+mkEQKBgF5rra3KRxaVVn5CZui7SQdVaGWh8eYW+mjJMxmWedehThsoin/h\\nFEYLAqlWfcOsKM1AKrTq+2M0GWS1Ce+qbX/uztTdy7PxGiomRlj/DB02qVLLI7vx\\nhG8nk3awNca9pm2lVx5dU//lRIMxNg0APO89N7Kouo9rqJk99d1wn5xlAoGBANOu\\npV5BAGiufaYRAYnWsuvclrGAY908UR4G6j3CeJGpapEgLywsQJ8YPwfitWohKGvo\\nUOwrMtpoLkQiMmz8S7Bc0fFsnJstfMH6cRQnVL/7r7s4v7QODicbQciam7CNFN6j\\n9U3btow0evHqjbITczBIlIlPmW2XHmyyIc7gVPKhAoGAL1rVI6avagczB/ZtXrJU\\ndmON2OnL/yBYgUFYF09SYSqGof7eplSnr/GjJZj5Q8GK1cTzjroHqxmL+QmE2G9C\\niIMGEVnZtBzLDys80nc5Ct6H22wZaXCOZ9e3R65cIBytltcS5M84BvTbPCPzJr9j\\n2hK3565QO34h8mKdyxWLd/g=\\n-----END PRIVATE KEY-----",\n' \
        '    "client_email": "ion8spstorage@spiderpig-348518.iam.gserviceaccount.com",\n' \
        '    "client_id": "101755883909502338154",\n' \
        '    "auth_uri": "https://accounts.google.com/o/oauth2/auth",\n' \
        '    "token_uri": "https://oauth2.googleapis.com/token",\n' \
        '    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",\n' \
        '    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ion8spstorage%40spiderpig-348518.iam.gserviceaccount.com"\n' \
        '}'

    with open(f"./{config_directory}/{service_account_file_name}", 'w+') as f:
        f.write(service_account)

    # Create .env
    with open(f"./{config_directory}/.env", 'w+') as f:
        f.write('GOOGLE_APPLICATION_CREDENTIALS="./config/service-account-file.json"\n')
        f.write(f'BUCKET_NAME="ion8-client-integrations"\n')
        f.write(f'CLIENT_NAME="{client}"\n')

    # Create .env
    with open(f"./{config_directory}/", 'w+') as f:
        # const command = "gcloud run services update SERVICE --update-env-vars KEY1=VALUE1,KEY2=VALUE2";
        f.write('GOOGLE_APPLICATION_CREDENTIALS="./config/service-account-file.json"\n')
        f.write(f'BUCKET_NAME="ion8-client-integrations"\n')
        f.write(f'CLIENT_NAME="{client}"\n')
        
if __name__ == "__main__":
    app()