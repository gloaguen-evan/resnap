from threading import Thread

from resnap.helpers.singleton import SingletonABCMeta, SingletonMeta


class SingletonMetaClass(metaclass=SingletonMeta):
    pass


class SingletonABCMetaClass(metaclass=SingletonABCMeta):
    pass


def test_single_instance() -> None:
    instance1 = SingletonMetaClass()
    instance2 = SingletonMetaClass()
    assert instance1 is instance2, "SingletonMeta did not return the same instance"


def test_single_instance_abc() -> None:
    instance1 = SingletonABCMetaClass()
    instance2 = SingletonABCMetaClass()
    assert instance1 is instance2, "SingletonMeta did not return the same instance"


def test_thread_safety() -> None:
    instances = []

    def create_instance():
        instances.append(SingletonABCMetaClass())

    threads = [Thread(target=create_instance) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    first_instance = instances[0]
    for instance in instances:
        assert instance is first_instance, "SingletonMeta did not return the same instance across threads"
