# key-switcheroo: SSH key rotator toolkit


## Table of Contents
1. [What is it?](#what-is-it)
2. [Features](#features)
    1. [Publisher](#publisher)
    2. [Retriever](#retriever)
    3. [Key Rotation](#key-rotation)
3. [Where to get it](#where-to-get-it)
4. [How to use](#how-to-use)
    1. [Publisher](#publisher-1)
    2. [Retriever](#retriever-1)
5. [Dependencies](#dependencies)
6. [Configuring your SSHD](#configuring-your-sshd)
7. [Contributing](#contributing-to-key-switcheroo)


## What is it?

**key-switcheroo** is a Python package that provides tools for **easy** :smile:, **reliable** :white_check_mark:, and **secure** :lock: SSH key management. The package contains tools to allow users to generate SSH public/private key pairs and securely store the public key either on AWS S3 or locally based on user preferences. The package also contains a tool used by the server host to retrieve and match the public keys with the corresponding private key during SSH connection attempts. Additionally, the package supports a feature for periodic rotation and swapping of public keys to enhance security.


## Features

### Publisher

The *publisher* tool offers a user-friendly interface to securely generate SSH public/private key pairs. It allows users to specify the storage location for the public key, either on AWS S3 or on their local machine. The generated private key is stored securely and can be used for SSH authentication.

### Retriever

The *retriever* tool is designed to be used by server hosts for retrieving the public keys stored by the *publisher*. When an SSH connection attempt is made, the *retriever* fetches the corresponding public key associated with the private key used in the connection attempt. The tool compares the retrieved public key with the provided public key, ensuring a secure and authenticated connection.

### Key rotation

To enhance security, **key-switcheroo** supports a key rotation feature. The user simply needs to call the publisher script again with the same credentials and the program will swap and rotate the stored public keys. This process helps mitigate the risks associated with long-term key exposure and strengthens the overall security posture.


## Where to get it

The source code is currently hosted on GitHub at: https://github.com/SSH-key-rotation-AWS/key-switcheroo

Binary installer for the latest released version is available at the [Python Package Index (PyPI)](https://pypi.org/project/key-switcheroo/).

`pip install key-switcheroo`


## How to use

Once the package is installed, commands can be called from the user's CLI for both the *publisher* and *retriever* using different optional arguments.

For help with command-line arguments,


`switcheroo_publish --help` or `switcheroo_publish -h`

`switcheroo_retrieve --help` or `switcheroo_retrieve -h`

### AWS Profile Management

Switcheroo uses its own AWS profile management system. This can be accessed by the base command `switcheroo_configure`. Run `switcheroo_configure -h` to get help.

The following command is used to create a profile, which is automatically used:

`switcheroo_configure add --access-key [access key] --secret-access-key [secret access key] --region [region]`

If multiple profiles are added, you can select which one to use with `switcheroo_configure select`, delete one with
`switcheroo_configure delete`, and view your profiles with `switcheroo_configure view`.

### Publisher

When using the *publisher* for creating and publishing new SSH keys, the user has a couple of different *optional* arguments, in addition to the *required* arguments.

**Required Arguments:**
1. `hostname` - host server. This is the return value of [`socket.getfqdn()`](https://docs.python.org/3/library/socket.html#socket.getfqdn).
2. `user` - username of the connecting client

**Optional Arguments:**
- `--datastore local` or `-ds local`
    - Stores the public key on the local file system
- `--datastore s3` or `-ds s3`
    - Stores the public key in an S3 bucket
    - If `s3` is selected, the user MUST also input `--bucket`, followed by a name for their S3 bucket
    - If no `--datastore` is selected, the program will default to `s3`
- `--sshdir path/to/key/dir`
    - Input the absolute path to your directory that stores the local keys (private key for S3 publisher)
    - Defaults to local .ssh home directory
- `--metric aws` or `-m aws`
    - Opt to have metrics published to AWS cloudwatch (time to generate keys and key count)
- `--metric file` or `-m file`
    - Opt to have metrics published to the local file system (time to generate keys and key count)
    - If `file` is selected, the user CAN also input `--metricpath`, followed by path to a directory to store the metrics in (default is `{user's home}/switcheroo_app_data/metrics`)


**Example**

`switcheroo_publish 127.0.0.1 johndoe -ds s3 --bucket mybucket --sshdir home/johndoe/.ssh -m aws`

`switcheroo_publish 127.0.0.1 johndoe --datastore local --metric file --metricpath home/switcheroo/metrics`

### Retriever

When using the *retriever* for fetching the public SSH keys, the user has a couple of different *optional* arguments, in addition to the *required* arguments.

**Required Arguments:**
1. `user` - username of the client whose key is being fetched

The `hostname` is assumed to be that of the executing computer, as retrieved by [`socket.getfqdn()`](https://docs.python.org/3/library/socket.html#socket.getfqdn).

**Optional Arguments:**
- `--datastore local` or `-ds local`
    - Retrieves the public key from the local file system
- `--datastore s3` or `-ds s3`
    - Retrieves the public key from the S3 bucket
    - If `s3` is selected, the user MUST also input `--bucket`, followed by their S3 bucket name
    - If no `--datastore` is selected, the program will default to `s3`
- `--sshdir path/to/key/dir`
    - The absolute path to your directory that stores the local keys (private key for S3 publisher)
    - Defaults to local .ssh home directory

**Example**

`switcheroo_retrieve johndoe --datastore s3 --bucket mybucket`

`switcheroo_retrieve johndoe -ds local --sshdir /home/johndoe/.ssh/keys`

## Configuring Your SSHD

If you want to configure your SSHD to use key-switcheroo for SSH connections, follow the following steps:

1. `pip install key-switcheroo`. Note that installing packages onto the system may cause issues, and should be done with care. You may want to consider using `pipx` to isolate the installation in a virtual environment.

2. Configure an AWS profile using `switcheroo_configure add`. Note that the user that configures this profile will be the user retrieving keys - SSH reccomends having a separate user to do this, such as `aws_user`.

3. Open your `sshd_config`, or create a *.conf file in `sshd_config.d`.

4. In the config, add the following two lines:

    `AuthorizedKeysCommand /path/to/python_exec_with_switcheroo_installed switcheroo_retrieve -ds s3 --bucket [your-bucket] %u`

    `AuthorizedKeysCommandUser [your user configured in step 2]`

5. Restart sshd/the system.

That's it! Now, if a public key is published to the bucket, your server will use it for SSH authentication.

## Dependencies

- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - Adds support for publishing public SSH keys to S3 using the AWS SDK for Python
- [pycryptodome](https://pycryptodome.readthedocs.io/en/latest/) - Provides tools for generating secure public/private SSH key pairs


## Contributing to key-switcheroo

Contributions to **key-switcheroo** are welcome! If you encounter any issues, have suggestions, or would like to add new features, please feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/SSH-key-rotation-AWS/key-switcheroo).