import assert from "node:assert/strict";
import { test } from "node:test";
import { decodeHtml, hostOnDomain, urlAtPath, urlOnDomain } from "../lib/html-url.js";

const BYPASSES = [
  "https://evil.com/?x=player.vimeo.com",
  "https://player.vimeo.com.evil.com/video/1",
  "https://user@player.vimeo.com@evil.com/video/1",
  "https://evilplayer.vimeo.com.net/",
  "javascript://player.vimeo.com/%0aalert(1)"
];

test("hostOnDomain matches exact host and subdomains only", () => {
  assert.ok(hostOnDomain("webflow.io", "webflow.io"));
  assert.ok(hostOnDomain("site.webflow.io", "webflow.io"));
  assert.ok(!hostOnDomain("evilwebflow.io", "webflow.io"));
  assert.ok(!hostOnDomain("webflow.io.evil.com", "webflow.io"));
  assert.ok(!hostOnDomain("", "webflow.io"));
});

test("urlOnDomain rejects substring bypasses", () => {
  assert.ok(urlOnDomain("https://player.vimeo.com/video/1", "player.vimeo.com"));
  for (const url of BYPASSES) {
    assert.ok(!urlOnDomain(url, "player.vimeo.com"), url);
  }
  assert.ok(!urlOnDomain("https://evil.com/?x=site.webflow.io", "webflow.io"));
});

test("urlAtPath checks host and path prefix", () => {
  assert.ok(urlAtPath("https://www.youtube.com/embed/abc", "youtube.com", "/embed"));
  assert.ok(!urlAtPath("https://evil.com/youtube.com/embed/abc", "youtube.com", "/embed"));
  assert.ok(!urlAtPath("https://www.youtube.com/watch?v=embed", "youtube.com", "/embed"));
});

test("decodeHtml decodes each entity once", () => {
  assert.equal(decodeHtml("a &amp; b &lt;c&gt; &quot;d&quot; &#39;e&#39;"), "a & b <c> \"d\" 'e'");
  assert.equal(decodeHtml("&amp;lt;script&amp;gt;"), "&lt;script&gt;");
  assert.equal(decodeHtml("&amp;amp;"), "&amp;");
});
