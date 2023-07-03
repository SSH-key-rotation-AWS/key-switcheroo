from pathlib import Path
import shutil
import os
import pkg_resources


class ProdBootstrap:
    appdata_dir = Path("/ssh_key_switcheroo")
    retrieval_script_loc = appdata_dir / "retrieve_public_keys.py"

    @staticmethod
    def _get_username():
        parts = Path("~").expanduser().parts
        return parts[len(parts) - 1]

    @classmethod
    def _ensure_boto3(cls) -> bool:
        return "boto3" in pkg_resources.working_set.entries

    @classmethod
    def _ensure_boto3_credentials(cls) -> bool:
        import boto3  # pylint: disable=import-outside-toplevel

        sts_client = boto3.client("sts")
        try:
            sts_client.get_caller_identity()
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    @classmethod
    def _copy_retriever_script_into_root(cls) -> None:
        root_dir = Path(__file__).parent.parent
        publisher_script: Path = (
            root_dir / "ssh_key_rotator" / "server" / "retrieve_public_keys.py"
        )
        cls.appdata_dir.mkdir(exist_ok=True)
        shutil.copy(publisher_script, cls.retrieval_script_loc)
        cls.retrieval_script_loc.chmod(0o755)
        shutil.chown(cls.retrieval_script_loc, 0, 0)

    @classmethod
    def _copy_sshd_config(
        cls, bucket_name: str | None, python_exec: str, aws_user: str = _get_username()
    ) -> str | None:
        if bucket_name is None:
            bucket_name = os.environ.get("SSH_KEY_DEV_BUCKET_NAME")
            if bucket_name is None:
                return "Bucket name was not passed in nor is it configured as an env variable!"
        sshd_config_target = Path("/etc", "ssh", "sshd_config.d", "ssh_switcheroo.conf")
        sshd_config_base = Path(Path(__file__).parent, "ssh_switcheroo.conf")
        with open(sshd_config_target, mode="w+t", encoding="utf-8") as write:
            with open(sshd_config_base, mode="rt", encoding="utf-8") as read:
                for line in read.readlines():
                    edited_line = (
                        line.replace("[USER]", aws_user)
                        .replace("[BUCKET]", bucket_name)
                        .replace("[EXEC]", python_exec)
                    )
                    write.write(f"{edited_line}\n")
        return None

    @staticmethod
    def _ask(question: str) -> bool:
        print(question+"\n")
        yes_no = input("please respond 'yes' if you are OK with this or 'no' to exit\n")
        return yes_no == "yes"

    @staticmethod
    def _print_separator():
        print("--------------------\n")

    @classmethod
    def run_setup(cls):
        if os.geteuid() != 0:
            print("Please run this script as root. Exiting...")
            return

        python_exec = input(
"""ssh_switcheroo requires boto3 to be installed in order to access AWS.
Please provide an absolute path to your python executable which can import
boto3.

You can reference the system executable if you wish, or create a virtual environment
and reference the executable in /[venv_folder]/bin/python.

To find the system executable, run 'which python'

If you wish to exit now and configure your python executable, type 'exit'.
Otherwise input the *absolute* path to your python executable.\n"""
        )

        if python_exec == "exit":
            print("Exiting...")
            return
        ok_to_use_exec = ProdBootstrap._ask(f"Your python executable: {python_exec}")
        if not ok_to_use_exec:
            print("Exiting...")
            return

        # This doesn't work yet
        # has_boto3 = ProdBootstrap._ensure_boto3()
        # if not has_boto3:
        #     #Presumably this will be better with a proper setup.py
        #     print("Please install boto3. Exiting...")
        #     return

        # valid_credentials = ProdBootstrap._ensure_boto3_credentials()
        # if not valid_credentials:
        #     print("Could not verify your aws credentials. Please ensure they are installed "+
        #           " at $HOME/.aws with aws configure")
        ProdBootstrap._print_separator()
        ok_to_copy = ProdBootstrap._ask(
f"Copying key retrieval script into {cls.retrieval_script_loc}. \
This uses root permissions."
        )
        if not ok_to_copy:
            return
        cls._copy_retriever_script_into_root()
        ProdBootstrap._print_separator()
        ok_to_config = ProdBootstrap._ask(
"""Copying sshd config modification into /etc/ssh/sshd_config.d.
This modifies the system sshd to use our key retrieval script. 

To undo this action, at any time you can simply delete this file and your \
initial configuration will not be harmed."""
        )
        if not ok_to_config:
            return
        ProdBootstrap._print_separator()
        ok_with_settings = False
        bucket = ""
        username = ""
        while not ok_with_settings:
            username = input(
"input the linux user to use for AWS calls. This user should have \
AWS CLI set up.\n"
            )
            if username == "":
                username = ProdBootstrap._get_username()
            ProdBootstrap._print_separator()
            bucket = input(
"input the S3 bucket name for the public keys to be stored in\n"
            )
            ProdBootstrap._print_separator()
            ok_with_settings = ProdBootstrap._ask(
f"""You have selected the following settings:
Python Executable (with boto3): {python_exec}
Linux User: {username if username!="" else ProdBootstrap._get_username()}
S3 Bucket: {bucket}
"""
            )
        cls._copy_sshd_config(bucket, python_exec, username)

        print("Finished configuration!")


if __name__ == "__main__":
    ProdBootstrap.run_setup()
