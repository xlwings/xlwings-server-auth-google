from googleapiclient.http import HttpMockSequence

from app import settings
from app.core import directory_env, directory_google


def test_directory_env():
    settings.group_admin = ["a@b.com", "c@d.com"]
    assert directory_env.is_member(email="a@b.com", group="group_admin")
    assert not directory_env.is_member(email="x@y.com", group="group_admin")


def test_directory_google():
    http = HttpMockSequence([({"status": "200"}, '{"isMember": true}')])
    assert directory_google.is_member("test@test.com", "test@test.com", http=http)
    http = HttpMockSequence([({"status": "200"}, '{"isMember": false}')])
    assert not directory_google.is_member("test@test.com", "test@test.com", http=http)
