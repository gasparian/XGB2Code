# XGBoost trees to plain C/C++/Python converter

I couldn't find a good solution for exporting trained tree based gradient boosting models to C/C++ code, so after studying several discussions on stackoverflow I decided to make it by my own.
Modify it for your purposes!

For more info see the code and docstring.

## Usage

```
xgb_get_code(model=xgb_model, spacer_base="    ", 
             print_only=False, path=path, lang='C', 
             packing_in_line=True)
```
Where `xgb_model` is trained [dmlc xgboost](https://github.com/dmlc/xgboost) regressor. 
This command will create a text file "xgb_dump.txt", which you can find in a repo as an example. 

## Dependencies  
* python 3.6
* xgboost 0.6
