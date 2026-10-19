# 问题/错误报告 Bug Report

该报告记录了在有错误程序中发现的问题（bugs），包括失败的测试用例、根本原因分析（root cause analysis）以及已应用的修复方案。

测试环境：Windows 11 / Python 3 / `unittest`。所有修复后测试均通过。

---

## 问题/错误报告 1：背靠背会议被错误判定为时间冲突

### 1. 测试程序 Program Under Test
- **File:** `problem4.py`
- **Class / Function:** `MeetingRoom.book()`

### 2. 失败的测试用例 Failing Test Case
测试代码 `test_problem4.py::TestMeetingRoom::test_back_to_back_meetings_allowed`：

```python
def test_back_to_back_meetings_allowed(self):
    self.assertTrue(self.room.book("B01", "Standup", 9, 10, 5))
    self.assertTrue(self.room.book("B02", "Planning", 10, 12, 8))

    self.assertEqual(len(self.room.bookings), 2)
    self.assertEqual(self.room.total_hours_booked, 3)
    self.assertEqual(self.room.get_free_slots(), [(8, 9), (12, 18)])
    self.assertEqual(self.room.get_utilization_rate(), 0.3)
```

运行命令：`python -m unittest test_problem4.py -v`

**测试输出 / 错误信息：**
```text
ERROR: test_back_to_back_meetings_allowed (test_problem4.TestMeetingRoom.test_back_to_back_meetings_allowed)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\DesKtop\Assignment2\test_problem4.py", line 69, in test_back_to_back_meetings_allowed
    self.assertTrue(self.room.book("B02", "Planning", 10, 12, 8))
  File "D:\DesKtop\Assignment2\problem4.py", line 60, in book
    raise ValueError(f"Time slot [{start_time}, {end_time}] conflicts with booking '{b['booking_id']}' [{b['start_time']}, {b['end_time']}]")
ValueError: Time slot [10, 12] conflicts with booking 'B01' [9, 10]
```

### 3. 根本原因分析 Root Cause Analysis
- **预期行为：** 规则 5 明确规定背靠背会议（例如 9-10 与 10-12）不冲突，应当允许预订。
- **实际行为：** 预订 10-12 时被判定为与 9-10 冲突并抛出 `ValueError`。
- **根本原因：** 冲突判断使用了严格不等号：

  `not (end_time < b["start_time"] or start_time > b["end_time"])`

  当新预订的开始时间恰好等于已有预订的结束时间（`start_time == b["end_time"]`）时，两个比较都为 `False`，条件取反后为 `True`，于是把端点相接的背靠背会议误判为重叠。应将判断改为“无重叠”的边界包含形式（`<=` / `>=`）。

### 4. 代码修复与差异 Code Fix & Diff
```diff
         for b in self.bookings:
-            if not (end_time < b["start_time"] or start_time > b["end_time"]):
+            if not (end_time <= b["start_time"] or start_time >= b["end_time"]):
                 raise ValueError(f"Time slot [{start_time}, {end_time}] conflicts with booking '{b['booking_id']}' [{b['start_time']}, {b['end_time']}]")
```

修复后 `test_back_to_back_meetings_allowed` 与 `test_overlapping_booking_rejected` 均通过。

---

## 问题/错误报告 2：min / max 聚合结果互换

### 1. 测试程序 Program Under Test
- **File:** `problem5.py`
- **Function:** `clean_and_aggregate()`

### 2. 失败的测试用例 Failing Test Case
测试代码 `test_problem5.py::TestDataAggregator::test_aggregate_min_and_max`：

```python
def test_aggregate_min_and_max(self):
    min_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="min")
    max_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="max")

    self.assertAlmostEqual(min_result["North"], 100.0)
    self.assertAlmostEqual(max_result["North"], 200.0)
    self.assertAlmostEqual(min_result["South"], 150.0)
    self.assertAlmostEqual(max_result["South"], 350.0)
```

运行命令：`python -m unittest test_problem5.py -v`

**测试输出 / 错误信息：**
```text
FAIL: test_aggregate_min_and_max (test_problem5.TestDataAggregator.test_aggregate_min_and_max)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\DesKtop\Assignment2\test_problem5.py", line 62, in test_aggregate_min_and_max
    self.assertAlmostEqual(min_result["North"], 100.0)
AssertionError: 200.0 != 100.0 within 7 places (100.0 difference)
```

### 3. 根本原因分析 Root Cause Analysis
- **预期行为：** `aggregation="min"` 返回每组的最小值（North 为 100.0），`aggregation="max"` 返回最大值（North 为 200.0）。
- **实际行为：** `min` 返回了最大值，`max` 返回了最小值。
- **根本原因：** 聚合分发逻辑中两个分支的实现写反了——`min` 分支调用了 `max(values)`，`max` 分支调用了 `min(values)`。

### 4. 代码修复与差异 Code Fix & Diff
```diff
         elif agg_op == "min":
-            val = max(values)
+            val = min(values)
         elif agg_op == "max":
-            val = min(values)
+            val = max(values)
```

---

## 问题/错误报告 3：空记录列表未按文档抛出 ValueError

### 1. 测试程序 Program Under Test
- **File:** `problem5.py`
- **Function:** `clean_and_aggregate()`

### 2. 失败的测试用例 Failing Test Case
测试代码 `test_problem5.py::TestDataAggregator::test_empty_dataset_raises_value_error`：

```python
def test_empty_dataset_raises_value_error(self):
    with self.assertRaises(ValueError):
        clean_and_aggregate([], group_by="region", metric="sales")
```

运行命令：`python -m unittest test_problem5.py -v`

**测试输出 / 错误信息：**
```text
FAIL: test_empty_dataset_raises_value_error (test_problem5.TestDataAggregator.test_empty_dataset_raises_value_error)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\DesKtop\Assignment2\test_problem5.py", line 95, in test_empty_dataset_raises_value_error
    with self.assertRaises(ValueError):
AssertionError: ValueError not raised
```

### 3. 根本原因分析 Root Cause Analysis
- **预期行为：** 文档字符串声明：如果 `records` 为空，应抛出 `ValueError`；如果 `records` 不是列表，应抛出 `TypeError`。
- **实际行为：** 传入空列表时函数直接返回空字典 `{}`，没有抛出任何异常；同时缺少显式的列表类型检查（非列表输入只是碰巧在逐条校验时抛出 `TypeError`）。
- **根本原因：** 函数入口处缺少对 `records` 的参数校验逻辑。

### 4. 代码修复与差异 Code Fix & Diff
```diff
+    if not isinstance(records, list):
+        raise TypeError("records must be a list")
+    if not records:
+        raise ValueError("records cannot be empty")
+
     valid_aggregations = {"sum", "mean", "min", "max", "count"}
     agg_op = aggregation.lower()
```

修复后 problem5 的 9 个测试全部通过。
