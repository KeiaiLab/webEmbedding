"""Host checks must reject substring bypasses."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

MCP_ROOT = Path(__file__).resolve().parents[1] / "bundle" / "source-first-clone" / "mcp"
sys.path.insert(0, str(MCP_ROOT))

from source_first_clone.platform_adapters import inspect_platform_adapter
from source_first_clone.reproduction import (
    classify_candidate,
    infer_platform,
)
from source_first_clone.url_hosts import (
    host_on_domain,
    html_links_domain,
    url_on_domain,
)

BYPASSES = (
    "https://evil.com/?x=figma.com",
    "https://figma.com.evil.com/file/abc",
    "https://user@figma.com@evil.com/",
    "https://evilfigma.com/file/abc",
    "javascript://figma.com/%0aalert(1)",
)


class HostOnDomainTest(unittest.TestCase):
    def test_exact_and_subdomain(self) -> None:
        self.assertTrue(host_on_domain("figma.com", "figma.com"))
        self.assertTrue(host_on_domain("www.figma.com", "figma.com"))

    def test_lookalikes(self) -> None:
        self.assertFalse(host_on_domain("evilfigma.com", "figma.com"))
        self.assertFalse(host_on_domain("figma.com.evil.com", "figma.com"))
        self.assertFalse(host_on_domain("", "figma.com"))

    def test_url_bypasses(self) -> None:
        self.assertTrue(url_on_domain("https://www.figma.com/file/abc", "figma.com"))
        for url in BYPASSES:
            with self.subTest(url=url):
                self.assertFalse(url_on_domain(url, "figma.com"))


class HtmlLinksDomainTest(unittest.TestCase):
    def test_links(self) -> None:
        self.assertTrue(html_links_domain('<iframe src="https://embed.readymag.com/x">', "embed.readymag.com"))
        self.assertTrue(html_links_domain('{"u":"https:\\/\\/www.figma.com\\/file"}', "figma.com"))

    def test_bypasses(self) -> None:
        self.assertFalse(html_links_domain('<a href="https://evil.com/?x=figma.com">', "figma.com"))
        self.assertFalse(html_links_domain('<a href="https://figma.com.evil.com/">', "figma.com"))
        self.assertFalse(html_links_domain('<a href="https://notfigma.com/">', "figma.com"))


class InferPlatformTest(unittest.TestCase):
    def test_known(self) -> None:
        self.assertEqual(infer_platform("https://www.figma.com/file/abc"), "figma")
        self.assertEqual(infer_platform("https://youtu.be/abc"), "youtube")
        self.assertEqual(infer_platform("https://player.vimeo.com/video/1"), "vimeo")
        self.assertEqual(infer_platform("https://codepen.io/a/pen/b"), "codepen")

    def test_bypasses(self) -> None:
        for url in BYPASSES:
            with self.subTest(url=url):
                self.assertNotEqual(infer_platform(url), "figma")
        self.assertEqual(infer_platform("https://evil.com/?v=youtube.com"), "generic")


class ClassifyCandidateTest(unittest.TestCase):
    def test_known(self) -> None:
        self.assertEqual(classify_candidate("https://www.figma.com/embed?url=x"), "figma-embed")
        self.assertEqual(classify_candidate("https://embed.readymag.com/abc"), "readymag-embed")
        self.assertEqual(classify_candidate("https://www.youtube.com/embed/abc"), "youtube-embed")
        self.assertEqual(classify_candidate("https://player.vimeo.com/video/1"), "vimeo-embed")
        self.assertEqual(classify_candidate("https://codepen.io/a/embed/b"), "codepen-embed")
        self.assertEqual(classify_candidate("https://app.spline.design/file/x?view=preview"), "spline-preview")

    def test_bypasses(self) -> None:
        self.assertNotEqual(classify_candidate("https://evil.com/?x=https://www.figma.com/embed"), "figma-embed")
        self.assertNotEqual(classify_candidate("https://www.figma.com.evil.com/embed"), "figma-embed")
        self.assertNotEqual(classify_candidate("https://user@www.youtube.com@evil.com/embed/x"), "youtube-embed")
        self.assertNotEqual(classify_candidate("https://embed.readymag.com.evil.com/"), "readymag-embed")


class PlatformAdapterTest(unittest.TestCase):
    def test_figma_host(self) -> None:
        adapter = inspect_platform_adapter("https://www.figma.com/file/abc/x", "")
        self.assertEqual(adapter["platform"], "figma")
        self.assertEqual(adapter["candidates"][0]["kind"], "figma-embed")

    def test_figma_bypasses(self) -> None:
        for url in BYPASSES:
            with self.subTest(url=url):
                self.assertNotEqual(inspect_platform_adapter(url, "")["platform"], "figma")

    def test_readymag_lookalike(self) -> None:
        adapter = inspect_platform_adapter("https://evilreadymag.com/", "")
        self.assertNotEqual(adapter["platform"], "readymag")


if __name__ == "__main__":
    unittest.main()
