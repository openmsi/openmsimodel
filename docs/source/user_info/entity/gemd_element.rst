============================================
Gemd Element: Enhancing What Already Exists
============================================

.. role:: underline
    :class: underline
    

The `GEMDElement` class serves as a foundational element for materials, processes, and measurements in GEMD (Graphical Expression of Materials Data). These elements act as wrappers for GEMD entities, containing templates, specs, and runs for the same type of entity. This class facilitates the creation, updating, linking, and outputting of these entities.

To subclass `GEMDElement`, one must follow a specific procedure, including instantiating `TEMPLATE` based on the desired kind (i.e., Material Template), specifying `_ATTRS` to add template conditions, parameters, and/or properties, and calling `finalize_template()`. Alternatively, instantiation can be done in code by passing a template.

Convenience added by the use of `GEMDElement` includes access to template, run, and spec via `@property` methods, and the existence of `_ATTRS`, a way to access template attributes in a more readable manner.

Note: `_ATTRS` will be extended to access spec and run attributes as they synchronize with each of your changes.

Key methods of `GEMDElement` include methods for preparing and updating attributes (**update_attributes**, **remove_attributes**), which are essential for defining the characteristics of the element. Additionally, the class provides functionality for managing tags and file links associated with the element.

TODO: Expand on the underlying back-end

**Additional details that are key to understanding how `GEMDElement` and its children classes behave:**

Ingredient specs and runs and Material specs do not require any attributes, while Material runs and measurement templates utilize properties.

- Since properties are only shared among material templates and specs and measurement runs, **update_properties** and **remove_properties** are implemented inside the main **GEMDElement** class for convenience.

In contrast, Measurement and Process templates, runs and specs are the only ones to utilize parameters and conditions. Similarly, Measurement and Process have a 'source' field to determine who completed the task.

- We have therefore created a **ProcessOrMeasurement** class, which is inherited by **Process** and **Measurement**, to implement methods pertaining to conditions and parameters. Those are **update_conditions**, **remove_conditions**, **update_parameters**, and **remove_parameters**.
- **set_source** and **get_source** are pertinent to **Process** and **Measurement** only and are also implemented inside **ProcessOrMeasurement**.

TODO: expand on illustrative methods

In short, `GEMDElement` provides a structured approach to handling materials, processes, and measurements within the GEMD framework, enabling efficient management and manipulation of these entities.

.. toctree::
   
   gemd_element_api