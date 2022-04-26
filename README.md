# How to ...

## ... install the dependencies

Before doing any operation, you need to have these requirements installed :

- _python 3.7_
- _pipenv_ installed in the python above

To manage the dependencies, we use the tool [Pipenv](https://pipenv.pypa.io/en/latest/). It also
creates a virtual environment called **venv**.

A list of scripts have been created to help developers develop, but you can execute your own
commands from the virtual environment using `pipenv run
<command>`.

With that done, you can install the dependencies with the following command :

`pipenv install --dev`

## ... launch the script

To launch the script, you can use the following command :

`pipenv run start`

> As said previously, it's possible to run the script using python simply with `pipenv run
 python git4school_watch_dog.py` or creating a python run configuration with PyCharm.
> In the case you're using the run configuration of PyCharm, you have to check `Emulate 
terminal in output console` under `Execution` settings.

## ... check the code

To check the code, we have chosen [prospector](http://prospector.landscape.io/en/master/) which
packages a bunch of code quality tools and linters.

To run it, you can use the following command :

`pipenv run lint`

> _Prospector_ reads the file _.prospector.yml_ to configure the checks.

There is also the possibility to run [bandit](https://bandit.readthedocs.io/en/latest/) to check
security issues :

`pipenv run lint-security`

## ... run the tests

To run the tests, you can use the following command :

`pipenv run tests`

If you want to run tests besides this command, with an IDE like _PyCharm_, you have to make sure the
working directory is the root of the project. On _PyCharm_, you will be able to set the working
directory in the _run configuration_.

## ... generate the executable file

To generate a single file executable, you can use the following command :

`pipenv run package`

> To generate the executable, [pyinstaller](https://pyinstaller.readthedocs.io/en/stable/) uses the operating system it's running on.
> This means that you can only generate a Windows executable file from Windows, etc.