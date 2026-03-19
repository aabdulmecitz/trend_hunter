/**
 * Global Meme & Trend Hunter v3.0 — Dashboard App
 * =================================================
 * Loads global_trends.json and renders all platform + AI sections.
 */

const DATA_FILE = "global_trends.json";

// ── Particles ────────────────────────────────────────────
function createParticles() {
    const c = document.getElementById("particles");
    const colors = ["#4f8eff","#a855f7","#ec4899","#f97316","#22c55e","#06b6d4","#ef4444"];
    for (let i = 0; i < 25; i++) {
        const p = document.createElement("div");
        p.className = "particle";
        const sz = Math.random() * 4 + 2;
        p.style.width = sz + "px"; p.style.height = sz + "px";
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        p.style.left = Math.random() * 100 + "%";
        p.style.animationDuration = (Math.random() * 20 + 15) + "s";
        p.style.animationDelay = (Math.random() * 10) + "s";
        c.appendChild(p);
    }
}

// ── Loader ───────────────────────────────────────────────
async function loadData() {
    try {
        const r = await fetch(DATA_FILE);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return await r.json();
    } catch (e) {
        document.querySelector(".container").innerHTML = `
            <div style="text-align:center;padding:60px;color:var(--text-muted)">
                <p style="font-size:1.3rem;margin-bottom:10px">❌ Could not load data</p>
                <p>Make sure <code>global_trends.json</code> is in the same directory and served via HTTP.</p>
                <p style="margin-top:10px;font-family:var(--font-mono);font-size:.8rem;opacity:.5">${e.message}</p>
            </div>`;
        return null;
    }
}

function esc(s) { if (!s) return ""; const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

// ═══════════════════════════════════════════════════════════
// PHASE 1 RENDERERS — Trend Data
// ═══════════════════════════════════════════════════════════

function renderMeta(d) {
    const date = d.meta?.generated_at ? new Date(d.meta.generated_at) : null;
    document.getElementById("generated-at").textContent = date
        ? date.toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })
        : "Unknown";
}

function renderStats(d) {
    const us = d.google_trends_us || [];
    const world = d.google_trends_worldwide || [];
    const hasErr = us.length === 1 && us[0].error;
    document.getElementById("stat-google").textContent = hasErr ? "—" : (us.length + world.length);
    document.getElementById("stat-youtube").textContent = (d.youtube_trending?.videos || []).length || "—";
    const ttH = (d.tiktok_trends?.trending_hashtags || []).length;
    const ttS = (d.tiktok_trends?.viral_sounds || []).length;
    document.getElementById("stat-tiktok").textContent = (ttH + ttS) || "—";
    document.getElementById("stat-instagram").textContent = (d.instagram_trends?.trending_hashtags || []).length || "—";
    document.getElementById("stat-reddit").textContent = (d.reddit_trends?.combined_top_keywords || []).length || "—";
    document.getElementById("stat-slang").textContent = Object.keys(d.meme_dictionary || {}).length || "—";
}

function renderGoogle(d) {
    const usC = document.getElementById("us-trends");
    const wC = document.getElementById("world-trends");
    const us = d.google_trends_us || [];
    const w = d.google_trends_worldwide || [];

    if (!us.length || (us.length === 1 && us[0].error)) {
        usC.innerHTML = `<div class="trend-empty">⚠️ Unavailable<br><small>${esc(us[0]?.error||'')}</small></div>`;
    } else {
        usC.innerHTML = us.map(t => `
            <div class="trend-item">
                <span class="trend-rank">${t.rank}</span>
                <span class="trend-term">${esc(t.term)}</span>
                ${t.traffic && t.traffic !== 'N/A' ? `<span class="trend-traffic">${esc(t.traffic)}</span>` : ''}
            </div>`).join("");
    }

    if (!w.length) { wC.innerHTML = `<div class="trend-empty">No worldwide trends</div>`; }
    else { wC.innerHTML = w.map(t => `
            <div class="trend-item">
                <span class="trend-rank">${t.rank}</span>
                <span class="trend-term">${esc(t.term)}</span>
                ${t.traffic && t.traffic !== 'N/A' ? `<span class="trend-traffic">${esc(t.traffic)}</span>` : ''}
            </div>`).join(""); }
}

function renderYouTube(d) {
    const yt = d.youtube_trending || {};
    const vids = yt.videos || [];
    const method = yt.method || "unknown";

    const badge = document.getElementById("yt-method");
    badge.textContent = vids.length ? method.toUpperCase().replace(/_/g," ") : "UNAVAILABLE";
    badge.className = `badge ${vids.length ? "badge-red" : "badge-orange"}`;

    const grid = document.getElementById("yt-grid");
    if (!vids.length) {
        grid.innerHTML = `<div class="trend-empty" style="grid-column:1/-1">No YouTube trending data</div>`;
        return;
    }
    grid.innerHTML = vids.slice(0, 12).map(v => `
        <div class="yt-card">
            <span class="yt-rank">#${v.rank}</span>
            <div class="yt-title">${esc(v.title)}</div>
            <div class="yt-channel">📺 ${esc(v.channel || 'N/A')}</div>
            <div class="yt-meta">${esc(v.views || '')} ${v.published ? '· '+esc(v.published) : ''}</div>
        </div>`).join("");
}

function renderTikTok(d) {
    const tt = d.tiktok_trends || {};
    const mode = tt.source_mode || "unknown";
    const badge = document.getElementById("tiktok-mode");
    badge.textContent = mode === "simulation" ? "SIMULATED" : "LIVE";
    badge.className = `badge ${mode === "simulation" ? "badge-orange" : "badge-green"}`;
    document.getElementById("tiktok-note").textContent = tt.note || "";

    document.getElementById("tt-hashtags").innerHTML = (tt.trending_hashtags || []).map(h =>
        `<span class="tag-pill tt">${esc(h.hashtag)}</span>`).join("");

    const icons = ["🎶","🎵","🎸","🎤","🎧","🥁","🎹","🎺"];
    document.getElementById("tt-sounds").innerHTML = (tt.viral_sounds || []).map((s, i) => `
        <div class="sound-item">
            <span class="sound-item-rank">${icons[i % icons.length]}</span>
            <div class="sound-item-info">
                <div class="sound-item-name">${esc(s.name)}</div>
                <div class="sound-item-artist">${esc(s.artist || 'N/A')}</div>
            </div>
            <div class="sound-item-meta">${esc(s.estimated_videos || s.category || '')}</div>
        </div>`).join("");
}

function renderInstagram(d) {
    const ig = d.instagram_trends || {};
    const mode = ig.source_mode || "unknown";
    const badge = document.getElementById("ig-mode");
    badge.textContent = mode === "curated" ? "CURATED" : "LIVE";
    badge.className = `badge ${mode === "curated" ? "badge-orange" : "badge-gradient"}`;

    document.getElementById("ig-hashtags").innerHTML = (ig.trending_hashtags || []).map(h =>
        `<span class="tag-pill ig">${esc(h.hashtag)}</span>`).join("");

    document.getElementById("ig-reels").innerHTML = (ig.reel_trends || []).map(r => {
        const sc = (r.status||'').toLowerCase();
        const cls = sc === 'hot' ? 'reel-status-hot' : sc === 'trending' ? 'reel-status-trending' : 'reel-status-evergreen';
        return `<div class="reel-item">
            <div class="reel-name">${esc(r.trend)}</div>
            <div class="reel-desc">${esc(r.description || '')}</div>
            ${r.status ? `<span class="reel-status ${cls}">${esc(r.status)}</span>` : ''}
        </div>`;
    }).join("");
}

function renderReddit(d) {
    const rd = d.reddit_trends || {};
    const perSub = rd.per_subreddit || {};
    const grid = document.getElementById("reddit-grid");
    const icons = {"r/memes":"😂","r/dankmemes":"💀","r/me_irl":"🙃","r/shitposting":"🗿",
        "r/discordapp":"💬","r/skibiditoilet":"🚽","r/tiktokcringe":"🎵",
        "r/internetculture":"🌐","r/trendingsubreddits":"📈"};

    const entries = Object.entries(perSub).filter(([_, info]) => info.posts_analyzed > 0);
    grid.innerHTML = entries.map(([sub, info]) => {
        const mx = Math.max(...info.top_keywords.map(k => k.raw_count), 1);
        return `<div class="reddit-card">
            <h3><span>${icons[sub]||'📌'} ${sub}</span><span class="reddit-count">${info.posts_analyzed} posts</span></h3>
            <div style="margin-top:12px">${info.top_keywords.slice(0,8).map(kw => `
                <div class="keyword-bar-row">
                    <span class="keyword-name">${esc(kw.keyword)}</span>
                    <div class="keyword-bar-bg"><div class="keyword-bar-fill" style="width:${kw.raw_count/mx*100}%"></div></div>
                    <span class="keyword-count">${kw.raw_count}</span>
                </div>`).join("")}
            </div></div>`;
    }).join("");
}

function renderDictionary(d) {
    const dict = d.meme_dictionary || {};
    const grid = document.getElementById("dictionary-grid");
    const emojis = {"aura":"✨","sigma":"🐺","rizz":"😏","skibidi":"🚽","brainrot":"🧠","mewing":"🗿","l":"📉","w":"📈","gyatt":"😳","slay":"💅","ratio":"📊","npc":"🤖","delulu":"🌈","sus":"🔍","cap":"🧢","bet":"🤝","fire":"🔥","goat":"🐐","vibe":"🌊","stan":"💜","based":"👑","cringe":"😬","cope":"🥲","mogged":"💪","bussin":"😋","simp":"💸","chad":"🗿"};

    grid.innerHTML = Object.entries(dict).map(([term, info]) => {
        const em = emojis[term] || "🏷️";
        const sc = info.source === "builtin_dictionary" ? "dict-source-builtin" : "dict-source-urban";
        const sl = info.source === "builtin_dictionary" ? "Built-in" : info.source === "urban_dictionary" ? "Urban Dict" : "Unknown";
        return `<div class="dict-card"><div class="dict-term"><span>${em}</span><span class="dict-term-text">${esc(term)}</span><span class="dict-source ${sc}">${sl}</span></div><div class="dict-definition">${esc(info.definition)}</div></div>`;
    }).join("");
}

// ═══════════════════════════════════════════════════════════
// PHASE 2 RENDERERS — AI Generated Content
// ═══════════════════════════════════════════════════════════

const PFP_COLORS = ["#4f8eff","#a855f7","#ec4899","#f97316","#22c55e","#ef4444","#06b6d4","#eab308"];

function renderAnalysis(d) {
    const ai = d.ai_generated_content || {};
    const card = document.getElementById("analysis-card");

    if (ai.error) {
        const isSetup = !!ai.setup_instructions;
        card.innerHTML = `<div class="ai-error" style="grid-column:1/-1">
            <p>⚠️ ${isSetup ? 'Gemini API key not configured' : esc(ai.error)}</p>
            ${isSetup ? `<p style="margin-top:12px;font-size:.85rem;color:var(--text-secondary)">
                1. Get a free key from <a href="https://aistudio.google.com/apikey" style="color:var(--accent-blue)" target="_blank">aistudio.google.com</a><br>
                2. Create a <code>.env</code> file: <code>GEMINI_API_KEY=your_key</code><br>
                3. Re-run <code>python3 main.py</code>
            </p>` : ''}
        </div>`;
        // Hide AI sections if no API key
        document.querySelectorAll("#sec-jokes, #sec-beluga, #sec-ideas").forEach(s => s.style.display = isSetup ? "none" : "block");
        return;
    }

    const analysis = ai.trend_analysis || {};
    if (!analysis.hottest_trend) {
        card.innerHTML = `<div class="ai-error" style="grid-column:1/-1">No trend analysis available</div>`;
        return;
    }

    const lvl = (analysis.meme_potential || '').toLowerCase();
    const lcls = lvl.includes('high') ? 'analysis-high' : lvl.includes('low') ? 'analysis-low' : 'analysis-medium';

    card.innerHTML = `
        <div>
            <div class="hottest">🔥 ${esc(analysis.hottest_trend)}</div>
            <div class="why">${esc(analysis.why_its_viral)}</div>
        </div>
        <span class="analysis-badge ${lcls}">Meme Potential: ${esc(analysis.meme_potential)}</span>`;
}

function renderJokes(d) {
    const jokes = (d.ai_generated_content || {}).jokes || [];
    const grid = document.getElementById("jokes-grid");
    if (!jokes.length) { grid.innerHTML = `<div class="trend-empty" style="grid-column:1/-1">No jokes generated</div>`; return; }

    grid.innerHTML = jokes.map(j => `
        <div class="joke-card">
            <span class="joke-style">${esc(j.style || '')}</span>
            <div class="joke-setup">${esc(j.setup)}</div>
            <div class="joke-punchline">😂 ${esc(j.punchline)}</div>
            ${j.trend_reference ? `<div class="joke-ref">📌 ${esc(j.trend_reference)}</div>` : ''}
        </div>`).join("");
}

function renderScenarios(d) {
    const scenarios = (d.ai_generated_content || {}).scenarios || [];
    const container = document.getElementById("scenarios-container");
    if (!scenarios.length) { container.innerHTML = `<div class="trend-empty">No scenarios generated</div>`; return; }

    container.innerHTML = scenarios.map((sc, si) => {
        const chars = sc.characters || [];
        const charColors = {};
        chars.forEach((c, i) => { charColors[c.name] = PFP_COLORS[i % PFP_COLORS.length]; });

        const scriptHTML = (sc.script || []).map(line => {
            const clr = charColors[line.character] || "#666";
            const initial = (line.character || "?")[0].toUpperCase();
            return `<div class="discord-msg">
                <div class="discord-pfp" style="background:${clr}">${initial}</div>
                <div class="discord-body">
                    <div class="discord-name" style="color:${clr}">${esc(line.character)}</div>
                    ${line.action ? `<div class="discord-action">*${esc(line.action)}*</div>` : ''}
                    <div class="discord-txt">${esc(line.message)}</div>
                    ${line.visual_note ? `<div class="discord-visual">🎬 ${esc(line.visual_note)}</div>` : ''}
                </div>
            </div>`;
        }).join("");

        return `<div class="scenario-card">
            <div class="scenario-top">
                <div>
                    <div class="scenario-title-text">📺 ${esc(sc.title)}</div>
                    <div class="scenario-premise" style="margin-bottom:4px"><span class="badge badge-purple">${esc(sc.platform || 'Discord')}</span></div>
                    <div class="scenario-premise">${esc(sc.premise)}</div>
                </div>
                <div class="scenario-thumbnail">${esc(sc.thumbnail_idea || '')}</div>
            </div>
            <div class="discord-chat">${scriptHTML}</div>
            <div class="scenario-bottom">
                <div class="scenario-twist"><strong>Twist:</strong> ${esc(sc.twist)}</div>
                <div class="scenario-chars">
                    ${chars.map(c => `<span class="scenario-char-tag">${esc(c.name)}</span>`).join("")}
                </div>
            </div>
        </div>`;
    }).join("");
}

function renderVideoIdeas(d) {
    const ideas = (d.ai_generated_content || {}).video_content_ideas || [];
    const grid = document.getElementById("ideas-grid");
    if (!ideas.length) { grid.innerHTML = `<div class="trend-empty" style="grid-column:1/-1">No ideas generated</div>`; return; }

    grid.innerHTML = ideas.map(idea => {
        const vl = (idea.estimated_virality || '').toLowerCase();
        const vcls = vl.includes('high') ? 'idea-viral-high' : vl.includes('low') ? 'idea-viral-low' : 'idea-viral-medium';
        return `<div class="idea-card">
            <div class="idea-title">${esc(idea.title)}</div>
            <div class="idea-meta">
                <span class="idea-tag idea-platform">${esc(idea.platform || '')}</span>
                <span class="idea-tag idea-format">${esc(idea.format || '')}</span>
                <span class="idea-tag ${vcls}">🔥 ${esc(idea.estimated_virality || '')}</span>
            </div>
            <div class="idea-hook">🎣 "${esc(idea.hook)}"</div>
            <div class="idea-concept">${esc(idea.concept)}</div>
            <div class="idea-trends">
                ${(idea.trending_elements || []).map(t => `<span class="idea-trend-tag">${esc(t)}</span>`).join("")}
            </div>
        </div>`;
    }).join("");
}

// ── Init ─────────────────────────────────────────────────
async function init() {
    createParticles();
    const d = await loadData();
    if (!d) return;
    // Phase 1
    renderMeta(d); renderStats(d); renderGoogle(d); renderYouTube(d);
    renderTikTok(d); renderInstagram(d); renderReddit(d); renderDictionary(d);
    // Phase 2
    renderAnalysis(d); renderJokes(d); renderScenarios(d); renderVideoIdeas(d);
}
document.addEventListener("DOMContentLoaded", init);
