"""Skill registry. Maps skill names to instances."""

_registry: dict[str, object] = {}


def register(name: str, skill: object):
    _registry[name] = skill


def get_skill(name: str) -> object | None:
    return _registry.get(name)


def list_skills() -> list[str]:
    return list(_registry.keys())
