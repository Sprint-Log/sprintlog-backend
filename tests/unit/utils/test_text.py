from app.utils import camel_case, check_email, slugify


def test_check_email() -> None:
    valid_email = "test@test.com"
    valid_email_upper = "TEST@TEST.COM"

    assert check_email(valid_email) == valid_email
    assert check_email(valid_email_upper) == valid_email


def test_slugify() -> None:
    string = "This is a Test!"
    expected_slug = "this-is-a-test"
    assert slugify(string) == expected_slug
    assert slugify(string, separator="_") == "this_is_a_test"


def test_camel_case() -> None:
    string = "this_is_a_test"
    assert camel_case(string) == "thisIsATest"
