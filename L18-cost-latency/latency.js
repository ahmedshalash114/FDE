// L18 · Cost & latency — the same 20 customer messages (L12, with gold intents), the same model (qwen3.5:4b on Ollama),
// three ways to ask "what does the customer want?":
//   think   : thinking ON, free answer
//   plain   : thinking OFF, free answer ("reply with one word")
//   schema  : thinking OFF + JSON schema with an enum + a tiny token budget
// + streaming: for 5 full replies, time to the first token vs time to the whole reply.
// Paste in a browser tab on http://localhost:11434 (or run latency.py).
const MSGS = [["الأوردر 1042 لسه موصلش، هو فين؟","status"],["عايز أرجّع الجزمة اللي في أوردر 1051، المقاس طلع صغير","refund"],["الغوا الأوردر 1060 بسرعة لو سمحتم قبل ما يتشحن!!","cancel"],["المندوب كان قليل الذوق جدا ورمى الكرتونة على الأرض","complaint"],["انا مسافر بكرة الصبح والأوردر 1043 لازم يوصل النهارده ضروري","status"],["فلوس المرتجع بتاع 1045 لسه مرجعتش ليه؟ بقالها أسبوعين","refund"],["عندكم شاحن 65 وات؟","other"],["الشاشة اللي جت في 1072 مكسورة، عايز فلوسي","refund"],["ممكن أغيّر العنوان بتاع أوردر 1080؟","other"],["انا طلبت بالغلط، كنسل الطلب رقم ١٠٨٥","cancel"],["بقالي ساعة على خدمة العملاء محدش بيرد، ده مش احترام","complaint"],["أوردر 1090 اتشحن ولا لسه؟","status"],["الفاتورة بتاعة 1094 فيها ضريبة غلط","complaint"],["عايز استرجع فلوس السماعة، رقم الطلب 1101","refund"],["حد يرد عليا الأوردر 1103 اتأخر ٣ أيام وانا محتاجه للشغل حالاً","status"],["بتوصلوا أسوان؟","other"],["الغي طلبي 1110 لاقيته أرخص في حتة تانية","cancel"],["جالي لون غلط في أوردر 1115، عايز أبدّله","refund"],["ده تالت مرة الطلب يتأجل!!! أوردر 1120، هعمل شكوى في جهاز حماية المستهلك","complaint"],["شكرا الطلب وصل بسرعة 👌","other"]];
const INTENTS = ['status', 'refund', 'cancel', 'complaint', 'other'];
const SYS = 'Classify the customer message into one intent: status (where is my order), refund (money back, return or exchange an item), cancel, complaint, other.';
const MODES = {
  think:  { think: true,  system: SYS + ' Reply with the intent word only.', opts: {} },
  plain:  { think: false, system: SYS + ' Reply with the intent word only.', opts: { num_predict: 200 } },
  schema: { think: false, system: SYS, opts: { num_predict: 20 }, format: { type: 'object', properties: { intent: { type: 'string', enum: INTENTS } }, required: ['intent'] } },
};
async function classify(msg, gold, mode) {
  const m = MODES[mode], t0 = performance.now();
  const body = { model: 'qwen3.5:4b', stream: false, think: m.think, options: m.opts, messages: [{ role: 'system', content: m.system }, { role: 'user', content: msg }] };
  if (m.format) body.format = m.format;
  const r = await fetch('/api/chat', { method: 'POST', body: JSON.stringify(body) }).then(r => r.json());
  const text = (r.message.content || '').toLowerCase();
  let got = null; try { got = JSON.parse(text).intent; } catch (e) { got = INTENTS.find(i => text.includes(i)) || text.trim().slice(0, 20); }
  return { mode, msg, gold, got, ok: got === gold, out_tokens: r.eval_count, thinking_chars: (r.message.thinking || '').length,
           ms: Math.round(performance.now() - t0), load_ms: Math.round((r.load_duration || 0) / 1e6) };
}
const REPLY_SYS = 'You are Mona, the support agent of Mona Store (Egypt). Answer in Egyptian Arabic, at most two short sentences. Never promise a time or an amount.';
async function streamed(msg) {   // time to first token vs total
  const t0 = performance.now(); let first = null, text = '';
  const r = await fetch('/api/chat', { method: 'POST', body: JSON.stringify({ model: 'qwen3.5:4b', stream: true, think: false, options: { num_predict: 200 },
    messages: [{ role: 'system', content: REPLY_SYS }, { role: 'user', content: msg }] }) });
  const rd = r.body.getReader(), dec = new TextDecoder(); let buf = '';
  for (;;) { const { done, value } = await rd.read(); if (done) break; buf += dec.decode(value, { stream: true });
    let i; while ((i = buf.indexOf('\n')) >= 0) { const line = buf.slice(0, i); buf = buf.slice(i + 1); if (!line.trim()) continue;
      const j = JSON.parse(line); if (j.message && j.message.content) { if (first === null) first = performance.now() - t0; text += j.message.content; } } }
  return { msg, ttft_ms: Math.round(first), total_ms: Math.round(performance.now() - t0), reply: text };
}
async function runAll() {
  await classify(MSGS[0][0], MSGS[0][1], 'plain');   // warm-up: load the model once (cold start is L17's story)
  const res = { classify: [], stream: [] };
  for (const mode of Object.keys(MODES)) for (const [msg, gold] of MSGS) res.classify.push(await classify(msg, gold, mode));
  for (const [msg] of MSGS.slice(0, 5)) res.stream.push(await streamed(msg));
  return res;
}
