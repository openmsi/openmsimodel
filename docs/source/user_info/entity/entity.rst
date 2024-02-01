=============
Entity
=============

The 'Entity' API helps manage the layer around your data model to interact with its components as abstractly as possible (scalability), all while extending the capabilities of the model as desired (enhancement).

If your data at production (i.e., in its unedited format) is at level 0 of the data pyramid, and your data under your model of choice is at level 1, the 'Entity' API becomes the second layer, allowing to build on the semantics and rules of your data model while abstracting its specifities to the user. 

Its main class, the 'Element' class, intends to create a wrapper of the most basic elements in your data model of choice. For example, it has an assets() function that will always give you access to the core elements, regardless of the chosen data model.
In our case, GEMD (Graphical Expression of Materials Data) is the main data model, so the 'Gemd_Element' class extend the 'Element' class. It is inherited by the classes 'Process', 'Material', 'Ingredient', and 'Measurement'. 
Hence, instead of interacting and handling a GEMD Process Template, Spec, or Run separately, they can be managed all under one class, 'Process'. The same applies to 'Material', 'Measurement', and 'Ingredient'.
For example, GEMD is a linked model, so we are able to build and adjust links within and between structures as desired.  

wrapper around GEMD objects
has assets() api