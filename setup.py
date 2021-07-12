from setuptools import setup


with open('README.md', 'r') as f:
    readme = f.read()


setup(
    name='PyUpdater-GCS-Plugin',
    version='1.0.0',
    description='GCS plugin for PyUpdater',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Tartan Solutions',
    author_email='charlie.laymon@tartansolutions.com',
    url='https://github.com/PlaidCloud/PyUpdater-gcs-Plugin',
    platforms=['Any'],
    install_requires=['google-cloud-storage'],
    entry_points={
        'pyupdater.plugins.upload': [
            'gcs = gcs_uploader:GCSUploader',
        ],
    },
    py_modules=['gcs_uploader'],
    include_package_data=True,
    zip_safe=False,
)