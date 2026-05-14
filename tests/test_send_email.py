import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


def load_send_email_module():
    module_path = Path(__file__).resolve().parents[1] / ".github" / "actions" / "send_email.py"
    spec = importlib.util.spec_from_file_location("send_email_module", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("yagmail", types.SimpleNamespace(SMTP=object))
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SendEmailRemoteJobsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_send_email_module()

    def test_load_remote_jobs_report_reads_existing_markdown(self):
        report_body = """主题：每日远程岗位推荐 - 2026-05-08

今天找到 2 个值得投递的岗位。

## 国内高优先级可直接投

1. S | Senior Full Stack Engineer | Example Inc | 来源：V2EX
- 申请链接：https://example.com/job-1
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
            tmp.write(report_body)
            report_path = tmp.name

        report = self.module.load_remote_jobs_report(report_path)

        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["title"], "每日远程岗位推荐 - 2026-05-08")
        self.assertIn("Senior Full Stack Engineer", report["content"])

    def test_load_remote_jobs_report_marks_missing_file(self):
        report = self.module.load_remote_jobs_report("/tmp/does-not-exist-remote-jobs.md")

        self.assertEqual(report["status"], "ready")
        self.assertTrue(report["path"].endswith("remote-jobs/daily_remote_jobs_2026-05-13.md"))
        self.assertEqual(report["requested_path"], "/tmp/does-not-exist-remote-jobs.md")
        self.assertIn("已自动使用最近可用报告", report["fallback_message"])

    def test_load_remote_jobs_report_marks_missing_when_no_fallback_exists(self):
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                report = self.module.load_remote_jobs_report("remote-jobs/daily_remote_jobs_2099-01-01.md")
            finally:
                os.chdir(original_cwd)

        self.assertEqual(report["status"], "missing")
        self.assertIn("未找到", report["message"])

    def test_format_email_includes_remote_jobs_section_when_report_ready(self):
        report = {
            "status": "ready",
            "title": "每日远程岗位推荐 - 2026-05-08",
            "path": "/tmp/daily_remote_jobs_2026-05-08.md",
            "content": """主题：每日远程岗位推荐 - 2026-05-08

今天找到 2 个值得投递的岗位。

## 国内高优先级可直接投

1. S | Senior Full Stack Engineer | Example Inc | 来源：V2EX
- 远程范围：全球远程
- 申请链接：https://example.com/job-1
""",
        }

        html = self.module.format_email({"githubTrending": {}}, report)

        self.assertIn("每日远程岗位推荐 - 2026-05-08", html)
        self.assertIn("Senior Full Stack Engineer", html)
        self.assertIn("https://example.com/job-1", html)

    def test_format_email_omits_remote_jobs_section_when_not_requested(self):
        html = self.module.format_email({"githubTrending": {}}, None)

        self.assertNotIn("每日远程岗位推荐", html)
        self.assertNotIn("远程岗位", html)

    def test_format_email_shows_warning_when_report_is_missing(self):
        report = {
            "status": "missing",
            "message": "未找到远程岗位报告：remote-jobs/daily_remote_jobs_2026-05-08.md",
            "path": "remote-jobs/daily_remote_jobs_2026-05-08.md",
        }

        html = self.module.format_email({"githubTrending": {}}, report)

        self.assertIn("远程岗位报告未同步", html)
        self.assertIn("remote-jobs/daily_remote_jobs_2026-05-08.md", html)

    def test_format_email_handles_legacy_all_label_and_keeps_remote_jobs(self):
        report = {
            "status": "ready",
            "title": "每日远程岗位推荐 - 2026-05-13",
            "path": "/tmp/daily_remote_jobs_2026-05-13.md",
            "content": """主题：每日远程岗位推荐 - 2026-05-13

1. S | Full-Stack AI Engineer | Tripilot
- 申请链接：https://eleduck.com/posts/82f2d4
""",
        }
        data = {
            "githubTrending": {
                "": "All",
                "typescript": [
                    {
                        "title": "example/repo",
                        "description": "Example repository",
                        "language": "TypeScript",
                        "stars": "123",
                        "todayStars": "45 stars today",
                        "link": "/example/repo",
                    }
                ],
            }
        }

        html = self.module.format_email(data, report)

        self.assertIn("📦 GitHub Trending - All", html)
        self.assertIn("example/repo", html)
        self.assertIn("每日远程岗位推荐 - 2026-05-13", html)
        self.assertIn("https://eleduck.com/posts/82f2d4", html)

    def test_format_email_includes_fallback_hint_when_using_latest_report(self):
        report = {
            "status": "ready",
            "title": "每日远程岗位推荐 - 2026-05-13",
            "path": "/tmp/daily_remote_jobs_2026-05-13.md",
            "requested_path": "/tmp/daily_remote_jobs_2026-05-14.md",
            "fallback_message": "已自动使用最近可用报告：daily_remote_jobs_2026-05-13.md",
            "content": """主题：每日远程岗位推荐 - 2026-05-13

1. A | Example Role | Example Inc
- 申请链接：https://example.com/jobs/1
""",
        }

        html = self.module.format_email({"githubTrending": {}}, report)

        self.assertIn("已自动使用最近可用报告", html)
        self.assertIn("daily_remote_jobs_2026-05-13.md", html)


if __name__ == "__main__":
    unittest.main()
