import pandas as pd
from datetime import date, timedelta, datetime

class DataFrameFilter:
    """
    Enable filtering of a dataframe using a list of simplified "logic marbles", that are JSON compliant
    Can receive either a sav ID or a Pandas dataframe with the IB data
    The main method to use is called filter, which receives a list of "logic marbles" that follow this structure:
    [<[AND|OR|NOT]>, <expression_1>, <expression_2>, ...]
    The <[AND|OR|NOT]> element at the start of the list is optional. If not indicated, then AND is used
    Each expression uses this structure:
    ['column', 'operator', 'value']
    where:
        column is the name of the dataframe column to filter by
        operator is the boolean operation (equal_to, greater_than, etc.)
        value is the threshold value (can be integer, float or string)
    Few examples:
    [['sub_business_entity', 'equal_to', 'Security Endpoints']]
    ['OR', ['sub_business_entity', 'equal_to', 'Security Endpoints'], ['sub_business_entity', 'equal_to', 'Ent Switching']]
    ['AND', ['sub_business_entity', 'equal_to', 'Security Endpoints'], ['shipdate', 'earlier_than', '2020-01-01']]
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.functions_dict = {
            'AND': self.AND,
            'NOT': self.NOT,
            'OR': self.OR,
            'greater_than': self.greater_than,
            'greater_equal_than': self.greater_equal_than,
            'less_than': self.less_than,
            'less_equal_than': self.less_equal_than,
            'equal_to': self.equal_to,
            'is_in': self.is_in,
            'contains': self.contains,
            'earlier_than': self.earlier_than,
            'later_than': self.later_than
        }

    @staticmethod
    def greater_than(a, b) -> bool:

        return a > b

    @staticmethod
    def greater_equal_than(a, b) -> bool:

        return a >= b

    @staticmethod
    def less_than(a, b) -> bool:

        return a < b

    @staticmethod
    def less_equal_than(a, b) -> bool:

        return a <= b

    @staticmethod
    def equal_to(a, b):

        return a == b

    @staticmethod
    def not_equal_to(a, b):

        return a != b

    @staticmethod
    def is_in(a, b) -> bool:
        """
        IS IN operator. Is A in B?
        Overwrites is_in function inherited from BasicOperators, as dataframe filtering using is_in uses a different syntax
        """

        return a.isin(b)

    @staticmethod
    def contains(a, b) -> bool:
        """
        Contains operator. Does A contain B?
        """

        return a.astype(str).str.contains(b)

    def later_than(self, a, b) -> bool:
        """
        Later than date operator. Returns True if a is later than b
        """

        return a > self._convert_date(b)

    def earlier_than(self, a, b) -> bool:
        """
        Earlier than date operator. Returns True if a is earlier than b
        """

        return a < self._convert_date(b)

    @staticmethod
    def _convert_date(value: str) -> date:
        """
        Convert the value used in a JSON rule to a valid date object.
        Some of the supported values are:
            TODAY
            LAST_X_DAYS
            NEXT_X_DAYS
        Plus dates as string in iso format: YYYY-MM-DD (i.e. 2023, March 30th = 2023-03-30)
        """

        date_mapping = {
            'TODAY': pd.to_datetime(date.today())
            }

        if value in date_mapping.keys():
            return date_mapping[value]

        # Check if value is LAST/NEXT_DAYS
        if '_DAYS' in value:
            if 'LAST_' in value:
                days = int(value.split('LAST_')[1].split('_DAYS')[0])
                return pd.to_datetime(date.today() - timedelta(days=days))
            elif 'NEXT_' in value:
                days = int(value.split('NEXT_')[1].split('_DAYS')[0])
                return pd.to_datetime(date.today() + timedelta(days=days))
            else:
                raise Exception(f'Invalid date value. Value passed: {value}')

        # Finally tries to parse value as an ISO format date
        try:
            return pd.to_datetime(datetime.strptime(value, '%Y-%m-%d').date())
        except:
            pass

        # If passed value doesn't match any of the above, then an exception is raised
        raise Exception('Invalid date value passed')

    @staticmethod
    def __dot(filter_masks: list) -> list:
        """
        Apply an AND operation on a list of pandas filter masks, using dot product
        (Dot product of booleans is the same as AND)
        """

        result = filter_masks[0]
        for i in range(1, len(filter_masks)):
            arg = filter_masks[i]
            result *= arg
        return result

    @staticmethod
    def __sum(filter_masks: list) -> bool:
        """
        Apply an OR operation on a list of pandas filter masks, using sum
        (SUM of booleans is the same as OR)
        """

        result = filter_masks[0]
        for i in range(1, len(filter_masks)):
            arg = filter_masks[i]
            result += arg
        return result

    def __filter(self, args: list) -> list:
        """
        Helper function to handle dataframe filtering based on a list of criteria
        i.e.: ['OR', ['sub_business_entity', 'equal_to', 'Network Security'], ['sub_business_entity', 'equal_to', 'Security Endpoints']]
        Returns a list of filter masks in pd.Series format
        """

        results = []
        for arg in args:
            if isinstance(arg, pd.Series):
                results.append(arg)
            else:
                rule = self.functions_dict[arg['comparison_operator']]
                value_to_compare = self.data[arg['key_to_compare']]
                results.append(rule(value_to_compare, arg['value_to_compare']))

        return results

    def AND(self, *args) -> pd.Series:
        """
        AND operator. Dot product is applied on a list of dataframe filter masks (Product of booleans = AND)
        """

        results = self.__filter(args)
        return self.__dot(results)

    def OR(self, *args) -> pd.Series:
        """
        AND operator. Sum operation is applied on a list of dataframe filter masks (Sum of booleans = OR)
        """

        results = self.__filter(args)
        return self.__sum(results)

    def NOT(self, *args) -> pd.Series:
        """
        NOT operator. Negates a list of dataframe filter masks
        """

        results = self.__filter(args)
        return results[0].apply(lambda x: not x)

    def filter(self, filters_json) -> pd.DataFrame:
        """
        Filter a dataframe using a series of filters structured as a JSON.
        Example:
            ['AND', ['sub_business_entity', 'equal_to', 'Ent. Switching'], ['last_support_date', 'earlier_than', 'TODAY']
        equals to:
            items where sub_business_entity == Ent. Switching AND last_support_date earlier than TODAY
        """

        filter_masks = self.evaluate_expression(filters_json)
        return self.data[filter_masks]

    def evaluate_expression(self, expression: list) -> bool:
        """
        Evaluate a list of expressions
        """

        if isinstance(expression[0], list) or isinstance(expression[0], dict):
            expression.insert(0, 'AND')

        operation = self.functions_dict[expression[0]]

        args = []
        for i in range(1, len(expression)):
            triplet = expression[i]
            if 'AND' in triplet or 'OR' in triplet or 'NOT' in triplet:
                args.append(self.evaluate_expression(triplet))
            else:
                args.append(triplet)

        return operation(*args)
