from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton
from pipeline import Pipeline


class JobContainer(DeclarativeContainer):
    job_config: Configuration = Configuration()
    test = job_config.test
    pipeline: Pipeline = Singleton(Pipeline)
