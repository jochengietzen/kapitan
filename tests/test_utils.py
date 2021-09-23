import unittest

from kapitan.errors import CompileError
from kapitan.utils import name_replace_by_func, generate_replace_func_comp_settings


class ReplaceFuncTest(unittest.TestCase):
    def setUp(self):
        self.repl_lambda_no_args = lambda: "bar"
        self.repl_lambda_too_many_args = lambda arg0, arg1: "bar"
        self.repl_lambda = lambda name: "bar"

        def find_replace_add(name: str):
            return name + "bar"

        self.find_replace_add = find_replace_add
        self.replace_settings_simple = {"find": "foo", "replace": "bar"}
        self.regex_settings_simple = {"regex_find": ".j(inja)?2$", "regex_replace": ""}
        self.regex_settings_group = {"regex_find": "(.*)\.jinja2", "regex_replace": "\g<1>"}

    def test_name_replace_by_func(self):
        """
        Tests the utils function name_replace_by_func
        """
        # Needs to take at least one argument
        self.assertRaises(TypeError, name_replace_by_func, ("foo", self.repl_lambda_no_args))

        # Needs to take at most one argument
        self.assertRaises(TypeError, name_replace_by_func, ("foo", self.repl_lambda_too_many_args))

        # Identity if no function
        self.assertEqual("foo", name_replace_by_func("foo", None))

        # Proper foo bar replacement
        self.assertEqual("bar", name_replace_by_func("foo", self.repl_lambda))

        # Normal callable function
        self.assertEqual("foobar", name_replace_by_func("foo", self.find_replace_add))

    def test_generate_replace_func_comp_settings(self):
        """
        Tests the utils function generate_replace_func_comp_settings
        """
        kwargs = {}
        r_key = "test_key"
        # Nothing should be changed, if no function is provided
        generate_replace_func_comp_settings(
            kwargs,
            replace_settings=None,
            repl_func_key=r_key,
        )
        # kwargs shouldn't be changed and no r_key should be present
        self.assertEqual(0, len(kwargs.keys()))
        self.assertTrue(r_key not in kwargs)

        # Test simple replace funciton
        kwargs = {}
        generate_replace_func_comp_settings(
            kwargs,
            replace_settings=self.replace_settings_simple,
            repl_func_key=r_key,
        )
        # kwargs should not be empty anymore
        self.assertNotEqual(0, len(kwargs.keys()))
        self.assertTrue(r_key in kwargs)
        # Function should work
        self.assertEqual("bar", kwargs[r_key]("foo"))
        self.assertEqual("bar2", kwargs[r_key]("foo2"))

        # Test first regex function
        kwargs = {}
        generate_replace_func_comp_settings(
            kwargs,
            replace_settings=self.regex_settings_simple,
            repl_func_key=r_key,
        )
        # kwargs should not be empty anymore
        self.assertNotEqual(0, len(kwargs.keys()))
        self.assertTrue(r_key in kwargs)
        # Function should work
        self.assertEqual("foo.yml", kwargs[r_key]("foo.yml.jinja2"))
        self.assertEqual("foo.yml", kwargs[r_key]("foo.yml.j2"))

        # Test second regex function
        kwargs = {}
        generate_replace_func_comp_settings(
            kwargs,
            replace_settings=self.regex_settings_group,
            repl_func_key=r_key,
        )
        # kwargs should not be empty anymore
        self.assertNotEqual(0, len(kwargs.keys()))
        self.assertTrue(r_key in kwargs)
        # Function should work
        self.assertEqual("foo.yml", kwargs[r_key]("foo.yml.jinja2"))

        # Test correct errors
        self.assertRaises(
            CompileError,
            generate_replace_func_comp_settings,
            {},
            {"find": "a", "repl": "b"},
        )
        # Test incorrect regex
        self.assertRaises(
            CompileError,
            generate_replace_func_comp_settings,
            {},
            {"regex_find": "^.(a", "regex_replace": "b"},
        )

        # Test evaluation order
        kwargs = {}
        generate_replace_func_comp_settings(
            kwargs,
            replace_settings={**self.replace_settings_simple, **self.regex_settings_simple},
            repl_func_key=r_key,
        )
        self.assertEqual("bar.jinja2", kwargs[r_key]("foo.jinja2"))
