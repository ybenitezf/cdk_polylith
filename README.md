## Monorepo architecture for Python code with Polylith and Poetry

By: Yoel Benitez Fonseca

Review and Corrections by: Robmay S. Garcia

This article explores a technique or methodology for achieving a "monorepo" architecture for code by leveraging the [Polylith](https://polylith.gitbook.io/polylith/) philosophy, along with a few [poetry](https://python-poetry.org/docs/) plugins, for implementation in Python CDK applications.

---

## Requirements

Let's go ahead and get our dependencies installed for poetry and the plugins:

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry self add poetry-multiproject-plugin
poetry self add poetry-polylith-plugin
```

You will also need  `AWS CDK` installed on your system. I will recommend you to follow the [requirements section of the aws cdk workshop site](https://cdkworkshop.com/15-prerequisites.html):

```bash
npm install -g aws-cdk
```

Here I leave some additional readings about poetry and its plugins.[multiproject](https://github.com/DavidVujic/poetry-multiproject-plugin) and for [polylith](https://davidvujic.github.io/python-polylith-docs/).


## Starting point

Let's get started. As a starting point we will be using the final version of the CDK Python Workshop. Simply clone the code from the repository  [https://github.com/aws-samples/aws-cdk-intro-workshop/tree/master/code/python/main-workshop](https://github.com/aws-samples/aws-cdk-intro-workshop/tree/master/code/python/main-workshop). Our [first commit](https://github.com/ybenitezf/cdk_polylith/commit/dc0033ffb7bfc30f604692948a9390b228c92af6) will be like this and the resulting source tree should looks like:

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

Now, let's turn this source tree into a poetry project by executing:

```bash
poetry init
```

When asked for the main and development dependencies answer no, we will add then later. The result should look like (`pyproject.toml`):

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

Additionally, let's add a poetry configuration file `poetry.toml` to have poetry build the python virtual environment in the project folder before installing the dependencies. The file content should look like:

```toml
[virtualenvs]
path = ".venv"
in-project = true
```

Create [a commit](https://github.com/ybenitezf/cdk_polylith/commit/08b4391ea1298c86a92ec3c7829dde22bba00113) with what we already have.


## Configuring polylith

Before delving into the code, I strongly recommend you to read the following polylith core concepts: [workspace](https://polylith.gitbook.io/polylith/architecture/2.1.-workspace), [component](https://polylith.gitbook.io/polylith/architecture/2.3.-component), [base](https://polylith.gitbook.io/polylith/architecture/2.2.-base), [project](https://polylith.gitbook.io/polylith/architecture/2.6.-project) and [development project](https://polylith.gitbook.io/polylith/architecture/2.4.-development) taking into account that the [python-polylith](https://github.com/DavidVujic/python-polylith) is an adaptation of those concepts for Python.

For those of you who are impatient, running the following command (only once) in our repository will create the necessary folder structure for our project:

```bash
poetry poly create workspace --name="cdk_workshop" --theme=loose
```

> **note**: The `--name` parameter here will set the base package structure, all the code then will be imported from this namespace, for example `from cdk_workshop ...` for more details on this read the [official documentation](https://davidvujic.github.io/python-polylith-docs/)

After running the above command our source tree will look like this, note the new folders created (bases, components, development, and projects):

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

The `workspace.toml` file will configure the behavior of the `poetry poly ...` commands

Let's create a new [ commit](https://github.com/ybenitezf/cdk_polylith/commit/bfc66d18ba91139e46251e446f2fbb3d14253f67). From now on, we will be moving the old code to this new structure.


## Managing project requirements.

Before we go any further let's install the poetry project:

```bash
poetry install
```

> **note**: ignore the warning about the project not containing any element's

And now we move our dependencies from `requirements.txt` and `requirements-dev.txt` to the `pyproject.toml` format:

```bash
poetry add aws-cdk-lib~=2.68
poetry add 'constructs>=10.0.0,<11.0.0'
poetry add cdk-dynamo-table-view==0.2.438
```

And for dev requirements:

```bash
poetry add pytest==7.2.2 -G dev
```

Now we can remove  `requirements.txt` and `requirements-dev.txt` files because they will be managed by the `pyproject.toml`. The content of the file will now look like:

![pyproject.toml after adding the requirements](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ows5ycgnhoek2ell67sc.png)

All the [changes will be visible in this commit](https://github.com/ybenitezf/cdk_polylith/commit/a05638728e299fadd5f7498e00abcb648956d590).

> **note**: Poetry developers recommend to add the `poetry.lock` to the repository. Other developers have reported problems with architecture changes and the `.lock` file, so I will leave it up to you to decide if you want to use it or not.


# Components

From the polylith documentation (https://polylith.gitbook.io/polylith/architecture/2.3.-component):

> A component is an encapsulated block of code that can be assembled together with a base (it's often just a single base) and a set of components and libraries into services, libraries or tools. Components achieve encapsulation and composability by separating their private implementation from their public interface.

So in CDK term's our component should be _Stacks_ or _Constructs_ since this are the reusable parts.

In this application we have the `HitCounter` construct and the `CdkWorkshopStack` stack, lets add them as components to our project:

```
poetry poly create component --name hit_counter
poetry poly create component --name cdk_workshop_stack
```

We will get a new directory under `components` with the name of the workspace (`cdk_workshop`) and under this a python package for each of the components. The same has happened to the tests folder (that is why we used `--theme=loose` when creating the workspace).

Next, we need to modify `pyproject.toml` to recognize this components. Edit and add the following to the package property in the `[tool.poetry]` section:

```toml
packages = [
    {include = "cdk_workshop/hit_counter", from = "components"},
    {include = "cdk_workshop/cdk_workshop_stack", from = "components"}
]
```

To make sure all is fine, run:

```bash
poetry install && poetry run pytest test/
```

if we run  `poetry poly info` we will see our new components listed under the bricks section

![poetry poly info](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/4ff7di6dixc18qoklswk.png)

Alright, let's [commit this changes](https://github.com/ybenitezf/cdk_polylith/commit/b77d8d5272bd629efb3588d6df151e19079c8061) before moving into the code.

### The `hit_counter` component

Now that we have a `HitCounter` construct, we will copy the code in `cdk_workshop/hitcounter.py` to `components/cdk_workshop/hit_counter/core.py` by executing:

```bash
cp cdk_workshop/hitcounter.py components/cdk_workshop/hit_counter/core.py
git rm cdk_workshop/hitcounter.py
```

The code in this construct will need additional refactoring but we will come back to it later, for now we [commit this change as is](https://github.com/ybenitezf/cdk_polylith/commit/9e17a1f7ff9e2537453ee7e80bacfd665d10a647).

### The `cdk_workshop_stack` component

We repeat the same process for the  `CdkWorkshopStack` component, just change the file name and destination as shown below:

```
cp cdk_workshop/cdk_workshop_stack.py components/cdk_workshop/cdk_workshop_stack/core.py
git rm cdk_workshop/*
```

Now, pay attention to this little but important detail. There is a dependency between both components, `cdk_workshop_stack` needs the construct defined in `hit_counter` so we need to edit `components/cdk_workshop/cdk_workshop_stack/core.py` file to fix the import statement as shown in line 8 of the following snippet:

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

> **Note**: Now we are able to use the fully qualified path to the class component like (`cdk_workshop.hit_counter.core`). The path is composed by `cdk_workshop` the workspace, `hit_counter` the component, and `core` the module in `hit_counter`.

Let's add [another commit](https://github.com/ybenitezf/cdk_polylith/commit/c57b58c0a0f15044f59dbb52c6d981ba83d02165).


## Bases

From the polylith documentation (https://polylith.gitbook.io/polylith/architecture/2.2.-base), *bases* are the building blocks that exposes a public API to the outside world.

> A base has a "thin" implementation which delegates to components where the business logic is implemented.
> A base has one role and that is to be a bridge between the outside world and the logic that performs the "real work", our components. Bases don't perform any business logic themselves, they only delegate to components.

So, in the context of the AWS CDK application the candidate for a base will be the module that defines the application and do the synthesis, in other words the code that now resides on `app.py`.

Let's add a base to the project:

```bash
poetry poly create base --name workshop_app
```

Like in the case of the components, the previous command, will add a new package but in the bases directory. This time, under the path `bases/cdk_workshop/workshop_app` with a module for us to define the code of our base - `poetry poly` will add a demo test code too.

We need to alter our package list on `pyproject.toml` to add the newly created base to the Python project:

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

The file content should look like:

```python
import aws_cdk as cdk

from cdk_workshop.cdk_workshop_stack.core import CdkWorkshopStack

app = cdk.App()
CdkWorkshopStack(app, "cdk-workshop")

app.synth()

```

The result can be seen [in this commit](https://github.com/ybenitezf/cdk_polylith/commit/db9974030b63d42d519fd5ea1de9969ccc40e087).

If you run `poetry poly info` you should see something like this:

![Workspace Summary](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/143ofyw8wag2y2dta7hk.png)


### Remarks 

I suggest the use of a single base for each cdk application, but if more than one is necessary, each base should reuse the stacks and constructs defined in the components.

If you are facing a large CDK project, I recommend maintaining a single component package (a single component in polylith is a python package) for all the constructs, one construct per module. And a component for each Stack, the reason being to maintain a single source of dependencies between the components in the project: `construct component ->  stack component` assuming the stack's components do not depend on the others stack components.


## Projects

> Projects configure Polylith's deployable artifacts.

In other words, projects define what we deploy, we combine one (or several bases but that's rare) base and several components into an artifact that allow us to deploy our code.

In polylith the projects live in the `projects` folder and they ***should not contain code*** unless such code is related to the deployment or building of the artifacts, in other words ***no python code there***.

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

Note the content of the `"app"` key, we've removed `app.py` and now we need to do something else, beginning by adding a new project to our polylith repository:

```bash
poetry poly create project --name cdk_app
```

The project name can be anything you need or want, this will be used to build a python package. Now the projects folder have a new subfolder `cdk_app` with a `pyproject.toml` file on it. In this file is where we combine our bases and components to build the artifact to deploy. Edit this file to add our include statements under the `package` property as shown below:

```toml
packages = [
    {include = "cdk_workshop/workshop_app", from = "../../bases"},
    {include = "cdk_workshop/hit_counter", from = "../../components"},
    {include = "cdk_workshop/cdk_workshop_stack", from = "../../components"}
]
```

Note that we've added a `../../` to bases and components because this pyproject file is two levels down in the path

Next, we need to add the necessary dependencies form the `pyproject.toml` in the root folder, from there we only copy what we need for the bases and components, no dev dependencies.

```toml
[tool.poetry.dependencies]
python = "^3.10"
aws-cdk-lib = ">=2.68,<3.0"
constructs = ">=10.0.0,<11.0.0"
cdk-dynamo-table-view = "0.2.438"
```

The final result should be something like:

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

![Workspace Summary](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/2qycwdgpi3fqult0mjwp.png)

As you can see a new column has appeared and the bricks (bases and components) used by the project are marked.

Next, move the `cdk.json` file to the project folder
```bash
mv cdk.json projects/cdk_app/cdk.json
```

But because we move our app object to the `bases/cdk_workshop/workshop_app/core.py` module we need to edit `cdk.json` and change the `app` entry to:

```
  "app": "python3 -m cdk_workshop.workshop_app.core"

```

Let's add a [checkpoint here and commit our changes](https://github.com/ybenitezf/cdk_polylith/commit/8a581b042588a0ec0271047fa293d143df0235fc).


## cdk project new home

At this point we should be able to deploy our CDK application (theoretically speaking), let's test that assumption:

```bash
cd projects/cdk_app
poetry build-project
```

This `build-project` command will create a `dist` directory under `projects/cdk_app` containing the python package.

> This new directory need to be include in the `.gitignore` file. To make this step simpler, copy the content of the [recommended gitignore for python](https://github.com/github/gitignore/blob/main/Python.gitignore) file and add it to the .gitignore in the repository root as shown in [this example commit](https://github.com/ybenitezf/cdk_polylith/commit/0c0eda0cf6f2d75e6899a8e18b2374663d4a8b8d).

![Here is a view of the project folder file tree](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/h1tz7t111dvxwnzv2li9.png)

This python package contains our CDK app. So, to test our theory we need to created a python virtual env, install this package, and run `cdk synth` (under the `projects/cdk_app` folder) to see the CloudFormation template:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install dist/cdk_app-0.1.0-py3-none-any.whl
cdk synth
```

But wait, we get and error. Something like:

```
RuntimeError: Cannot find asset at cdk_polylith/projects/cdk_app/lambda
```

The root cause for this error is that the previous implementation assumed that any cdk command would be execute on the root of the repository but our app has been moved to `projects/cdk_app`. To fix this, we need to move the `lambda` folder under `projects/cdk_app` and run `cdk synth` again:

```bash
cd ../../
mv lambda/ projects/cdk_app/
cd projects/cdk_app/
cdk synth
```

Now all should work great!!! ... ummm no, not really. The idea behind polylith is that all code should live in the components or bases folders.

So, let's go back, discard these last changes and solve this problem in the polylith way - (don't forget to exit the venv created for the `cdk_app` project).


## Include lambda functions code, the polilyth way.

In this project we have 2 lambdas:

```
./lambda/
├── hello.py
└── hitcount.py
```

The plan here is to add to bases (one for each function) to the project. Both are pretty simple, only `hitcount.py` have an external dependency to boto3.

Let's add the bases first:

```
poetry poly create base --name hello_lambda
poetry poly create base --name hitcounter_lambda
```

> **Note**: If these functions shared code (e.g: something that could be refactored so that they both use it), it would be a good idea to add a new component for this feature.

Next, we add this new bases to the main `pyproject.toml` packages property:

```toml
packages = [
    {include = "cdk_workshop/workshop_app", from = "bases"},
    {include = "cdk_workshop/hello_lambda", from = "bases"},
    {include = "cdk_workshop/hitcounter_lambda", from = "bases"},
    {include = "cdk_workshop/hit_counter", from = "components"},
    {include = "cdk_workshop/cdk_workshop_stack", from = "components"}
]
```

Adding any dependencies too:

```
poetry add boto3
```

Run `poetry install && poetry run pytest test/` to ensure all is correct.

Now, let's move the code:

```bash
mv lambda/hello.py bases/cdk_workshop/hello_lambda/core.py
mv lambda/hitcount.py bases/cdk_workshop/hitcounter_lambda/core.py
rm -rf lambda/
```

Let's add a [checkpoint here and commit our changes](https://github.com/ybenitezf/cdk_polylith/commit/61d24f3917fb90a822bfca542bfa1576c01dc3a7).

The trick now is to generate a python package for each lambda function and use the bundling options of the lambda cdk construct to inject our code and requirements for the lambdas. Let's begin by adding the projects for each lambda:

```bash
poetry poly create project --name hello_lambda_project
poetry poly create project --name hitcounter_lambda_project
```

Similar to the `cdk_app`, the `projects/hello_lambda_project/pyproject.toml` should reference the corresponding `hello_lambda` base:

```toml
...

packages = [
    {include = "cdk_workshop/hello_lambda", from = "../../bases"}
]

...
```

And, the same for `projects/hitcounter_lambda_project/pyproject.toml` for `hitcounter_lambda` - including the dependency for `boto3`:

```toml
packages = [
    {include = "cdk_workshop/hitcounter_lambda", from = "../../bases"}
]

[tool.poetry.dependencies]
python = "^3.10"
boto3 = "^1.26.123"

```

In the `CdkWorkshopStack` file code we change the lambda function definition to:

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

Note the `handler` declaration, like in `cdk.json` file we are using the package fully qualified namespace to declare our handler. The `_lambda.Runtime.PYTHON_3_9.bundling_image` property will build the lambda distribution using a `requirements.txt` file that we will generate.

Let's repeat the process for the `hitcounter_lambda`. In `components/cdk_workshop/hit_counter/core.py` we change:

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

Add the required folders (assets folders) to the `cdk_app` project.

```
mkdir -p mkdir -p projects/cdk_app/lambda/{hello,hitcounter}
touch projects/cdk_app/lambda/{hello,hitcounter}/requirements.txt
```

Alright, time for a [checkpoint and commit our changes](https://github.com/ybenitezf/cdk_polylith/commit/61d24f3917fb90a822bfca542bfa1576c01dc3a7).

Ok, let's try the deploy again. First, we build the lambda packages:

```bash
cd projects/hello_lambda_project
poetry build-project
cd ../hitcounter_lambda_project/
poetry build-project
cd ../../
```

Our projects folder structure should look like this:

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

> note: `Runtime.PYTHON_3_9.bundling_image` will fail if any of the packages need a greater version of python.

Now we can deploy again:

```bash
# from the projects/cdk_app/ with the python virtual env active
cdk deploy
```

It is important to note that most of this process is probably part of the DevOps setup, and rarely you will have to do any of this manually. But hey! it is better to know where things come from and be able to fix it than waiting on somebody else to fix it for you.

**IMPORTANT**, the lambdas will fail complaining that they can not find the handler module event if it is included correctly in the lambda package code. For this to work you'll need `Runtime.PYTHON_3_9` at least


Let's add the last [checkpoint here and commit our changes](https://github.com/ybenitezf/cdk_polylith/commit/e70193a0c53f4cfd404cc00a1c8a382ce560b541).


## Final considerations

- This monorepo methodology makes it easy to start a new project or change an existing one.
- All your repositories will look consistent with the same structure and elements.
- With all the code in the same repository you can detect if something could potentially break other parts of the system even if they are deployed separately.
- Last but not least, there is a clear separation between the code and the deploy artifacts


I hope this article help you improve your coding skills, make your projects more organized and professional, and save you some time in the future.
Go do something fun with that extra time.

Until the next post,
Take care and happy coding.

## Acknowledgments

Thanks to Robmay S. Garcia for the review, corrections and help.

Thanks [David Vujic](https://github.com/DavidVujic) for this excellent tool.