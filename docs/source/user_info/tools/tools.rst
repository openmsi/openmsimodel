=======
Tools
=======


In our tools section, structures are pivotal components that facilitate the organization and manipulation of data elements within the GEMD (Graphical Expression of Materials Data) framework. These structures are primarily built around the 'Element' class, providing a means to establish logical relationships between various data entities.

For instance, consider the MaterialsSequence, which represents the natural and common sequence of ingredients being used in a process, resulting in the generation of materials, which are then subjected to measurements. This sequence highlights the interconnectedness of these elements within the data model.

Similarly, the MaterialsRepeatedSequence offers a means to group sequences that share a common template across an entire graph. While it may not directly aid in model construction, it serves to streamline data organization and management within the GEMD framework.

These examples demonstrate the versatility of our tools in abstracting the complexities of the initial GEMD layer, allowing users to structure and manipulate data elements efficiently.

Build your GEMD models with our structure (Forward)

Utilize our structures, such as MaterialsSequence, to effectively organize and structure your data objects within the GEMD framework. These structures enable users to establish logical relationships between various data elements, facilitating the construction of comprehensive GEMD models.

Structure your existing GEMD models with our tools (Backward)

Our tools also offer functionalities for structuring existing GEMD models in a backward manner. For example, the 'from_spec_or_run' method allows users to efficiently extract and structure data from specifications or runs within the GEMD framework. This backward structuring aids in organizing and managing existing data sets within the GEMD framework, enhancing overall data coherence and accessibility.
