from unittest import TestCase
from ams.protocol import BaseTask

_job_data = ('KGRwMQpTJ2FyZzEnCnAyClMndmFsMScKcDMKc1MnYXJnMicKcDQKUyd2YWw'
             'yJwpwNQpzUyd0eXBl\nJwpwNgpTJ3Rlc3QtdHlwZScKcDcKcy4=\n')
_job_data = _job_data.decode("base64")

class ProtocolFormatTests(TestCase):
    def test_encode(self):
        task = BaseTask("test-type", {"arg1": "val1", "arg2": "val2"})
        self.assertEqual(task.encode(), _job_data)

    def test_decode(self):
        task = BaseTask(*BaseTask.decode(_job_data))
        self.assertEqual(task.type_name, "test-type")
        self.assertEqual(task.args, {"arg1": "val1", "arg2": "val2"})

    def test_equality(self):
        task_a = BaseTask("test-type", {"arg2": "val2", "arg1": "val1"})
        task_b = BaseTask("test-type", {"arg1": "val1", "arg2": "val2"})
        self.assertEqual(task_a, task_b)
