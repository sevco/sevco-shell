# Sevco Shell
You can interact with the Sevco platform using our command line tool

# Dependencies

-Python 3.7+
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

You can install using pip3 From the source root:
```
pip3 install .
```

# Execution

Run `svsh` from the install directory or include the installation bin directory your $PATH

On first run, the Sevco shell will ask you to provide your credential details (api_host,auth_token):
The authorization token can be retrieved from my.sevcolabs.com/profile
```
api_host = "https://dev.api.sevcolabs.com"
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
