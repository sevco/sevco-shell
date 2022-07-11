# Sevco Shell
You can interact with the Sevco platform using our command line tool

# Dependencies

- Python 3.7+
You must have Python 3.7 or later to install the Sevco Shell
Check your installed python version by running
```
python --version
```
- Python3 setuptools: pip
Check if pip is installed by running
```
pip3 --version
```

# Installation

Sevco Shell uses Python setuptools for packaging. 

You can install using pip3 from the source root:
```
pip3 install .
```

# Execution

Run `svsh` from the install directory or include the installation bin directory your $PATH

On first run, the Sevco shell will ask you to provide your credential details (api_host,auth_token):
The authorization token can be retrieved from my.sevcolabs.com/profile
```
api_host = "https://api.sev.co"
auth_token = "Bearer sfkjsdfklghsdklfgjhsdfklgjhdfklgjhsdf"
```

Credentials are passed on to the cli with:

--api-host, --auth-token
environment vars (SVSH\_API\_HOST, SVSH\_AUTH\_TOKEN)
or defined in ~/.sevco/credentials.

The `svsh` reads credentials in the above order.


# Credentials File

You can manually edit ~/.sevco/credentials to update your credentials.
```
[default]
api_host = "https://dev.api.sevcolabs.com"
auth_token = "Bearer abcd1234"
```

# Example Shell Output
There are built in commands for all the common functions, here is a quick snapshot of the `sources` command to list, configure a new or modify an existing data source:
```
[svsh > sevco]
> help

Available commands (type help <topic>):
=======================================
back  configs  exit  help  quit  runners  sources  users

[svsh > sevco]
> sources

                                       Source
     ========================================
[ 1]                                   Nessus
[ 2]                                     Zoom
[ 3]                                JumpCloud
[ 4]                                  Duo 2FA
[ 5]             ManageEngine Desktop Central
[ 6]                                   Sophos
[ 7]      Google Workspace (Formerly G Suite)
[ 8]                              Bitdefender
[ 9]                                   Meraki
[10]                                     Okta
[11]                                  Cylance
[12]               Microsoft Active Directory
[13]      Microsoft 365 (Formerly Office 365)

[svsh > sevco]
> help sources
Sources - work with available integration sources available in the source catalog.

sources                       list available sources
sources [idx]                 change scope into source [idx]
sources add                   add new source
sources config [idx]          configure source [idx]
```
