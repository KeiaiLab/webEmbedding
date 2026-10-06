"""Hostname matching on parsed URLs.

Substring checks such as ``"figma.com" in url`` accept
``https://evil.com/?x=figma.com`` and ``https://figma.com.evil.com``.
These helpers compare the parsed hostname instead.
"""

from __future__ import annotations

import re
from functools import cache
from urllib.parse import SplitResult, urlsplit

HTTPS_SCHEME = "https"
WEB_SCHEMES = frozenset({"http", HTTPS_SCHEME})


def split_url(url: str) -> SplitResult | None:
    """Parse ``url``; ``None`` when it is malformed."""
    try:
        return urlsplit((url or "").strip())
    except ValueError:
        return None


def url_host(url: str) -> str:
    """Lower-cased hostname of ``url``, ``""`` when absent."""
    parts = split_url(url)
    if parts is None:
        return ""
    try:
        return (parts.hostname or "").lower()
    except ValueError:
        return ""


def host_on_domain(host: str, *domains: str) -> bool:
    """True when ``host`` equals a domain or is its subdomain.

    ``www.figma.com`` is on ``figma.com``; ``figma.com.evil.com`` and
    ``evilfigma.com`` are not.
    """
    host = (host or "").lower().rstrip(".")
    if not host:
        return False
    for domain in domains:
        if host == domain or host.endswith("." + domain):
            return True
    return False


def url_on_domain(url: str, *domains: str) -> bool:
    """True when ``url`` is an http(s) URL whose host is on a domain."""
    parts = split_url(url)
    if parts is None or parts.scheme.lower() not in WEB_SCHEMES:
        return False
    return host_on_domain(url_host(url), *domains)


def https_url_at(url: str, host: str, path_prefix: str = "/") -> bool:
    """True for ``https://<host><path_prefix>...`` with an exact host."""
    parts = split_url(url)
    if parts is None or parts.scheme.lower() != HTTPS_SCHEME:
        return False
    if url_host(url) != host:
        return False
    return parts.path.lower().startswith(path_prefix)


@cache
def _domain_link_re(domain: str) -> re.Pattern[str]:
    # "//" (or JSON-escaped "\/\/") + optional subdomain labels + domain,
    # then an authority end.
    return re.compile(
        r"(?://|\\/\\/)(?:[a-z0-9-]+\.)*" + re.escape(domain) + r"(?=[/:?#\"'\s\\]|$)",
        re.IGNORECASE,
    )


def html_links_domain(html: str, domain: str) -> bool:
    """True when ``html`` references a URL whose host is on ``domain``."""
    return bool(_domain_link_re(domain).search(html or ""))
