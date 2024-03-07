===============
Stores
===============

The OpenMSIModel framework includes two key components: the StoresConfig class and the GEMDTemplateStore class, both designed to enhance the management and access of GEMD (Generic Model for Data) templates.

The StoresConfig class manages default configurations for activating stores, specifying the default store's name, and maintaining a list of IDs for all template stores. This class is instrumental in configuring and initializing template stores, ensuring they are ready for use within the framework.

On the other hand, the GEMDTemplateStore class serves as a central repository for storing and managing GEMD template objects. It allows for loading templates from files, registering new templates, and accessing existing templates based on their names. The class supports different types of templates, including properties, parameters, conditions, materials, measurements, and processes, making it versatile for various scientific modeling and analysis tasks.

Together, these components provide a robust infrastructure for handling GEMD templates within the OpenMSIModel framework, enabling users to efficiently organize, access, and utilize template data in their scientific projects.