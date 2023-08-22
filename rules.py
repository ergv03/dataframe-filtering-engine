rule_example = ['OR',
                ['AND',
                 dict(key_to_compare='Country', comparison_operator='equal_to', value_to_compare='United Kingdom'),
                 dict(key_to_compare='Quantity', comparison_operator='greater_than', value_to_compare=40)
                 ],
                dict(key_to_compare='Description', comparison_operator='contains', value_to_compare='LANTERN')
                ]

date_example_1 = [
    'AND',
    dict(key_to_compare='Country', comparison_operator='equal_to', value_to_compare='United Kingdom'),
    dict(key_to_compare='InvoiceDate', comparison_operator='earlier_than', value_to_compare='TODAY'),
    dict(key_to_compare='InvoiceDate', comparison_operator='later_than', value_to_compare='2011-01-01')
]

date_example_2 = [
    'AND',
    dict(key_to_compare='Country', comparison_operator='equal_to', value_to_compare='United Kingdom'),
    dict(key_to_compare='InvoiceDate', comparison_operator='earlier_than', value_to_compare='LAST_30_DAYS'),
    dict(key_to_compare='InvoiceDate', comparison_operator='later_than', value_to_compare='2011-01-01')
]
