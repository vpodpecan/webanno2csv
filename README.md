## A converter from WebAnno tsv to csv

This repository contains a converver from a WebAnno .tsv file to a set of .csv files.
Please note that the input tsv is **specific to the [TermFrame project](https://termframe.ff.uni-lj.si/) project** and is expected to contain custom annotation columns for:

1.  cannonical form,
2.  category,
3.  definition element,
4.  relation, and
5.  relation definition/relation verb frame.

Here is a example of a valid input file containing annotations of one sentence:

```
#FORMAT=WebAnno TSV 3.2
#T_SP=webanno.custom.Canonicalform|Canonical
#T_SP=webanno.custom.Category|Category
#T_SP=webanno.custom.Definitionelement|Def_element
#T_SP=webanno.custom.Relation|Relation
#T_SP=webanno.custom.Relation_definitor|Rel_verb_frame

#Text=An  aquifer is a body  of rock that can store and transmit significant quantities of water (Gunn, 2004).
1-1   0-2      An           _  _            _              _                  _                
1-2   4-11     aquifer      _  C. Geome     DEFINIENDUM    _                  _                
1-3   12-14    is           _  _            DEFINITOR[14]  _                  _                
1-4   15-16    a            _  _            DEFINITOR[14]  _                  _                
1-5   17-21    body         _  _            GENUS[15]      _                  _                
1-6   23-25    of           _  _            GENUS[15]      _                  _                
1-7   26-30    rock         _  D.1 Abiotic  GENUS[15]      _                  _                
1-8   31-35    that         _  _            _              _                  _                
1-9   36-39    can          _  _            _              HAS\_FUNCTION[46]  frame\_FUNCTION  
1-10  40-45    store        _  _            _              HAS\_FUNCTION[46]  _                
1-11  46-49    and          _  _            _              HAS\_FUNCTION[46]  _                
1-12  50-58    transmit     _  _            _              HAS\_FUNCTION[46]  _                
1-13  59-70    significant  _  _            _              HAS\_FUNCTION[46]  _                
1-14  71-81    quantities   _  _            _              HAS\_FUNCTION[46]  _                
1-15  82-84    of           _  _            _              HAS\_FUNCTION[46]  _                
1-16  85-90    water        _  D.1 Abiotic  _              HAS\_FUNCTION[46]  _                
1-17  91-92    (            _  _            _              _                  _                
1-18  92-96    Gunn         _  _            _              _                  _                
1-19  96-97    ,            _  _            _              _                  _                
1-20  98-102   2004         _  _            _              _                  _                
1-21  102-103  )            _  _            _              _                  _                
1-22  103-104  .            _  _            _              _                  _                
```


## Requirements

-  Python 3.6+
-  pandas 1.2+
-  Flask 1.1+ (required for the web application)

## How to use

The converter can be used as a standalone python application or as a very simple web application.


#### Standalone application

1. Clone this repository

1. Prepare a virtual environment
    ```bash
    python3 -m
    ```

Python 3.6+ and `pandas` are required.


#### Web application
