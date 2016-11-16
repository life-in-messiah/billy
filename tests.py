import unittest
from billybot import Billy


class TestBillyMessagingMethods(unittest.TestCase):
    def test_send_message(self):
        billy = Billy()
        billy.send_slack_message("#search-dev", "Slack messaging unit test. :tada:")

    def test_send_failing_message(self):
        billy = Billy(token="foo")
        self.assertRaises(AttributeError, billy.send_slack_message, "#search-dev", "This should not be appear.")

if __name__ == "__main__":
    unittest.main()