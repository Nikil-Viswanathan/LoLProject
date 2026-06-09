"use client";

import { useCallback, useEffect, useState } from "react";

type Stat = "kills" | "damage" | "gold" | "cs";
type Champion = {
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
type Matchup = { champions: [Champion, Champion]; stat: Stat };

const statConfig = {
  kills: { label: "Kills", hint: "Champion takedowns", color: "#f36b57" },
  damage: { label: "Damage", hint: "Damage dealt to champions", color: "#df4f71" },
  gold: { label: "Gold", hint: "Total gold earned", color: "#d6a84b" },
  cs: { label: "CS", hint: "Minions and monsters slain", color: "#63c6a5" },
};
const roleLabels: Record<string, string> = {
  TOP: "Top",
  MIDDLE: "Mid",
  JUNGLE: "Jungle",
  BOTTOM: "Bottom",
  UTILITY: "Support",
};

function formatTime(seconds: number) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

function ChampionCard({
  champion,
  index,
  hiddenStat,
  onChoose,
}: {
  champion: Champion;
  index: number;
  hiddenStat: Stat;
  onChoose: () => void;
}) {
  const initials = champion.champion.slice(0, 2).toUpperCase();
  const kills = hiddenStat === "kills" ? "?" : champion.kills;
  return (
    <article className={`champ-card side-${index + 1}`}>
      <div className="card-topline">
        <span className="side-label">CONTENDER {index + 1}</span>
        <span className={`result-pill ${champion.win ? "victory" : "defeat"}`}>
          {champion.win ? "Victory" : "Defeat"}
        </span>
      </div>
      <div className="champ-identity">
        <div className="champ-avatar">{initials}</div>
        <div>
          <h2>{champion.champion}</h2>
          <p>{roleLabels[champion.lane] ?? champion.lane} · Level {champion.level}</p>
        </div>
      </div>
      <div className="quick-stats">
        <div><strong>{kills}/{champion.deaths}/{champion.assists}</strong><span>KDA</span></div>
        <div><strong>{champion.vision}</strong><span>Vision</span></div>
        <div><strong>{formatTime(champion.timePlayed)}</strong><span>Game time</span></div>
      </div>
      <button onClick={onChoose}>Choose {champion.champion}</button>
    </article>
  );
}

function Scoreboard({
  matchup,
  reveal,
}: {
  matchup: Matchup;
  reveal: boolean;
}) {
  const fields: { key: keyof Champion; label: string }[] = [
    { key: "champion", label: "Champion" },
    { key: "lane", label: "Role" },
    { key: "level", label: "Level" },
    { key: "kills", label: "Kills" },
    { key: "deaths", label: "Deaths" },
    { key: "assists", label: "Assists" },
    { key: "damage", label: "Damage" },
    { key: "gold", label: "Gold" },
    { key: "cs", label: "CS" },
    { key: "vision", label: "Vision" },
    { key: "win", label: "Result" },
    { key: "timePlayed", label: "Duration" },
  ];

  const display = (champion: Champion, key: keyof Champion) => {
    if (!reveal && key === matchup.stat) return "Hidden";
    if (key === "win") return champion.win ? "Victory" : "Defeat";
    if (key === "lane") return roleLabels[champion.lane] ?? champion.lane;
    if (key === "timePlayed") return formatTime(champion.timePlayed);
    const value = champion[key];
    return typeof value === "number" ? value.toLocaleString() : String(value);
  };

  return (
    <section className="scoreboard-section">
      <div>
        <span className="section-kicker">MATCH DATA</span>
        <h2>Full scoreboard</h2>
        {!reveal && <p>{statConfig[matchup.stat].label} stays hidden until the round ends.</p>}
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr>{fields.map((field) => <th key={field.key}>{field.label}</th>)}</tr></thead>
          <tbody>
            {matchup.champions.map((champion) => (
              <tr key={champion.champion}>
                {fields.map((field) => <td key={field.key}>{display(champion, field.key)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function Home() {
  const [matchup, setMatchup] = useState<Matchup | null>(null);
  const [score, setScore] = useState(0);
  const [best, setBest] = useState(0);
  const [round, setRound] = useState(1);
  const [gameOver, setGameOver] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadMatchup = useCallback(async () => {
    setLoading(true);
    const response = await fetch("/api/matchup", { cache: "no-store" });
    setMatchup(await response.json());
    setLoading(false);
  }, []);

  useEffect(() => { void loadMatchup(); }, [loadMatchup]);

  async function choose(index: number) {
    if (!matchup) return;
    const [selected, other] = [matchup.champions[index], matchup.champions[1 - index]];
    if (selected[matchup.stat] >= other[matchup.stat]) {
      const next = score + 1;
      setScore(next);
      setBest((current) => Math.max(current, next));
      setRound((current) => current + 1);
      await loadMatchup();
    } else {
      setGameOver(true);
    }
  }

  async function restart() {
    setScore(0);
    setRound(1);
    setGameOver(false);
    await loadMatchup();
  }

  return (
    <main>
      <header className="hero">
        <div>
          <span className="eyebrow">RIFT RANKINGS · HIGHER OR LOWER</span>
          <h1>Read the match.<br />Call the stat.</h1>
          <p>Two players from the same ranked game. One hidden stat. Pick who posted the higher number.</p>
        </div>
        <div className="score-strip">
          <div><span>Score</span><strong>{score}</strong></div>
          <div><span>Best</span><strong>{best}</strong></div>
          <div><span>Round</span><strong>{round}</strong></div>
        </div>
      </header>

      {loading || !matchup ? (
        <div className="loading">Loading matchup...</div>
      ) : gameOver ? (
        <>
          <section className="game-over">
            <span>RUN COMPLETE</span>
            <h2>{score} correct {score === 1 ? "call" : "calls"}</h2>
            <p>The hidden {statConfig[matchup.stat].label.toLowerCase()} totals were:</p>
            <div className="answers">
              {matchup.champions.map((champion) => (
                <div key={champion.champion}><span>{champion.champion}</span><strong>{champion[matchup.stat].toLocaleString()}</strong></div>
              ))}
            </div>
            <button onClick={restart}>Start a new run</button>
          </section>
          <Scoreboard matchup={matchup} reveal />
        </>
      ) : (
        <>
          <section className="challenge">
            <span>THIS ROUND</span>
            <h2>Who had more <em style={{ color: statConfig[matchup.stat].color }}>{statConfig[matchup.stat].label}</em>?</h2>
            <p>{statConfig[matchup.stat].hint} · ties count as correct</p>
          </section>
          <section className="contenders">
            {matchup.champions.map((champion, index) => (
              <ChampionCard
                key={`${champion.champion}-${index}`}
                champion={champion}
                index={index}
                hiddenStat={matchup.stat}
                onChoose={() => choose(index)}
              />
            ))}
          </section>
          <Scoreboard matchup={matchup} reveal={false} />
        </>
      )}
      <footer className="site-footer">
        <a href="/privacy">Privacy policy</a>
        <p className="disclaimer">Rift Rankings isn&rsquo;t endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends &copy; Riot Games, Inc.</p>
      </footer>
    </main>
  );
}
