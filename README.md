# Example Release Upload

This is an example of [creating a new release](https://keygen.sh/docs/api/#releases)
and [uploading an artifact](https://keygen.sh/docs/api/#releases-artifacts-upload)
using Keygen's distribution API.

## Running the example

First up, configure a few environment variables:

```bash
# Your Keygen product token. You can generate a product token via the API
# or your admin dashboard.
export KEYGEN_PRODUCT_TOKEN="A_KEYGEN_PRODUCT_TOKEN"

# Your Keygen account ID. Find yours at https://app.keygen.sh/settings.
export KEYGEN_ACCOUNT_ID="YOUR_KEYGEN_ACCOUNT_ID"

# Your Keygen product ID.
export KEYGEN_PRODUCT_ID="YOUR_KEYGEN_ACCOUNT_ID"
```

You can either run each line above within your terminal session before
starting the app, or you can add the above contents to your `~/.bashrc`
file and then run `source ~/.bashrc` after saving the file.

Next, install dependencies with [`pip`](https://packaging.python.org/):

```
pip install -r requirements.txt
```

To create and upload a new release, run the program:

```
python main.py
```

The script will upsert a new `1.0.0` release for `dist/hello-world.txt`,
and upload the `file` to the release's artifact relationship.

## Questions?

Reach out at [support@keygen.sh](mailto:support@keygen.sh) if you have any
questions or concerns!
