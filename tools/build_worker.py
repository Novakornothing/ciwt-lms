"""Build the novakornothing.com Cloudflare Worker (red-heart-caee) deploy script from the Flask templates.

Usage: DATABASE_URL=sqlite:////tmp/copy.db python tools/build_worker.py /tmp/cf_deploy.js
Renders /landing, /terms, /security, /specs with the Flask test client, rewrites links that the Worker does not
serve to https://novak-lms.onrender.com, embeds llms/robots/sitemap + the emblem, and writes a Cloudflare
`execute` script (assets upload session + multipart PUT). Refuses to build if forbidden claims appear.
"""
import base64
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
RENDER = 'https://novak-lms.onrender.com'
WORKER_PATHS = ('/terms', '/terms.html', '/legal/terms', '/dmca', '/security', '/security.html', '/compliance',
                '/specs', '/compare', '/llms.txt', '/llms-full.txt', '/robots.txt', '/sitemap.xml',
                '/navy-n.png', '/navy-n-512.webp', '/static/img/navy-n-512.webp', '/static/img/navy-n-256.png',
                '/static/img/navy-n.png', '/tqi.html')
REDIRECTS = ('/consult', '/schedule-consult', '/pricing', '/roi', '/pilot/start', '/demo', '/demo/tour', '/register',
             '/login', '/privacy', '/my-data', '/helix/try', '/contact', '/demo/enter/student', '/demo/enter/instructor',
             '/demo/enter/admin')
FORBIDDEN = ('ciwt', 'soc 2', 'soc2', 'hecvat', 'not built yet', 'not in this prototype', 'official comptia practice exam',
             'cmi5 compliant', 'cmi5 conformant', '(cmi5)', '9274', 'roadmap')


def rewrite(html):
    def fix(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if url.startswith('//') or not url.startswith('/'):
            return m.group(0)
        path = url.split('#', 1)[0].split('?', 1)[0]
        if path in WORKER_PATHS and path != '/':
            return m.group(0)
        return f'{attr}={q}{RENDER}{url}{q}'
    return re.sub(r'\b(href|src|action)=(["\'])(/[^"\']*)\2', fix, html)


def main(out_path):
    import app as lms
    lms.app.config.update(TESTING=True)
    c = lms.app.test_client()
    pages = {}
    for name, path in (('INDEX_HTML', '/landing'), ('TERMS_HTML', '/terms'), ('SECURITY_HTML', '/security'),
                       ('SPECS_HTML', '/specs')):
        r = c.get(path)
        assert r.status_code == 200, (path, r.status_code)
        pages[name] = rewrite(r.get_data(as_text=True))
    for name, fn in (('LLMS_TXT', 'llms.txt'), ('LLMS_FULL_TXT', 'llms-full.txt'), ('ROBOTS_TXT', 'robots.txt'),
                     ('SITEMAP_XML', 'sitemap.xml')):
        with open(os.path.join(ROOT, 'static', fn), encoding='utf-8') as fh:
            pages[name] = fh.read()
    for k, v in pages.items():
        low = v.lower()
        bad = [f for f in FORBIDDEN if f in low]
        assert not bad, (k, bad)
    with open(os.path.join(ROOT, 'static', 'img', 'navy-n-512.webp'), 'rb') as fh:
        logo = base64.b64encode(fh.read()).decode()
    consts = ''.join(f'const {k} = {json.dumps(v)};\n' for k, v in pages.items())
    consts += f'const LOGO_WEBP_B64 = {json.dumps(logo)};\n'
    worker_paths = [p for p in WORKER_PATHS]
    code = consts + r'''
function b64ToBytes(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}
const REDIRECTS = new Set(''' + json.dumps(list(REDIRECTS)) + r''');
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const p = url.pathname.replace(/\/+$/, "") || "/";
    const text = { "Content-Type": "text/plain; charset=utf-8", "Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=300" };
    const html = { "Content-Type": "text/html; charset=utf-8", "Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=300" };
    if (p === "/navy-n-512.webp" || p === "/static/img/navy-n-512.webp" || p === "/static/img/navy-n-256.png" || p === "/static/img/navy-n.png" || p === "/navy-n.png") {
      return new Response(b64ToBytes(LOGO_WEBP_B64), { status: 200, headers: { "Content-Type": "image/webp", "Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=86400, immutable" } });
    }
    if (p === "/" || p === "/index.html" || p === "/landing") return new Response(INDEX_HTML, { status: 200, headers: html });
    if (p === "/terms" || p === "/terms.html" || p === "/legal/terms" || p === "/dmca") return new Response(TERMS_HTML, { status: 200, headers: html });
    if (p === "/security" || p === "/security.html" || p === "/compliance") return new Response(SECURITY_HTML, { status: 200, headers: html });
    if (p === "/specs" || p === "/compare") return new Response(SPECS_HTML, { status: 200, headers: html });
    if (p === "/llms.txt") return new Response(LLMS_TXT, { status: 200, headers: text });
    if (p === "/llms-full.txt") return new Response(LLMS_FULL_TXT, { status: 200, headers: text });
    if (p === "/robots.txt") return new Response(ROBOTS_TXT, { status: 200, headers: text });
    if (p === "/sitemap.xml") return new Response(SITEMAP_XML, { status: 200, headers: { "Content-Type": "application/xml; charset=utf-8", "Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=300" } });
    if (REDIRECTS.has(p)) return Response.redirect("https://novak-lms.onrender.com" + p + url.search, 302);
    if (env.ASSETS) {
      const res = await env.ASSETS.fetch(req);
      const h = new Headers(res.headers);
      h.set("Access-Control-Allow-Origin", "*");
      return new Response(res.body, { status: res.status, headers: h });
    }
    return new Response("Not found", { status: 404 });
  }
};
'''
    deploy = r'''async () => {
  const manifest = {
    "/index.html": { hash: "5c3721e566e02abd244e8e2af038bd03", size: 293633 },
    "/navy-n.png": { hash: "7a7fa22e6afd7d3959ab78ef57db0fdc", size: 2182160 },
    "/tqi.html": { hash: "65116edaa42641db498149f7d92d00ff", size: 12486 }
  };
  const session = await cloudflare.request({ method: "POST", path: `/accounts/${accountId}/workers/scripts/red-heart-caee/assets-upload-session`, body: { manifest } });
  const completionJwt = session.result.jwt;
  const workerCode = ''' + json.dumps(code) + r''';
  const b2 = `----CFWorker${Date.now()}`;
  const meta = { main_module: "index.js", compatibility_date: "2026-09-06",
    assets: { jwt: completionJwt, config: { html_handling: "auto-trailing-slash", not_found_handling: "none", run_worker_first: true } },
    bindings: [{ type: "assets", name: "ASSETS" }] };
  const putBody = [
    `--${b2}`, 'Content-Disposition: form-data; name="metadata"', 'Content-Type: application/json', '', JSON.stringify(meta),
    `--${b2}`, 'Content-Disposition: form-data; name="index.js"; filename="index.js"', 'Content-Type: application/javascript+module', '', workerCode,
    `--${b2}--`, ''
  ].join("\r\n");
  return await cloudflare.request({ method: "PUT", path: `/accounts/${accountId}/workers/scripts/red-heart-caee`, body: putBody, contentType: `multipart/form-data; boundary=${b2}`, rawBody: true });
}
'''
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(deploy)
    with open(out_path + '.worker.js', 'w', encoding='utf-8') as fh:
        fh.write(code)
    print('wrote', out_path, len(deploy), 'bytes; index', len(pages['INDEX_HTML']))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/tmp/cf_deploy_phase1.js')
