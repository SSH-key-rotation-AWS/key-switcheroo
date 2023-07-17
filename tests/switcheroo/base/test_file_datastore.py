from pathlib import Path
from hamcrest import assert_that, equal_to
from tests.switcheroo.base.resources import Person
from tests.switcheroo.base.conftest import (
    PersonReader,
    PersonPublisher,
    PersonLocator,
)
from tests.switcheroo.base import HasFileMode
from switcheroo.base.data_store import FileDataStore


def test_publish(
    file_datastore: FileDataStore,
    rand_person: Person,
    read_person_from_file: PersonReader,
):
    # Publish the person
    file_datastore.publish(rand_person, rand_person.relative_loc)
    # Read the person
    person_stored = read_person_from_file(rand_person)
    assert_that(person_stored, equal_to(rand_person))


def test_retrieve(
    file_datastore: FileDataStore,
    rand_person: Person,
    publish_person_to_file: PersonPublisher,
):
    # Publish the person
    publish_person_to_file(rand_person)
    # Read the person
    person_stored = file_datastore.retrieve(rand_person.relative_loc, Person)
    assert_that(person_stored, equal_to(rand_person))


def test_can_specify_file_permissions(
    file_datastore: FileDataStore,
    rand_person: Person,
    person_locator: PersonLocator,
):
    file_datastore.register_file_permissions(
        Person, FileDataStore.FilePermissions(0o755)
    )
    # Publish the person
    file_datastore.publish(rand_person, rand_person.relative_loc)
    # Check file permissions
    person_absolute_location = Path(person_locator(rand_person))
    assert_that(person_absolute_location, HasFileMode(755))


def test_default_file_permissions_are_777(
    file_datastore: FileDataStore,
    rand_person: Person,
    person_locator: PersonLocator,
):
    # Publish the person
    file_datastore.publish(rand_person, rand_person.relative_loc)
    # Check file permissions
    person_absolute_location = Path(person_locator(rand_person))
    assert_that(person_absolute_location, HasFileMode(777))
