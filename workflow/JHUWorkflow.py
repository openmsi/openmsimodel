from .Folder import Folder
from gemd.json import GEMDJson
from collections import defaultdict

#TODO: extend Logging
class Workflow(Folder):
    '''
    mode 1: write everything in build_worfklow_model by (a) defining BaseNode/Block objects or (b) calling custom BaseNode/Block objects
    mode 2: write everything using the add_block method
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
         # blocks and terminal_materials can be overwritten to fit a structure
        self.blocks = defaultdict()
        self.terminal_materials = defaultdict()
        self.encoder = GEMDJson()
        self.output_folder = kwargs['output_folder']
        
    def thin_dumps():
        '''
        '''
        pass 
    
    def dumps():
        '''
        '''
        pass 
    
    def thin_loads():
        '''
        '''
        pass
    
    def loads():
        '''
        '''
        pass
    
    def print_encoded(self, obj):
        print(self.encoder.dumps(obj, indent=3))
    
    def print_thin_encoded(self, obj):
        print(self.encoder.thin_dumps(obj, indent=3))
    
    def build_model():
        '''
        This function builds the entire GEMD model that represents a certain Workflow. 
        It is intended be overwritten by child Workflow objects specific to a user case. 
        '''
        pass 
    
    def add_block():
        '''
        mode 2 
        this like to add an existing block seq.
        should link everything
        '''
        
        pass
    
    def return_run_instance(obj_name, terminal=False):
        '''
        takes terminal param so you can do on any object.
        also can find middle object with name, uids, etc
        '''
        pass 
    
    def return_spec_instance(obj_name, terminal=False):
        pass 
    
    def make_run_instance():
        pass
    
    def make_spec_instance():
        pass