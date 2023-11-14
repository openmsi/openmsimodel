=============
Next Steps
=============

2 big things for 0.2.0:
- capability to organize into materials sequences and a science kit from folder/list of GEMD files
- overall cleanup and testing, especially for element entity module

_____

New GEMD versions

GEMDLite

* uses a txt based model building in conjusting with a global or local stores to instantiate a barebone GEMD model

Smaller/Larger GEMD

 - GEMDAttributes

 - GEMDTags

 - GEMDFileLinks

 - GEMDFileLinksPresentOrNot

 - GEMDDataQuality

checks if files are still present; checks colliding files from diff sources; tells u when ur naming patterns are inconsistent and where is the prob; tells u when the data is corrupted and can’t be opened; flags when our metadata and formats are not respected (data governance)    


___

Expanding tools

- add structure tools

RepeatSequence (finds all sequences that have the same structure)

MissingSequence (complete a sequence of gemd objects based on inference from RepeatSequence )

- add stastistics tools

basic stats (e.g., avg, std) tools 

- add agents

AiAgent (which can acts on ur data using assets() API )

___

RealTime OpenMSIModel

Stateful OpenMSIModel

---

GUI for model visualization and building

___ 

Strategy:
* capitalizing on stores and GEMDLite to lower entry and increase nb of users + in-house data  
* gemd becomes a graph object with open_graph: what computational tools should we build for graphs or in python memory?
___

Benchmarking
- opengraph perf with 5/6 figures (not $$$) number of nodes