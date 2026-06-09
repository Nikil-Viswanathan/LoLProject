export default function PrivacyPage() {
  return (
    <main>
      <header className="hero" style={{ marginBottom: 48 }}>
        <div>
          <span className="eyebrow">RIFT RANKINGS · PRIVACY</span>
          <h1>Privacy Policy</h1>
          <p>Last updated: June 2026</p>
        </div>
      </header>

      <section className="privacy-body">
        <h2>What we collect</h2>
        <p><strong>Nothing.</strong> Rift Rankings does not collect, store, or transmit any personal data. There are no user accounts, no sign-up forms, no cookies, and no analytics or tracking scripts of any kind. All game state (your score, best streak, current round) is kept in your browser&rsquo;s memory and disappears when you close the tab.</p>

        <h2>Third-party services</h2>
        <p>This site is hosted on <strong>Vercel</strong>. Like virtually every hosting platform, Vercel automatically captures standard server logs (IP address, browser user-agent, requested pages, timestamps) as part of normal operation. Vercel&rsquo;s handling of this data is governed by their own privacy policy at <a href="https://vercel.com/privacy" target="_blank" rel="noopener noreferrer">vercel.com/privacy</a>.</p>
        <p>We use <strong>Google Fonts</strong> (DM Sans and Space Grotesk) for typography. When your browser loads these fonts, Google may receive your IP address. Google&rsquo;s privacy policy is available at <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">policies.google.com/privacy</a>.</p>

        <h2>Data source</h2>
        <p>The matchup data shown in the game is sourced from Riot Games&rsquo; API and consists of anonymised, publicly available match statistics from the SG2 server. No personal player information is displayed or stored by this site.</p>

        <h2>Your rights</h2>
        <p>If you are in the EU or California, you have rights regarding any personal data processed by third-party services used by this site. To exercise those rights, please contact the relevant third party (Vercel or Google) directly.</p>

        <h2>Changes</h2>
        <p>If this policy ever changes, the &ldquo;Last updated&rdquo; date at the top will reflect that. We&rsquo;ll never start collecting data without telling you first.</p>

        <h2>Contact</h2>
        <p>If you have questions, feel free to open an issue on the project&rsquo;s repository.</p>

        <p className="back-link"><a href="/">&larr; Back to the game</a></p>
      </section>
    </main>
  );
}
