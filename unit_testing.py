import unittest
from unittest.mock import patch, mock_open, MagicMock
import importlib.util
import sys
import os
import time

# Load your keylogger module dynamically
SCRIPT_FILENAME = "key.py"
file_path = os.path.join(os.path.dirname(__file__), SCRIPT_FILENAME)
spec = importlib.util.spec_from_file_location("keylogger", file_path)
keylogger = importlib.util.module_from_spec(spec)
sys.modules["keylogger"] = keylogger
spec.loader.exec_module(keylogger)


class TestKeylogger(unittest.TestCase):

    def setUp(self):
        # Reset global vars in keylogger before each test
        keylogger.t = ""
        keylogger.pics_names = []
        keylogger.interval = 60
        keylogger.start_time = time.time()

    def tearDown(self):
        # Clean up any created files
        if os.path.exists("Logfile.txt"):
            os.remove("Logfile.txt")
        # Remove any screenshot files
        for pic in keylogger.pics_names:
            if os.path.exists(pic):
                os.remove(pic)
        keylogger.t = ""
        keylogger.pics_names = []

    @patch("keylogger.OpenKey")
    @patch("keylogger.SetValueEx")
    def test_add_startup(self, mock_setvalueex, mock_openkey):
        keylogger.addStartup()
        mock_openkey.assert_called()
        mock_setvalueex.assert_called()

    @patch("keylogger.win32console.GetConsoleWindow")
    @patch("keylogger.win32gui.ShowWindow")
    def test_hide(self, mock_show, mock_getwin):
        mock_getwin.return_value = 1234
        keylogger.Hide()
        mock_show.assert_called_with(1234, 0)

    @patch("pyautogui.screenshot")
    def test_screenshot(self, mock_screenshot):
        mock_img = MagicMock()
        mock_screenshot.return_value = mock_img
        keylogger.ScreenShot()
        self.assertEqual(len(keylogger.pics_names), 1)
        mock_img.save.assert_called_once()

    @patch("keylogger.smtplib.SMTP")
    @patch("builtins.open", new_callable=mock_open, read_data="dummydata")
    def test_mail_it(self, mock_file, mock_smtp):
        smtp_instance = MagicMock()
        mock_smtp.return_value = smtp_instance

        keylogger.Mail_it("Hello", ["test.png"])
        smtp_instance.login.assert_called()
        smtp_instance.sendmail.assert_called()
        smtp_instance.quit.assert_called()

    def test_on_press_logic_triggers_mail(self):
        class FakeKey:
            def __init__(self, char):
                self.char = char

        fake_key = FakeKey('x')

        with patch("keylogger.Mail_it") as mock_mail:
            keylogger.t = "existing data "
            # Set start_time so interval triggers mail sending
            keylogger.start_time = time.time() - (keylogger.interval + 1)

            keylogger.on_press(fake_key)

            # Check that Mail_it was called with the expected data
            mock_mail.assert_called_once()
            # Check that t was reset after sending
            self.assertEqual(keylogger.t, "")

    def test_on_press_logic_no_mail_trigger(self):
        class FakeKey:
            def __init__(self, char):
                self.char = char

        fake_key = FakeKey('y')

        with patch("keylogger.Mail_it") as mock_mail:
            keylogger.t = ""
            keylogger.start_time = time.time()  # Not enough time passed to trigger mail

            keylogger.on_press(fake_key)

            self.assertIn("Keyboard Key", keylogger.t)
            mock_mail.assert_not_called()

    def test_on_click_logic(self):
        with patch("keylogger.Mail_it") as mock_mail, patch("keylogger.ScreenShot") as mock_shot:
            keylogger.t = "a" * 301  # trigger screenshot
            keylogger.start_time = time.time() - (keylogger.interval + 1)  # force mail sending
            keylogger.on_click(100, 100, "Button.left", True)
            mock_shot.assert_called()
            mock_mail.assert_called()

    def test_logfile_write_on_large_buffer(self):
        class FakeKey:
            def __init__(self, char):
                self.char = char

        fake_key = FakeKey('z')
        
        # Make t long enough to trigger file write
        keylogger.t = "x" * 501
        
        with patch("builtins.open", mock_open()) as mock_file:
            keylogger.on_press(fake_key)
            mock_file.assert_called_with("Logfile.txt", "a")
            handle = mock_file()
            handle.write.assert_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)


    