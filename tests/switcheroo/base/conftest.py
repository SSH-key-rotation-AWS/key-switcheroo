from pathlib import Path
from typing import Callable, TypeAlias, Generator
from tempfile import TemporaryDirectory
import random
import json
import uuid
import pytest
from switcheroo.base.data_store import FileDataStore
from tests.switcheroo.base.resources import Person, PersonSerializer, Figure


@pytest.fixture(name="tmp_pathlib_dir")
def fixture_tmp_pathlib_dir()->Generator[Path, None, None]:
    temp_dir = TemporaryDirectory()
    with temp_dir:
        yield Path(temp_dir.name)

@pytest.fixture(name="file_datastore")
def fixture_file_datastore(tmp_pathlib_dir: Path)->FileDataStore: #Standard pytest tmpdir fixture
    file_ds = FileDataStore(FileDataStore.RootInfo(tmp_pathlib_dir))
    file_ds.register_serializer(Person, PersonSerializer())
    return file_ds

#Utility fixtures for the Person dataclass

PersonGenerator: TypeAlias = Callable[[], Person]
PersonLocator: TypeAlias = Callable[[Person], Path]
PersonReader: TypeAlias = Callable[[Person], Person]
PersonPublisher: TypeAlias = Callable[[Person], None]

@pytest.fixture(name="person_locator")
def fixture_person_locator(tmp_pathlib_dir: Path)->PersonLocator:
    """Fixture to locate the absolute Path of where a Person is stored using the FileDataStore

    Args:
        tmpdir (Path): standard pytest tmpdir fixture - root location for storage

    Returns:
        PersonLocator: A function to locate the absolute path of a Person
    """
    def _locate_person(person: Person)->Path:
        return tmp_pathlib_dir/person.relative_loc
    return _locate_person

@pytest.fixture
def read_person_from_file(person_locator: PersonLocator)->PersonReader:
    """Reads a person from a file based on their expected location via the given PersonLocator

    Args:
        person_locator (PersonLocator): Used to give the absolute path for a Person

    Returns:
        PersonReader: A function to read a person from their expected location
    """
    def _read_person_from_file(person: Person)->Person:
        person_location = person_locator(person)
        with open(person_location, mode="rt", encoding="utf-8") as person_data:
            data_obj = json.load(person_data)
            return Person(data_obj["unique_id"], data_obj["name"], data_obj["age"], data_obj["bio"])
    return _read_person_from_file

@pytest.fixture
def publish_person_to_file(person_locator: PersonLocator)->PersonPublisher:
    def _publish_person_to_file(person: Person):
        person_location = person_locator(person)
        with open(person_location, mode="wt", encoding="utf-8") as person_data:
            json.dump(person.__dict__, person_data)
    return _publish_person_to_file

@pytest.fixture(scope="session", name="person_generator")
def fixture_person_generator()->PersonGenerator:
    names = ["Reuven","Shimon","Levi","Yehuda","Yissachar","Zevulun"]
    colors = ["red","yellow","orange","green","blue","purple"]
    def _person_generator()->Person:
        unique_id = str(uuid.uuid4())
        name = random.choice(names)
        color = random.choice(colors)
        age = random.randint(1,120)
        return Person(unique_id, name, age, f"{name} really likes the color {color}")
    return _person_generator

@pytest.fixture
def rand_person(person_generator: PersonGenerator)->Person:
    return person_generator()

#Utility fixtures for the Figure dataclass
#Very similar to the Person one
FigureGenerator: TypeAlias = Callable[[], Figure]
# FigureLocator: TypeAlias = Callable[[Figure], Path]
# FigureReader: TypeAlias = Callable[[Figure], Figure]
# FigurePublisher: TypeAlias = Callable[[Figure], None]

@pytest.fixture(scope="session", name="figure_generator")
def fixture_figure_generator()->FigureGenerator:
    shapes = ["Square","Circle","Triangle"]
    colors = ["red","yellow","orange","green","blue","purple"]
    def _figure_generator()->Figure:
        unique_id = str(uuid.uuid4())
        shape = random.choice(shapes)
        color = random.choice(colors)
        size = random.randint(1,1000)
        return Figure(unique_id, shape, color, size)
    return _figure_generator

@pytest.fixture
def rand_figure(figure_generator: FigureGenerator)->Figure:
    return figure_generator()



# @pytest.fixture(name="figure_locator")
# def fixture_figure_locator(tmp_pathlib_dir: Path)->FigureLocator:
#     """Fixture to locate the absolute Path of where a Figure is stored using the FileDataStore

#     Args:
#         tmpdir (Path): standard pytest tmpdir fixture - root location for storage

#     Returns:
#         FigureLocator: A function to locate the absolute path of a Figure
#     """
#     def _locate_figure(figure: Figure)->Path:
#         return tmp_pathlib_dir/figure.relative_loc
#     return _locate_figure

# @pytest.fixture
# def read_figure_from_file(figure_locator: FigureLocator)->FigureReader:
#     """Reads a figure from a file based on their expected location via the given FigureLocator

#     Args:
#         figure_locator (PersonLocator): Used to give the absolute path for a Figure

#     Returns:
#         FigureReader: A function to read a figure from their expected location
#     """
#     def _read_person_from_file(figure: Figure)->Figure:
#         figure_location = figure_locator(figure)
#         with open(figure_location, mode="rt", encoding="utf-8") as person_data:
#             data_ob = json.load(person_data)
#             return Figure(data_ob["unique_id"], data_ob["shape"], data_ob["color"], data_ob["size"])
#     return _read_person_from_file

# @pytest.fixture
# def publish_figure_to_file(figure_locator: FigureLocator)->FigurePublisher:
#     def _publish_figure_to_file(figure: Figure):
#         figure_location = figure_locator(figure)
#         with open(figure_location, mode="wt", encoding="utf-8") as figure_data:
#             json.dump(figure.__dict__, figure_data)
#     return _publish_figure_to_file
