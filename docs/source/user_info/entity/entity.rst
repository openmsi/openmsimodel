=============
Entity
=============

The 'Entity' API serves to abstractly manage the layer(s) surrounding your data model, facilitating interaction with its components in a scalable manner, while simultaneously enhancing the capabilities of the model.

If your production data, in its unaltered format, resides at level 0 of the data pyramid, the 'Entity' API constitutes the first, second and the third layer, where your data starts taking shape to your advantage. These layers allows for the construction upon the semantics and rules of your data model, while abstracting its specifics for the user.

The primary class within this API, the **'CoreElement'** class, is the first layer. It aims to encapsulate the most fundamental elements within your chosen data model. For instance, it includes a function 'assets()' that consistently provides access to the core elements, regardless of the selected data model.

In our context, GEMD (Graphical Expression of Materials Data) serves as the principal data model. Therefore, the **'GEMDElement'** class extends the **'CoreElement'** class as the second layer. It is inherited by the **'Process'**, **'Material'**, **'Ingredient'**, and **'Measurement'** classes, which constitute the third layer. Instead of individually interacting with and managing GEMD Process Templates, Specifications, or Runs, these two together help handle all the details under a single class, and provides refactored approaches and extensions to GEMD.

Among the added benefits of these layers:

* Managing consistent naming across runs, specs and templates if desired

* Accessing assets API() for convenient access to ressources

* Accesing attributes, like properties, in more friendly formats like dictionnaries

* Initializing GEMD Templates inside a persistent file

* Adding the capability to remove and delete attributes

* Avoiding redundant or duplicate specs and templates

* Placing additional checks on the data

* Storing gemd assets into stores, whether global or local, so templates and specs can be reused

more importantly,

* Less lines of code for development!

.. toctree::
   :caption: Learn more about our layers:

   core_element
   gemd_element