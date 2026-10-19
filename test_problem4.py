"""
问题 4 单元测试: MeetingRoom

说明：
使用 Python 的 unittest 框架补全下面的单元测试方法。
你的测试方法必须断言 MeetingRoom 对象上的多个属性
（例如 bookings 列表、total_hours_booked、free slots、utilization rate）
以验证会议室状态和冲突管理。

运行测试：
    python -m unittest test_problem4.py -v
"""
import unittest
from problem4 import MeetingRoom


class TestMeetingRoom(unittest.TestCase):

    def setUp(self):
        """
        在每个测试方法执行前设置测试夹具。
        """
        self.room = MeetingRoom("Conference-A", capacity=10)

    def test_initial_state_multi_attributes(self):
        """
        验证空会议室的初始状态。
        """
        self.assertEqual(self.room.room_id, "Conference-A")
        self.assertEqual(self.room.capacity, 10)
        self.assertEqual(self.room.bookings, [])
        self.assertEqual(self.room.total_hours_booked, 0)
        self.assertFalse(self.room.is_maintenance)
        self.assertEqual(self.room.get_free_slots(), [(8, 18)])
        self.assertEqual(self.room.get_utilization_rate(), 0.0)

        # 容量必须为正
        with self.assertRaises(ValueError):
            MeetingRoom("Invalid", capacity=0)

    def test_single_booking_multi_attributes(self):
        """
        测试创建一个有效预订。
        验证 bookings 列表、total_hours_booked、utilization rate 和 free slots。
        """
        result = self.room.book("B01", "Team Sync", 10, 12, 5)

        self.assertTrue(result)
        self.assertEqual(len(self.room.bookings), 1)

        booking = self.room.bookings[0]
        self.assertEqual(booking["booking_id"], "B01")
        self.assertEqual(booking["title"], "Team Sync")
        self.assertEqual(booking["start_time"], 10)
        self.assertEqual(booking["end_time"], 12)
        self.assertEqual(booking["attendees"], 5)

        self.assertEqual(self.room.total_hours_booked, 2)
        self.assertEqual(self.room.get_utilization_rate(), 0.2)
        self.assertEqual(self.room.get_utilization_rate(total_available_hours=2), 1.0)
        self.assertEqual(self.room.get_free_slots(), [(8, 10), (12, 18)])

    def test_back_to_back_meetings_allowed(self):
        """
        测试有效的连续/背靠背会议 (例如 9-10 和 10-12) 不会引发冲突错误。
        验证两个预订成功后的多属性状态。
        """
        self.assertTrue(self.room.book("B01", "Standup", 9, 10, 5))
        self.assertTrue(self.room.book("B02", "Planning", 10, 12, 8))

        self.assertEqual(len(self.room.bookings), 2)
        self.assertEqual(
            [b["booking_id"] for b in self.room.bookings],
            ["B01", "B02"]
        )
        self.assertEqual(self.room.total_hours_booked, 3)
        self.assertEqual(self.room.get_utilization_rate(), 0.3)
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (12, 18)])

    def test_overlapping_booking_rejected(self):
        """
        测试重叠预订（例如 9-11 与 10-12, 或完全包含在 9-12 与 10-11 之间）
        应抛出 ValueError, 并保持会议室状态不变。
        """
        self.room.book("B01", "Workshop", 9, 11, 5)

        with self.assertRaises(ValueError):
            self.room.book("B02", "Overlap", 10, 12, 5)
        with self.assertRaises(ValueError):
            self.room.book("B03", "Containing", 8, 12, 5)
        with self.assertRaises(ValueError):
            self.room.book("B04", "Contained", 10, 11, 5)

        # 失败的重叠预订不应改变任何状态
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0]["booking_id"], "B01")
        self.assertEqual(self.room.total_hours_booked, 2)
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (11, 18)])

        # 失败之后，背靠背预订仍然允许
        self.assertTrue(self.room.book("B05", "Adjacent", 11, 12, 5))
        self.assertEqual(len(self.room.bookings), 2)
        self.assertEqual(self.room.total_hours_booked, 3)

    def test_cancel_booking_updates_all_attributes(self):
        """
        测试取消预订是否能正确从 bookings 中移除，
        减少 total_hours_booked, 并恢复 free slots。
        """
        self.room.book("B01", "Morning", 9, 11, 5)
        self.room.book("B02", "Afternoon", 13, 15, 5)

        self.assertEqual(self.room.total_hours_booked, 4)
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (11, 13), (15, 18)])

        self.assertTrue(self.room.cancel("B01"))

        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0]["booking_id"], "B02")
        self.assertEqual(self.room.total_hours_booked, 2)
        self.assertEqual(self.room.get_utilization_rate(), 0.2)
        self.assertEqual(self.room.get_free_slots(), [(8, 13), (15, 18)])

        # 取消不存在的预订应抛出 KeyError 且状态不变
        with self.assertRaises(KeyError):
            self.room.cancel("UNKNOWN")
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.total_hours_booked, 2)

    def test_capacity_and_validation_exceptions(self):
        """
        测试边界情况和异常：
        - 参与人数超过容量 (ValueError)
        - 开始时间 >= 结束时间 (ValueError)
        - 预订 ID 重复 (ValueError)
        - 会议室处于维护状态时预订 (RuntimeError)
        - 取消不存在的预订 (KeyError)
        """
        # 参与人数无效
        with self.assertRaises(ValueError):
            self.room.book("B01", "Too many", 9, 10, 11)
        with self.assertRaises(ValueError):
            self.room.book("B01", "No attendees", 9, 10, 0)

        # 时间无效
        with self.assertRaises(ValueError):
            self.room.book("B01", "Zero duration", 9, 9, 5)
        with self.assertRaises(ValueError):
            self.room.book("B01", "Reversed", 10, 9, 5)
        with self.assertRaises(ValueError):
            self.room.book("B01", "Negative start", -1, 5, 5)

        # 创建一个有效预订
        self.assertTrue(self.room.book("B01", "Valid", 9, 10, 5))

        # 重复的预订 ID
        with self.assertRaises(ValueError):
            self.room.book("B01", "Duplicate", 11, 12, 5)

        # 取消不存在的预订
        with self.assertRaises(KeyError):
            self.room.cancel("UNKNOWN")

        # 维护状态禁止预订
        self.room.is_maintenance = True
        with self.assertRaises(RuntimeError):
            self.room.book("B02", "Maintenance", 11, 12, 5)

        # 所有失败操作后状态保持一致
        self.assertTrue(self.room.is_maintenance)
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0]["booking_id"], "B01")
        self.assertEqual(self.room.total_hours_booked, 1)
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (10, 18)])


if __name__ == "__main__":
    unittest.main()
