"""Unit tests for tools/subnet.py (run: python -m unittest discover -s tests -v)."""
import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import subnet  # noqa: E402


def run(*args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = subnet.main(list(args))
    return code, out.getvalue()


class Conversions(unittest.TestCase):
    def test_round_trip(self):
        for ip in ("0.0.0.0", "10.0.0.1", "192.168.1.130", "255.255.255.255"):
            self.assertEqual(subnet.to_ip(subnet.to_int(ip)), ip)

    def test_to_int(self):
        self.assertEqual(subnet.to_int("1.2.3.4"), 0x01020304)

    def test_bad_addresses(self):
        for ip in ("256.1.1.1", "1.2.3", "1.2.3.4.5", "-1.0.0.0"):
            with self.subTest(ip=ip), self.assertRaises(ValueError):
                subnet.to_int(ip)


class Parse(unittest.TestCase):
    def test_cidr(self):
        self.assertEqual(subnet.parse("192.168.1.130/26"), (subnet.to_int("192.168.1.130"), 26))

    def test_dotted_mask(self):
        self.assertEqual(subnet.parse("10.0.0.5", "255.255.255.252"), (subnet.to_int("10.0.0.5"), 30))

    def test_mask_with_holes_is_refused(self):
        with self.assertRaises(ValueError):
            subnet.parse("10.0.0.5", "255.0.255.0")


class Describe(unittest.TestCase):
    def test_slash_26(self):
        code, out = run("192.168.1.130/26")
        self.assertEqual(code, 0)
        self.assertIn("mask       255.255.255.192   (block size 64)", out)
        self.assertIn("network    192.168.1.128", out)
        self.assertIn("broadcast  192.168.1.191", out)
        self.assertIn("hosts      192.168.1.129 - 192.168.1.190   (62 usable)", out)
        self.assertNotIn("warning", out)

    def test_slash_30_has_two_hosts(self):
        _, out = run("10.0.0.5/30")
        self.assertIn("(2 usable)", out)

    def test_slash_31_and_32_print_no_host_range(self):
        for cidr in ("10.0.0.4/31", "10.0.0.4/32"):
            with self.subTest(cidr=cidr):
                _, out = run(cidr)
                self.assertNotIn("hosts", out)

    def test_network_and_broadcast_addresses_warn(self):
        for cidr in ("192.168.1.128/26", "192.168.1.191/26"):
            with self.subTest(cidr=cidr):
                _, out = run(cidr)
                self.assertIn("warning", out)

    def test_dotted_mask_form(self):
        _, out = run("192.168.1.130", "255.255.255.192")
        self.assertIn("network    192.168.1.128", out)


class SameSubnet(unittest.TestCase):
    def test_same_and_different(self):
        _, out = run("10.0.0.5/30", "10.0.0.6", "10.0.0.9")
        self.assertRegex(out, r"10\.0\.0\.6\s+same subnet")
        self.assertRegex(out, r"10\.0\.0\.9\s+DIFFERENT subnet")


class Usage(unittest.TestCase):
    def test_no_arguments_prints_help(self):
        code, out = run()
        self.assertEqual(code, 1)
        self.assertIn("Subnet calculator", out)


if __name__ == "__main__":
    unittest.main()
