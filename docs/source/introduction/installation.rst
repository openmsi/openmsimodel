
=============
Installation
=============


.. code-block:: none

   pip install openmsimodel


External Requirements
---------------------

for Mac users, especially with M1 chips, the following steps might be required:

.. code-block:: none

    brew install graphviz
    python -m pip install \
        --global-option=build_ext \
        --global-option="-I$(brew --prefix graphviz)/include/" \
        --global-option="-L$(brew --prefix graphviz)/lib/" \
        pygraphviz
    pip install openmsimodel
