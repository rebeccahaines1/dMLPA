# Developer

The project has the following structure:

```bash
.dMLPA
    ├── docs
    ├── htmlcov
    ├── output
    ├── dMLPA
    ├── test_data
    └── tests
```

The source code for dMLPA is contained in the dMLPA directory:

```bash

    ├── dMLPA
    │   ├── app.py
    │   ├── backend.py
    │   ├── config.py
    │   ├── environment.yml
    │   ├── __init__.py
    │   └── templates
    └──      └── index.html
```

**dMLPA** contains the majority of the code for processing samples

**report_template.html** is the HTML template for the report.

## Automated Testing Using Pytest

dMLPA has two types of tests

```bash
dMLPA
    └── tests
        ├── functional
        └── unit
```

### Unit Tests

Unit tests are used to test the functionality of individual functions within the script to ensure they return expected results.

### Functional Tests

Functional tests run test data through the software and compare the output to benchmark results.

### Coverage

The amount of code covered by the testing is calculated using coverage.py, the results of which can be found as an HTML report in:

```bash
dMLPA
    └── htmlcov
        └── index.html
```

### Run Tests and Coverage

```bash
# Run the tests use the following command within the local repo:
python -m pytest

# Calculate test coverage and produce HTML report (dMLPA/htmlcov/index.html)
pytest --cov=dMLPA
```

### Debugging Tests

There is a known issue where the VS Code debugger doesn't stop at breakpoints set in pytest test modules if pytest-cov is used to calculate coverage.  This issue also affects PyCharm.  When debugging tests you can manually set the "--no-cov" flag in the VS Code's settings.json as shown below.

```json
{
    "python.testing.pytestArgs": [
        ".",
        "--no-cov",
    ]
}
```

You can then debug the tests using breakpoints.  Remember to change the settings.json back again once the debugging is completed.

## Sphinx Documentation

The documentation for dMLPA is generated using Sphinx.
The docstrings in the python modules are parsed using sphinx-apidoc and are automatically added to the documentation.

### Editing Sphinx Documentation

The source files for the docs are located in the source folder as shown below.  The majority of these source files are in markdown, with some being in rst or HTML.  These files can be edited in a text editor and compiled following the instructions in the next section.  This will build the corresponding HTML files from the source files and store the output in the build folder.

```bash
dMLPA
    └── docs
        ├── apidocs
        ├── build
        └── source
```

### Compiling Sphinx Documentation

```bash
# From within the local repo run the following commands.

# Auto generate documentation from docstrings
sphinx-apidoc -f -o docs/apidocs dMLPA/

# Build documentation from source files
(cd docs && make clean) # Optional - removes any cached html files
sphinx-build -b html docs/source docs/build
```

To view the output open index.html in the build folder.

## Release Process

TODO