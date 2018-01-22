# model2code

I couldn't find a good solution for exporting trained tree based gradient boosting models to C++ code, so after studying several discussions on stackoverflow I decided to make it by my own.
Modify it for your purposes!

For more info see the code and docstring.

## Usage

In the case of [dmlc xgboost](https://github.com/dmlc/xgboost) regressor:  

```
xgb_get_code(model=xgb_model, spacer_base="    ", print_only=False, path=path, lang='C', packing_in_line=True)
```

This command will create a text file "xgb_dump.txt", which you can find in a repo as an example. 

## Dependencies  
* python 3.6
* xgboost 0.6
