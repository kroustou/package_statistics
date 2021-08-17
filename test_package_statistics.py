#!/usr/bin/env python3
import unittest
import requests
from unittest.mock import patch
from package_statistics import ContentParser

MOCK_FILE = b""" FILE                                                    LOCATION
bin/bsd-csh                                             shells/csh
bin/busybox                                             utils/busybox,shells/busybox-static
bin/live-boot                                           misc/live-boot,admin/open-infrastructure-system-boot
bin/live-config                                         misc/live-config,admin/open-infrastructure-system-confiiiiiiag
bin/setupcon                                            utils/console-setup,utils/console-setup-mini,three,four,five
bin/sh                                                  shells/dash,more,more,more,more,more,more,more
bin/signify-openbsd                                     utils/signify-openbsd
bin/sleep                                               utils/coreutils
bin/ss                                                  net/iproute2
bin/stty                                                utils/coreutils
bin/su                                                  utils/util-linux
bin/sync                                                utils/coreutils
bin/systemctl                                           admin/systemd
bin/systemd                                             admin/systemd
bin/systemd-ask-password                                admin/systemd
bin/systemd-escape                                      admin/systemd
bin/systemd-hwdb                                        admin/udev
bin/loginctl                                            admin/elogind,admin/systemd,q,w,e,r,t,w,e,r,w,e,w,e,w,ew,w,s,w,ew,w,s,we
"""


class TestContentParser(unittest.TestCase):

    @patch("package_statistics.requests")
    @patch("package_statistics.gzip")
    def test_statistics(self, m_gzip, m_requests):
        content_parser = ContentParser("mock_url_is_mock")
        m_gzip.decompress.return_value = MOCK_FILE
        content_parser.get_statistics("amd64")
        self.assertEqual(
            content_parser.get_statistics("amd64"),
            {
                "bin/loginctl": 23,
                "bin/sh": 8,
                "bin/setupcon": 5,
                "bin/busybox": 2,
                "bin/live-boot": 2,
                "bin/live-config": 2,
                "bin/bsd-csh": 1,
                "bin/signify-openbsd": 1,
                "bin/sleep": 1,
                "bin/ss": 1,
            },
        )
        with self.assertRaises(TypeError):
            content_parser.get_statistics()

        m_gzip.decompress.side_effect = Exception(
            "corrupt"
        )
        with self.assertRaises(Exception):
            content_parser.get_statistics()


    @patch("package_statistics.requests")
    @patch("package_statistics.gzip")
    def test_contents(self, m_gzip, m_requests):

        content_parser = ContentParser("mock_url_is_mock")
        with self.assertRaises(TypeError):
            content_parser._get_contents()

        m_requests.get.side_effect = requests.exceptions.HTTPError(
            "requests unsuccessful"
        )
        with self.assertRaises(requests.exceptions.HTTPError):
            content_parser._get_contents("arch")

        m_requests.get.side_effect = None
        m_gzip.decompress.side_effect = Exception(
            "corrupt"
        )
        with self.assertRaises(Exception):
            content_parser._get_contents("arch")

    def test_init(self):
        content_parser = ContentParser("https://foo.bar/")
        self.assertEqual(content_parser._repository, "https://foo.bar")


if __name__ == "__main__":
    unittest.main()
