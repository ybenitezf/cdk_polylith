In this article we will see a way to achieve a "monorepo" architecture for the code using [Polylith](https://polylith.gitbook.io/polylith/) philosophy and a couple of [poetry](https://python-poetry.org/docs/) plugins to achieve this in a Python CDK applications.

---

## Requirements

As advertised go ahead and install poetry and the plugins:

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry self add poetry-multiproject-plugin
poetry self add poetry-polylith-plugin
```

I left to you to read about the plugins for poetry, you can find details on the author repositories for [multiproject](https://github.com/DavidVujic/poetry-multiproject-plugin) and for [polylith](https://davidvujic.github.io/python-polylith-docs/).

Also, you will need `aws cdk` installed on your system, i recommend to follow the [requirements section of the aws cdk workshop site](https://cdkworkshop.com/15-prerequisites.html):

```bash
npm install -g aws-cdk
```

## Starting point

I will assume as a starting point the final version of the CDK Python Workshop, we will simply copy the code from the folder [https://github.com/aws-samples/aws-cdk-intro-workshop/tree/master/code/python/main-workshop](https://github.com/aws-samples/aws-cdk-intro-workshop/tree/master/code/python/main-workshop) and this will be our [first commit](https://github.com/ybenitezf/cdk_polylith/commit/dc0033ffb7bfc30f604692948a9390b228c92af6), the source tree should looks like:

```
.
├── app.py
├── cdk.json
├── cdk_workshop
│   ├── cdk_workshop_stack.py
│   ├── hitcounter.py
│   └── __init__.py
├── lambda
│   ├── hello.py
│   └── hitcount.py
├── README.md
├── requirements-dev.txt
├── requirements.txt
└── source.bat
```

First of all let's turn this into a poetry project executing:

```bash
poetry init
```

When asked for the main and development dependencies answer no, since we will add then later. The result should looks something like (`pyproject.toml`):

```toml
[tool.poetry]
name = "cdk-polylith"
version = "0.1.0"
description = ""
authors = ["Yoel Benitez Fonseca <ybenitezf@gmail.com>"]
readme = "README.md"
packages = [{include = "cdk_polylith"}]

[tool.poetry.dependencies]
python = "^3.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

Additionally, lets add a poetry config to make poetry build the python virtual environment in the project folder before installing the dependencies, let create a `poetry.toml` file with the content:

```toml
[virtualenvs]
path = ".venv"
in-project = true
```

And add [a commit](https://github.com/ybenitezf/cdk_polylith/commit/08b4391ea1298c86a92ec3c7829dde22bba00113) with this.

## Configuring polylith

Before delving into the code it's is recommended to read the core concepts of polylith: [workspace](https://polylith.gitbook.io/polylith/architecture/2.1.-workspace), [component](https://polylith.gitbook.io/polylith/architecture/2.3.-component), [base](https://polylith.gitbook.io/polylith/architecture/2.2.-base), [project](https://polylith.gitbook.io/polylith/architecture/2.6.-project) and [development project](https://polylith.gitbook.io/polylith/architecture/2.4.-development) taking into account that the [python-polylith](https://github.com/DavidVujic/python-polylith) is an adaptation of those concepts for Python.

Running (once) the following command in our repository will create the necessary folder structure to our project:

```bash
poetry poly create workspace --name="cdk_workshop" --theme=loose
```

> **note**: The `--name` parameter here will set the base package structure, all the code then will be imported from this namespace, for example `from cdk_workshop ...` for more see the [oficial documentation](https://davidvujic.github.io/python-polylith-docs/)

After this command our source tree will look like (note the new folders: bases, components, development and projects):

```
.
├── app.py
├── bases
├── cdk.json
├── cdk_workshop
│   ├── cdk_workshop_stack.py
│   ├── hitcounter.py
│   └── __init__.py
├── components
├── development
├── lambda
│   ├── hello.py
│   └── hitcount.py
├── poetry.toml
├── projects
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── source.bat
└── workspace.toml
```

The `workspace.toml` will configure the behavior of the `poetry poly ...` commands

Let's add [this commit](https://github.com/ybenitezf/cdk_polylith/commit/bfc66d18ba91139e46251e446f2fbb3d14253f67). From now on, we will be moving the old code to this new structure.

## Project requirements, requirements, requirements

Before we go further let's install the poetry project:

```bash
poetry install
```

> **note**: ignore the warning about the project not containing any element's

And now we move ours dependencies from `requirements.txt` and `requirements-dev.txt` to the `pyproject.toml` format:

```bash
poetry add aws-cdk-lib~=2.68
poetry add 'constructs>=10.0.0,<11.0.0'
poetry add cdk-dynamo-table-view==0.2.438
```

And dev requirements:

```bash
poetry add pytest==7.2.2 -G dev
```

We can remove now `requirements.txt` and `requirements-dev.txt` because those will be managed by the `pyproject.toml`, the new versión will looks like:

![pyproject.toml after adding the requirements](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ows5ycgnhoek2ell67sc.png)

All this [changes are in this commit](https://github.com/ybenitezf/cdk_polylith/commit/a05638728e299fadd5f7498e00abcb648956d590).

> **note**: poetry developers recommend to add the `poetry.lock` to the repository, some others have reported problems between architecture changes and the `.lock` file, so i will leave to you where to include or not this file.

# Components

From the polylith documentation (https://polylith.gitbook.io/polylith/architecture/2.3.-component):

> A component is an encapsulated block of code that can be assembled together with a base (it's often just a single base) and a set of components and libraries into services, libraries or tools. Components achieve encapsulation and composability by separating their private implementation from their public interface.

So in CDK term's our's component should be _Stacks_ or _Construct's_ since this are the reusable parts.

In this application we have the `HitCounter` construct and the `CdkWorkshopStack` stack, lets add then as components to our project:

```
poetry poly create component --name hit_counter
poetry poly create component --name cdk_workshop_stack
```

Automatically we will get a new directory under `components` with the name of the workspace (`cdk_workshop`) and under this a python package for each of the components. The same has happened to the test's folder (that is way we put `--theme=loose` when creating the workspace).

We need now to modify `pyproject.toml` to recognize the new components, edit and add the following to the package property in the `[tool.poetry]` section:

```toml
packages = [
    {include = "cdk_workshop/hit_counter", from = "components"},
    {include = "cdk_workshop/cdk_workshop_stack", from = "components"}
]
```

To ensure all is fine, run:

```bash
poetry install && poetry run pytest test/
```

if we run now `poetry poly info` we will see our new components listed under the bricks section

![poetry poly info](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/4ff7di6dixc18qoklswk.png)

Let's [commit this](https://github.com/ybenitezf/cdk_polylith/commit/b77d8d5272bd629efb3588d6df151e19079c8061) before moving the code.

### `hit_counter` component

First with the the `HitCounter` construct, we will copy the code from `cdk_workshop/hitcounter.py` to `components/cdk_workshop/hit_counter/core.py`

```bash
cp cdk_workshop/hitcounter.py components/cdk_workshop/hit_counter/core.py
git rm cdk_workshop/hitcounter.py
```

The code in this construct will need more refactoring, we will come back later for now we [commit this as it is](https://github.com/ybenitezf/cdk_polylith/commit/9e17a1f7ff9e2537453ee7e80bacfd665d10a647).

### `cdk_workshop_stack` component

And with the `CdkWorkshopStack` we repeat the process:

```
cp cdk_workshop/cdk_workshop_stack.py components/cdk_workshop/cdk_workshop_stack/core.py
git rm cdk_workshop/*
```

There is a dependency, `cdk_workshop_stack` need's the construct defined in `hit_counter` so we need to edit `components/cdk_workshop/cdk_workshop_stack/core.py` and fix the import in the line 8:

```python
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from cdk_dynamo_table_view import TableViewer
from cdk_workshop.hit_counter.core import HitCounter

...
```

> **Note**: now we use the full path to the class in the component (`cdk_workshop.hit_counter.core`), `cdk_workshop` the workspace, `hit_counter` the component and `core` witch is a module in `hit_counter`, and this makes the component `cdk_workshop_stack` depends on the `hit_counter` component and for the first we need the second.

This will add [another commit](https://github.com/ybenitezf/cdk_polylith/commit/c57b58c0a0f15044f59dbb52c6d981ba83d02165).

## Bases

From the polylith documentation (https://polylith.gitbook.io/polylith/architecture/2.2.-base), *bases* are the building blocks that exposes a public API to the outside world.

> A base has a "thin" implementation which delegates to components where the business logic is implemented.
> A base has one role and that is to be a bridge between the outside world and the logic that performs the "real work", our components. Bases don't perform any business logic themselves, they only delegate to components.

So in the context of the Aws CDK application the candidate for a base will be the module that defines the application and do the synthesis, in other words the code that now resides on `app.py`.

Let's add a base to the project:

```bash
poetry poly create base --name workshop_app
```

Like in the case of the components, the previous command, will add a new package but in the bases directory: `bases/cdk_workshop/workshop_app` with a module for us to define the code of our base - `poetry poly` will add a demo test code to.

We need to alter our package list on `pyproject.toml` to add the new base to the Python project:

```toml
packages = [
    {include = "cdk_workshop/workshop_app", from = "bases"},
    {include = "cdk_workshop/hit_counter", from = "components"},
    {include = "cdk_workshop/cdk_workshop_stack", from = "components"}
]
```

Let's copy the code and fix the imports:

```bash
cp app.py bases/cdk_workshop/workshop_app/core.py
git rm app.py
```

The content of should be like:

```python
import aws_cdk as cdk

from cdk_workshop.cdk_workshop_stack.core import CdkWorkshopStack

app = cdk.App()
CdkWorkshopStack(app, "cdk-workshop")

app.synth()

```

The result can be seen [in this commit](https://github.com/ybenitezf/cdk_polylith/commit/db9974030b63d42d519fd5ea1de9969ccc40e087).

If you run `poetry poly info` you should see something like this:

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/143ofyw8wag2y2dta7hk.png)

### Remarks 

I propose a base for each cdk application if more than one is necessary, each base will use and reuse the stacks and constructs defined in the components.

If you are facing a large CDK project i recommend maintaining a single component package (a single component in polylith witch is a python package) for all the constructs, one construct per module. And a component for each Stack, the reason being to maintain a single source of dependencies between the components in the project: `construct component ->  stack component` assuming the stack's components do not depend on the others stack components.

## Projects

> Projects configure Polylith's deployable artifacts.

In other words, projects define what we deploy, we combine one (or several bases but that's is rare) bases and several components into an artifact that allow's us to deploy our code.

In polylith the projects live in the `projects` folder and they ***should not contain code*** unless sough code is related to the deployment or building of the artifacts, in resume no python code there.

A CDK application is defined by the `cdk.json` file, in our case:

```json
{
  "app": "python3 app.py",
  "context": {
    "@aws-cdk/aws-apigateway:usagePlanKeyOrderInsensitiveId": true,
    "@aws-cdk/core:stackRelativeExports": true,
    "@aws-cdk/aws-rds:lowercaseDbIdentifier": true,
    "@aws-cdk/aws-lambda:recognizeVersionProps": true,
    "@aws-cdk/aws-cloudfront:defaultSecurityPolicyTLSv1.2_2021": true
  }
}
```

Note the content of the `"app"` key, we removed `app.py` and now we need to do something else, beginning by adding a new project to our polylith repository:

```bash
poetry poly create project --name cdk_app
```

The project name can be anything you need or want, this will be used to build a python package. Now the projects folder have a new subfolder `cdk_app` with a `pyproject.toml` file on it, is in this file that we combine our bases and components to build the artifact to deploy, edit this file and in the `package` property we will add what we need:

```toml
packages = [
    {include = "cdk_workshop/workshop_app", from = "../../bases"},
    {include = "cdk_workshop/hit_counter", from = "../../components"},
    {include = "cdk_workshop/cdk_workshop_stack", from = "../../components"}
]
```

Note that we added a `../../` to bases and components since this pyproject file is two levels down in the path

We need to add the necessary dependencies form the `pyproject.toml` in the root folder, from there we only copy the need's for the bases and components included - no dev dependency.

```toml
[tool.poetry.dependencies]
python = "^3.10"
aws-cdk-lib = ">=2.68,<3.0"
constructs = ">=10.0.0,<11.0.0"
cdk-dynamo-table-view = "0.2.438"
```

The final result should be something like

```toml
[tool.poetry]
name = "cdk_app"
version = "0.1.0"
description = ""
authors = ['Yoel Benitez Fonseca <ybenitezf@gmail.com>']
license = ""

packages = [
    {include = "cdk_workshop/workshop_app", from = "../../bases"},
    {include = "cdk_workshop/hit_counter", from = "../../components"},
    {include = "cdk_workshop/cdk_workshop_stack", from = "../../components"}
]

[tool.poetry.dependencies]
python = "^3.10"
aws-cdk-lib = ">=2.68,<3.0"
constructs = ">=10.0.0,<11.0.0"
cdk-dynamo-table-view = "0.2.438"

[tool.poetry.group.dev.dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

Running `poetry poly info` will show:

![poetry poly info](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/2qycwdgpi3fqult0mjwp.png)

As you can see a new column has appeared and the brick's (bases and component) that the project use are marked.

Move the `cdk.json` file to the project folder

```bash
mv cdk.json projects/cdk_app/cdk.json
```

But because we move our app object to the `bases/cdk_workshop/workshop_app/core.py` module we need to edit `cdk.json` and change the `app` entry to:

```

  "app": "python3 -m cdk_workshop.workshop_app.core"

```

Let add a [checkpoint here and commit our changes](https://github.com/ybenitezf/cdk_polylith/commit/8a581b042588a0ec0271047fa293d143df0235fc).

## cdk project new home

In theory with this we can deploy our CDK application, lets test this:

```bash
cd projects/cdk_app
poetry build-project
```

This will create a `dist` directory in `projects/cdk_app` with the python package.

> this need's to be include in the `.gitignore`, to make this more simple copy over the [recommended gitignore for python](https://github.com/github/gitignore/blob/main/Python.gitignore) and add it to the .gitignore in the repository root (https://github.com/ybenitezf/cdk_polylith/commit/0c0eda0cf6f2d75e6899a8e18b2374663d4a8b8d).

![project folder files tree](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/h1tz7t111dvxwnzv2li9.png)

This python package contains our CDK app, so to test our theory we need to created a python virtual env, install this package and run `cdk synth` (in the `projects/cdk_app` folder) and will see the cloudformation template:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install dist/cdk_app-0.1.0-py3-none-any.whl
cdk synth
```

Oops !!!, we get and error, something like:

```
RuntimeError: Cannot find asset at cdk_polylith/projects/cdk_app/lambda
```

The cause of this is that the previous implementation assumed that any cdk command would be execute on the root of the repository and we have moved on to `projects/cdk_app`, to fix this we can move the `lambda` folder to `projects/cdk_app` and test again:

```bash
cd ../../
mv lambda/ projects/cdk_app/
cd projects/cdk_app/
cdk synth
```

And now all work great !!! ... ummm not not really, all the idea behind polylith is that all the code live in the components or bases folders.

Let's discard this last change and solve this problem in the polylith way - (remember to exit the venv created for the `cdk_app` project).

## Include lambda functions code

So in this project we have 2 lambdas:

```
./lambda/
├── hello.py
└── hitcount.py
```

The plan here is to add two bases (one for each function). Botch are pretty simple, only `hitcount.py` have an external dependency to boto3.

Let's add the bases first:

```
poetry poly create base --name hello_lambda
poetry poly create base --name hitcounter_lambda
```

> **Note**: if these functions shared code, ie something that could be refactored so that they both use it, it would be a good idea to add a new component for this feature.

And we add this new bases to the main `pyproject.toml` packages property:

```toml
packages = [
    {include = "cdk_workshop/workshop_app", from = "bases"},
    {include = "cdk_workshop/hello_lambda", from = "bases"},
    {include = "cdk_workshop/hitcounter_lambda", from = "bases"},
    {include = "cdk_workshop/hit_counter", from = "components"},
    {include = "cdk_workshop/cdk_workshop_stack", from = "components"}
]
```

And we add the dependencies to:

```
poetry add boto3
```

Run `poetry install && poetry run pytest test/` to ensure all is correct.

And move the code:

```bash
mv lambda/hello.py bases/cdk_workshop/hello_lambda/core.py
mv lambda/hitcount.py bases/cdk_workshop/hitcounter_lambda/core.py
rm -rf lambda/
```

Let add a [checkpoint here and commit our changes](https://github.com/ybenitezf/cdk_polylith/commit/61d24f3917fb90a822bfca542bfa1576c01dc3a7).

The trick now is to generate a python package for each lambda function and use the bundling options of the lambda cdk construct to inject our code and requirements for the lambda's. Let begin by adding the projects for each lambda:

```bash
poetry poly create project --name hello_lambda_project
poetry poly create project --name hitcounter_lambda_project
```

we repeat the process, the same as for the `cdk_app`, the `projects/hello_lambda_project/pyproject.toml` should reference the `hello_lambda` base:

```toml
...

packages = [
    {include = "cdk_workshop/hello_lambda", from = "../../bases"}
]

...
```

And `projects/hitcounter_lambda_project/pyproject.toml` for `hitcounter_lambda` - including the dependency for `boto3`:

```toml
packages = [
    {include = "cdk_workshop/hitcounter_lambda", from = "../../bases"}
]

[tool.poetry.dependencies]
python = "^3.10"
boto3 = "^1.26.123"

```

In the `CdkWorkshopStack` code we change the lambda function definition to:

```python


        hello = _lambda.Function(
            self,
            "HelloHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                "lambda/hello",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t"
                        " /asset-output && cp -au . /asset-output"
                    ]
                )
            ),
            handler="cdk_workshop.hello_lambda.core.handler",
        )


```

Note the `handler` declaration, as in `cdk.json` we are using the package full namespace to declare our handler, `_lambda.Runtime.PYTHON_3_9.bundling_image` will bundle the lambda code using the requirements.txt that we will generate.

Let repeat the process for the `hitcounter_lambda`, in `components/cdk_workshop/hit_counter/core.py` we change:

```python

            handler="cdk_workshop.hitcounter_lambda.core.handler",
            code=_lambda.Code.from_asset(
                "lambda/hello",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t"
                        " /asset-output && cp -au . /asset-output"
                    ]
                )
            ),
            runtime=_lambda.Runtime.PYTHON_3_9,

```

Add let's add the required folders (assets folders) to the `cdk_app` project.

```
mkdir -p mkdir -p projects/cdk_app/lambda/{hello,hitcounter}
touch projects/cdk_app/lambda/{hello,hitcounter}/requirements.txt
```

Let add a [checkpoint here and commit our changes](https://github.com/ybenitezf/cdk_polylith/commit/61d24f3917fb90a822bfca542bfa1576c01dc3a7).

Now we try the deploy again, first we build the lambda's packages:

```bash
cd projects/hello_lambda_project
poetry build-project
cd ../hitcounter_lambda_project/
poetry build-project
cd ../../
```

Our projects/ folder should have this structure:

```
./projects/
├── cdk_app
│   ├── cdk.json
│   ├── dist
│   │   ├── cdk_app-0.1.0-py3-none-any.whl
│   │   └── cdk_app-0.1.0.tar.gz
│   ├── lambda
│   │   ├── hello
│   │   │   └── requirements.txt
│   │   └── hitcounter
│   │       └── requirements.txt
│   └── pyproject.toml
├── hello_lambda_project
│   ├── dist
│   │   ├── hello_lambda_project-0.1.0-py3-none-any.whl
│   │   └── hello_lambda_project-0.1.0.tar.gz
│   └── pyproject.toml
└── hitcounter_lambda_project
    ├── dist
    │   ├── hitcounter_lambda_project-0.1.0-py3-none-any.whl
    │   └── hitcounter_lambda_project-0.1.0.tar.gz
    └── pyproject.toml
```

We will need to add the `.whl` of the lambdas to the respective `requirements.txt` files on the `cdk_app` project:

```bash
cd projects/cdk_app/
cp ../hello_lambda_project/dist/*.whl lambda/hello/
cp ../hitcounter_lambda_project/dist/*.whl lambda/hitcounter/
cd lambda/hello/
ls * | find -type f -name "*.whl" > requirements.txt
cd ../hitcounter/
ls * | find -type f -name "*.whl" > requirements.txt
cd ../../ # back to projects/cdk_app
poetry build-project # need to rebuild since we make changes
source .venv/bin/activate
# --force-reinstall is necessary unless we change the package version
pip install --force-reinstall dist/cdk_app-0.1.0-py3-none-any.whl
```

Now we can deploy again:

```bash
# from the projects/cdk_app/ with the python virtualenv active
cdk deploy
```

It is importan to note that most of this process probably will be part of the DevOps setup, and rarely you will to any of this manually.

**IMPORTANT** the lambda's will fail complaining that they can not find the handler module event if it is include correctly in the lambda package code, for this to work you need `Runtime.PYTHON_3_9` at least


Let's add the last [checkpoint here and commit our changes](https://github.com/ybenitezf/cdk_polylith/commit/e70193a0c53f4cfd404cc00a1c8a382ce560b541).


## Final considerations

- If you manage all your projects in this way, changing or staring a new project is an easy thing: all the repositories will look the same and have the same elements.
- With all the code in the same repository you can see if something will break others parts of the system even if they are deployed separately.
- There is a clear separation between the code and the deploy artifacts


- Thanks to Sebastian Aurei for the revision, corrections and help.
- Thanks David Vujic for this excellent tool.
