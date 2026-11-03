// SYNDICATE alarm relay: a Cloudflare Worker, separate from ukraine-alarm-viber.
// Once a minute it reads every active alert from Ukraine Alarm and posts the air-raid
// picture to the server, signed with HMAC SHA-256 over "{timestamp}.{body}".
// The server replaces its state with each picture, so a missed minute heals by itself.
//
// Secrets (Worker -> Settings -> Variables and Secrets, type Secret):
//   UA_API_KEY    the Ukraine Alarm API key (the same one the Viber Worker uses)
//   RELAY_SECRET  the shared secret, also stored in Vault as alarm_relay_secret
// Trigger: Cron "* * * * *".

const API_URL = "https://api.ukrainealarm.com/api/v3/alerts";
const TARGET_URL = "https://syndicateholding.com/webhook/alarm-relay";

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(relay(env));
  },
};

async function relay(env) {
  const answer = await fetch(API_URL, { headers: { Authorization: env.UA_API_KEY } });
  if (!answer.ok) {
    // Nothing is sent: the server notices the silence and warns Andrii.
    console.log(`ukrainealarm answered ${answer.status}`);
    return;
  }
  const body = JSON.stringify({ regions: airRaidLevels(await answer.json()) });
  const timestamp = String(Math.floor(Date.now() / 1000));
  const sent = await fetch(TARGET_URL, {
    method: "POST",
    body,
    headers: {
      "Content-Type": "application/json",
      "X-Alarm-Timestamp": timestamp,
      "X-Alarm-Signature": await sign(env.RELAY_SECRET, `${timestamp}.${body}`),
    },
  });
  if (!sent.ok) console.log(`server answered ${sent.status}`);
}

// Region id -> "R" (red level) or "Y" (any other active air-raid alert).
function airRaidLevels(regions) {
  const levels = {};
  for (const region of regions) {
    for (const alert of region.activeAlerts || []) {
      if (alert.type !== "AIR") continue;
      const id = String(alert.regionId || region.regionId);
      const red = (alert.activeAlertLevels || []).some((level) => String(level.alertLevel).toLowerCase() === "red");
      levels[id] = red || levels[id] === "R" ? "R" : "Y";
    }
  }
  return levels;
}

async function sign(secret, text) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", encoder.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = await crypto.subtle.sign("HMAC", key, encoder.encode(text));
  return [...new Uint8Array(mac)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}
