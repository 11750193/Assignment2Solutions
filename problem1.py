"""
Problem 1: Doctest - Ride Fare Calculator (乘车票价计算器)
"""

def calculate_trip_fare(distance_km: float, is_rush_hour: bool = False, passenger_type: str = "adult") -> float:
    """
    Calculate the total taxi/ride fare based on distance, rush hour status, and passenger type.
    根据距离、高峰时段状态和乘客类型计算出租车/拼车的总票价。

    Pricing Rules:
    定价规则：
    1. 基础票价：$3.00（涵盖前 2.0 公里）
    2. 额外距离：若距离 > 2.0 公里，则每额外 1 公里收取 $1.50
       （例如，若为 5.0 公里，则距离费用 = 3.00 + (5.0 - 2.0) * 1.50 = $7.50）。
    3. 高峰时段附加费：如果 is_rush_hour 为 True，则在票价上额外加收 25% 费用（即，fare * 1.25）。
    4. 乘客优惠：Passenger Discounts:
       - "adult": no discount (full price) [无优惠（全价）]
       - "senior": 30% discount (pays 70% of total) [30% 折扣（支付总额的 70%）]
       - "child": 50% discount (pays 50% of total) [50% 折扣（支付总额的 50%）]
    5. 输出：返回四舍五入到 2 位小数后的最终票价。
    6. 异常(Exceptions):
       - Raise ValueError("distance_km cannot be negative") if distance_km < 0.
         - 若 distance_km < 0，则抛出 ValueError("distance_km cannot be negative")。
       - Raise ValueError("invalid passenger_type: must be 'adult', 'child', or 'senior'")
         if passenger_type is not one of {"adult", "child", "senior"}.
         
    示例 / 文档测试(Examples / Doctests):

    Standard normal trip / 常规正常路线:
    >>> calculate_trip_fare(5.0)
    7.5
    >>> calculate_trip_fare(1.5)
    3.0

    Boundary cases / 边界情况:
    >>> calculate_trip_fare(0.0)
    3.0
    >>> calculate_trip_fare(2.0)
    3.0

    Rush hour surcharge / 高峰时段附加费:
    >>> calculate_trip_fare(10.0, is_rush_hour=True)
    18.75

    Passenger discounts / 乘客优惠:
    >>> calculate_trip_fare(5.0, passenger_type="child")
    3.75
    >>> calculate_trip_fare(5.0, passenger_type="senior")
    5.25

    Combination of rush hour and discount / 高峰时段与优惠组合:
    >>> calculate_trip_fare(10.0, is_rush_hour=True, passenger_type="child")
    9.38
    >>> calculate_trip_fare(5.0, is_rush_hour=True, passenger_type="senior")
    6.56

    Exceptions / 异常情况:
    >>> calculate_trip_fare(-1.0)
    Traceback (most recent call last):
        ...
    ValueError: distance_km cannot be negative
    >>> calculate_trip_fare(5.0, passenger_type="veteran")
    Traceback (most recent call last):
        ...
    ValueError: invalid passenger_type: must be 'adult', 'child', or 'senior'
    """
    if distance_km < 0:
        raise ValueError("distance_km cannot be negative")
    
    valid_passenger_types = {"adult", "child", "senior"}
    if passenger_type not in valid_passenger_types:
        raise ValueError("invalid passenger_type: must be 'adult', 'child', or 'senior'")
    
    # Calculate base and distance fare
    if distance_km <= 2.0:
        fare = 3.0
    else:
        fare = 3.0 + (distance_km - 2.0) * 1.50

    # Apply rush hour surcharge
    if is_rush_hour:
        fare *= 1.25

    # Apply passenger discount
    if passenger_type == "child":
        fare *= 0.50
    elif passenger_type == "senior":
        fare *= 0.70

    return round(fare, 2)


if __name__ == "__main__":
    import doctest
    # Run doctests and display verbose results
    doctest.testmod(verbose=True)
