import ipywidgets
from IPython.display import JSON, display
import pandas as pd
import traitlets
import json
import ipydatagrid

class BODisplay(traitlets.HasTraits):
    df = traitlets.Instance(pd.DataFrame)

    def _ipython_display_(self):
        dg = ipydatagrid.DataGrid(self.df, selection_mode="row")
        out = ipywidgets.Output()

        def on_change(change):
            new_row = change["new"][-1]["r1"]
            j = json.loads(self.df.iloc[new_row]["context"])
            # print(j)
            # print(type(j))
            out.clear_output()
            with out:
                # display(JSON(j, expanded=True))
                display(j)

        dg.observe(on_change, ["selections"])
        gsl = ipywidgets.GridspecLayout(1, 2)
        gsl[0, 0] = dg
        gsl[0, 1] = out
        display(gsl)
