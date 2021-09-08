# PyUpdater GCS Plugin

A plugin for PyUpdater that allows for GCS storage of packages.

## Before you begin
To use this plugin, you'll first need to create a GCS bucket to store your builds, and create a service account that has read/write permissions on the bucket. In most cases, you will probably want the bucket to be publicly readable, as this is where PyUpdater will download from. Download the JSON credentials file for the service account, it will be used in the setup process later.

## Usage
If you haven't done so already, flollow the [pyupdater setup guide][pyupdater] to create a pyupdater repo for your project

Install this plugin via pip:

```shell
pip install pyupdater-gcs-plugin
```

Once installed in a pyupdater repo, configure the plugin:

```shell
pyupdater settings --plugin gcs
```

You will be asked for the following information:
1. The name of the bucket to store completed builds in
2. A bucket key. This is the path within the bucket to store builds. It can be left blank if you want to store builds in the root of the bucket.
3. The path to the Google Application Credentials file for the service account that you downloaded earlier. Note that this plugin will respect the `GOOGLE_APPLICATION_CREDENTIALS` environment variable if it is set.

The plugin should be successfully configured at this point. Once a project build has been completed, processed, and signed, you can upload it by running

```shell
pyupdater upload --service gcs
```


[pyupdater]: https://www.pyupdater.org/usage-cli/
