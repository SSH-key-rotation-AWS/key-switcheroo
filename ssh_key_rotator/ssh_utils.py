import functools
from unittest import IsolatedAsyncioTestCase
from tempfile import TemporaryDirectory
from paramiko import RSAKey
from ssh_key_rotator.connections import ServerContext, Client
from ssh_key_rotator.util import get_default_authorized_keys_path
from ssh_key_rotator.custom_keygen import generate_private_public_key_in_file

def with_ssh_server(port: int, authorized_keys_path = get_default_authorized_keys_path()):
    def decorator_server(func):
        @functools.wraps(func)
        async def test_with_server(*args, **kwargs):
            async with ServerContext(port):
                return func(*args, *kwargs)
        return test_with_server
    return decorator_server

def with_ssh_server_and_client(port: int):
    def ssh_server_and_keys_decorator(func):
        @functools.wraps(func)
        async def generate_keys_wrapper(*args, **kwargs):
            with TemporaryDirectory() as mock_home_dir:
                #shutil.chown(mock_home_dir, get_username(), group=get_username())
                #os.chmod(mock_home_dir, 0o700)
                ssh_dir = mock_home_dir
                #os.mkdir(ssh_dir)
                #os.chmod(ssh_dir, 0o700)
                public_key = generate_private_public_key_in_file(ssh_dir)
                authorized_keys_path = f"{ssh_dir}/authorized_keys"
                with open(authorized_keys_path, mode="wb") as authorized_keys_file:
                    authorized_keys_file.write(public_key)
                #shutil.chown(authorized_keys_path, get_username(), get_username())
                #os.chmod(authorized_keys_path, mode=0o600)
                async with ServerContext(port=2900, authorized_keys_file=authorized_keys_path):
                    #key = RSAKey.from_private_key_file(f"{ssh_dir}/key")
                    client = Client("127.0.0.1",2900,"yginsburg")
                    client.connect_via_key(key_location=ssh_dir)
                    kwargs["client"] = client
                    return func(*args, **kwargs)
        return generate_keys_wrapper
    return ssh_server_and_keys_decorator

#DOES NOT WORK YET, DO NOT USE
# def SSHTestCase(port:int):
#     def class_decorator(cls):
#         methods_in_base_class = {func for func in dir(IsolatedAsyncioTestCase) if callable(func)}
#         methods_in_this_class = {func for func in dir(cls) if callable(func) and not func.startsWith("__")}
#         test_methods = methods_in_this_class.difference(methods_in_base_class)
#         @functools.wraps(cls)
#         def class_wrapper(*args, **kwargs):
#             print('At wrapper')
#             for base_class_method in methods_in_base_class:
#                 cls.setattr(cls, base_class_method, base_class_method)
#             for test_method in methods_in_this_class:
#                 print(test_method)
#                 cls.setattr(cls, test_method, with_ssh_server(port)(test_method))
#             return cls(*args, **kwargs)
#         return class_wrapper
#     return class_decorator