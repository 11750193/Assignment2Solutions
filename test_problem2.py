"""
问题 2单元测试: BankAccount

说明：
使用 Python 的 unittest 框架补全下面的测试方法。
你的测试方法必须断言 BankAccount 对象上的多个属性
（例如 balance、status、transaction_history、summary）以验证状态一致性。

运行测试：
    python -m unittest test_problem2.py -v
"""
import unittest
from problem2 import BankAccount


class TestBankAccount(unittest.TestCase):

    def setUp(self):
        """
        Set up test fixtures before each test method.
        在每个测试方法执行前设置测试夹具（test fixtures）。
        """
        self.account_empty = BankAccount("ACC001", "Alice", initial_balance=0.0, overdraft_limit=100.0)
        self.account_funded = BankAccount("ACC002", "Bob", initial_balance=200.0, overdraft_limit=50.0)

    def test_initial_state_multi_attributes(self):
        """
        验证新创建的账户是否正确初始化所有属性。
        检查 balance、owner、status、overdraft_limit、transaction_history 和 summary。
        """
        # 测试空账户
        self.assertEqual(self.account_empty.account_id, "ACC001")
        self.assertEqual(self.account_empty.owner, "Alice")
        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.overdraft_limit, 100.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(self.account_empty.transaction_history, [])

        summary_empty = self.account_empty.get_summary()
        self.assertEqual(summary_empty["account_id"], "ACC001")
        self.assertEqual(summary_empty["owner"], "Alice")
        self.assertEqual(summary_empty["balance"], 0.0)
        self.assertEqual(summary_empty["status"], "ACTIVE")
        self.assertEqual(summary_empty["overdraft_limit"], 100.0)
        self.assertEqual(summary_empty["transaction_count"], 0)

        # 测试存款账户
        self.assertEqual(self.account_funded.account_id, "ACC002")
        self.assertEqual(self.account_funded.owner, "Bob")
        self.assertEqual(self.account_funded.balance, 200.0)
        self.assertEqual(self.account_funded.overdraft_limit, 50.0)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(len(self.account_funded.transaction_history), 1)

        initial_deposit = self.account_funded.transaction_history[0]
        self.assertEqual(initial_deposit["type"], "INITIAL_DEPOSIT")
        self.assertEqual(initial_deposit["amount"], 200.0)
        self.assertEqual(initial_deposit["fee"], 0.0)
        self.assertEqual(initial_deposit["balance_after"], 200.0)

        summary_funded = self.account_funded.get_summary()
        self.assertEqual(summary_funded["balance"], 200.0)
        self.assertEqual(summary_funded["status"], "ACTIVE")
        self.assertEqual(summary_funded["overdraft_limit"], 50.0)
        self.assertEqual(summary_funded["transaction_count"], 1)

    def test_deposit_updates_multiple_attributes(self):
        """
        测试存款是否正确更新 balance、transaction_history 和 summary
        """
        result = self.account_empty.deposit(150.0)

        self.assertTrue(result)
        self.assertEqual(self.account_empty.balance, 150.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(len(self.account_empty.transaction_history), 1)

        transaction = self.account_empty.transaction_history[-1]
        self.assertEqual(transaction["type"], "DEPOSIT")
        self.assertEqual(transaction["amount"], 150.0)
        self.assertEqual(transaction["fee"], 0.0)
        self.assertEqual(transaction["balance_after"], 150.0)

        summary = self.account_empty.get_summary()
        self.assertEqual(summary["balance"], 150.0)
        self.assertEqual(summary["status"], "ACTIVE")
        self.assertEqual(summary["transaction_count"], 1)

    def test_withdrawal_within_balance_multi_attributes(self):
        """
        测试当余额充足时提款是否正确
        """
        result = self.account_funded.withdraw(50.0, fee=2.50)

        self.assertTrue(result)
        self.assertEqual(self.account_funded.balance, 147.5)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(len(self.account_funded.transaction_history), 2)

        transaction = self.account_funded.transaction_history[-1]
        self.assertEqual(transaction["type"], "WITHDRAWAL")
        self.assertEqual(transaction["amount"], 50.0)
        self.assertEqual(transaction["fee"], 2.50)
        self.assertEqual(transaction["balance_after"], 147.5)

        summary = self.account_funded.get_summary()
        self.assertEqual(summary["balance"], 147.5)
        self.assertEqual(summary["status"], "ACTIVE")
        self.assertEqual(summary["transaction_count"], 2)

    def test_overdraft_withdrawal_and_status_transition(self):
        """
        测试使用透支保护的提款 (余额变为负数，但仍 >= -overdraft_limit)
        """
        result = self.account_empty.withdraw(50.0)

        self.assertTrue(result)
        self.assertEqual(self.account_empty.balance, -50.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")
        self.assertEqual(len(self.account_empty.transaction_history), 1)

        transaction = self.account_empty.transaction_history[-1]
        self.assertEqual(transaction["type"], "WITHDRAWAL")
        self.assertEqual(transaction["amount"], 50.0)
        self.assertEqual(transaction["balance_after"], -50.0)

        summary = self.account_empty.get_summary()
        self.assertEqual(summary["balance"], -50.0)
        self.assertEqual(summary["status"], "OVERDRAWN")
        self.assertEqual(summary["transaction_count"], 1)

        # 恰好达到透支上限 -100.0 仍然允许
        self.assertTrue(self.account_empty.withdraw(50.0))
        self.assertEqual(self.account_empty.balance, -100.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")

        # 超过透支上限的提款应被拒绝，且账户状态保持不变
        with self.assertRaises(ValueError):
            self.account_empty.withdraw(0.01)
        self.assertEqual(self.account_empty.balance, -100.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")
        self.assertEqual(len(self.account_empty.transaction_history), 2)

    def test_deposit_recovering_from_overdrawn_status(self):
        """
        测试当存款足以使余额 >= 0 时，状态从 OVERDRAWN 转回 ACTIVE。
        """
        self.account_empty.withdraw(50.0)
        self.assertEqual(self.account_empty.balance, -50.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")

        # 部分存款后余额仍为负，状态应保持 OVERDRAWN
        self.account_empty.deposit(20.0)
        self.assertEqual(self.account_empty.balance, -30.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")

        # 存款使余额恢复到 0，状态应变为 ACTIVE
        self.account_empty.deposit(30.0)
        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")

        summary = self.account_empty.get_summary()
        self.assertEqual(summary["balance"], 0.0)
        self.assertEqual(summary["status"], "ACTIVE")
        self.assertEqual(summary["transaction_count"], 3)

    def test_transfer_between_accounts_multi_attributes(self):
        """
        测试两个账户之间的资金转账。
        """
        result = self.account_funded.transfer_to(self.account_empty, 50.0, transfer_fee=5.0)

        self.assertTrue(result)

        # 发送方：200 - (50 + 5) = 145
        self.assertEqual(self.account_funded.balance, 145.0)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(len(self.account_funded.transaction_history), 2)

        # 收款方：0 + 50 = 50
        self.assertEqual(self.account_empty.balance, 50.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(len(self.account_empty.transaction_history), 1)

        withdrawal = self.account_funded.transaction_history[-1]
        self.assertEqual(withdrawal["type"], "WITHDRAWAL")
        self.assertEqual(withdrawal["amount"], 50.0)
        self.assertEqual(withdrawal["fee"], 5.0)
        self.assertEqual(withdrawal["balance_after"], 145.0)

        deposit = self.account_empty.transaction_history[-1]
        self.assertEqual(deposit["type"], "DEPOSIT")
        self.assertEqual(deposit["amount"], 50.0)
        self.assertEqual(deposit["balance_after"], 50.0)

        self.assertEqual(self.account_funded.get_summary()["balance"], 145.0)
        self.assertEqual(self.account_funded.get_summary()["transaction_count"], 2)
        self.assertEqual(self.account_empty.get_summary()["balance"], 50.0)
        self.assertEqual(self.account_empty.get_summary()["transaction_count"], 1)

    def test_frozen_account_restrictions(self):
        """
        测试 FROZEN 账户在存款、取款和转账时会抛出 RuntimeError。
        """
        # 冻结账户
        self.account_empty.freeze()
        self.assertEqual(self.account_empty.status, "FROZEN")

        with self.assertRaises(RuntimeError):
            self.account_empty.deposit(10.0)
        with self.assertRaises(RuntimeError):
            self.account_empty.withdraw(10.0)
        # 向冻结账户转账也应被拒绝
        with self.assertRaises(RuntimeError):
            self.account_funded.transfer_to(self.account_empty, 10.0)

        # 失败的操作不应改变任何状态
        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.transaction_history, [])
        self.assertEqual(self.account_funded.balance, 200.0)
        self.assertEqual(len(self.account_funded.transaction_history), 1)

        # 冻结转出方账户
        self.account_funded.freeze()
        with self.assertRaises(RuntimeError):
            self.account_funded.transfer_to(self.account_empty, 10.0)
        self.account_funded.unfreeze()
        self.assertEqual(self.account_funded.status, "ACTIVE")

        # 解冻余额为 0 的账户应恢复为 ACTIVE
        self.account_empty.unfreeze()
        self.assertEqual(self.account_empty.status, "ACTIVE")

        # 解冻余额为负的账户应恢复为 OVERDRAWN
        self.account_empty.withdraw(30.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")
        self.account_empty.freeze()
        self.assertEqual(self.account_empty.status, "FROZEN")
        self.account_empty.unfreeze()
        self.assertEqual(self.account_empty.status, "OVERDRAWN")
        self.assertEqual(self.account_empty.balance, -30.0)

    def test_invalid_operations_raise_exceptions(self):
        """
        测试异常处理。
        """
        # 构造参数无效
        with self.assertRaises(ValueError):
            BankAccount("ACC003", "Charlie", initial_balance=-10.0)
        with self.assertRaises(ValueError):
            BankAccount("ACC004", "Dana", overdraft_limit=-1.0)

        # 存款金额必须大于 0
        with self.assertRaises(ValueError):
            self.account_empty.deposit(0.0)
        with self.assertRaises(ValueError):
            self.account_empty.deposit(-5.0)

        # 提款金额必须大于 0，手续费不能为负
        with self.assertRaises(ValueError):
            self.account_funded.withdraw(0.0)
        with self.assertRaises(ValueError):
            self.account_funded.withdraw(10.0, fee=-1.0)

        # 超过透支上限
        with self.assertRaises(ValueError):
            self.account_empty.withdraw(100.01)

        # 转账参数无效
        with self.assertRaises(ValueError):
            self.account_funded.transfer_to(self.account_empty, 0.0)
        with self.assertRaises(ValueError):
            self.account_funded.transfer_to(self.account_empty, 10.0, transfer_fee=-1.0)
        with self.assertRaises(ValueError):
            self.account_empty.transfer_to(self.account_funded, 150.0)  # 超过透支上限
        with self.assertRaises(TypeError):
            self.account_funded.transfer_to("not-an-account", 10.0)

        # 所有失败的操作都不应改变账户状态
        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(self.account_empty.transaction_history, [])
        self.assertEqual(self.account_funded.balance, 200.0)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(len(self.account_funded.transaction_history), 1)


if __name__ == "__main__":
    unittest.main()
