// URL host matching and HTML entity decoding for the hosted intake.
//
// Substring checks such as url.includes("player.vimeo.com") accept
// https://evil.com/?x=player.vimeo.com; compare the parsed hostname.

const WEB_PROTOCOLS = new Set(["http:", "https:"]);
const HTML_ENTITIES = {
  "&amp;": "&",
  "&lt;": "<",
  "&gt;": ">",
  "&quot;": '"',
  "&#39;": "'"
};
const HTML_ENTITY_PATTERN = /&(?:amp|lt|gt|quot|#39);/g;

function parseUrl(value) {
  try {
    return new URL(value);
  } catch {
    return null;
  }
}

// True when host equals a domain or is its subdomain.
export function hostOnDomain(host, ...domains) {
  const normalized = String(host || "").toLowerCase().replace(/\.$/, "");
  if (!normalized) {
    return false;
  }
  return domains.some((domain) => normalized === domain || normalized.endsWith(`.${domain}`));
}

// True for an http(s) URL whose host is on one of the domains.
export function urlOnDomain(value, ...domains) {
  const parsed = parseUrl(value);
  if (!parsed || !WEB_PROTOCOLS.has(parsed.protocol)) {
    return false;
  }
  return hostOnDomain(parsed.hostname, ...domains);
}

// True for an http(s) URL on a domain whose path starts with pathPrefix.
export function urlAtPath(value, domain, pathPrefix) {
  if (!urlOnDomain(value, domain)) {
    return false;
  }
  return new URL(value).pathname.toLowerCase().startsWith(pathPrefix);
}

// Single-pass decode: "&amp;lt;" becomes "&lt;", never "<".
export function decodeHtml(value) {
  return String(value).replace(HTML_ENTITY_PATTERN, (entity) => HTML_ENTITIES[entity]);
}
