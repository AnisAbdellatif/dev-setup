"""python3 -B scripts/test_picker.py  (unit tests; the pty smoke test needs prompt_toolkit, skipped if absent)"""
import os
import pty
import select
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from picker import visible

ROWS = [{"id": "git", "label": "Git VCS", "group": "Core CLI"},
        {"id": "uv", "label": "uv python", "group": "Python (uv)"},
        {"id": "ripgrep", "label": "fast grep", "group": "Core CLI"}]


class Visible(unittest.TestCase):
    def test_filter(self):
        self.assertEqual(len(visible(ROWS, "")), 3)
        self.assertEqual([r["id"] for r in visible(ROWS, "GREP")], ["ripgrep"])
        self.assertEqual([r["id"] for r in visible(ROWS, "core fast")], ["ripgrep"])  # group + label words
        self.assertEqual(visible(ROWS, "zzz"), [])


@unittest.skipUnless(os.name == "posix", "pty is POSIX only")
class Pty(unittest.TestCase):
    def test_pick_roundtrip(self):
        try:
            import prompt_toolkit  # noqa: F401
        except ImportError:
            self.skipTest("prompt_toolkit missing")
        code = ("import picker;r=[{'id':'a','label':'alpha','group':'G'},{'id':'b','label':'beta','group':'G'}]"
                "\nprint('RESULT',sorted(picker.pick(r,{'a'},'t')))")
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(os.path.dirname(__file__))
            os.execv(sys.executable, [sys.executable, "-c", code])
        out = b""

        def pump(t=0.6):
            nonlocal out
            end = time.time() + t
            while time.time() < end:
                if select.select([fd], [], [], 0.1)[0]:
                    try:
                        out += os.read(fd, 65536)
                    except OSError:
                        return
        pump(1.5)
        os.write(fd, b"be")      # filter to beta
        pump()
        os.write(fd, b" ")       # toggle it
        pump()
        os.write(fd, b"\r")      # done
        pump(1.0)
        os.waitpid(pid, 0)
        self.assertIn(b"RESULT ['a', 'b']", out)


if __name__ == "__main__":
    unittest.main()
