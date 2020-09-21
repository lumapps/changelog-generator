import re
from typing import List, Optional

re_header_pattern = re.compile(
    "^(?P<type>[^\(]+)\((?P<scope>[^\)]+)\): (?P<subject>.+)$"
)
re_jira_pattern = re.compile("([A-Z]{2,4}-[0-9]{1,6})")
re_broke_pattern = re.compile("^BROKEN:$")
re_revert_header_pattern = re.compile("^[R|r]evert:? (?P<summary>.*)$")
re_revert_commit_pattern = re.compile("^This reverts commit ([a-f0-9]+)")
re_temp_header_pattern = re.compile("^(fixup!|squash!).*$")


class Commit:
    sha1: str
    short: str
    summary: str
    message: str

    revert: Optional["Commit"]
    type: Optional[str]
    scope: Optional[str]
    subject: Optional[str]
    jiras: List[str]

    def getHeaderData(self) -> None:
        self.type = None
        self.scope = None
        self.subject = None

        res = re_header_pattern.match(self.summary)
        if res:
            self.type = res.group("type")
            self.scope = res.group("scope")
            self.subject = res.group("subject")
        else:
            self.type = "unknown"
            self.scope = "any"
            self.subject = self.summary

    def getRevertData(self) -> None:
        self.revert = None

        res = re_revert_header_pattern.match(self.summary)
        if res:
            self.type = "revert"

            # TODO: properly fetch the reverted commit */
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

    def getJiraData(self) -> None:
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

        self.getHeaderData()
        self.getRevertData()
        self.getJiraData()
