from hamcrest import assert_that, equal_to
from tests.switcheroo.base.resources import Person
from tests.switcheroo.base.conftest import PersonReader, PersonPublisher
from switcheroo.base.data_store.s3 import S3DataStore


def test_publish(
    s3_datastore: S3DataStore,
    rand_person: Person,
    read_person_from_s3: PersonReader,
):
    # Publish the person
    s3_datastore.publish(rand_person, rand_person.relative_loc)
    # Read the person
    person_stored = read_person_from_s3(rand_person)
    assert_that(person_stored, equal_to(rand_person))


def test_retrieve(
    s3_datastore: S3DataStore,
    rand_person: Person,
    publish_person_to_s3: PersonPublisher,
):
    # Publish the person
    publish_person_to_s3(rand_person)
    # Read the person
    person_stored = s3_datastore.retrieve(rand_person.relative_loc, Person)
    assert_that(person_stored, equal_to(rand_person))
