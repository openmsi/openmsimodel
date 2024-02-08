=============
Entity
=============

The 'Entity' API serves to abstractly manage the layer surrounding your data model, facilitating interaction with its components in a scalable manner, while simultaneously enhancing the capabilities of the model.

If your production data, in its unaltered format, resides at level 0 of the data pyramid, and your data within your chosen model is at level 1, the 'Entity' API constitutes the second layer. This layer allows for the construction upon the semantics and rules of your data model, while abstracting its specifics for the user.

The primary class within this API, the 'Element' class, aims to encapsulate the most fundamental elements within your chosen data model. For instance, it includes a function 'assets()' that consistently provides access to the core elements, regardless of the selected data model.

In our context, GEMD (Graphical Expression of Materials Data) serves as the principal data model. Therefore, the 'Gemd_Element' class extends the 'Element' class, and is inherited by the 'Process', 'Material', 'Ingredient', and 'Measurement' classes. Consequently, instead of individually interacting with and managing GEMD Process Templates, Specifications, or Runs, they can all be handled under a single class, 'Process'. The same principle applies to 'Material', 'Measurement', and 'Ingredient'.

For instance, given that GEMD is a linked model, we have the capability to construct and adjust links within and between structures as needed. Additionally, the API serves as a wrapper around GEMD objects and includes the 'assets()' API for convenient access to resources.