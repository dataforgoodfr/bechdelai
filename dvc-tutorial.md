# DVC

## Use case

One of the main uses of DVC repositories is the **versioning of data and model files**.

The repository would have **all the metadata and change history** for the data it tracks. We could see who changed what and when, and use pull requests to update data like we do with code. This is what we call a data registry

Advantages of data registries:
- **Reusability**: reproduce and organize feature stores with a simple CLI (`dvc get` and `dvc import` commands).
- **Persistence**: remote storage (e.g. an S3 bucket) tracked by the DVC registry improves data security.
- **Storage optimization**: centralize data shared by multiple projects in a single location (distributed copies are possible too). This simplifies data management and optimizes space requirements.
- **Data as code**: leverage Git workflows such as commits, branching, pull requests, reviews, and even CI/CD for your data lifecycle. Think "Git for cloud storage".
- **Security**: registries can be setup with read-only remote storage (e.g. an HTTP server).

## Adding new files

Adding datasets to a registry can be as simple as placing the data file or directory in question inside the workspace, and track it with `dvc add`.

A regular Git workflow can be followed with the `.dvc` files that **substitute the actual data** (e.g. music/songs.dvc below).

The actual data is stored in the **project's cache**, and can be pushed to one or more **remote storage locations** so the registry can be accessed from other locations and by other people with `dvc push`

## Using registry

The **main methods** to consume artifacts from a data registry are the `dvc import` and `dvc get` commands, as well as the Python API `dvc.api`

### Listing data

`dvc list -R https://github.com/dataforgoodfr/bechdelai`

### Data downloads

To get a dataset from a DVC repo, we can run something like this:

`dvc get https://github.com/dataforgoodfr/bechdelai data/audio`

This downloads data/audio from the project's default remote and places it in the current working directory.

### Data import

`dvc import` uses the same syntax as dvc get

Besides downloading the data, importing saves the information about the dependency that the local project has on the data source (registry repo).

### Using DVC data from Python code

```
import dvc.api.open

model_path = 'model.pkl'
repo_url = 'https://github.com/example/registry'

with dvc.api.open(model_path, repo_url) as fd:
    model = pickle.load(fd)
    # ... Use the model!
```

See also the `dvc.api.read()` function.

## Updating registry

Just change the data in the registry, and apply the updates by running `dvc add`.

DVC modifies the corresponding .dvc file to reflect the changes, and this is picked up by Git

And let's not forget to `dvc push` data changes to the remote storage, so others can obtain them!

## More info
[DVC Documentation](https://dvc.org/doc/use-cases/data-registries)