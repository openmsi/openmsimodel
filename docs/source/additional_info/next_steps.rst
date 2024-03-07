=============
Next Steps
=============

New GEMD Versions

GEMDLite

Introduce GEMDLite, a lightweight version of GEMD that uses a text-based model building approach.
Utilize global or local stores to instantiate a barebones GEMD model, making it easier for users to get started.

Smaller/Larger GEMD

Explore the possibility of creating versions of GEMD that are smaller or larger in scope, catering to different user needs.

GEMD Attributes, Tags, File Links, and Data Quality

Enhance GEMD with new features related to attributes, tags, file links, and data quality.
Implement checks to ensure files are still present, detect colliding files from different sources, and flag naming inconsistencies and data corruption.

Expanding Tools

Structure Tools

Develop tools like RepeatSequence to find all sequences with the same structure.

Implement MissingSequence to complete a sequence of GEMD objects based on inference from RepeatSequence.

Statistics Tools

Add basic statistical tools (e.g., average, standard deviation) for analyzing GEMD data.

Agents

Introduce an AiAgent that can act on GEMD data using the assets() API, providing advanced data manipulation capabilities.


Real-Time OpenMSIModel / Stateful OpenMSIModel

Implement a stateful OpenMSIModel that can retain its state across multiple operations, enabling real-time data processing.

GUI for Model Visualization and Building

Develop a graphical user interface (GUI) for visualizing and building GEMD models, making it easier for users to interact with the data.

Strategy

Capitalize on stores and GEMDLite to lower the entry barrier and increase the number of users.
Transform GEMD into a graph object with Open Graph: exploring computational tools and Python memory management strategies for graph-based operations.

Benchmarking

Perform benchmarking of Open Graph performance, aiming for 5/6 figure metrics (not cost), such as the number of nodes, to evaluate scalability and efficiency.