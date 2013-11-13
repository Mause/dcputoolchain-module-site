import common

from mock import patch, MagicMock, ANY


@patch('logging.error', autospec=True)
@patch('dtmm_utils.users', autospec=True)
@patch('dtmm_utils.development', autospec=True)
@patch('dtmm_utils.BaseRequestHandler.dorender', autospec=True)
class TestBaseRequestHandler(common.DMSTestCase):
    def setUp(self):
        super(TestBaseRequestHandler, self).setUp()
        self.testbed.init_mail_stub()

    def test_base_handler_is_development(self, dorender, development, users, error):
        development.return_value = True

        import dtmm_utils
        handler = dtmm_utils.BaseRequestHandler(MagicMock(), MagicMock())
        try:
            raise Exception()
        except Exception as e:
            self.assertRaises(
                Exception,
                lambda: handler.handle_exception(e, MagicMock())
            )

    def test_base_handler_not_development(self, dorender, development, users, error):
        dorender.return_value = 'world'
        development.return_value = False

        import dtmm_utils
        handler = dtmm_utils.BaseRequestHandler(MagicMock(), MagicMock())

        self.assertRaises(
            Exception,
            lambda: handler.handle_exception(Exception(), MagicMock()),
        )

    def test_base_handler_not_admin(self, dorender, development, users, error):
        dorender.return_value = 'world'
        development.return_value = False
        users.is_current_user_admin.return_value = False

        import webapp2
        response = MagicMock(name='response', spec=webapp2.Response)

        import dtmm_utils
        handler = dtmm_utils.BaseRequestHandler(MagicMock(), response)

        handler.handle_exception(AssertionError(), MagicMock())
        dorender.assert_called_with(ANY, 'unexpected_result.html', {})
        self.assertEqual(response.status, 500)

        handler.handle_exception(Exception(), MagicMock())
        self.assertEqual(response.status, 500)

    def test_base_handler_is_admin(self, dorender, development, users, error):
        dorender.return_value = 'world'
        development.return_value = False
        users.is_current_user_admin.return_value = True

        import dtmm_utils
        handler = dtmm_utils.BaseRequestHandler(MagicMock(), MagicMock())

        self.assertRaises(
            Exception, handler.handle_exception, (Exception(), MagicMock()))

if __name__ == '__main__':
    common.main()
