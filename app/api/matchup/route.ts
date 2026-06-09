import { readFile } from "node:fs/promises";
import path from "node:path";

export const runtime = "nodejs";

type Champion = {
  match_id: string;
  champion: string;
  win: boolean;
  kills: number;
  deaths: number;
  assists: number;
  gold: number;
  level: number;
  lane: string;
  damage: number;
  vision: number;
  cs: number;
  timePlayed: number;
};

const numericFields = new Set([
  "kills",
  "deaths",
  "assists",
  "gold",
  "level",
  "damage",
  "vision",
  "cs",
  "timePlayed",
]);

let matches: Champion[][] | undefined;

async function loadMatches() {
  if (matches) return matches;

  const csv = await readFile(
    path.join(process.cwd(), "sg2_match_dataset.csv"),
    "utf8",
  );
  const [headerLine, ...lines] = csv.trim().split(/\r?\n/);
  const headers = headerLine.split(",");
  const grouped = new Map<string, Champion[]>();

  for (const line of lines) {
    const values = line.split(",");
    const raw = Object.fromEntries(
      headers.map((header, index) => [header, values[index]]),
    );
    const champion = Object.fromEntries(
      Object.entries(raw).map(([key, value]) => {
        if (numericFields.has(key)) return [key, Number(value)];
        if (key === "win") return [key, value === "True"];
        return [key, value];
      }),
    ) as Champion;

    const current = grouped.get(champion.match_id) ?? [];
    current.push(champion);
    grouped.set(champion.match_id, current);
  }

  matches = [...grouped.values()].filter(
    (match) => match.some((player) => player.win) && match.some((player) => !player.win),
  );
  return matches;
}

function sample<T>(items: T[]) {
  return items[Math.floor(Math.random() * items.length)];
}

export async function GET() {
  const match = sample(await loadMatches());
  const winner = sample(match.filter((player) => player.win));
  const loser = sample(match.filter((player) => !player.win));
  const matchup = Math.random() > 0.5 ? [winner, loser] : [loser, winner];
  const champions = matchup.map(
    ({
      champion,
      win,
      kills,
      deaths,
      assists,
      gold,
      level,
      lane,
      damage,
      vision,
      cs,
      timePlayed,
    }) => ({
      champion,
      win,
      kills,
      deaths,
      assists,
      gold,
      level,
      lane,
      damage,
      vision,
      cs,
      timePlayed,
    }),
  );
  const stat = sample(["kills", "damage", "gold", "cs"] as const);

  return Response.json({ champions, stat });
}
