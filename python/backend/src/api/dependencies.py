from typing import Type, TypeVar

from fastapi import FastAPI

T = TypeVar("T")


def inject_dependency(app: FastAPI, type_: Type[T], value: T):
    if not hasattr(app.state, "dependencies"):
        app.state.dependencies = {}

    if not isinstance(value, type_):
        raise ValueError("value needs to be an instance of type_")

    app.state.dependencies[type_] = value


# NB: Prefer extractors over this function.
# See `ApiStateExtractor` in `src/api/state.py` for an example.
def get_dependency(app: FastAPI, type_: Type[T]) -> T:
    value = app.state.dependencies[type_]
    if not isinstance(value, type_):
        raise ValueError(
            "The dependency that was found under the key type_ is not an instance of"
            " type_"
        )
    return value
