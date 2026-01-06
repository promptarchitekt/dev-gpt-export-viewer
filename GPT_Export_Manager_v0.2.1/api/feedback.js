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
    // Helper functions for defensive validation
    const toNum = (v) => {
      if (typeof v === "number") return v;
      if (typeof v === "string") {
        const n = Number(v);
        return isFinite(n) ? n : null;
      }
      return null;
    };
    const isRating = (v) => {
      const n = toNum(v);
      return n !== null && n >= 1 && n <= 5;
    };
    if (
      !isRating(overall) ||
      !isRating(clarity) ||
      !isRating(functionality) ||
      !isRating(structure)
    ) {
      return res.status(400).json({ error: "invalid ratings" });
    }

    const title = `[Feedback] ${app || "app"} v${
      version || "0.0.0"
    } – ${new Date(time || Date.now()).toISOString()}`;
    // Handle helpful: accept array OR string
    const helpfulVal = Array.isArray(helpful) ? helpful.join(", ") : (helpful || "-");
    // Truncate and sanitize comment (max 5000 chars)
    const commentVal = String(comment || "")
      .slice(0, 5000)
      .replace(/[\u0000-\u001F\u007F-\u009F]/g, "");
    const body = [
      `Overall: ${toNum(overall)}/5`,
      `Clarity: ${toNum(clarity)}/5`,
      `Functionality: ${toNum(functionality)}/5`,
      `Structure: ${toNum(structure)}/5`,
      `Helpful: ${helpfulVal}`,
      "",
      "Comment:",
      commentVal || "(none)",
      "",
      "Meta:",
      `User-Agent: ${ua || "-"}`,
      `Time: ${time || new Date().toISOString()}`,
    ].join("\n");

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
