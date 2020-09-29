import re
from typing import List, Optional

re_header_pattern = re.compile(
    r"^(?P<type>[^\(]+)\((?P<scope>[^\)]+)\): (?P<subject>.+)$"
)
re_jira_pattern = re.compile(r"([A-Z]{2,4}-[0-9]{1,6})")
re_broke_pattern = re.compile(r"^BROKEN:$")
re_revert_header_pattern = re.compile(r"^[R|r]evert:? (?P<summary>.*)$")
re_revert_commit_pattern = re.compile(r"^This reverts commit ([a-f0-9]+)")
re_temp_header_pattern = re.compile(r"^(fixup!|squash!).*$")


class Commit:
    sha1: str
    short: str
    summary: str
    message: str

    revert: Optional["Commit"]
    commit_type: Optional[str]
    scope: Optional[str]
    subject: Optional[str]
    jiras: List[str]

    def get_header_data(self) -> None:
        self.commit_type = None
        self.scope = None
        self.subject = None

        res = re_header_pattern.match(self.summary)
        if res:
            self.commit_type = res.group("type")
            self.scope = res.group("scope")
            self.subject = res.group("subject")
        else:
            self.commit_type = "unknown"
            self.scope = "any"
            self.subject = self.summary

    def get_revert_data(self) -> None:
        self.revert = None

        res = re_revert_header_pattern.match(self.summary)
        if res:
            self.commit_type = "revert"

            self.revert = Commit(
                hexsha="", summary=res.group("summary"), message=res.group("summary")
            )

            summary_res = re_header_pattern.match(res.group("summary"))
            if summary_res:
                self.scope = summary_res.group("scope")
                self.subject = "revert %s" % summary_res.group("subject")
            else:
                self.scope = "any"
                self.subject = "revert %s" % res.group("summary")

    def get_jira_data(self) -> None:
        self.jiras = []

        for line in self.message.split("\n"):
            res = re_jira_pattern.findall(line)
            if res:
                self.jiras.extend(res)

    def __init__(self, hexsha: str, summary: str, message: str) -> None:
        self.sha1 = hexsha
        self.short = hexsha[:8]
        self.message = message
        self.summary = summary

        self.get_header_data()
        self.get_revert_data()
        self.get_jira_data()
