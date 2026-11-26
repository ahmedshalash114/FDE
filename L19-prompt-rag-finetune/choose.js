// L19 · Prompt vs RAG vs fine-tuning — which tool for which problem? (qwen3.5:4b on Ollama, think off)
// Part 1 · KNOWLEDGE: 12 questions about Mona Store's own policies (facts the model can't know).
//   prompt : just the persona, no facts            stuff : the whole policy in the system prompt
//   rag    : only the 3 chunks most similar to the question (character 3-gram TF-IDF, no extra model)
// Part 2 · A FACT CHANGES: Cairo shipping goes from 45 to 60 EGP -> edit one chunk, ask again (no retraining).
// Part 3 · BEHAVIOUR: L18's 20 intent messages, instructions only vs + 6 worked examples (few-shot).
// Paste in a browser tab on http://localhost:11434 (or run choose.py).
const POLICY = [
  'الاسترجاع: تقدر ترجّع أي منتج خلال 14 يوم من الاستلام، بشرط يكون في علبته الأصلية.',
  'فلوس المرتجع: بترجع على نفس وسيلة الدفع خلال 7 أيام عمل بعد ما المنتج يوصل المخزن.',
  'الشحن داخل القاهرة والجيزة: يوصل في يوم أو يومين، ومصاريفه 45 جنيه، ومجاني للأوردر فوق 1500 جنيه.',
  'الشحن للمحافظات: من 3 لـ 5 أيام ومصاريفه 75 جنيه. أسوان والأقصر والبحر الأحمر: من 5 لـ 7 أيام.',
  'الإلغاء: تقدر تلغي الأوردر مجانًا قبل ما يتشحن. بعد الشحن بيبقى استرجاع عادي.',
  'الدفع عند الاستلام: متاح للأوردرات لحد 5000 جنيه.',
  'التقسيط: على 6 شهور من غير فوايد لأي أوردر فوق 3000 جنيه بكروت البنوك المشاركة.',
  'الضمان: الأجهزة الإلكترونية عليها ضمان سنة من الوكيل، والسماعات ضمانها 6 شهور.',
  'تغيير المقاس: مجاني مرة واحدة خلال 14 يوم من الاستلام.',
  'مواعيد خدمة العملاء: من 9 الصبح لحد 11 بالليل كل يوم، ما عدا الجمعة من 2 الضهر.',
  'المنتج المكسور أو التالف: صوّره وابعت الصورة في الشات خلال 48 ساعة من الاستلام.',
  'الفاتورة الضريبية: بتوصل على الإيميل خلال 24 ساعة من التسليم.',
];
const QS = [
  ['لو الجزمة طلعت صغيرة، أقدر أرجّعها لحد إمتى؟', '(14|١٤|اربعتاشر|أربعتاشر|أربعة عشر|اربعة عشر)'],
  ['فلوس المرتجع بتاخد قد إيه عشان ترجع؟', '(7|٧|سبع)'],
  ['الشحن جوه القاهرة بكام؟', '(45|٤٥)'],
  ['بتوصلوا أسوان في قد إيه؟', '(5|٥|خمس).{0,15}(7|٧|سبع)'],
  ['الدفع عند الاستلام متاح لحد كام؟', '(5000|5,000|٥٠٠٠|خمس.{0,3}(آلاف|تلاف|الاف))'],
  ['التقسيط بيبدأ من أوردر بكام؟', '(3000|3,000|٣٠٠٠|تلات.{0,3}(آلاف|تلاف|الاف))'],
  ['التقسيط على كام شهر؟', '(6|٦|ست)'],
  ['السماعة ضمانها قد إيه؟', '(6|٦|ست).{0,6}(شهور|أشهر|اشهر)'],
  ['الشحن بيبقى ببلاش من أول كام؟', '(1500|1,500|١٥٠٠)'],
  ['خدمة العملاء بتقفل الساعة كام؟', '(11|١١|حداشر|احداشر|إحدى عشر)'],
  ['المنتج جالي مكسور، لازم أبلغ في خلال قد إيه؟', '(48|٤٨)'],
  ['الفاتورة الضريبية بتوصل إمتى؟', '(24|٢٤)'],
];
const DONT = /(مش عارف|معرفش|لا أعرف|لا اعرف|مش متأكد|غير متأكد|مفيش عندي معلومة|ليس لدي|تواصل مع|راجع الموقع|اتصل ب)/;
const PERSONA = 'You are Mona, the support agent of Mona Store (Egypt). Answer in Egyptian Arabic in one or two short sentences.';
const norm = s => s.replace(/[ً-ْ]/g, '').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي');
const grams = s => { const g = {}; for (const w of norm(s).split(/[^؀-ۿ0-9]+/).filter(Boolean)) { const p = ' ' + w + ' '; for (let i = 0; i < p.length - 2; i++) g[p.slice(i, i + 3)] = (g[p.slice(i, i + 3)] || 0) + 1; } return g; };
function retrieve(q, docs, k = 3) {   // TF-IDF over character 3-grams: survives ال / و prefixes and Egyptian spelling
  const G = docs.map(grams), df = {}; G.forEach(g => Object.keys(g).forEach(t => df[t] = (df[t] || 0) + 1));
  const vec = g => { const v = {}; let n = 0; for (const t in g) { v[t] = g[t] * Math.log(1 + docs.length / (df[t] || 1)); n += v[t] ** 2; } n = Math.sqrt(n) || 1; for (const t in v) v[t] /= n; return v; };
  const qv = vec(grams(q)); return G.map((g, i) => { const dv = vec(g); let s = 0; for (const t in qv) if (dv[t]) s += qv[t] * dv[t]; return [i, s]; }).sort((a, b) => b[1] - a[1]).slice(0, k).map(x => x[0]);
}
async function chat(system, user, opts = { num_predict: 150 }) {
  const t0 = performance.now();
  const r = await fetch('/api/chat', { method: 'POST', body: JSON.stringify({ model: 'qwen3.5:4b', stream: false, think: false, options: opts,
    messages: [{ role: 'system', content: system }, { role: 'user', content: user }] }) }).then(r => r.json());
  return { text: r.message.content || '', prompt_tokens: r.prompt_eval_count, out_tokens: r.eval_count, ms: Math.round(performance.now() - t0) };
}
function grade(text, gold) { return new RegExp(gold).test(text) ? 'correct' : DONT.test(text) ? 'dont_know' : 'wrong'; }
async function ask(mode, q, gold, policy = POLICY) {
  let system = PERSONA, ctx = null;
  if (mode === 'stuff') system += '\nAnswer ONLY from the store policy below. If it is not there, say you are not sure.\n\nSTORE POLICY:\n' + policy.join('\n');
  if (mode === 'rag') { ctx = retrieve(q, policy); system += '\nAnswer ONLY from the policy excerpts below. If it is not there, say you are not sure.\n\nPOLICY EXCERPTS:\n' + ctx.map(i => policy[i]).join('\n'); }
  const r = await chat(system, q); return Object.assign({ mode, q, result: grade(r.text, gold), chunks: ctx }, r);
}
const SYS = 'Classify the customer message into one intent: status (where is my order), refund (money back, return or exchange an item), cancel, complaint, other. Reply with the intent word only.';
const SHOTS = [['فين الطلب بتاعي؟ بقاله أسبوع', 'status'], ['عايز أبدّل التيشيرت بمقاس أكبر', 'refund'], ['كنسلوا الطلب، غيّرت رأيي', 'cancel'],
  ['التغليف كان بايظ والمندوب اتأخر ساعتين', 'complaint'], ['شكرا جدا على الخدمة', 'other'], ['عندكم فرع في المنصورة؟', 'other']];
async function intent(msg, few) {
  const ex = few ? '\n\nExamples:\n' + SHOTS.map(([m, i]) => m + ' -> ' + i).join('\n') : '';
  const r = await chat(SYS + ex, msg, { num_predict: 20 }); const t = r.text.toLowerCase();
  return Object.assign({ got: ['status', 'refund', 'cancel', 'complaint', 'other'].find(i => t.includes(i)) || t.trim() }, r);
}
async function runAll(MSGS) {   // MSGS = L18's 20 [message, gold intent] pairs
  await chat(PERSONA, 'أهلا');   // warm-up
  const res = { knowledge: [], update: [], behaviour: [] };
  for (const mode of ['prompt', 'stuff', 'rag']) for (const [q, g] of QS) res.knowledge.push(await ask(mode, q, g));
  const NEW = POLICY.slice(); NEW[2] = NEW[2].replace('45', '60');
  for (const mode of ['prompt', 'stuff', 'rag']) res.update.push(await ask(mode, QS[2][0], '(60|٦٠|ستين)', NEW));
  for (const few of [false, true]) for (const [m, g] of MSGS) { const r = await intent(m, few); res.behaviour.push(Object.assign({ few, msg: m, gold: g, ok: r.got === g }, r)); }
  return res;
}
