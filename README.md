# XGBoost trees to plain C/Python converter

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
