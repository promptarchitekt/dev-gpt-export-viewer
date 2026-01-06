export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }
  try {
    const {
      overall,
      clarity,
      functionality,
      structure,
      helpful,
      comment,
      app,
      version,
      time,
      ua,
    } = req.body || {};
    const toNum = (v) => (typeof v === "string" ? Number(v) : v);
    const isRating = (v) => Number.isFinite(v) && v >= 1 && v <= 5;

    const overallN = toNum(overall);
    const clarityN = toNum(clarity);
    const functionalityN = toNum(functionality);
    const structureN = toNum(structure);

    if (
      !isRating(overallN) ||
      !isRating(clarityN) ||
      !isRating(functionalityN) ||
      !isRating(structureN)
    ) {
      return res.status(400).json({ error: "invalid_ratings" });
    }

    const helpfulVal =
      Array.isArray(helpful) ? helpful.join(", ") : helpful || "-";
    const commentVal = String(comment || "").slice(0, 5000);

    const safeTime = (() => {
      const d = new Date(time || Date.now());
      return Number.isFinite(d.getTime()) ? d.toISOString() : new Date().toISOString();
    })();
    const title = `[Feedback] ${app || "app"} v${
      version || "0.0.0"
    } – ${safeTime}`;
    const body = [
      `Overall: ${overallN}/5`,
      `Clarity: ${clarityN}/5`,
      `Functionality: ${functionalityN}/5`,
      `Structure: ${structureN}/5`,
      `Helpful: ${helpfulVal}`,
      "",
      "Comment:",
      commentVal || "(none)",
      "",
      "Meta:",
      `App: ${app || "-"}`,
      `Version: ${version || "-"}`,
      `User-Agent: ${ua || "-"}`,
      `Time: ${time || new Date().toISOString()}`,
    ].join("
");

    const GH_TOKEN = process.env.GH_TOKEN;
    // Neutral default: set GH_REPO via environment when deploying if you want GitHub issues created
    const GH_REPO = process.env.GH_REPO || "";
    if (!GH_TOKEN || !GH_REPO) {
      // Not configured for remote issue creation — accept but don't forward
      return res.status(200).json({ ok: true, stored: false });
    }
    const resp = await fetch(`https://api.github.com/repos/${GH_REPO}/issues`, {
      method: "POST",
      headers: {
        Authorization: `token ${GH_TOKEN}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title, body, labels: ["feedback"] }),
    });
    if (!resp.ok) {
      const text = await resp.text();
      return res.status(500).json({ error: "github_error", details: text });
    }
    const json = await resp.json();
    return res.status(200).json({ ok: true, issue: json.html_url });
  } catch (e) {
    return res.status(500).json({ error: "server_error", details: String(e) });
  }
}
