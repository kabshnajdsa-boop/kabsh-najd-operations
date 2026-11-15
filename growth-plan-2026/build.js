const pptxgen = require("pptxgenjs");
const path = require("path");
const { applyTheme } = require(process.env.APPLY_THEME || "./apply_theme.js");

const OUT = process.argv[2] || "Kabsh_Najd_Growth_Plan.pptx";
const D = path.join(__dirname, "assets");

// ---------- Brand ----------
const RED = "9A2021", CREAM = "FFF7E8", WHITE = "FFFFFF", INK = "2B1A12", MUTED = "6B5A50",
  GOLD = "B8962E", SAND = "F3E6CC", ROSE = "E9C9C3", GREEN = "2E6B4F", LINE = "E6D6BC";
const F = "Estedad";

const THEME = {
  name: "Kabsh Najd 2026",
  headFontFace: F, bodyFontFace: F,
  colors: { dk1: INK, lt1: WHITE, dk2: RED, lt2: CREAM, accent1: RED, accent2: GOLD, accent3: "5B3A29",
    accent4: "C97A6E", accent5: "8C8C8C", accent6: GREEN, hlink: RED, folHlink: "5B3A29" },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.rtlMode = true;
pres.title = "كبش نجد — خطة النمو التسويقي";
pres.author = "Claude Code";
pres.company = "Kabsh Najd";
pres.theme = { headFontFace: F, bodyFontFace: F };

const W = 13.333, H = 7.5, M = 0.6;

// ---------- Layouts ----------
pres.defineSlideMaster({
  title: "COVER", background: { color: RED },
  objects: [],
});
pres.defineSlideMaster({
  title: "SECTION", background: { color: RED },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.9, w: W - 2 * M, h: 1.2, fontFace: F, fontSize: 44, bold: true, color: WHITE, align: "right", valign: "middle", rtlMode: true }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 4.1, w: W - 2 * M, h: 0.8, fontFace: F, fontSize: 18, color: SAND, align: "right", valign: "top", rtlMode: true }, text: "" } },
  ],
  slideNumber: { x: 0.5, y: 6.95, w: 0.6, h: 0.3, fontFace: F, fontSize: 10, color: SAND },
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: CREAM },
  objects: [
    { image: { path: path.join(D, "logo_h.png"), x: 0.55, y: 6.92, w: 1.0, h: 0.373 } },
    { text: { text: "كبش نجد  |  خطة النمو التسويقي  |  سري — للإدارة والمساهمين", options: { x: 4.5, y: 6.95, w: 8.25, h: 0.3, fontFace: F, fontSize: 9, color: MUTED, align: "right", rtlMode: true } } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.75, fontFace: F, fontSize: 30, bold: true, color: RED, align: "right", valign: "middle", rtlMode: true }, text: "" } },
  ],
  slideNumber: { x: 1.65, y: 6.95, w: 0.5, h: 0.3, fontFace: F, fontSize: 9, color: MUTED },
});

// ---------- Helpers ----------
function T(s, text, x, y, w, h, o = {}) {
  s.addText(text, Object.assign({ x, y, w, h, fontFace: F, fontSize: 14, color: INK, align: "right", valign: "top", rtlMode: true, isTextBox: true, margin: 0.05 }, o));
}
function card(s, x, y, w, h, fill = WHITE, o = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({ x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: LINE, width: 0.75 },
    shadow: { type: "outer", color: "8A6A4A", opacity: 0.12, blur: 6, offset: 2, angle: 90 } }, o));
}
function stat(s, x, y, w, h, big, label, sub, fill = WHITE, bigColor = RED) {
  card(s, x, y, w, h, fill);
  T(s, big, x + 0.15, y + 0.15, w - 0.3, h * 0.45, { fontSize: 30, bold: true, color: bigColor, valign: "middle" });
  T(s, label, x + 0.15, y + h * 0.5, w - 0.3, 0.35, { fontSize: 13, bold: true });
  if (sub) T(s, sub, x + 0.15, y + h * 0.5 + 0.35, w - 0.3, h * 0.5 - 0.45, { fontSize: 11, color: MUTED });
}
function bullets(s, items, x, y, w, h, o = {}) {
  const arr = items.map((t, i) => {
    const runOpts = { bullet: { indent: 14 }, breakLine: i < items.length - 1, paraSpaceAfter: 6 };
    if (Array.isArray(t)) return t.map((r, j) => ({ text: r.text, options: Object.assign({}, j === 0 ? { bullet: { indent: 14 }, paraSpaceAfter: 6 } : {}, r.options || {}, { breakLine: j === t.length - 1 && i < items.length - 1 }) }));
    return [{ text: t, options: runOpts }];
  }).flat();
  T(s, arr, x, y, w, h, Object.assign({ fontSize: 14 }, o));
}
function pill(s, text, x, y, w, fill = RED, color = WHITE) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.36, rectRadius: 0.18, fill: { color: fill }, line: { color: fill } });
  T(s, text, x, y, w, 0.36, { fontSize: 11, bold: true, color, align: "center", valign: "middle", margin: 0 });
}
function circleNum(s, n, x, y, d = 0.5, fill = RED) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  T(s, String(n), x, y, d, d, { fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
}
function source(s, text) {
  T(s, text, M, 6.55, W - 2 * M, 0.3, { fontSize: 9, color: MUTED });
}
const chartBase = () => ({
  catAxisLabelColor: MUTED, valAxisLabelColor: MUTED, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  catAxisLabelFontSize: 10, valAxisLabelFontSize: 9, dataLabelFontFace: "+mn-lt", dataLabelFontSize: 10, dataLabelColor: INK,
  valGridLine: { color: "E8DCC8", size: 0.5 }, catGridLine: { style: "none" }, titleFontFace: "+mn-lt",
  legendFontFace: "+mn-lt", legendFontSize: 10, legendColor: INK,
});
function content(title, section) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  return s;
}
function sectionSlide(title, sub, section) {
  const s = pres.addSlide({ masterName: "SECTION", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addText(sub, { placeholder: "body" });
  return s;
}

// =====================================================================
// 1. COVER
pres.addSection({ title: "الافتتاح" });
{
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: "الافتتاح" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 0.7, w: 3.2, h: 1.35, rectRadius: 0.15, fill: { color: CREAM }, line: { color: CREAM } });
  s.addImage({ path: path.join(D, "logo_h.png"), x: 0.95, y: 0.88, w: 2.7, h: 1.008, altText: "شعار كبش نجد" });
  s.addImage({ path: path.join(D, "c7.png"), x: 0.9, y: 2.85, w: 3.4, h: 3.4, altText: "صندوق كبش نجد" });
  T(s, "خطة النمو التسويقي", 4.6, 1.6, 8.1, 1.0, { fontSize: 46, bold: true, color: WHITE });
  T(s, "خطة 90 يومًا: ديسمبر 2026 – فبراير 2027", 4.6, 2.6, 8.1, 0.5, { fontSize: 18, color: SAND });
  T(s, "تحليل بيانات آخر 3 أشهر (16 أغسطس – 14 نوفمبر 2026)، تحليل السوق والمنافسين وSWOT، وخطة تنفيذية قابلة للقياس", 4.6, 3.35, 8.1, 1.0, { fontSize: 16, color: WHITE });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 4.6 + 8.1 - 4.2, y: 4.75, w: 4.2, h: 1.1, rectRadius: 0.12, fill: { color: "7E1A1B" }, line: { color: "B84A4B", width: 0.75 } });
  T(s, [{ text: "مقدمة إلى: إدارة شركة كبش نجد والمساهمين", options: { breakLine: true, bold: true } }, { text: "تاريخ الإعداد: 15 نوفمبر 2026" }], 4.6 + 8.1 - 4.1, 4.85, 4.0, 0.9, { fontSize: 13, color: WHITE, valign: "middle" });
  s.addNotes("افتتاح: الهدف من الاجتماع اعتماد خطة نمو 90 يومًا مبنية على بيانات المتجر الفعلية، مع إصلاحات قياس عاجلة قبل زيادة أي ميزانية.");
}

// 2. EXEC SUMMARY
{
  const s = content("الخلاصة التنفيذية: الطلب موجود والتسريب داخلي", "الافتتاح");
  const cols = [
    { n: 1, h: "ما وجدناه", c: RED, items: [
      "إيراد مسجل 7.92 مليون ريال و10,278 طلبًا خلال 90 يومًا (GA4 الموقع)",
      "انخفاض الإيراد 18% عن الفترة السابقة، بسبب انخفاض متوسط السلة 16% بعد موسم الأضحى",
      "منذ 3 نوفمبر هبطت الطلبات المسجلة من نحو 150 إلى نحو 40 يوميًا رغم ثبات الزيارات والسلات",
    ] },
    { n: 2, h: "لماذا يهم", c: GOLD, items: [
      "نحو 84% ممن يبدؤون الدفع لا يكملون الشراء",
      "نحو 72% من الإيراد بلا مصدر واضح، فميزانية الإعلانات تُدار دون رؤية كافية",
      "العملاء العائدون 14% من المستخدمين و28% من الطلبات، والاحتفاظ غير مستغَل",
    ] },
    { n: 3, h: "ما نقترحه", c: GREEN, items: [
      "أسبوعان لإصلاح القياس والربط ومطابقة GA4 مع طلبات سلة",
      "رفع التحويل والسلة، ثم برنامج احتفاظ عبر واتساب والبريد",
      "حملة رمضان 1448 (يبدأ نحو 8 فبراير 2027) مع مسار للشركات والمناسبات",
    ] },
  ];
  const cw = 3.85, gap = 0.3, y = 1.35;
  cols.forEach((c, i) => {
    const x = W - M - cw - i * (cw + gap);
    card(s, x, y, cw, 4.25);
    circleNum(s, c.n, x + cw - 0.7, y + 0.25, 0.48, c.c);
    T(s, c.h, x + 0.2, y + 0.25, cw - 1.0, 0.48, { fontSize: 18, bold: true, color: c.c, valign: "middle" });
    bullets(s, c.items, x + 0.2, y + 0.95, cw - 0.4, 3.2, { fontSize: 13 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.8, w: W - 2 * M, h: 0.7, rectRadius: 0.1, fill: { color: RED }, line: { color: RED } });
  T(s, "هدف الخطة: الوصول إلى 150 طلبًا يوميًا وسلة 850 ريالًا بنهاية فبراير، أي نحو 10 ملايين ريال إيراد خلال 90 يومًا (+20% عن المسار الحالي)", M + 0.2, 5.8, W - 2 * M - 0.4, 0.7, { fontSize: 15, bold: true, color: WHITE, valign: "middle" });
  s.addNotes("الرسالة الأساسية: لا نحتاج إلى مضاعفة الإنفاق قبل إصلاح القياس والتحويل. الأرقام من GA4 لموقع kabshnajd.com وتحتاج مطابقة مع تقارير سلة الفعلية.");
}

// 3. DATA SOURCES
{
  const s = content("نطاق التحليل ومصادر البيانات: ما تحققنا منه وما ينقصنا", "الافتتاح");
  const rows = [
    ["المصدر", "الحالة", "ما استخدمناه"],
    ["Google Analytics 4 — الموقع (333082030)", "متصل ✔", "الزيارات، الطلبات، الإيراد، القنوات، المدن، المنتجات، القمع"],
    ["GA4 — التطبيق (460813092)", "متصل ✔", "طلبات iOS وAndroid؛ حدث begin_checkout غير مُرسل"],
    ["Google Keyword Planner / أبحاث البحث", "متصل ✔", "حجم البحث الشهري في السعودية والتكلفة التقديرية"],
    ["مكتبة إعلانات Meta (عامة)", "متصل ✔", "إعلانات المنافسين النشطة في السعودية"],
    ["Meta Ads (5 حسابات)", "انتهى الربط ✖", "انتهت الجلسة في 4 نوفمبر؛ الإنفاق وROAS غير متاحين"],
    ["Google Ads وMerchant Center", "انتهى الربط ✖", "يلزم إعادة تفويض Google"],
    ["جود — الربط الشامل (سلة، أودو، كرزون)", "يحتاج إعادة اتصال ✖", "الطلبات الفعلية والتكاليف والشكاوى غير متاحة لهذا العرض"],
  ];
  const tbl = rows.map((r, i) => r.map((c, j) => ({ text: c, options: {
    bold: i === 0 || j === 0, color: i === 0 ? WHITE : (j === 1 ? (c.includes("✔") ? GREEN : RED) : INK),
    fill: { color: i === 0 ? RED : (i % 2 ? WHITE : "FBF2E2") }, fontFace: F, fontSize: 12, align: "right", rtlMode: true, valign: "middle" } })));
  s.addTable(tbl, { x: M, y: 1.3, w: W - 2 * M, colW: [3.9, 2.0, 6.233], rowH: 0.52, border: { type: "solid", pt: 0.5, color: LINE } });
  T(s, "تنبيه منهجي: أرقام هذا العرض من GA4 (إسناد آخر نقرة) ولا تساوي بالضرورة دفاتر سلة وأودو. لا نجمع طلبات الموقع والتطبيق لاحتمال التداخل. نعرض المفقود كمفقود، لا كصفر.", M, 5.65, W - 2 * M, 0.8, { fontSize: 13, color: RED, bold: true });
  s.addNotes("الشفافية حول المصادر شرط لاعتماد الأرقام. أول توصية في الخطة: إعادة ربط Meta وGoogle وجود، ثم مطابقة الأرقام مع سلة.");
}

// =====================================================================
pres.addSection({ title: "تحليل الأداء" });
sectionSlide("أولًا: تحليل أداء آخر 90 يومًا", "16 أغسطس – 14 نوفمبر 2026 مقارنة بالـ90 يومًا السابقة (17 مايو – 15 أغسطس)", "تحليل الأداء");

// 5. KPI scoreboard
{
  const s = content("لوحة المؤشرات: طلبات شبه ثابتة، وإيراد أقل بسبب السلة", "تحليل الأداء");
  const k = [
    ["7.92M", "الإيراد (ريال)", "−18.1% عن 9.67 مليون"],
    ["10,278", "عدد الطلبات", "−2.3% عن 10,519"],
    ["771", "متوسط السلة (ريال)", "−16.2% عن 920 (موسم الأضحى)"],
    ["1.93%", "معدل التحويل", "+0.81 نقطة عن 1.12%"],
    ["531,698", "الجلسات", "−43.4% عن 940,143"],
    ["400,758", "المستخدمون", "94% منهم جدد"],
  ];
  const cw = 3.85, ch = 2.15, gx = 0.3, gy = 0.3;
  k.forEach((v, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = W - M - cw - col * (cw + gx), y = 1.35 + row * (ch + gy);
    const neg = v[2].startsWith("−");
    stat(s, x, y, cw, ch, v[0], v[1], v[2], WHITE, RED);
    pill(s, neg ? "▼" : "▲", x + 0.2, y + 0.25, 0.5, neg ? RED : GREEN);
  });
  T(s, "القراءة: انخفاض الجلسات 43% مع ثبات الطلبات يعني أن الزيارات المفقودة كانت ضعيفة الجودة. الفجوة الحقيقية في قيمة السلة.", M, 6.1, W - 2 * M, 0.45, { fontSize: 13, bold: true, color: INK });
  source(s, "المصدر: GA4 الموقع 333082030، استُخرجت في 15 نوفمبر 2026. الفترة السابقة تشمل عيد الأضحى (مايو 2026).");
}

// 6. Monthly trend
{
  const s = content("الاتجاه الشهري: الطلبات اليومية تتراجع منذ أغسطس", "تحليل الأداء");
  s.addChart(pres.charts.BAR, [{ name: "متوسط الطلبات اليومية", labels: ["أغسطس", "سبتمبر", "أكتوبر", "نوفمبر (1–14)"], values: [136, 126, 113, 61] }],
    Object.assign(chartBase(), { x: 5.2, y: 1.3, w: 7.5, h: 4.9, barDir: "col", chartColors: [RED], showValue: true, dataLabelPosition: "outEnd",
      showTitle: true, title: "متوسط الطلبات اليومية المسجلة", titleColor: INK, titleFontSize: 13, showLegend: false, valAxisHidden: true, barGapWidthPct: 60 }));
  const rows = [["الشهر", "الطلبات", "الإيراد", "السلة"], ["أغسطس", "4,217", "3.13M", "742"], ["سبتمبر", "3,780", "2.88M", "761"], ["أكتوبر", "3,507", "2.78M", "794"], ["نوفمبر 1–14", "859", "0.66M", "766"]];
  s.addTable(rows.map((r, i) => r.map(c => ({ text: c, options: { bold: i === 0, color: i === 0 ? WHITE : INK, fill: { color: i === 0 ? RED : WHITE }, fontFace: F, fontSize: 12, align: "center", valign: "middle" } }))),
    { x: M, y: 1.4, w: 4.3, colW: [1.45, 0.95, 1.0, 0.9], rowH: 0.42, border: { type: "solid", pt: 0.5, color: LINE } });
  card(s, M, 3.85, 4.3, 2.35, WHITE);
  bullets(s, ["الطلبات اليومية تراجعت 17% من أغسطس إلى أكتوبر", "نوفمبر يسير بنصف معدل أكتوبر، والسبب موضح في الشريحة التالية", "متوسط السلة مستقر حول 740–790 ريالًا، أقل من مستهدف 850"], M + 0.15, 3.98, 4.0, 2.1, { fontSize: 12.5 });
  source(s, "المصدر: GA4 الموقع، تجميع شهري. أغسطس كامل للعرض الشهري فقط.");
}

// 7. ALERT
{
  const s = content("تنبيه عاجل: الطلبات المسجلة هبطت 70% منذ 3 نوفمبر", "تحليل الأداء");
  const labels = ["25/10", "26/10", "27/10", "28/10", "29/10", "30/10", "31/10", "1/11", "2/11", "3/11", "4/11", "5/11", "6/11", "7/11", "8/11", "9/11", "10/11", "11/11", "12/11", "13/11", "14/11"];
  const tx = [86, 102, 249, 174, 153, 133, 144, 230, 159, 48, 37, 42, 39, 36, 32, 42, 45, 44, 36, 33, 36];
  s.addChart(pres.charts.LINE, [{ name: "طلبات مسجلة يوميًا", labels, values: tx }],
    Object.assign(chartBase(), { x: 4.6, y: 1.3, w: 8.1, h: 4.4, chartColors: [RED], lineSize: 2.5, lineDataSymbol: "circle", lineDataSymbolSize: 6,
      showTitle: true, title: "الطلبات المسجلة يوميًا", titleColor: INK, titleFontSize: 13, showLegend: false, catAxisLabelFontSize: 9 }));
  const facts = [
    ["150 ← 40", "طلبًا يوميًا: قبل 3 نوفمبر وبعده"],
    ["19.3% ← 6.7%", "من بدأ الدفع وأكمل الشراء"],
    ["1,195 ← 106", "طلبات قناة Direct في فترتين متقاربتين (13 و12 يومًا)"],
  ];
  facts.forEach((f, i) => stat(s, M, 1.3 + i * 1.5, 3.75, 1.35, f[0], f[1], null, WHITE, RED));
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.85, w: W - 2 * M, h: 0.65, rectRadius: 0.1, fill: { color: RED }, line: { color: RED } });
  T(s, "التشخيص: الزيارات والسلات وبدء الدفع لم تتغير، والقنوات المدفوعة مستقرة. الانهيار في Direct فقط، وهذا يرجّح خللًا في تتبع صفحة إتمام الطلب أو في بوابة الدفع. الإجراء خلال 48 ساعة: مطابقة يومية مع طلبات سلة.", M + 0.2, 5.85, W - 2 * M - 0.4, 0.65, { fontSize: 12.5, bold: true, color: WHITE, valign: "middle" });
  s.addNotes("هذه أهم نقطة تشغيلية. لا نستطيع الجزم إن كانت الطلبات انخفضت فعلًا أم أن التتبع تعطل، لأن ربط سلة عبر جود يحتاج إعادة اتصال. إذا كانت الطلبات الفعلية في سلة طبيعية، فالخلل في التتبع ويجب إصلاحه قبل أي قرار ميزانية. وإذا انخفضت فعلًا، فهي مشكلة دفع أو مخزون أو سعر.");
}

// 8. Payday weekly
{
  const s = content("نمط الراتب: الطلبات تتضاعف في أسبوع الصرف", "تحليل الأداء");
  const wk = ["16 أغس", "23 أغس", "30 أغس", "6 سبت", "13 سبت", "20 سبت", "27 سبت", "4 أكت", "11 أكت", "18 أكت", "25 أكت", "1 نوف", "8 نوف"];
  const v = [657, 1168, 1150, 796, 680, 723, 1222, 734, 696, 553, 1041, 591, 268];
  s.addChart(pres.charts.BAR, [{ name: "طلبات أسبوعية", labels: wk, values: v }],
    Object.assign(chartBase(), { x: M, y: 1.3, w: 8.0, h: 4.95, barDir: "col", chartColors: [RED],
      showValue: true, dataLabelPosition: "outEnd", showTitle: true, title: "الطلبات الأسبوعية حسب بداية الأسبوع", titleColor: INK, titleFontSize: 13, showLegend: false, valAxisHidden: true, barGapWidthPct: 40, catAxisLabelFontSize: 9 }));
  card(s, 8.9, 1.3, 3.83, 4.95, WHITE);
  T(s, "ماذا تعني؟", 9.05, 1.45, 3.55, 0.45, { fontSize: 17, bold: true, color: RED });
  bullets(s, [
    "أسابيع الصرف (27 من كل شهر) تحقق 1,040–1,220 طلبًا مقابل 550–800 في بقية الأسابيع",
    "قرابة ثلث طلبات الشهر يأتي في 7 أيام",
    "الفرصة: ركّز الميزانية وعروض الحزم في نافذة 25–3 من كل شهر",
    "ونفّذ عروض التقسيط وحجز الطلب المسبق في منتصف الشهر لتخفيف الفجوة",
  ], 9.05, 2.0, 3.55, 4.1, { fontSize: 12.5 });
  source(s, "المصدر: GA4 الموقع، أسابيع تبدأ الأحد. أسبوع 8 نوفمبر تأثر بخلل التتبع.");
}

// 9. Funnel
{
  const s = content("قمع الشراء: التسريب الأكبر بعد بدء الدفع", "تحليل الأداء");
  const steps = [
    ["531,698", "جلسة", 1.0],
    ["47,288", "إضافة للسلة", 0.78],
    ["65,406", "بدء الدفع (يشمل الشراء المباشر)", 0.62],
    ["10,278", "شراء مكتمل", 0.4],
  ];
  steps.forEach((st, i) => {
    const w = 7.2 * st[2], x = 0.6 + (7.2 - w) / 2 + 0.0, y = 1.35 + i * 1.22;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 1.0, rectRadius: 0.1, fill: { color: i === 3 ? RED : ["C97A6E", "B85A50", "A83A36"][i] }, line: { color: WHITE } });
    T(s, [{ text: st[0] + "  ", options: { bold: true, fontSize: 22 } }, { text: st[1], options: { fontSize: 13 } }], x, y, w, 1.0, { color: WHITE, align: "center", valign: "middle" });
  });
  card(s, 8.2, 1.35, 4.53, 4.66, WHITE);
  T(s, "أين نخسر العميل؟", 8.35, 1.5, 4.25, 0.45, { fontSize: 17, bold: true, color: RED });
  bullets(s, [
    "نحو 84% ممن بدؤوا الدفع لم يكملوا الشراء (إتمام 15.7%)",
    "تحويل الجلسة إلى طلب 1.93%، وهو جيد لفئة سلة 770 ريالًا",
    "أسباب محتملة يلزم التحقق منها: رسوم التوصيل عند الدفع، وتوفر موعد التوصيل، وخيارات الدفع والتقسيط، وطلب التسجيل",
    "كل نقطة إضافية في الإتمام تعني نحو 650 طلبًا (نحو نصف مليون ريال) كل 90 يومًا",
  ], 8.35, 2.0, 4.25, 3.95, { fontSize: 12.5 });
  source(s, "المصدر: GA4 الموقع. «بدء الدفع» أعلى من «إضافة للسلة» بسبب زر الشراء المباشر في سلة. التطبيق لا يرسل begin_checkout حاليًا.");
}

// 10. Channels
{
  const s = content("القنوات: 72% من الإيراد بلا مصدر إعلاني واضح", "تحليل الأداء");
  s.addChart(pres.charts.BAR, [{ name: "الإيراد (ألف ريال)", labels: ["Direct", "Paid Search", "Paid Social", "Cross-network", "Paid Other", "Organic Search", "Unassigned", "Referral", "Email", "Organic Social"],
    values: [5684, 774, 390, 290, 253, 201, 103, 99, 53, 49] }],
    Object.assign(chartBase(), { x: 6.2, y: 1.3, w: 6.53, h: 5.1, barDir: "bar", chartColors: [RED], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0",
      showTitle: true, title: "الإيراد حسب القناة (ألف ريال)", titleColor: INK, titleFontSize: 13, showLegend: false, valAxisHidden: true, catAxisOrientation: "maxMin", barGapWidthPct: 35 }));
  const rows = [["القناة", "الجلسات", "الطلبات", "التحويل"],
    ["Direct", "102,805", "7,364", "7.16%"], ["Paid Search", "34,783", "975", "2.80%"], ["Organic Search", "12,788", "248", "1.94%"], ["Email", "3,703", "78", "2.11%"],
    ["Cross-network", "37,983", "373", "0.98%"], ["Paid Other", "96,280", "338", "0.35%"], ["Paid Social", "188,697", "530", "0.28%"]];
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0 || j === 3, color: i === 0 ? WHITE : (j === 3 && i >= 5 ? RED : (j === 3 ? GREEN : INK)), fill: { color: i === 0 ? RED : (i % 2 ? WHITE : "FBF2E2") }, fontFace: F, fontSize: 11.5, align: "center", valign: "middle" } }))),
    { x: M, y: 1.35, w: 5.3, colW: [1.6, 1.3, 1.1, 1.3], rowH: 0.42, border: { type: "solid", pt: 0.5, color: LINE } });
  T(s, "Paid Social يجلب 36% من الجلسات و5% فقط من الطلبات. جزء من أثره يظهر لاحقًا داخل Direct والتطبيق، ولن يُقاس إلا بربط Meta CAPI وUTM موحّد.", M, 4.9, 5.3, 1.4, { fontSize: 12.5, bold: true });
  source(s, "المصدر: GA4 الموقع 16 أغسطس – 14 نوفمبر 2026، تجميع القنوات الافتراضي.");
}

// 11. Platform table
{
  const s = content("المنصات الإعلانية: Google Search الأعلى كفاءة في التحويل", "تحليل الأداء");
  const rows = [["المنصة (مصادر UTM مجمعة)", "الجلسات", "الطلبات", "التحويل", "الإيراد (ريال)", "الحكم الأولي"],
    ["Google Ads (cpc)", "86,142", "1,373", "1.59%", "1,078,643", "توسيع"],
    ["Snapchat", "142,547", "432", "0.30%", "313,193", "إعادة هيكلة"],
    ["Meta (FB/IG)", "74,451", "251", "0.34%", "187,883", "إعادة هيكلة + CAPI"],
    ["TikTok", "56,978", "167", "0.29%", "126,105", "اختبار محدود"],
    ["واتساب كرزون", "11,486", "92", "0.80%", "66,125", "توسيع (احتفاظ)"],
    ["البريد (Klaviyo/Mautic)", "3,193", "71", "2.22%", "49,446", "توسيع (احتفاظ)"],
    ["Google Organic", "12,238", "242", "1.98%", "196,120", "استثمار SEO"]];
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0 || j === 0 || j === 5, color: i === 0 ? WHITE : (j === 5 ? (c.startsWith("توسيع") || c.startsWith("استثمار") ? GREEN : RED) : INK), fill: { color: i === 0 ? RED : (i % 2 ? WHITE : "FBF2E2") }, fontFace: F, fontSize: 12, align: j === 0 ? "right" : "center", rtlMode: true, valign: "middle" } }))),
    { x: M, y: 1.3, w: W - 2 * M, colW: [3.0, 1.6, 1.4, 1.4, 2.1, 2.633], rowH: 0.5, border: { type: "solid", pt: 0.5, color: LINE } });
  card(s, M, 5.45, W - 2 * M, 1.0, WHITE);
  T(s, "ملاحظة: الإنفاق وتكلفة الطلب (CPA) وROAS غير متاحة لأن ربط Meta وGoogle Ads منتهٍ. الحكم هنا مبني على جودة الزيارة والتحويل فقط، ويُعاد حسابه بعد إعادة الربط وقبل نقل أي ميزانية.", M + 0.2, 5.5, W - 2 * M - 0.4, 0.9, { fontSize: 13, valign: "middle" });
  source(s, "المصدر: GA4 الموقع، sessionSource/Medium. يشمل Snapchat: snapchat/paid_social وsnapchat/paid وsnap/cpc.");
}

// 12. New vs returning
{
  const s = content("العملاء العائدون: 14% من المستخدمين و28% من الطلبات", "تحليل الأداء");
  s.addChart(pres.charts.DOUGHNUT, [{ name: "الطلبات", labels: ["عملاء جدد", "عملاء عائدون"], values: [7391, 2888] }],
    Object.assign(chartBase(), { x: 7.6, y: 1.3, w: 5.1, h: 4.9, chartColors: [ROSE, RED], holeSize: 58, showPercent: true, showValue: false, dataLabelColor: INK, dataLabelFontSize: 13,
      showLegend: true, legendPos: "b", showTitle: true, title: "توزيع الطلبات", titleColor: INK, titleFontSize: 13 }));
  stat(s, 3.9 + 0.1, 1.35, 3.45, 1.6, "62,699", "مستخدم عائد", "مقابل 376,538 جديدًا");
  stat(s, M, 1.35, 3.25, 1.6, "2.26%", "تحويل الجلسة العائدة", "مقابل 1.96% للجديدة");
  card(s, M, 3.2, 6.85, 3.0, WHITE);
  T(s, "الفرصة", M + 0.2, 3.3, 6.45, 0.45, { fontSize: 17, bold: true, color: RED });
  bullets(s, [
    "اللحوم والذبائح شراء متكرر بطبيعته (أسبوعي أو شهري أو موسمي)، لكن العائد لا يتجاوز ثلث الطلبات",
    "رفع حصة العائدين من 28% إلى 35% يضيف قرابة 700 طلب كل 90 يومًا دون تكلفة اكتساب",
    "الأدوات متوفرة: واتساب كرزون، وMautic/SES، والتطبيق بإشعاراته؛ الناقص هو رحلات الاحتفاظ المؤتمتة",
  ], M + 0.2, 3.8, 6.45, 2.35, { fontSize: 13 });
  source(s, "المصدر: GA4 الموقع، newVsReturning. يعتمد على ملفات تعريف المتصفح وقد يقلل عدد العائدين الفعلي.");
}

// 13. Geography
{
  const s = content("الجغرافيا: 3 مدن تحقق 80% من الإيراد، والمدينة والقصيم فرص قريبة", "تحليل الأداء");
  s.addChart(pres.charts.BAR, [{ name: "الإيراد (ألف ريال)", labels: ["الرياض", "جدة", "الدمام", "المدينة المنورة", "بريدة", "أبها", "مكة", "الجبيل", "الخبر", "تبوك"], values: [2963, 1930, 1490, 571, 147, 108, 105, 92, 87, 52] }],
    Object.assign(chartBase(), { x: 6.0, y: 1.3, w: 6.73, h: 5.1, barDir: "bar", chartColors: [RED], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0",
      showTitle: true, title: "الإيراد حسب المدينة (ألف ريال)", titleColor: INK, titleFontSize: 13, showLegend: false, valAxisHidden: true, catAxisOrientation: "maxMin", barGapWidthPct: 35 }));
  const rows = [["المدينة", "حصة الإيراد", "التحويل"], ["الرياض", "37%", "2.17%"], ["جدة", "24%", "1.68%"], ["الدمام", "19%", "2.40%"], ["المدينة المنورة", "7%", "2.06%"], ["بريدة", "1.9%", "1.42%"], ["الجبيل", "1.2%", "2.82%"]];
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0, color: i === 0 ? WHITE : INK, fill: { color: i === 0 ? RED : (i % 2 ? WHITE : "FBF2E2") }, fontFace: F, fontSize: 12, align: "center", valign: "middle" } }))),
    { x: M, y: 1.35, w: 5.1, colW: [2.0, 1.6, 1.5], rowH: 0.4, border: { type: "solid", pt: 0.5, color: LINE } });
  bullets(s, [
    "جدة ثاني سوق، لكن تحويلها الأدنى بين الكبار (1.68%)، فتحتاج تجربة توصيل وعروضًا محلية",
    "المدينة المنورة رابع سوق بلا تركيز إعلاني خاص",
    "القصيم (بريدة) سوق «حاشي» تقليدي وتحويله منخفض، فيستحق اختبارًا",
  ], M, 4.35, 5.1, 2.0, { fontSize: 12.5 });
  source(s, "المصدر: GA4 الموقع حسب مدينة الزائر. يجب مطابقة نطاق التوصيل الفعلي مع الفروع قبل التوسع.");
}

// 14. Products
{
  const s = content("المنتجات: الحزم تقود الإيراد، والأكثر مشاهدة لا يتحول", "تحليل الأداء");
  s.addChart(pres.charts.BAR, [{ name: "إيراد المنتج (ألف ريال)", labels: ["بوكسين نعيمي كشميري لباني 6+6", "خروف الجوهر الجذع", "20 كيلو حاشي محلي", "بوكس نعيمي كبير", "بوكس حري محلي كبير", "جذع كامل", "بوكس حري صغير", "2 بوكس لباني 6+6", "2 بوكس لباني 12 ك", "خروف الجوهر اللباني"],
    values: [476, 437, 430, 415, 366, 333, 286, 279, 275, 252] }],
    Object.assign(chartBase(), { x: 5.6, y: 1.3, w: 7.13, h: 5.1, barDir: "bar", chartColors: [RED], showValue: true, dataLabelPosition: "outEnd",
      showTitle: true, title: "أعلى 10 منتجات إيرادًا (ألف ريال)", titleColor: INK, titleFontSize: 13, showLegend: false, valAxisHidden: true, catAxisOrientation: "maxMin", barGapWidthPct: 35, catAxisLabelFontSize: 9.5 }));
  card(s, M, 1.35, 4.8, 2.35, "F1F7F3");
  T(s, "منتجات تتحول بقوة (شراء ÷ مشاهدة)", M + 0.15, 1.45, 4.5, 0.4, { fontSize: 14, bold: true, color: GREEN });
  bullets(s, ["لحم عجل مفروم 3 كيلو: 465 شراء من 962 مشاهدة، منتج إضافي مثالي للبيع المتقاطع", "حزم «2 بوكس»: 6% تحويل، فالعميل يفضّل الحزمة", "خروف الجوهر الهرفي: 8%"], M + 0.15, 1.88, 4.5, 1.8, { fontSize: 12 });
  card(s, M, 3.9, 4.8, 2.45, "FBEDEB");
  T(s, "منتجات تُستنزف فيها المشاهدات", M + 0.15, 4.0, 4.5, 0.4, { fontSize: 14, bold: true, color: RED });
  bullets(s, ["بوكس نعيمي صغير: 34,801 مشاهدة، 0.9% فقط", "بوكس نعيمي كبير: 30,151 مشاهدة، 1.3%", "الإجراء: اختبار السعر والصور وخيارات الوزن ووضوح التوصيل في هاتين الصفحتين أولًا"], M + 0.15, 4.43, 4.5, 1.85, { fontSize: 12 });
  source(s, "المصدر: GA4 الموقع، itemName، 16 أغسطس – 14 نوفمبر 2026. 167 منتجًا لها مبيعات. أسماء المنتجات مختصرة.");
}

// =====================================================================
pres.addSection({ title: "السوق والمنافسة" });
sectionSlide("ثانيًا: السوق والمنافسة", "حجم الطلب، سلوك البحث، المنافسون، وتحليل SWOT", "السوق والمنافسة");

// 16. Market
{
  const s = content("السوق: طلب كبير ينمو، والقناة الرقمية لا تزال في بدايتها", "السوق والمنافسة");
  const m = [["5.1 مليار $", "سوق اللحوم الطازجة في السعودية 2025", "نمو سنوي متوقع 5.5% (Statista)"], ["15–18%", "النمو السنوي للبقالة الإلكترونية", "حجمها نحو 1.8 مليار $ في 2025 (IMARC، PS Market Research)"], ["38%", "الاعتماد على الاستيراد", "تعرّض لتقلب الأسعار والإمداد (Ken Research)"], ["8 فبراير", "بداية رمضان 1448 تقريبًا", "وعيد الفطر نحو 9 مارس 2027"]];
  m.forEach((v, i) => stat(s, W - M - 2.9 - i * (2.9 + 0.2), 1.3, 2.9, 2.15, v[0], v[1], v[2]));
  s.addChart(pres.charts.BAR, [{ name: "بحث شهري", labels: ["حاشي", "مندي", "نعيمي", "لحوم", "خروف", "كبش نجد", "لحم مفروم", "ذبايح", "حري", "عقيقة"], values: [135000, 135000, 40500, 33100, 27100, 22200, 18100, 8100, 8100, 3600] }],
    Object.assign(chartBase(), { x: 4.9, y: 3.6, w: 7.83, h: 2.85, barDir: "col", chartColors: [RED], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0", dataLabelFontSize: 9,
      showTitle: true, title: "متوسط البحث الشهري في Google — السعودية", titleColor: INK, titleFontSize: 12, showLegend: false, valAxisHidden: true, barGapWidthPct: 40 }));
  card(s, M, 3.6, 4.1, 2.85, WHITE);
  bullets(s, ["البحث عن حاشي ومندي 135 ألفًا شهريًا لكل منهما، بينما جلب البحث العضوي 12.8 ألف جلسة فقط في 90 يومًا", "اسم كبش نجد يُبحث 22 ألف مرة شهريًا بمؤشر منافسة 100، أي أن منافسين يزايدون على اسم العلامة", "كلمة عقيقة الأعلى تكلفة للنقرة (5.6 دولار)، فهي نية شراء عالية القيمة"], M + 0.15, 3.72, 3.8, 2.65, { fontSize: 12 });
  source(s, "المصادر: Statista، IMARC، PS Market Research، Ken Research، تقويم أم القرى عبر Gulf News؛ Google Keyword Planner عبر HYPD (أكتوبر 2026). تقديرات الجهات تختلف بحسب النطاق.");
}

// 17. Competitors
{
  const s = content("المشهد التنافسي: المنافسون يبيعون بالمرونة والتقسيط والسعر", "السوق والمنافسة");
  const rows = [["المنافس", "قناة البيع", "زاوية الرسالة الإعلانية (نشطة نوفمبر 2026)", "ما نتعلمه"],
    ["حاشي القصيم", "واتساب + إنستغرام", "«سمّ بس والباقي علينا»: اختيار التقطيع حسب الرغبة", "التخصيص عبر واتساب يقلل الاحتكاك"],
    ["الريف للحوم", "تطبيق + متجر", "«الريف يختار لك أفضل ذبيحة» + تقسيط تابي", "التقسيط ضمن الرسالة الأساسية"],
    ["ذبائح الأمانة", "تطبيق + اتصال", "سواكني وحري وتيوس، تقطيع وتغليف وتوصيل", "منافسة سعرية محلية"],
    ["لحمة وشحمة (الرياض)", "متجر إلكتروني", "جودة الاختيار والتوصيل السريع", "تموضع مميز في الرياض"],
    ["مناسك / متجر أضحية", "موقع + Meta", "عقيقة وصدقة في أفريقيا بربع الثمن مع توثيق فيديو", "تهديد مباشر لطلبات العقيقة والصدقة"],
    ["الجزيرة للذبائح", "تطبيق", "توصيل مجاني؛ تقييم 4.4 مقابل 4.0 لكبش نجد", "تقييم التطبيق عامل ثقة"]];
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0 || j === 0, color: i === 0 ? WHITE : INK, fill: { color: i === 0 ? RED : (i % 2 ? WHITE : "FBF2E2") }, fontFace: F, fontSize: 11.5, align: "right", rtlMode: true, valign: "middle" } }))),
    { x: M, y: 1.3, w: W - 2 * M, colW: [2.2, 1.9, 4.6, 3.433], rowH: 0.6, border: { type: "solid", pt: 0.5, color: LINE } });
  T(s, "ميزتنا: علامة معروفة يُبحث عنها بالاسم، وشبكة فروع في 6 مناطق، وتطبيق وخدمة عملاء منظمة. المطلوب تحويلها إلى رسائل واضحة: الجودة، والتوقيت، والتقسيط، والتخصيص.", M, 5.65, W - 2 * M, 0.8, { fontSize: 13, bold: true, color: RED });
  source(s, "المصادر: مكتبة إعلانات Meta (إعلانات نشطة في السعودية، 15 نوفمبر 2026)، App Store. لا تُنشر بيانات إنفاق المنافسين.");
}

// 18. SWOT
{
  const s = content("تحليل SWOT لكبش نجد", "السوق والمنافسة");
  const q = [
    { t: "نقاط القوة", c: GREEN, f: "EEF5F0", items: ["طلب على العلامة: 22 ألف بحث شهري باسم كبش نجد", "العملاء المباشرون يتحولون بنسبة 7.2%", "سلة مرتفعة (771 ريالًا) وتشكيلة واسعة (167 منتجًا مباعًا)", "فروع في 6 مناطق، وتطبيق iOS وAndroid، وخدمة عملاء ومركز شكاوى منظم", "هوية بصرية معتمدة ومحتوى لحوم حقيقي"] },
    { t: "نقاط الضعف", c: RED, f: "FBEDEB", items: ["تعطل محتمل في تتبع الشراء منذ 3 نوفمبر، وانتهاء ربط الحسابات الإعلانية", "نحو 84% يتركون الدفع قبل الإتمام", "تحويل الإعلانات الاجتماعية لا يتجاوز 0.3%", "حصة العائدين 28% فقط وغياب برنامج ولاء", "بحث عضوي ضعيف، وتقييم التطبيق 4.0"] },
    { t: "الفرص", c: GOLD, f: "FBF4E0", items: ["رمضان وعيد الفطر 2027 وموسم الشتاء والكشتات (حاشي ومندي)", "دورة الرواتب: الطلبات تتضاعف أسبوع الصرف", "بحث شهري ضخم عن حاشي ومندي (135 ألفًا لكل منهما) لم نستثمره", "قطاع الشركات والمطاعم والمناسبات والعقيقة", "اشتراكات شهرية والتقسيط ونمو البقالة الإلكترونية 15–18%"] },
    { t: "التهديدات", c: "5B3A29", f: "F1EAE5", items: ["منافسو واتساب المحليون بأسعار أقل ومرونة أعلى", "عقيقة وصدقة خارجية بربع السعر", "مزايدة المنافسين على اسم العلامة في Google", "تقلب أسعار المواشي والاعتماد على الاستيراد (38%)", "ارتفاع تكلفة الإعلانات في رمضان وحساسية العميل للسعر"] },
  ];
  const cw = (W - 2 * M - 0.3) / 2, ch = 2.55;
  q.forEach((b, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = W - M - cw - col * (cw + 0.3), y = 1.25 + row * (ch + 0.2);
    card(s, x, y, cw, ch, b.f, { line: { color: b.c, width: 1 } });
    T(s, b.t, x + 0.2, y + 0.1, cw - 0.4, 0.42, { fontSize: 17, bold: true, color: b.c });
    bullets(s, b.items, x + 0.2, y + 0.55, cw - 0.4, ch - 0.62, { fontSize: 11.5 });
  });
}

// =====================================================================
pres.addSection({ title: "خطة النمو" });
sectionSlide("ثالثًا: خطة النمو 90 يومًا", "ديسمبر 2026 – فبراير 2027: قياس ثم تحويل ثم احتفاظ ثم رمضان", "خطة النمو");

// 20. Targets
{
  const s = content("الأهداف: من الوضع الحالي إلى نهاية فبراير 2027", "خطة النمو");
  const rows = [["المؤشر", "الأساس (أكتوبر 2026)", "هدف نهاية فبراير", "الرافعة الرئيسية"],
    ["الطلبات اليومية", "113", "150", "التحويل + الاحتفاظ + رمضان"],
    ["متوسط السلة", "794 ريال", "850 ريال", "الحزم والبيع المتقاطع وحد التوصيل المجاني"],
    ["الإيراد الشهري", "2.78 مليون", "3.8 مليون", "الطلبات × السلة"],
    ["إتمام الدفع", "19%", "24%", "تبسيط الدفع والتقسيط ووضوح التوصيل"],
    ["حصة العملاء العائدين", "28%", "35%", "رحلات واتساب والبريد والاشتراكات"],
    ["تحويل Paid Social", "0.3%", "0.6%", "CAPI وصفحات هبوط مخصصة وإعادة استهداف"],
    ["مطابقة GA4 مع سلة", "غير متحققة", "فرق ≤ 5%", "إصلاح التتبع والتتبع من الخادم"]];
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0 || j === 0 || j === 2, color: i === 0 ? WHITE : (j === 2 ? RED : INK), fill: { color: i === 0 ? RED : (i % 2 ? WHITE : "FBF2E2") }, fontFace: F, fontSize: 12.5, align: j === 3 || j === 0 ? "right" : "center", rtlMode: true, valign: "middle" } }))),
    { x: M, y: 1.3, w: W - 2 * M, colW: [2.8, 2.5, 2.5, 4.333], rowH: 0.53, border: { type: "solid", pt: 0.5, color: LINE } });
  T(s, "الأهداف مشروطة بنتيجة المطابقة مع سلة في الأسبوع الأول. إذا ظهر أن الأساس الحقيقي أعلى، تُعاد معايرة الأرقام دون تغيير الرافعات. المستهدف التاريخي للمالك (250 طلبًا يوميًا وسلة 850) هدف سنوي لا نَعِد به خلال 90 يومًا.", M, 5.65, W - 2 * M, 0.85, { fontSize: 12.5, color: MUTED });
}

// 21. Pillars
{
  const s = content("خمس ركائز للنمو", "خطة النمو");
  const p = [
    { t: "القياس أولًا", d: "إعادة ربط Meta وGoogle وجود؛ مطابقة يومية GA4 وسلة؛ Meta CAPI وSnap/TikTok Events API؛ UTM موحّد؛ إضافة begin_checkout للتطبيق", img: null },
    { t: "التحويل والسلة", d: "تبسيط الدفع وإظهار التوصيل والموعد مبكرًا؛ تابي وتمارا في صفحة المنتج؛ حزم وإضافات (مفروم، كبدة)؛ حد توصيل مجاني محسوب" },
    { t: "اكتساب أذكى", d: "توسيع Google Search وPMax وShopping على حاشي ونعيمي ومندي؛ حماية اسم العلامة؛ إعلانات اجتماعية مبنية على المنتجات الرابحة ونافذة الراتب" },
    { t: "الاحتفاظ والولاء", d: "رحلات آلية عبر واتساب والبريد: بعد الشراء، وإعادة الطلب بعد 30–45 يومًا، واسترجاع السلة، واستعادة العميل؛ اشتراك شهري؛ برنامج إحالة" },
    { t: "المواسم والشركات", d: "رمضان: حجز مسبق وسلال إفطار صائم؛ عقيقة ومناسبات؛ عروض للشركات والمطاعم والجمعيات" },
  ];
  const cw = (W - 2 * M - 4 * 0.2) / 5;
  p.forEach((v, i) => {
    const x = W - M - cw - i * (cw + 0.2), y = 1.4;
    card(s, x, y, cw, 4.9, WHITE);
    circleNum(s, i + 1, x + cw / 2 - 0.3, y + 0.25, 0.6, i === 0 ? RED : (i === 4 ? GOLD : "B85A50"));
    T(s, v.t, x + 0.12, y + 1.0, cw - 0.24, 0.5, { fontSize: 15.5, bold: true, color: RED, align: "center" });
    T(s, v.d, x + 0.12, y + 1.6, cw - 0.24, 3.2, { fontSize: 14 });
  });
}

// 22. Roadmap
{
  const s = content("خارطة التنفيذ: 3 مراحل في 90 يومًا", "خطة النمو");
  const ph = [
    { t: "المرحلة 1: إصلاح وقياس", d: "16 نوفمبر – 5 ديسمبر", c: RED, items: ["مطابقة طلبات سلة مع GA4 يوميًا منذ 25 أكتوبر", "إصلاح حدث purchase وصفحة الشكر وبوابة الدفع", "إعادة ربط Meta وGoogle Ads وMerchant وجود", "CAPI وEvents API وقاموس UTM", "لوحة متابعة أسبوعية موحدة", "حملة الراتب 25 نوفمبر – 3 ديسمبر"] },
    { t: "المرحلة 2: تحويل وسلة", d: "6 ديسمبر – 10 يناير", c: "B85A50", items: ["اختبارات A/B على صفحتي النعيمي الأكثر مشاهدة", "إظهار التقسيط والتوصيل في صفحة المنتج", "حزم الشتاء: حاشي ومندي وكشتة", "إطلاق رحلات واتساب والبريد الأساسية", "إعادة هيكلة Snap وMeta وTikTok", "حماية كلمة العلامة في Google"] },
    { t: "المرحلة 3: احتفاظ ورمضان", d: "11 يناير – 14 فبراير", c: GOLD, items: ["إطلاق الاشتراك الشهري وبرنامج الإحالة", "حجز رمضان المسبق من 20 يناير", "سلال إفطار صائم للشركات والجمعيات", "حملة العقيقة والمناسبات", "ذروة رمضان 8 فبراير مع حماية المخزون", "مراجعة 90 يومًا وقرار الميزانية التالية"] },
  ];
  const cw = (W - 2 * M - 0.4) / 3;
  ph.forEach((v, i) => {
    const x = W - M - cw - i * (cw + 0.2), y = 1.3;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: 0.95, rectRadius: 0.1, fill: { color: v.c }, line: { color: v.c } });
    T(s, [{ text: v.t, options: { bold: true, fontSize: 16, breakLine: true } }, { text: v.d, options: { fontSize: 12 } }], x + 0.15, y, cw - 0.3, 0.95, { color: WHITE, valign: "middle" });
    card(s, x, y + 1.1, cw, 3.95, WHITE);
    bullets(s, v.items, x + 0.15, y + 1.25, cw - 0.3, 3.7, { fontSize: 13.5 });
  });
  source(s, "التواريخ تقريبية. موعد رمضان مرتبط برؤية الهلال (تقويم أم القرى: نحو 8 فبراير 2027).");
}

// 23. Channel plan / budget
{
  const s = content("خطة القنوات وتوزيع الميزانية المقترح", "خطة النمو");
  s.addChart(pres.charts.DOUGHNUT, [{ name: "الميزانية", labels: ["Google Search/PMax/Shopping", "Meta (FB/IG)", "Snapchat", "TikTok", "CRM وواتساب والمؤثرين", "احتياطي اختبارات"], values: [35, 22, 18, 8, 10, 7] }],
    Object.assign(chartBase(), { x: 7.6, y: 1.3, w: 5.13, h: 5.1, chartColors: [RED, "B85A50", GOLD, "5B3A29", GREEN, "C9B8A8"], holeSize: 52, showPercent: true, showValue: false, dataLabelColor: WHITE, dataLabelFontSize: 11,
      showLegend: true, legendPos: "b", legendFontSize: 9.5, showTitle: true, title: "التوزيع المقترح (% من الإنفاق)", titleColor: INK, titleFontSize: 13 }));
  const rows = [["القناة", "الدور", "قاعدة القرار"],
    ["Google Search/PMax", "التقاط الطلب (حاشي، نعيمي، مندي، عقيقة)", "توسيع ما دام CPA ضمن الحد"],
    ["Meta", "الكتالوج الديناميكي وإعادة الاستهداف", "إيقاف أي إعلان بلا شراء بعد 3× CPA"],
    ["Snapchat", "الوصول للشباب ونافذة الراتب", "تحويل الهدف من الزيارات إلى الشراء"],
    ["TikTok", "محتوى التجهيز والطبخ وصناع محتوى", "اختبار 4 أسابيع ثم قرار"],
    ["واتساب والبريد", "الاحتفاظ والاسترجاع", "قياس الإيراد لكل رسالة"]];
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0 || j === 0, color: i === 0 ? WHITE : INK, fill: { color: i === 0 ? RED : (i % 2 ? WHITE : "FBF2E2") }, fontFace: F, fontSize: 11.5, align: "right", rtlMode: true, valign: "middle" } }))),
    { x: M, y: 1.35, w: 6.8, colW: [1.8, 2.8, 2.2], rowH: 0.62, border: { type: "solid", pt: 0.5, color: LINE } });
  T(s, "الحد الأعلى للإنفاق يُحدَّد بعد إعادة ربط الحسابات وفق سياسة التكلفة المعتمدة. المبدأ: لا زيادة إنفاق قبل إصلاح القياس، والتحويل من القنوات الضعيفة إلى Google والاحتفاظ تدريجيًا (20% أسبوعيًا كحد أقصى).", M, 5.2, 6.8, 1.25, { fontSize: 12, color: MUTED });
}

// 24. CRM journeys
{
  const s = content("برنامج الاحتفاظ: 6 رحلات آلية عبر واتساب والبريد والتطبيق", "خطة النمو");
  const j = [
    ["سلة متروكة", "خلال ساعة: تذكير + رابط إكمال + خيار التقسيط", "استرجاع 8–12% من السلات"],
    ["بعد الشراء", "تأكيد، ثم تقييم بعد التسليم، ثم طلب مراجعة في التطبيق", "رفع تقييم التطبيق إلى 4.5"],
    ["إعادة الطلب", "يوم 30–45 حسب المنتج: «حان وقت تجديد مخزونك؟»", "+5 نقاط في حصة العائدين"],
    ["نافذة الراتب", "يوم 26: عرض حزمة للعملاء السابقين", "تركيز الطلب في الذروة"],
    ["استعادة العميل", "بعد 90 يومًا بلا طلب: عرض شخصي", "إعادة تنشيط 5% من الخاملين"],
    ["المناسبات", "عقيقة وزواج ورمضان: نموذج حجز مسبق", "طلبات عالية القيمة"],
  ];
  const cw = (W - 2 * M - 0.4) / 3, ch = 2.35;
  j.forEach((v, i) => {
    const col = i % 3, row = Math.floor(i / 3), x = W - M - cw - col * (cw + 0.2), y = 1.3 + row * (ch + 0.2);
    card(s, x, y, cw, ch, WHITE);
    circleNum(s, i + 1, x + cw - 0.65, y + 0.2, 0.45);
    T(s, v[0], x + 0.15, y + 0.2, cw - 0.9, 0.45, { fontSize: 15.5, bold: true, color: RED, valign: "middle" });
    T(s, v[1], x + 0.15, y + 0.75, cw - 0.3, 0.95, { fontSize: 12.5 });
    pill(s, v[2], x + 0.15, y + ch - 0.52, cw - 0.3, SAND, INK);
  });
  source(s, "الأدوات: كرزون (واتساب)، Mautic/SES (البريد)، إشعارات التطبيق. الرسائل تتبع سياسة خدمة العملاء المعتمدة وموافقات الإرسال.");
}

// 25. Ramadan
{
  const s = content("رمضان 1448: الموسم الأهم في الخطة", "خطة النمو");
  s.addImage({ path: path.join(D, "c6.png"), x: M, y: 1.4, w: 3.3, h: 3.3, altText: "ذبيحة مع الرز" });
  s.addImage({ path: path.join(D, "c3.png"), x: M + 0.9, y: 4.35, w: 2.1, h: 2.1, altText: "حاشي" });
  const items = [
    ["20 يناير", "فتح الحجز المسبق", "اختيار موعد التوصيل خلال رمضان، مع عربون أو تقسيط"],
    ["1 فبراير", "سلال إفطار صائم", "باقات للشركات والجمعيات والمساجد بفواتير وتوزيع مجدول"],
    ["8 فبراير", "إطلاق رمضان", "عروض يومية للعائلات (ذبيحة مع الرز، حاشي، بوكسات تخزين)"],
    ["العشر الأواخر", "استعداد العيد", "حجز ذبائح العيد مبكرًا وضمان السعة التشغيلية"],
  ];
  items.forEach((v, i) => {
    const y = 1.35 + i * 1.25, x = 4.3, w = W - M - x;
    card(s, x, y, w, 1.1, WHITE);
    pill(s, v[0], x + w - 1.75, y + 0.37, 1.55, RED);
    T(s, v[1], x + 0.2, y + 0.12, w - 2.2, 0.4, { fontSize: 15.5, bold: true, color: RED });
    T(s, v[2], x + 0.2, y + 0.55, w - 2.2, 0.48, { fontSize: 12.5 });
  });
  T(s, "شروط النجاح: تأكيد السعة مع الفروع والمسالخ، وتثبيت أسعار الشراء مبكرًا، ورفع جاهزية خدمة العملاء (الرد خلال 24 ساعة كحد أقصى)", 4.3, 6.35, W - M - 4.3, 0.35, { fontSize: 11, color: MUTED });
}

// 26. Financial scenario
{
  const s = content("الأثر المالي المتوقع: +1.6 مليون ريال خلال 90 يومًا", "خطة النمو");
  s.addChart(pres.charts.BAR, [
    { name: "المسار الحالي (أساس أكتوبر)", labels: ["ديسمبر", "يناير", "فبراير"], values: [2.78, 2.78, 2.78] },
    { name: "مع تنفيذ الخطة", labels: ["ديسمبر", "يناير", "فبراير"], values: [3.05, 3.35, 3.57] },
  ], Object.assign(chartBase(), { x: 5.3, y: 1.3, w: 7.43, h: 5.1, barDir: "col", chartColors: ["C9B8A8", RED], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00",
    showTitle: true, title: "الإيراد الشهري (مليون ريال)", titleColor: INK, titleFontSize: 13, showLegend: true, legendPos: "b", valAxisHidden: true, barGapWidthPct: 50 }));
  stat(s, M, 1.35, 4.5, 1.5, "10.0M", "إيراد 90 يومًا مع الخطة", "مقابل 8.35 مليون في المسار الحالي");
  card(s, M, 3.05, 4.5, 3.35, WHITE);
  T(s, "افتراضات السيناريو", M + 0.15, 3.15, 4.2, 0.4, { fontSize: 15, bold: true, color: RED });
  bullets(s, ["ديسمبر: 120 طلبًا يوميًا × 820 ريالًا (إصلاح التتبع والدفع)", "يناير: 128 × 845 (احتفاظ + حزم الشتاء)", "فبراير: 150 × 850 (حجز رمضان وبدايته)", "الحساسية: كل 10 طلبات يومية ≈ 255 ألف ريال شهريًا", "لا يشمل عيد الفطر (مارس)"], M + 0.15, 3.6, 4.2, 2.75, { fontSize: 12 });
  source(s, "تقدير إداري مبني على GA4. الربحية تُحسب بعد ربط تكاليف أودو والإنفاق الإعلاني وفق سياسة التكلفة المعتمدة (≤ 68%).");
}

// 27. KPIs & governance
{
  const s = content("الحوكمة: كيف نتابع ونقرر أسبوعيًا", "خطة النمو");
  const g = [
    ["يوميًا", "مطابقة طلبات سلة مع GA4، الإنفاق اليومي، تنبيهات الهبوط > 20%"],
    ["أسبوعيًا (الأحد)", "لوحة: الطلبات، السلة، الإتمام، CPA وROAS لكل منصة، حصة العائدين، الشكاوى"],
    ["كل أسبوعين", "مراجعة الاختبارات (A/B، الإعلانات، الرسائل) وقرار التوسيع أو الإيقاف"],
    ["شهريًا", "تقرير للإدارة والمساهمين: الإيراد، الربحية، تكلفة الاكتساب، قيمة العميل"],
  ];
  g.forEach((v, i) => {
    const y = 1.35 + i * 1.08;
    card(s, M, y, W - 2 * M, 0.92, WHITE);
    pill(s, v[0], W - M - 2.35, y + 0.28, 2.15, RED);
    T(s, v[1], M + 0.2, y, W - 2 * M - 2.75, 0.92, { fontSize: 14, valign: "middle" });
  });
  T(s, "المسؤوليات المقترحة", W - M - 3.0, 5.75, 3.0, 0.4, { fontSize: 14, bold: true, color: RED });
  T(s, "مدير النمو: الخطة والميزانية  •  محلل البيانات: القياس واللوحة  •  مدير CRM: الرحلات  •  التشغيل والفروع: السعة والتوصيل", M, 6.1, W - 2 * M, 0.4, { fontSize: 12.5 });
}

// 28. Risks
{
  const s = content("المخاطر وخطط المعالجة", "خطة النمو");
  const r = [
    ["تأكُّد انخفاض الطلبات الفعلي (ليس خلل تتبع)", "عالٍ", "فحص بوابة الدفع والأسعار والمخزون خلال 48 ساعة، وحملة استرجاع فورية"],
    ["تأخر إعادة ربط الحسابات", "عالٍ", "تجميد زيادات الميزانية حتى الربط؛ تصدير يدوي مؤقت للتقارير"],
    ["ارتفاع أسعار المواشي قبل رمضان", "متوسط", "تثبيت عقود شراء مبكرًا وتسعير الحجز المسبق بهامش"],
    ["ضغط تشغيلي في الذروة", "متوسط", "سقف يومي للطلبات حسب الفرع وجدولة مواعيد التوصيل"],
    ["إرهاق العملاء من الرسائل", "منخفض", "حد أقصى رسالتان أسبوعيًا وإلغاء اشتراك سهل"],
  ];
  const rows = [["الخطر", "الأثر", "المعالجة"]].concat(r);
  s.addTable(rows.map((row, i) => row.map((c, j) => ({ text: c, options: { bold: i === 0 || j === 0, color: i === 0 ? WHITE : (j === 1 ? (c === "عالٍ" ? RED : (c === "متوسط" ? GOLD : GREEN)) : INK), fill: { color: i === 0 ? RED : (i % 2 ? WHITE : "FBF2E2") }, fontFace: F, fontSize: 12.5, align: j === 1 ? "center" : "right", rtlMode: true, valign: "middle" } }))),
    { x: M, y: 1.35, w: W - 2 * M, colW: [4.2, 1.3, 6.633], rowH: 0.75, border: { type: "solid", pt: 0.5, color: LINE } });
}

// 29. Decisions
pres.addSection({ title: "القرار" });
{
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: "القرار" });
  T(s, "القرارات المطلوبة اليوم", M, 0.55, W - 2 * M, 0.9, { fontSize: 38, bold: true, color: WHITE });
  const d = [
    "اعتماد خطة 90 يومًا والأهداف المرحلية، مع مراجعة بعد المرحلة الأولى",
    "تفويض فوري لإعادة ربط Meta وGoogle Ads وMerchant Center وجود، وإصلاح التتبع",
    "تعيين مالك واحد للنمو ولوحة أسبوعية موحدة تُعرض على الإدارة",
    "اعتماد ميزانية اختبار للتحويل والاحتفاظ (التقسيط، الحزم، رحلات واتساب)",
    "الموافقة على مسار رمضان والشركات وبدء التحضير التشغيلي من ديسمبر",
  ];
  d.forEach((t, i) => {
    const y = 1.65 + i * 0.92;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: W - 2 * M - 3.9, h: 0.75, rectRadius: 0.1, fill: { color: "7E1A1B" }, line: { color: "B84A4B", width: 0.75 } });
    circleNum(s, i + 1, W - M - 3.9 - 0.65, y + 0.14, 0.47, GOLD);
    T(s, t, M + 0.2, y, W - 2 * M - 3.9 - 1.0, 0.75, { fontSize: 15, color: WHITE, valign: "middle" });
  });
  s.addImage({ path: path.join(D, "c5.png"), x: W - M - 3.4, y: 2.0, w: 3.4, h: 3.4, altText: "نعيمي" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: W - M - 3.0, y: 5.85, w: 2.6, h: 0.95, rectRadius: 0.12, fill: { color: CREAM }, line: { color: CREAM } });
  s.addImage({ path: path.join(D, "logo_h.png"), x: W - M - 2.75, y: 5.95, w: 2.1, h: 0.784, altText: "شعار كبش نجد" });
}

// 30. Sources appendix
{
  const s = content("ملحق: المصادر والتعريفات", "القرار");
  bullets(s, [
    "Google Analytics 4 — خاصية الموقع 333082030 وخاصية التطبيق 460813092، عبر HYPD، استُخرجت في 15 نوفمبر 2026 بتوقيت الرياض",
    "Google Keyword Planner عبر HYPD — السعودية، العربية، متوسط 12 شهرًا حتى أكتوبر 2026",
    "مكتبة إعلانات Meta — إعلانات نشطة في السعودية بكلمة «ذبائح»، 15 نوفمبر 2026",
    "Statista: Fresh Meat — Saudi Arabia؛ IMARC: Saudi Arabia Red Meat Market؛ PS Market Research: Saudi Online Grocery؛ Ken Research: Saudi Red Meat Market",
    "Gulf News وThe National: موعد رمضان 2027 وفق تقويم أم القرى",
    "App Store: صفحات تطبيقات كبش نجد والجزيرة للذبائح",
    "قاعدة معرفة كبش نجد (لقطة 9 نوفمبر 2026): الهوية، الفروع، المستهدفات التاريخية، سياسة التكلفة",
    "تعريفات: التحويل = الطلبات ÷ الجلسات؛ إتمام الدفع = الطلبات ÷ بدء الدفع؛ السلة = الإيراد ÷ الطلبات؛ الإسناد = آخر نقرة في GA4",
  ], M, 1.35, W - 2 * M, 5.1, { fontSize: 13 });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("written", OUT);
})();
