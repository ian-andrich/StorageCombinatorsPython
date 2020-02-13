import abc
import json
import os
import pathlib
import pickle
import typing as t


class Reference(object):
    """
    References encode the information about the type of resource and
    the nested path to it.
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
    def put(self, ref: Reference, obj: t.Any):
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

    def put(self, ref: Reference, obj: t.Any):
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


class DiskStoreBase(StorageEndpoint):
    def merge(self, ref: Reference, obj):
        self.put(ref, obj)

    def delete_at(self, ref: Reference):
        pathlib.Path(ref.path).unlink()


class DiskStoreText(DiskStoreBase):
    def __init__(self):
        pass

    def get(self, ref: Reference):
        return pathlib.Path(ref.path).read_text()

    def put(self, ref: Reference, obj):
        # Write as a file with a `.` prepended then moving.
        target_path = pathlib.Path(ref.path)
        temp_path = target_path.with_suffix(".tmp")
        temp_path.write_text(obj)

        try:  # Careful with the transactional semantics
            old_data = None
            if target_path.is_file():  # Just stage old data
                old_data = target_path.read_text()

            temp_path.rename(target_path)
        except Exception as e:
            if old_data is not None:  # Repair old data.
                target_path.unlink()
                target_path.write_text(old_data)
            temp_path.unlink()
            raise e


class DiskStoreBytes(DiskStoreText):
    def get(self, ref: Reference):
        return pathlib.Path(ref.path).read_bytes()

    def put(self, ref: Reference, obj):
        target_path = pathlib.Path(ref.path)
        temp_path = target_path.with_suffix(".tmp")
        temp_path.write_bytes(obj)

        try:  # Careful with the transactional semantics
            old_data = None
            if target_path.is_file():  # Just stage old data
                old_data = target_path.read_bytes()

            temp_path.rename(target_path)
        except Exception as e:
            if old_data is not None:  # Repair old data.
                target_path.unlink()
                target_path.write_bytes(old_data)
            temp_path.unlink()
            raise e


class PassThroughStore(AbstractStorage):
    def __init__(self, store: AbstractStorage):
        self._other = store

    def get(self, ref: Reference):
        return self._other.get(ref)

    def put(self, ref: Reference, obj: t.Any):
        self._other.put(ref, obj)

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

    def put(self, ref: Reference, obj: t.Any):
        self.source.put(self.map_ref(ref), self.map_to_store(obj, ref))

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

    def put(self, ref: Reference, obj: t.Any):
        self.store_for_ref(ref).put(ref, obj)

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


class CacheStore(PassThroughStore):
    def __init__(self, base: AbstractStorage, cache: AbstractStorage):
        self.base = base
        self.cache = cache

    def get(self, ref: Reference):
        try:
            val = self.cache.get(ref)
            if val is not None:
                return val
        except Exception:
            pass  # In case the store throws an error instead of returning None
        # Return to the happy path
        return self.base.get(ref)

    def put(self, ref: Reference, obj: t.Any):
        self.cache.put(ref, obj)
        self.base.put(ref, obj)

    def delete_at(self, ref: Reference):
        self.cache.delete_at(ref)
        self.base.delete_at(ref)

    def merge(self, ref: Reference, obj: t.Any):
        self.cache.merge(ref, obj)
        self.base.merge(ref, obj)


class RelativeStore(BaseMappingStore):
    pass


class FilePathMapper(RelativeStore):
    """
    This file path mapper prepends the given path to the given Reference.

    The default path is the current working directory.
    """

    def __init__(
        self,
        file_store: AbstractStorage,
        base_dir: t.Union[str, pathlib.Path] = os.path.abspath(os.curdir),
    ):
        super().__init__(file_store)
        if isinstance(base_dir, str):
            self.base_dir = pathlib.Path(base_dir)
        elif isinstance(base_dir, pathlib.Path):
            self.base_dir = base_dir
        else:
            raise TypeError(f"Base dir must be str or Path but was {type(base_dir)}")

    def map_ref(self, ref: Reference):
        schema = ref.scheme
        old_path = pathlib.Path(ref.path)
        new_path = self.base_dir / old_path
        return Reference(schema, new_path.as_posix())
