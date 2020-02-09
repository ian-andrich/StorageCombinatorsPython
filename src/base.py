import abc
import json
import pathlib
import pickle
import tempfile
import typing as t


class Reference(object):
    """
    References encode the information about the type of resource and the nested path to it.
    """

    def __init__(self, scheme: str, path: str):
        self.path = path
        self.path_components = self.path.lstrip("/").split("/")
        self.scheme = scheme


class AbstractStorage(abc.ABC):
    @abc.abstractmethod
    def get(self, ref: Reference):
        pass

    @abc.abstractmethod
    def post(self, ref: Reference, obj: t.Any):
        pass

    @abc.abstractmethod
    def merge(self, ref: Reference, obj: t.Any):
        pass

    @abc.abstractmethod
    def delete_at(self, ref: Reference):
        pass


class DictStore(AbstractStorage):
    """
    DictStores are a basic in memory store to use for testing
    """

    def __init__(self):
        self._data = {}

    def get(self, ref: Reference):
        return self._data[(ref.scheme, ref.path)]

    def post(self, ref: Reference, obj: t.Any):
        self._data[(ref.scheme, ref.path)] = obj

    def merge(self, ref: Reference, obj: t.Any):
        self._data[(ref.scheme, ref.path)] = obj

    def delete_at(self, ref: Reference):
        try:
            del self._data[(ref.scheme, ref.path)]
        except Exception:
            pass


class StorageEndpoint(AbstractStorage):
    pass


class DiskStoreText(StorageEndpoint):
    def __init__(self):
        pass

    def get(self, ref: Reference):
        return pathlib.Path(ref.path).read_text()

    def post(self, ref: Reference, obj: str):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            name = f.name
            f.write(obj)

        try:
            pathlib.Path(f.name).rename(ref.path)
        except Exception as e:
            pathlib.Path(name).unlink()
            raise e

    def merge(self, ref: Reference, obj: str):
        self.post(ref, obj)

    def delete_at(self, ref: Reference):
        pathlib.Path(ref.path).unlink()


class DiskStoreBytes(DiskStoreText):
    def get(self, ref: Reference):
        return pathlib.Path(ref.path).read_bytes()

    def post(self, ref: Reference, obj: str):
        with tempfile.NamedTemporaryFile(mode="wb+", delete=False) as f:
            name = f.name
            f.write(obj)

        try:
            pathlib.Path(f.name).rename(ref.path)
        except Exception as e:
            pathlib.Path(name).unlink()
            raise e


class PassThroughStore(AbstractStorage):
    def __init__(self, store: AbstractStorage):
        self._other = store

    def get(self, ref: Reference):
        return self._other.get(ref)

    def post(self, ref: Reference, obj: t.Any):
        self._other.post(ref, obj)

    def merge(self, ref: Reference, obj: t.Any):
        self._other.merge(ref, obj)

    def delete_at(self, ref: Reference):
        self._other.delete_at(ref)


class BaseMappingStore(AbstractStorage):
    """
    This class handles serialization for pulling things and putting things into storage.

    Need to provide instances of the source property and the map_ref, map_retrieved
    and map_to_store functions to implement the functionality.

    Default implementation leaves these as no-ops.
    """

    def __init__(self, store: AbstractStorage, *args, **kwargs):
        self._source = store

    @property
    def source(self) -> AbstractStorage:
        return self._source

    def map_ref(self, ref: Reference) -> t.Any:
        return ref

    def map_retrieved(self, obj: t.Any, ref: Reference):
        return obj

    def map_to_store(self, obj: t.Any, ref: Reference):
        return obj

    def get(self, ref: Reference):
        return self.map_retrieved(self.source.get(self.map_ref(ref)), ref)

    def post(self, ref: Reference, obj: t.Any):
        self.source.post(self.map_ref(ref), self.map_to_store(obj, ref))

    def merge(self, ref: Reference, obj: t.Any):
        self.source.merge(self.map_ref(ref), self.map_to_store(obj, ref))

    def delete_at(self, ref: Reference):
        self.source.delete_at(self.map_ref(ref))


_JSONScalars = t.Union[float, int, str]


class JSONStore(BaseMappingStore):
    """
    The JSON store is responsible for marshalling and unmarshalling json.
    """

    def __init__(self, store=DictStore()):
        super().__init__(store=store)

    def map_to_store(self, obj: t.Any, ref: Reference) -> str:
        return json.dumps(obj)

    def map_retrieved(
        self, obj: t.Any, ref: Reference
    ) -> t.Union[dict, list, _JSONScalars]:
        return json.loads(obj)


class PickleStore(BaseMappingStore):
    """
    The pickle store is responsible for pickling and unpickling objects.
    By default it chooses a dictionary backend, but it is more appropriate
    to choose a file system based store for most use cases.
    """

    def __init__(self, store: AbstractStorage = DictStore()):
        super().__init__(store=store)

    def map_to_store(self, obj: t.Any, ref: Reference) -> bytes:
        return pickle.dumps(obj)

    def map_retrieved(self, obj: bytes, ref: Reference) -> t.Any:
        return pickle.loads(obj)


class Switch(AbstractStorage):
    def __init__(self, backing_storage=DictStore()):
        self._backing_storage = backing_storage

    @property
    def backing_store(self):
        self._backing_storage

    @abc.abstractmethod
    def reference_switch_logic(self, ref: Reference) -> t.Hashable:
        pass

    def store_for_ref(self, ref: Reference) -> AbstractStorage:
        return self.backing_store.get(self.reference_switch_logic(ref))

    def get(self, ref: Reference) -> t.Any:
        return self.store_for_ref(ref).get(ref)

    def post(self, ref: Reference, obj: t.Any):
        self.store_for_ref(ref).post(ref, obj)

    def merge(self, ref: Reference, obj: t.Any):
        self.store_for_ref(ref).merge(ref, obj)

    def delete_at(self, ref: Reference):
        self.store_for_ref(ref).delete_at(ref)


class SchemeSwitch(Switch):
    def __init__(self, backing_store: AbstractStorage = DictStore()):
        super().__init__(backing_storage=backing_store)

    def reference_switch_logic(self, ref: Reference) -> t.Hashable:
        return ref.scheme

    @property
    def backing_store(self) -> AbstractStorage:
        return self._backing_storage


class FirstPathSwitch(Switch):
    def __init__(self, backing_store: AbstractStorage = DictStore()):
        super().__init__(backing_storage=backing_store)

    def reference_switch_logic(self, ref: Reference) -> t.Hashable:
        return ref.path_components[0]
