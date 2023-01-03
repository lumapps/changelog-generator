from changelog_generator.commit import Commit


def test_no_reference():
    commit = Commit("", "", "a commit without any reference")

    assert commit.jiras == []


def test_one_reference():
    commit = Commit("", "", "this is a reference ABCD-1")

    assert commit.jiras == ["ABCD-1"]


def test_several_reference():
    commit = Commit(
        "",
        "",
        "valid references ABCD-1 AB-0001 FOO2-1, and not valid ones A-123 abc-145 ABC_524 ",
    )

    assert commit.jiras == ["ABCD-1", "AB-0001", "FOO2-1"]
