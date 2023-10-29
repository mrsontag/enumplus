from unittest import TestCase
from app.enriched_enum import ElevatedEnum, EnumIntItem

class TestEnum(ElevatedEnum):
    default_attributes = {
        "default_int": 1,
        "default_string": "default_value",
        "default_bool": False,
        "default_list": [1, 2, 3],
    }

    one = EnumIntItem(
        1,
        label="One",
    )
    two = EnumIntItem(
        2,
        label="two",
        default_string="Value of Two",
        default_bool=True,
        default_list=[2, 3, 4],
        default_int=4
    )
    three = EnumIntItem(
        3,
        label="Three"
    )

class EnumInstanceTestCase(TestCase):
    def test_enum_isinstance(self):
        """
        Individual Enums are instances of their Enum Class, the ElevatedEnum class, and the EnumItem class
        """
        one_enum = TestEnum.one
        self.assertTrue(isinstance(one_enum, TestEnum))
        self.assertTrue(isinstance(one_enum, EnumIntItem))
        self.assertTrue(isinstance(one_enum, ElevatedEnum))

    def test_cannot_add_attributes(self):
        """
        Individual Enum Instances cannot have attributes added to them at run-time
        """
        one_enum = TestEnum.one
        with self.assertRaises(AttributeError):
            one_enum.new_attribute = "Test"
        
    def test_attributes_all_same_type(self):
        with self.assertRaises(TypeError):
            class TestEnum(ElevatedEnum):
                one = EnumIntItem(
                    1,
                    "one",
                    test=1  # Not the same datatype as in TestEnum.two
                )
                two = EnumIntItem(
                    2,
                    "one",
                    test="string"  # Not the same datatype as in TestEnum.one
                )

class EnumAttributesTestCase(TestCase):
    def test_by_int(self):
        self.assertEqual(TestEnum.by_default_int(4), TestEnum.two)

    def test_by_string(self):
        self.assertEqual(TestEnum.by_default_string("Value of Two"), TestEnum.two)

    def test_by_bool(self):
        self.assertEqual(TestEnum.by_default_bool(True), TestEnum.two)

    def test_by_int(self):
        self.assertEqual(TestEnum.by_default_int(4), TestEnum.two)


class EnumHelperMethodsTestCase(TestCase):
    def test_to_dict(self):
        expected = {
            1: {"label": "One", "default_int": 1, "default_bool": False},
            2: {"label": "two", "default_int": 4, "default_bool": True},
            3: {"label": "Three", "default_int": 1, "default_bool": False}
        }
        self.assertDictEqual(
            TestEnum.to_dict(attributes=["label", "default_int", "default_bool"]),
            expected
        )
    def test_choices(self):
        expected = (
            (1, "One"),
            (2, "two"),
            (3, "Three"),
        )
        self.assertEqual(
            TestEnum.choices(),
            expected,
        )