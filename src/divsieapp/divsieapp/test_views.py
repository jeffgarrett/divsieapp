import unittest

from pyramid import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from divsieapp.views import my_view
        request = testing.DummyRequest()
        request.user = None
        info = my_view(request)
        self.assertEqual(info['project'], 'divsieapp')
