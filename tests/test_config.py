import os
import unittest
from pathlib import Path
from examai.config import get_settings, update_config_key

class TestConfig(unittest.TestCase):
    def test_settings_load(self):
        """Test that settings load successfully with default values."""
        settings = get_settings()
        self.assertIsNotNone(settings.db_host)
        self.assertIsNotNone(settings.db_port)
        self.assertIsNotNone(settings.default_provider)

    def test_settings_update(self):
        """Test that we can update settings keys successfully."""
        settings_before = get_settings()
        original_theme = settings_before.theme
        
        # Test changing theme
        update_config_key("THEME", "matrix")
        settings_after = get_settings()
        self.assertEqual(settings_after.theme, "matrix")
        
        # Restore theme
        update_config_key("THEME", original_theme)
