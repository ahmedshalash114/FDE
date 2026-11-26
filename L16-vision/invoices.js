// L16 · Vision + PDFs — 10 supplier invoices, drawn on a canvas, read 3 ways by the same model:
//   text  : the text layer you get from a digital PDF (no image at all)
//   clean : a clean scan (PNG, 800 px)
//   photo : a phone photo (rotated, shadow, blur, small, JPEG)
// Runs in any page on http://localhost:11434 (Ollama) — paste it in the browser console, or let vision.py drive it with Playwright.
const VENDORS = ['شركة النيل للإلكترونيات', 'المصرية للتوريدات', 'دلتا تك', 'الأهرام للأجهزة', 'سمارت هوم مصر', 'القاهرة للكابلات', 'نور للتجارة', 'الإسكندرية للإكسسوارات', 'ميدل إيست سبلاي', 'جيزة جروب'];
const ITEMS = [['شاحن 65 وات', 520], ['سماعة بلوتوث', 890], ['كابل تايب سي', 75], ['باور بانك 20 ألف', 690], ['ماوس لاسلكي', 230], ['جراب موبايل', 55], ['ساعة ذكية', 1850], ['فلاشة 64 جيجا', 160], ['راوتر', 1450], ['ميكروفون', 640]];
let seed = 16; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const AR = s => String(s).replace(/[0-9]/g, d => '٠١٢٣٤٥٦٧٨٩'[d]);
const INV = VENDORS.map((v, i) => {
  const n = 2 + Math.floor(rnd() * 4), lines = [];
  for (let k = 0; k < n; k++) { const [name, p] = ITEMS[Math.floor(rnd() * ITEMS.length)]; lines.push([name, 1 + Math.floor(rnd() * 12), p]); }
  const sub = lines.reduce((a, [, q, p]) => a + q * p, 0), vat = Math.round(sub * 14) / 100, total = Math.round((sub + vat) * 100) / 100;
  const no = `INV-${2026}-${String(300 + Math.floor(rnd() * 600)).padStart(4, '0')}`, date = `2026-${String(9 + (i % 3)).padStart(2, '0')}-${String(1 + Math.floor(rnd() * 27)).padStart(2, '0')}`;
  return { vendor: v, no, date, lines, sub, vat, total, arabicDigits: i % 3 === 2 };
});
const money = (x, ar) => { const s = x.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); return ar ? AR(s) : s; };
function draw(inv, mode) {
  const W = 800, H = 1000, c = document.createElement('canvas'); c.width = W; c.height = H; const x = c.getContext('2d');
  x.fillStyle = '#fff'; x.fillRect(0, 0, W, H); x.fillStyle = '#111'; x.direction = 'rtl'; x.textAlign = 'right';
  const D = s => inv.arabicDigits ? AR(s) : String(s);
  x.font = 'bold 34px sans-serif'; x.fillText(inv.vendor, W - 40, 70);
  x.font = '22px sans-serif'; x.fillText('فاتورة ضريبية', W - 40, 110);
  x.direction = 'ltr'; x.textAlign = 'left'; x.font = '20px monospace';
  x.fillText('Invoice No: ' + inv.no, 40, 160); x.fillText('Date: ' + D(inv.date), 40, 190);
  x.strokeStyle = '#333'; x.lineWidth = 2; x.strokeRect(40, 230, W - 80, 60 + inv.lines.length * 44);
  x.direction = 'rtl'; x.textAlign = 'right'; x.font = 'bold 20px sans-serif';
  x.fillText('الصنف', W - 60, 268); x.fillText('الكمية', 420, 268); x.fillText('السعر', 290, 268); x.fillText('الإجمالي', 150, 268);
  x.font = '20px sans-serif';
  inv.lines.forEach(([n, q, p], k) => { const y = 312 + k * 44; x.fillText(n, W - 60, y); x.fillText(D(q), 420, y); x.fillText(money(p, inv.arabicDigits), 290, y); x.fillText(money(q * p, inv.arabicDigits), 150, y); });
  const y0 = 330 + inv.lines.length * 44 + 30;
  [['الإجمالي قبل الضريبة', inv.sub], ['ضريبة القيمة المضافة 14%', inv.vat], ['الإجمالي المستحق', inv.total]].forEach(([l, v], k) => {
    x.font = (k === 2 ? 'bold 26px' : '22px') + ' sans-serif'; x.fillText(l, W - 60, y0 + k * 44); x.fillText(money(v, inv.arabicDigits) + ' ج.م', 260, y0 + k * 44); });
  x.font = '16px sans-serif'; x.fillStyle = '#666'; x.fillText('شكراً لتعاملكم معنا', W - 40, H - 40);
  if (mode === 'clean') return c.toDataURL('image/png').split(',')[1];
  // phone photo: small, rotated, shadow, blur, jpeg
  const P = document.createElement('canvas'); P.width = 480; P.height = 640; const y = P.getContext('2d');
  y.fillStyle = '#6b6358'; y.fillRect(0, 0, 480, 640); y.save(); y.translate(240, 320); y.rotate(0.07); y.filter = 'blur(0.8px)';
  y.drawImage(c, -210, -265, 420, 525); y.restore(); y.filter = 'none';
  const g = y.createLinearGradient(0, 0, 480, 640); g.addColorStop(0, 'rgba(0,0,0,0.35)'); g.addColorStop(0.6, 'rgba(0,0,0,0)'); y.fillStyle = g; y.fillRect(0, 0, 480, 640);
  return P.toDataURL('image/jpeg', 0.55).split(',')[1];
}
function asText(inv) {   // what a digital PDF's text layer gives you
  return [inv.vendor, 'فاتورة ضريبية', 'Invoice No: ' + inv.no, 'Date: ' + inv.date, 'الصنف | الكمية | السعر | الإجمالي',
    ...inv.lines.map(([n, q, p]) => `${n} | ${q} | ${money(p)} | ${money(q * p)}`),
    'الإجمالي قبل الضريبة ' + money(inv.sub), 'ضريبة القيمة المضافة 14% ' + money(inv.vat), 'الإجمالي المستحق ' + money(inv.total) + ' ج.م'].join('\n');
}
const SCHEMA = { type: 'object', properties: { invoice_no: { type: 'string' }, date: { type: 'string' }, total: { type: 'number' }, items: { type: 'integer' } }, required: ['invoice_no', 'date', 'total', 'items'] };
const ASK = 'Extract from this supplier invoice: invoice_no, date (YYYY-MM-DD, western digits), total (the final amount due incl. VAT, a number) and items (how many product lines). Return JSON.';
async function read(inv, mode) {
  const msg = mode === 'text' ? { role: 'user', content: ASK + '\n\n' + asText(inv) } : { role: 'user', content: ASK, images: [draw(inv, mode)] };
  const t0 = performance.now();
  const r = await fetch('/api/chat', { method: 'POST', body: JSON.stringify({ model: 'qwen3.5:4b', stream: false, think: false, format: SCHEMA, messages: [msg], options: { num_predict: 200 } }) }).then(r => r.json());
  let out = {}; try { out = JSON.parse(r.message.content); } catch (e) { }
  const norm = s => String(s || '').replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/\s/g, '').toUpperCase();
  const ok = { invoice_no: norm(out.invoice_no) === inv.no, date: norm(out.date) === inv.date, total: Math.abs(Number(out.total) - inv.total) < 0.01, items: Number(out.items) === inv.lines.length };
  return { no: inv.no, mode, out, ok, ms: Math.round(performance.now() - t0), prompt_tokens: r.prompt_eval_count, gold: { invoice_no: inv.no, date: inv.date, total: inv.total, items: inv.lines.length } };
}
async function runAll() { const res = []; for (const inv of INV) for (const m of ['text', 'clean', 'photo']) res.push(await read(inv, m)); return res; }
