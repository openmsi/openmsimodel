from pathlib import Path
from openmsimodel.stores.gemd_template_store import GEMDTemplateStore
from openmsimodel.stores.gemd_spec_store import GEMDSpecStore
from abc import ABC, abstractmethod

class StoresConfig(ABC):
    """
    Managing the default configurations for activating store, name of the default store and a list of ids of all template stores

    Example:
    >>> from openmsimodel.stores.gemd_template_store import StoresConfig, stores_config
    >>> stores_config = StoresConfig(activated=True) # default name is local
    >>> stores_config.designated_store_id
    "local"
    >>> stores_config = StoresConfig(activated=True, designated_store_id="local_2")

    """

    all_template_stores: dict
    activated: bool
    designated_store_id: str
    designated_root: str

    def __init__(
        self,
        activated=False,
        designated_store_id: str = "local",
        designated_root: str = Path(__file__).parent / "stores/local",
    ):
        self.all_template_stores = {}
        self.all_spec_stores = {}
        self.template_to_spec_map = {}
        self.run_to_template_map = {}
        self.run_to_spec_map = {}
        self.activated = activated
        if self.activated:
            self.designated_store_id = designated_store_id
            self.designated_root = designated_root
            self.deploy_primary_store(designated_store_id)

    def deploy_primary_store(self, id):
        if id in self.all_template_stores.keys():
            raise NameError(f"template store with id {id} already exists.")
        self.all_template_stores[id] = GEMDTemplateStore(id, root=self.designated_root, stores_config=self, load_all_files=False)
        # self.all_template_stores[id].root = self.designated_root
        # self.all_template_stores[id].initialize_store()
        self.all_spec_stores[id] = GEMDSpecStore(id, root=self.designated_root, stores_config=self, load_all_files=False)
        # self.all_spec_stores[id].root = self.designated_root
        # self.all_spec_stores[id].initialize_store()

    def register_store(self, store):
        if type(store) == GEMDTemplateStore:
            if store.id in self.all_template_stores.keys():
                raise NameError(f"template store with id {store.id} already exists.")
            if self.activated:
                self.all_template_stores[store.id] = store
                self.all_template_stores[store.id].stores_config = self
                self.all_template_stores[store.id].initialize_store()
        if type(store) == GEMDSpecStore:
            if store.id in self.all_spec_stores.keys():
                raise NameError(f"spec store with id {store.id} already exists.")
            if self.activated:
                self.all_spec_stores[store.id] = store
                self.all_template_stores[store.id].stores_config = self
                self.all_spec_stores[store.id].initialize_store()
            


stores_config = StoresConfig()