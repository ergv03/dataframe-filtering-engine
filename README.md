## Overview

Novel way to filter pandas dataframe based on a business logic stored in a JSON object. Not super useful by itself, as data filtering using pandas own functions is straightforward; still, this repo can be leveraged to enable non-technical people to explore your data by wrapping it with a proper UI (which is where the idea for this code originally came from). Also it's a good example of how to create a simple domain specific language, abstracting parts of your code.

Your business logic can be stored in a JSON, allowing it to be stored in most databases, and you can also easily create REST APIs to allow your application to create/modify such JSON objects. This way, you can for example have a UI where non-technical people (Sales, HR, etc.) can manage business rules, and then such rules can be applied to a dataframe by your code in the backend.

## How it works

This code allows the filtering of a dataframe based on a JSON object that uses the following structure:

```[<AND|OR|NOT>, <expression_1>, <expression_2>, ...]```

where each expression is a dictionary with three keys:

```
{
  key_to_compare:
  comparison_operator:
  value_to_compare:
}
```
For example:

```
[
    'AND',
    dict(key_to_compare='Country', comparison_operator='equal_to', value_to_compare='United Kingdom'),
    dict(key_to_compare='InvoiceDate', comparison_operator='earlier_than', value_to_compare='TODAY'),
]
```

Will return data where Country is equal to United Kingdom, and InvoiceDate is earlier than TODAY.

These expressions can be nested. The following example is valid:

```
['OR',
  ['AND',
   dict(key_to_compare='Country', comparison_operator='equal_to', value_to_compare='United Kingdom'),
   dict(key_to_compare='Quantity', comparison_operator='greater_than', value_to_compare=40)
   ],
  dict(key_to_compare='Description', comparison_operator='contains', value_to_compare='LANTERN')
]
```

and it translates to: (Country equal to United Kingdom AND Quantity greater than 40) OR (Description contains "LANTERN")

For more examples, check the rules.py file.

