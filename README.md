# Sevco Shell
You can interact with the Sevco platform using our command line tool

# Dependencies

Python 3.7+
You must have Python 3.7 or later to install the Sevco Shell
Check your installed python version by running
```
python --version
```

# Configuraion
Credentials will be pulled from cli args (--api-host, --api-key), environment vars (SVSH\_API\_HOST, SVSH\_API\_KEY),
and ~/.sevco/credentials in that order.

Example ~/.sevco/credentials
```
[default]
api_host = "https://dev.api.sevcolabs.com"
auth_token = "Bearer abcd1234"
```

# Installation

Sevco Shell uses Python setuptools for packaging.  You can install using setup.py.

Global install (as root)
```
python setup.py install
```

Local install
```
python setup.py install --user
```

# Execution

Run `svsh` from the install directory or include the installation bin directory your $PATH

At run, the Sevco shell will ask you to provide your credential details:
Authorization Token can be retrieved from my.sevcolabs.com/profile
```
api_host = "https://dev.api.sevcolabs.com"
auth_token = "Bearer sfkjsdfklghsdklfgjhsdfklgjhdfklgjhsdf"
```

Credentials can be pass on to the cli (--api-host, --api-key), set as environment vars (SVSH_API_HOST, SVSH_API_KEY), or defined in ~/.sevco/credentials.
The `svsh` reads credentials in the above order.
