from pathlib import Path
from hamcrest import assert_that, equal_to
from tests.switcheroo.base import Person
from tests.switcheroo.base.conftest import (
    PersonGenerator,
    PersonReader,
    PersonPublisher,
    PersonLocator,
)
from tests.switcheroo.base import HasFileMode
from switcheroo.base.data_store import FileDataStore


def test_publish(
    file_datastore: FileDataStore,
    person_generator: PersonGenerator,
    read_person_from_file: PersonReader,
):
    generated_person = person_generator()
    # Publish the person
    file_datastore.publish(generated_person, generated_person.relative_loc)
    # Read the person
    person_stored = read_person_from_file(generated_person)
    assert_that(person_stored, equal_to(generated_person))


def test_retrieve(
    file_datastore: FileDataStore,
    person_generator: PersonGenerator,
    publish_person_to_file: PersonPublisher,
):
    generated_person = person_generator()
    # Publish the person
    publish_person_to_file(generated_person)
    # Read the person
    person_stored = file_datastore.retrieve(generated_person.relative_loc, Person)
    assert_that(person_stored, equal_to(generated_person))


def test_can_specify_file_permissions(
    file_datastore: FileDataStore,
    person_generator: PersonGenerator,
    person_locator: PersonLocator,
):
    file_datastore.register_file_permissions(
        Person, FileDataStore.FilePermissions(0o755)
    )
    generated_person = person_generator()
    # Publish the person
    file_datastore.publish(generated_person, generated_person.relative_loc)
    # Check file permissions
    person_absolute_location = Path(person_locator(generated_person))
    assert_that(person_absolute_location, HasFileMode(755))


def test_default_file_permissions_are_777(
    file_datastore: FileDataStore,
    person_generator: PersonGenerator,
    person_locator: PersonLocator,
):
    generated_person = person_generator()
    # Publish the person
    file_datastore.publish(generated_person, generated_person.relative_loc)
    # Check file permissions
    person_absolute_location = Path(person_locator(generated_person))
    assert_that(person_absolute_location, HasFileMode(777))
