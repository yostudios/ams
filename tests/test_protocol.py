from unittest import TestCase
from ams.protocol import BaseTask

class ProtocolFormatTests(TestCase):
    def test_encode(self):
        task = BaseTask("test-type", {"arg1": "val1", "arg2": "val2"})
        self.assertEqual(task.encode(),
            '{"arg1": "val1", "arg2": "val2", "type": "test-type"}')

    def test_decode(self):
        task = BaseTask(*BaseTask.decode(
            '{"arg1": "val1", "arg2": "val2", "type": "test-type"}'))
        self.assertEqual(task.type_name, "test-type")
        self.assertEqual(task.args, {"arg1": "val1", "arg2": "val2"})

    def test_equality(self):
        task_a = BaseTask("test-type", {"arg2": "val2", "arg1": "val1"})
        task_b = BaseTask("test-type", {"arg1": "val1", "arg2": "val2"})
        self.assertEqual(task_a, task_b)
