from typing import Sequence
import argparse
import sys
from aws_profiles import ProfileManager
from switcheroo.base import Constants


def create_argparser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser()
    sub_parsers = arg_parser.add_subparsers(dest="command", required=True)

    def add_add_subparser():
        add_parser = sub_parsers.add_parser("add", help="Add a profile")
        add_parser.add_argument(
            "--access-key",
            required=True,
            help="The profile's access key",
        )
        add_parser.add_argument(
            "--secret-access-key",
            required=True,
            help="The profile's secret access key",
        )
        add_parser.add_argument("--region", required=True, help="The profile's region")

    def add_delete_subparser():
        delete_parser = sub_parsers.add_parser("delete", help="Delete a profile by ID")
        delete_parser.add_argument(
            "--id",
            required=True,
            type=int,
            help="The profile ID to delete (see the 'view' command)",
        )

    def add_select_subparser():
        select_parser = sub_parsers.add_parser(
            "select", help="Select a profile to use by ID"
        )
        select_parser.add_argument(
            "--id",
            required=True,
            type=int,
            help="The profile to select as the one to use (see the 'view' command)",
        )

    add_add_subparser()
    add_delete_subparser()
    add_select_subparser()
    sub_parsers.add_parser("view", help="View all profiles")
    return arg_parser


def run_with(args: Sequence[str]):
    parser = create_argparser()
    try:
        parsed = parser.parse_args(args)
    except Exception as exc:
        command = " ".join(args)
        raise RuntimeError(
            f"Something went wrong when parsing your command: {command}"
        ) from exc
    command = parsed.command
    profile_manager = ProfileManager(Constants.APP_DATA_DIR)
    if command == "add":
        dict_args = vars(parsed)
        profile_manager.add(
            dict_args["access_key"], dict_args["secret_access_key"], parsed.region
        )
        print("Successfully added new profile!")
    elif command == "delete":
        try:
            profile_manager.remove(parsed.id)
        except KeyError as exc:
            raise RuntimeError(
                "Your input ID ${parsed.id} does not exist - use the view \
command to view your profiles"
            ) from exc
        print(f"Successfully removed profile with id {parsed.id}!")
    elif command == "select":
        profile_manager.select(parsed.id)
        print(f"Now using profile id {parsed.id}.")
    elif command == "view":
        for profile in profile_manager.profiles:
            selected = profile_manager.current_profile == profile
            print(f"ID: {profile.id_number}{' (Selected)' if selected else ''}\n")
            print(
                f"""
                         Access Key: {profile.access_key}
                         Secret Access Key: {profile.secret_access_key}
                         Region: {profile.region}"""
            )
    profile_manager.save()


def run_with_cli():
    run_with(sys.argv[1:])
