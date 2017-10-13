# model2code

Here I will upload Python code for exporting trained ML models to executable code on different languages.  

The story began, when i really needed to export trained xgboost model to C++ code to use it inside the CVG (coriolis vibrating gyroscope) as a temperature correction algorithm.  
I couldn't find a good solution for this problem so after studying several discussions on stackoverflow I decided to make it by my own.

I will upload almost unchanged code which basically converts models to C++. So you can modify it for your purposes.  

For more info see the code and docstring.

## Usage

Let's start with the [dmlc xgboost](https://github.com/dmlc/xgboost) regressor:  

```
xgb_get_code(model=xgb_model, spacer_base="    ", print_only=False, path=path, lang='C', packing_in_line=True)
```

This command will create a text file "xgb_dump.txt", which you can find in a repo as an example. 

## Dependencies  
* python 3.6
* xgboost 0.6
