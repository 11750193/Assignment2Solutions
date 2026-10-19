"""
问题 3 单元测试: Order

说明：
使用 Python 的 unittest 框架补全下面的单元测试方法。
你的测试方法必须断言 Order 对象上的多个属性
（例如 subtotal、discount_amount、tax_amount、shipping_fee、final_total、status）
以验证在各种条件下的状态一致性。

运行测试：
    python -m unittest test_problem3.py -v
"""
import unittest
from problem3 import Order


class TestOrder(unittest.TestCase):

    def setUp(self):
        """
        在每个测试方法执行前设置测试夹具。
        """
        self.regular_order = Order("ORD100", customer_tier="regular")
        self.silver_order = Order("ORD200", customer_tier="silver")
        self.gold_order = Order("ORD300", customer_tier="gold")

    def test_initial_state_multi_attributes(self):
        """
        验证新订单的初始状态：空商品、PENDING 状态、各项金额为 0。
        """
        self.assertEqual(self.regular_order.order_id, "ORD100")
        self.assertEqual(self.regular_order.customer_tier, "regular")
        self.assertEqual(self.regular_order.items, {})
        self.assertEqual(self.regular_order.status, "PENDING")
        self.assertIsNone(self.regular_order.applied_coupon)
        self.assertEqual(self.regular_order.subtotal, 0.0)
        self.assertEqual(self.regular_order.discount_amount, 0.0)
        self.assertEqual(self.regular_order.tax_amount, 0.0)
        self.assertEqual(self.regular_order.shipping_fee, 0.0)
        self.assertEqual(self.regular_order.final_total, 0.0)

        summary = self.regular_order.get_summary()
        self.assertEqual(summary["order_id"], "ORD100")
        self.assertEqual(summary["tier"], "regular")
        self.assertEqual(summary["status"], "PENDING")
        self.assertEqual(summary["item_count"], 0)
        self.assertEqual(summary["subtotal"], 0.0)
        self.assertEqual(summary["final_total"], 0.0)

        # 会员等级大小写不敏感
        upper_tier_order = Order("ORD999", customer_tier="GOLD")
        self.assertEqual(upper_tier_order.customer_tier, "gold")

    def test_add_items_and_recalculation(self):
        """
        测试添加商品后 subtotal、tax、shipping、final_total 和 summary 的更新，
        以及重复添加同名商品时只增加数量。
        """
        self.regular_order.add_item("Laptop", 1000.0, 1, "electronics")

        self.assertEqual(len(self.regular_order.items), 1)
        self.assertEqual(self.regular_order.subtotal, 1000.0)
        self.assertEqual(self.regular_order.discount_amount, 0.0)
        self.assertEqual(self.regular_order.tax_amount, 80.0)
        self.assertEqual(self.regular_order.shipping_fee, 0.0)
        self.assertEqual(self.regular_order.final_total, 1080.0)

        self.regular_order.add_item("Apple", 10.0, 2, "grocery")

        self.assertEqual(len(self.regular_order.items), 2)
        self.assertEqual(self.regular_order.items["Apple"]["quantity"], 2)
        self.assertEqual(self.regular_order.subtotal, 1020.0)
        self.assertEqual(self.regular_order.tax_amount, 80.0)  # 食品不计税
        self.assertEqual(self.regular_order.final_total, 1100.0)

        # 重复添加同名商品应累加数量而不是新增条目
        self.regular_order.add_item("Apple", 10.0, 1, "grocery")
        self.assertEqual(len(self.regular_order.items), 2)
        self.assertEqual(self.regular_order.items["Apple"]["quantity"], 3)
        self.assertEqual(self.regular_order.subtotal, 1030.0)
        self.assertEqual(self.regular_order.final_total, 1110.0)

        summary = self.regular_order.get_summary()
        self.assertEqual(summary["item_count"], 4)
        self.assertEqual(summary["subtotal"], 1030.0)
        self.assertEqual(summary["final_total"], 1110.0)

    def test_tier_discounts(self):
        """
        测试 regular、silver、gold 三种会员等级对应的 0%、5%、10% 折扣。
        """
        for order in (self.regular_order, self.silver_order, self.gold_order):
            order.add_item("Keyboard", 100.0, 1, "electronics")

        # regular: 无折扣
        self.assertEqual(self.regular_order.subtotal, 100.0)
        self.assertEqual(self.regular_order.discount_amount, 0.0)
        self.assertEqual(self.regular_order.tax_amount, 8.0)
        self.assertEqual(self.regular_order.shipping_fee, 0.0)
        self.assertEqual(self.regular_order.final_total, 108.0)

        # silver: 5% 折扣
        self.assertEqual(self.silver_order.subtotal, 100.0)
        self.assertEqual(self.silver_order.discount_amount, 5.0)
        self.assertEqual(self.silver_order.tax_amount, 7.6)
        self.assertEqual(self.silver_order.final_total, 102.6)

        # gold: 10% 折扣
        self.assertEqual(self.gold_order.subtotal, 100.0)
        self.assertEqual(self.gold_order.discount_amount, 10.0)
        self.assertEqual(self.gold_order.tax_amount, 7.2)
        self.assertEqual(self.gold_order.final_total, 97.2)

        self.assertEqual(self.gold_order.get_summary()["discount_amount"], 10.0)

    def test_coupon_discounts_and_validation(self):
        """
        测试 SAVE10（10% 折扣）与 FLAT15（$15 立减）优惠券，
        包括与会员折扣的组合、代码规范化以及无效代码的处理。
        """
        self.regular_order.add_item("Monitor", 100.0, 1, "electronics")
        self.regular_order.apply_coupon(" save10 ")

        self.assertEqual(self.regular_order.applied_coupon, "SAVE10")
        self.assertEqual(self.regular_order.subtotal, 100.0)
        self.assertEqual(self.regular_order.discount_amount, 10.0)
        self.assertEqual(self.regular_order.tax_amount, 7.2)
        self.assertEqual(self.regular_order.shipping_fee, 0.0)
        self.assertEqual(self.regular_order.final_total, 97.2)

        # silver（5%）+ FLAT15（$15）
        self.silver_order.add_item("Monitor", 100.0, 1, "electronics")
        self.silver_order.apply_coupon("FLAT15")

        self.assertEqual(self.silver_order.applied_coupon, "FLAT15")
        self.assertEqual(self.silver_order.discount_amount, 20.0)
        self.assertEqual(self.silver_order.tax_amount, 6.4)
        self.assertEqual(self.silver_order.final_total, 86.4)

        # 无效优惠券应抛出 ValueError，且不改变订单状态
        with self.assertRaises(ValueError):
            self.gold_order.apply_coupon("INVALID")
        self.assertIsNone(self.gold_order.applied_coupon)
        self.assertEqual(self.gold_order.final_total, 0.0)

    def test_grocery_tax_exemption_and_proportional_discount(self):
        """
        测试食品(grocery)免税，以及折扣按比例分摊到应税商品的计算方式。
        """
        self.gold_order.add_item("Milk", 20.0, 1, "Grocery")
        self.gold_order.add_item("Bread", 10.0, 1, "grocery")

        # 商品分类统一转为小写
        self.assertEqual(self.gold_order.items["Milk"]["category"], "grocery")

        # 小计 30，gold 折扣 10% = 3，净额 27，食品不计税，运费 5.99
        self.assertEqual(self.gold_order.subtotal, 30.0)
        self.assertEqual(self.gold_order.discount_amount, 3.0)
        self.assertEqual(self.gold_order.tax_amount, 0.0)
        self.assertEqual(self.gold_order.shipping_fee, 5.99)
        self.assertEqual(self.gold_order.final_total, 32.99)

        # 加入应税商品：小计 130，折扣 13，净额 117，按 90% 比例计税
        self.gold_order.add_item("Headphones", 100.0, 1, "electronics")
        self.assertEqual(self.gold_order.subtotal, 130.0)
        self.assertEqual(self.gold_order.discount_amount, 13.0)
        self.assertEqual(self.gold_order.tax_amount, 7.2)
        self.assertEqual(self.gold_order.shipping_fee, 0.0)
        self.assertEqual(self.gold_order.final_total, 124.2)

    def test_shipping_fee_threshold_and_discount_effect(self):
        """
        测试净小计 >= $50 免运费、低于 $50 收取 $5.99，
        以及优惠券使净小计降到阈值以下时重新收取运费。
        """
        # 净小计恰好 50：免运费
        self.regular_order.add_item("Book", 50.0, 1, "general")
        self.assertEqual(self.regular_order.subtotal, 50.0)
        self.assertEqual(self.regular_order.shipping_fee, 0.0)
        self.assertEqual(self.regular_order.tax_amount, 4.0)
        self.assertEqual(self.regular_order.final_total, 54.0)

        # 净小计 49.99：收取标准运费
        self.silver_order.add_item("Book", 49.99, 1, "general")
        self.assertEqual(self.silver_order.subtotal, 49.99)
        self.assertEqual(self.silver_order.discount_amount, 2.5)
        self.assertEqual(self.silver_order.tax_amount, 3.8)  # 47.49 * 8% = 3.7992
        self.assertEqual(self.silver_order.shipping_fee, 5.99)
        self.assertEqual(self.silver_order.final_total, 57.28)

        # gold + FLAT15：净小计 34.5 < 50，需支付运费
        self.gold_order.add_item("Book", 55.0, 1, "general")
        self.gold_order.apply_coupon("FLAT15")
        self.assertEqual(self.gold_order.subtotal, 55.0)
        self.assertEqual(self.gold_order.discount_amount, 20.5)
        self.assertEqual(self.gold_order.tax_amount, 2.76)
        self.assertEqual(self.gold_order.shipping_fee, 5.99)
        self.assertEqual(self.gold_order.final_total, 43.25)

    def test_remove_item_multi_attribute_updates(self):
        """
        测试删除商品/减少数量后，items、subtotal、折扣、税费、运费和订单总额的更新。
        """
        self.gold_order.add_item("A", 20.0, 5, "general")
        self.gold_order.add_item("B", 30.0, 1, "electronics")

        self.assertEqual(self.gold_order.subtotal, 130.0)
        self.assertEqual(self.gold_order.discount_amount, 13.0)
        self.assertEqual(self.gold_order.tax_amount, 9.36)
        self.assertEqual(self.gold_order.final_total, 126.36)

        # 减少数量
        self.gold_order.remove_item("A", quantity=2)
        self.assertEqual(self.gold_order.items["A"]["quantity"], 3)
        self.assertEqual(self.gold_order.subtotal, 90.0)
        self.assertEqual(self.gold_order.discount_amount, 9.0)
        self.assertEqual(self.gold_order.tax_amount, 6.48)
        self.assertEqual(self.gold_order.final_total, 87.48)

        # 完全删除商品
        self.gold_order.remove_item("B")
        self.assertNotIn("B", self.gold_order.items)
        self.assertEqual(self.gold_order.subtotal, 60.0)
        self.assertEqual(self.gold_order.discount_amount, 6.0)
        self.assertEqual(self.gold_order.tax_amount, 4.32)
        self.assertEqual(self.gold_order.shipping_fee, 0.0)
        self.assertEqual(self.gold_order.final_total, 58.32)

        # 删除数量必须为正
        with self.assertRaises(ValueError):
            self.gold_order.remove_item("A", quantity=0)
        self.assertEqual(self.gold_order.subtotal, 60.0)

        # 删除不存在的商品
        with self.assertRaises(KeyError):
            self.gold_order.remove_item("Missing")

        # 删除剩余全部数量后订单金额归零
        self.gold_order.remove_item("A", quantity=3)
        self.assertEqual(self.gold_order.items, {})
        self.assertEqual(self.gold_order.subtotal, 0.0)
        self.assertEqual(self.gold_order.discount_amount, 0.0)
        self.assertEqual(self.gold_order.tax_amount, 0.0)
        self.assertEqual(self.gold_order.shipping_fee, 0.0)
        self.assertEqual(self.gold_order.final_total, 0.0)
        self.assertEqual(self.gold_order.get_summary()["item_count"], 0)

    def test_checkout_cancel_and_status_restrictions(self):
        """
        测试订单状态转换：空订单不能结账；PAID 后禁止修改/取消；
        PENDING 可取消，CANCELLED 后禁止任何修改。
        """
        # 空订单不能结账
        with self.assertRaises(ValueError):
            self.regular_order.checkout()
        self.assertEqual(self.regular_order.status, "PENDING")

        self.regular_order.add_item("Phone", 500.0, 1, "electronics")
        self.assertTrue(self.regular_order.checkout())
        self.assertEqual(self.regular_order.status, "PAID")
        self.assertEqual(self.regular_order.get_summary()["status"], "PAID")

        # PAID 订单禁止修改、重复结账和取消
        with self.assertRaises(RuntimeError):
            self.regular_order.add_item("Case", 20.0, 1, "general")
        with self.assertRaises(RuntimeError):
            self.regular_order.remove_item("Phone")
        with self.assertRaises(RuntimeError):
            self.regular_order.apply_coupon("SAVE10")
        with self.assertRaises(RuntimeError):
            self.regular_order.checkout()
        with self.assertRaises(RuntimeError):
            self.regular_order.cancel()

        # 取消 PENDING 订单
        self.silver_order.add_item("Phone", 500.0, 1, "electronics")
        self.assertTrue(self.silver_order.cancel())
        self.assertEqual(self.silver_order.status, "CANCELLED")
        self.assertEqual(self.silver_order.get_summary()["status"], "CANCELLED")

        # CANCELLED 订单禁止修改和结账
        with self.assertRaises(RuntimeError):
            self.silver_order.add_item("Case", 20.0, 1, "general")
        with self.assertRaises(RuntimeError):
            self.silver_order.remove_item("Phone")
        with self.assertRaises(RuntimeError):
            self.silver_order.apply_coupon("SAVE10")
        with self.assertRaises(RuntimeError):
            self.silver_order.checkout()

    def test_invalid_inputs_raise_exceptions(self):
        """
        测试无效的会员等级、商品价格、数量和优惠券所引发的异常。
        """
        with self.assertRaises(ValueError):
            Order("ORD400", customer_tier="platinum")

        # 价格必须为正
        with self.assertRaises(ValueError):
            self.regular_order.add_item("Freebie", 0.0, 1, "general")
        with self.assertRaises(ValueError):
            self.regular_order.add_item("Negative", -5.0, 1, "general")

        # 数量必须为正
        with self.assertRaises(ValueError):
            self.regular_order.add_item("Zero", 10.0, 0, "general")
        with self.assertRaises(ValueError):
            self.regular_order.add_item("NegativeQty", 10.0, -1, "general")

        # 失败的添加操作不应改变订单状态
        self.assertEqual(self.regular_order.items, {})
        self.assertEqual(self.regular_order.subtotal, 0.0)
        self.assertEqual(self.regular_order.final_total, 0.0)

        # 无效优惠券代码
        with self.assertRaises(ValueError):
            self.regular_order.apply_coupon("FREE100")
        self.assertIsNone(self.regular_order.applied_coupon)


if __name__ == "__main__":
    unittest.main()
