export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  try {
    const { overall, clarity, functionality, structure, helpful, comment, app, version, time, ua } = req.body || {};
    // Basic validation
    const isNum = (v) => typeof v === 'number' && v >= 1 && v <= 10;
    if (!isNum(overall) || !isNum(clarity) || !isNum(functionality) || !isNum(structure)) {
      return res.status(400).json({ error: 'invalid ratings' });
    }
    // Compose issue payload
    const title = `[Feedback] ${app || 'app'} v${version || '0.0.0'} – ${new Date(time || Date.now()).toISOString()}`;
    const body = [
      `Overall: ${overall}/10`,
      `Clarity: ${clarity}/10`,
      `Functionality: ${functionality}/10`,
      `Structure: ${structure}/10`,
      `Helpful: ${helpful || '-'}`,
      '',
      'Comment:',
      comment || '(none)',
      '',
      'Meta:',
      `User-Agent: ${ua || '-'}`,
      `Time: ${time || new Date().toISOString()}`,
    ].join('\n');

    const GH_TOKEN = process.env.GH_TOKEN;
    const GH_REPO = process.env.GH_REPO || 'promptarchitekt/dev-gpt-export-viewer';
    if (!GH_TOKEN) {
      // If not configured, accept but do nothing (or log minimal)
      return res.status(200).json({ ok: true, stored: false });
    }
    const resp = await fetch(`https://api.github.com/repos/${GH_REPO}/issues`, {
      method: 'POST',
      headers: {
        'Authorization': `token ${GH_TOKEN}`,
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title, body, labels: ['feedback'] })
    });
    if (!resp.ok) {
      const text = await resp.text();
      return res.status(500).json({ error: 'github_error', details: text });
    }
    const json = await resp.json();
    return res.status(200).json({ ok: true, issue: json.html_url });
  } catch (e) {
    return res.status(500).json({ error: 'server_error', details: String(e) });
  }
}

