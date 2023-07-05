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
6. [Contributing](#contributing-to-key-switcheroo)


## What is it?

**key-switcheroo** is a Python package that provides tools for **easy** :smile:, **reliable** :white_check_mark:, and **secure** :lock: SSH key management. The package contains tools to allow users to generate SSH public/private key pairs and securely store the public key either on AWS S3 or locally based on user preferences. The package also contains a tool used by the server host to retrieve and match the public keys with the corresponding private key during SSH connection attempts. Additionally, the package includes a feature for periodic rotation and swapping of public keys to enhance security.


## Features

### Publisher

The *publisher* tool offers a user-friendly interface to securely generate SSH public/private key pairs. It allows users to specify the storage location for the public key, either on AWS S3 or on their local machine. The generated private key is stored securely and can be used for SSH authentication.

### Retriever

The *retriever* tool is designed to be used by server hosts for retrieving the public keys stored by the *publisher*. When an SSH connection attempt is made, the *retriever* fetches the corresponding public key associated with the private key used in the connection attempt. The tool compares the retrieved public key with the provided public key, ensuring a secure and authenticated connection.

### Key rotation

To enhance security, **key-switcheroo** includes a key rotation feature. The program periodically swaps and rotates the stored public keys. This process helps mitigate the risks associated with long-term key exposure and strengthens the overall security posture.


## Where to get it

The source code is currently hosted on GitHub at: https://github.com/SSH-key-rotation-AWS/team-henrique

Binary installer for the latest released version is available at the [Python Package Index (PyPI)](https://pypi.org/project/key-switcheroo/).

`pip install key-switcheroo`


## How to use

Once the package is installed, commands can be called from the user's CLI for both the *publisher* and *retriever* using different optional arguments.

For help with command-line arguments,

`switcheroo --help` or `switcheroo -h`

### Publisher

When using the *publisher* for creating and publishing new SSH keys, the user has a couple of different *optional* arguments, in addition to the *required* arguments.

**Required Arguments:**
1. `hostname`
2. `user`

**Optional Arguments:**
- `--datastore local` or `-ds local`
- `--datastore s3` or `-ds s3`
    - If `s3` is selected, the user MUST also input `--bucketname`, followed by a name for their S3 bucket
    - If no `--datastore` is selected, the program will default to `s3`


### Retriever




## Dependencies

- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - Adds support for publishing public SSH keys to S3 using the AWS SDK for Python
- [pycryptodome](https://pycryptodome.readthedocs.io/en/latest/) - Provides tools for generating secure public/private SSH key pairs


## Contributing to key-switcheroo

Contributions to **key-switcheroo** are welcome! If you encounter any issues, have suggestions, or would like to add new features, please feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/SSH-key-rotation-AWS/team-henrique).