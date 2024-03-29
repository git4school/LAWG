# How to ...

## ... install the dependencies

Before doing any operation, you need to have these requirements installed:

- _python 3.9_
- _pipenv_ installed in the python above

To manage the dependencies, we use the tool [Pipenv](https://pipenv.pypa.io/en/latest/). It also
creates a virtual environment called **venv**.

A list of scripts have been created to help developers develop, but you can execute your own
commands from the virtual environment using `pipenv run
<command>`.

With that done, you can install the dependencies with the following command:

`pipenv install --dev`

## ... start the script ...

To launch the script, you can use the following command:

`pipenv run start`

> As said previously, it's possible to run the script using python simply with `pipenv run
 python lawg.py` or creating a python run configuration with PyCharm.
> In the case you're using the run configuration of PyCharm, you have to check `Emulate 
terminal in output console` under `Execution` settings.

### ... and authenticate

LAWG performs pushes which requires to authenticate to Github or another one.
To do this, you have 2 options:
 - Generate a Personal Access Token (PAT) on Github and enter it in the configuration file, prefixed with your Github username, separated by ":"
   - In this case, LAWG will modify the remote `origin` to add the authentication tuple
   >   **Example:**
   > 
   >   `pat: "johndoe:ghp_glfjbdxedgUGKgU4MkjWedCUgb2hwe"`
 - Generate an SSH key, add it to Github and enter the path to the key in the configuration file 
   > **Example:** 
   > 
   > `ssh_path: /Users/johndoe/.ssh/id_rsa`

## ... check the code

To check the code, we have chosen [prospector](http://prospector.landscape.io/en/master/) which
packages a bunch of code quality tools and linters.

To run it, you can use the following command:

`pipenv run lint`

> _Prospector_ reads the file _.prospector.yml_ to configure the checks.

There is also the possibility to run [bandit](https://bandit.readthedocs.io/en/latest/) to check
security issues:

`pipenv run lint-security`

## ... run the tests

To run the tests, you can use the following command:

`pipenv run tests`

If you want to run tests besides this command, with an IDE like _PyCharm_, you have to make sure the
working directory is the root of the project. On _PyCharm_, you will be able to set the working
directory in the _run configuration_.

## ... generate the executable file ...

To generate a single file executable, you can use the following command:

`pipenv run package`

> To generate the executable, [pyinstaller](https://pyinstaller.readthedocs.io/en/stable/) uses the operating system it's running on.
> This means that you can only generate a Windows executable file from Windows, etc.

### ... with options

During the generation of the executable, options can be set, as boolean constants in the _utils/constant.py_ file. 
The different options currently available are the following:

- `NO_WATCHER` : No changes are automatically committed if set to `True`
- `NO_SESSION_CLOSURE` : The working directory is not closed if set to `True`
- `NO_FIX_LIMITATION` : Unlisted questions can be used with the command `Fix` if set to `True`

> All options are disabled (set to `False`) for the generation of executables available in the [releases](https://github.com/git4school/lawg/releases).
