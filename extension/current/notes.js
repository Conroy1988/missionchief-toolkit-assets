const TKB_RELEASE_NOTES={
  "version": "2.0.0",
  "major": true,
  "previousVersion": "1.8.2",
  "title": "What’s New in Toolkit 2.0",
  "intro": "The complete upgrade from Chrome Store 1.8.2 to 2.0.0 — new tools, expanded controls and fixes, grouped by feature.",
  "sections": [
    [
      "Vehicle Purchaser",
      [
        "New Operations tool for purchasing vehicles across multiple stations in one reviewed order.",
        "Filter by station type, dispatch centre or station name; scan live vehicle markets and available bays.",
        "Choose Credits or Coins, select individual stations or Select ALL Stations, and set vehicle quantities with 1, 5, 10, MAX or a custom amount.",
        "Review station orders and combined costs before buying; open station links to inspect a vehicle market.",
        "Ambulance preset: fill available spaces with ambulances while providing one Mass Casualty Equipment vehicle.",
        "The preset can build a missing Mass Casualty extension, complete construction with Coins and activate it for use. Extension costs and the combined Coin allowance are reviewed before starting.",
        "Progress, pause and resume support checks pending purchases before continuing, helping avoid duplicate orders after interruptions."
      ]
    ],
    [
      "Staff Training — station planning",
      [
        "Scan already trained refreshes qualification counts across every scanned station and page, with progress and Stop.",
        "Collapsed station rows show red “No Staff Trained”, green trained counts, or an amber unknown/failed-scan state for the chosen qualification.",
        "Staff who already hold the chosen qualification have green labelled rows and appear after other staff. Multiple qualifications are recognised.",
        "Hide Already Trained removes those rows from view without changing station totals; changing the course updates the filter.",
        "Filter stations by none, some or all trained; eligible staff; staff currently training; or scans needing attention.",
        "Sort by name, trained count, trained percentage, eligible count, total staff or staff in training, in either direction. Unknown counts stay last.",
        "Filters and sorting cover the full result set before pagination. A notice identifies selections in hidden stations.",
        "New station checkboxes, Select all stations, Select matching stations and Clear stations work across result pages.",
        "Select X untrained per selected station chooses up to your specified number at each station and reports shortages.",
        "Top up selected stations to X trained subtracts the staff already holding that qualification and selects only the missing number.",
        "Both bulk options select completely untrained staff only: anyone with any qualification or active training is excluded. Rosters are refreshed first and eligibility is checked again before enrolment.",
        "Top-up reports and skips uncertain stations with training already in progress instead of guessing their future qualification count. Bulk selection prepares your selection; it does not start a course."
      ]
    ],
    [
      "Staff Training — course completion",
      [
        "Complete ALL finishes all listed eligible classes after you review the combined Coin cost and tick its confirmation.",
        "Batch completion shows progress, supports Stop after current request and verifies interrupted completions before any retry.",
        "Completed entries update in the course list. Completion applies to the entire class, including other participants, and only verified completion offers are included."
      ]
    ],
    [
      "Emergency Payout Flash studio",
      [
        "Rebuilt payout settings as a visual studio with a 16-style gallery, artwork thumbnails and an animated preview.",
        "The gallery includes GTA V Inspired, Vice City Inspired, Bad Company Inspired, Scarface Inspired, Cyberpunk Inspired, DOOM / Slayer Protocol, Fallout Inspired and Factorio Industrial.",
        "Also includes 007 Intelligence, Hyrule Quest Reward, The Godfather Offer, Galactic / Spectre Command, Dark Fantasy / Grace Restored, Umbrella Containment, Underworld / Blood Covenant and Pixel Kingdom / 16-Bit.",
        "Choose Compact, Banner or Cinematic presentation; top, centre or bottom placement; and small, medium or large size.",
        "Set the minimum payout, banner duration and Major, High value and Elite tier thresholds, with optional tier-scaled effects.",
        "Choose banner and audio themes independently, or match them. Control volume, mute theme audio and let an audio cue finish after the banner.",
        "Bundled audio cues, including GTA V and 007, play locally; styles without a bundled track use a synthesised cue.",
        "Separate switches control the banner, red/blue map glow, cinematic particles and static presentation.",
        "Clear motion status explains paused effects; an Enable animated effects control is available alongside reduced-motion and Economy behaviour.",
        "Preview banner, Full-map test, Play Sound and Stop Preview let you try your setup. Recent payouts can be replayed without changing earnings.",
        "Rapid payouts are grouped while the current celebration finishes, avoiding overlapping celebrations. Studio preferences save with Toolkit settings."
      ]
    ],
    [
      "Mission list and vehicle loading",
      [
        "Refresh Mission List updates the current mission list and markers without reloading the whole game.",
        "An optional Auto Refresh pill checks every five seconds while the tab is visible. It starts Off and stops if refresh encounters an error.",
        "Refresh keeps mission-list scroll position, checks the game account and avoids overwriting newer live mission updates with an older downloaded snapshot.",
        "Auto load all vehicles now recognises the native missing-vehicles control and is enabled by default when no explicit preference is saved."
      ]
    ],
    [
      "Patient Transport Sweeper",
      [
        "The maximum run limit and default for new settings are now 1,000.",
        "Discovery shows eligible transports progressively, reuses very recent unchanged scan results and avoids immediately repeating a fresh scan when starting.",
        "Full Rescan discards recent scan results and fetches them again.",
        "Improved handling of complete vehicle lists reduces unnecessary fallback requests; unavailable and unchecked missions remain visible in scan progress.",
        "A stable progress panel shows the current phase, elapsed time, checked/completed counts and active mission.",
        "Follow-active behaviour keeps the current mission in view while preserving manual scrolling through results and logs."
      ]
    ],
    [
      "Operations workspace and progress",
      [
        "Cleaner Operations launch tiles remove static Ready, New and Testing badges while retaining live task activity.",
        "Scroll position and focused controls are preserved during progress updates across maintained building, training, recruitment, icon and vehicle-switching task views.",
        "Shared progress displays show current items and completed/total counts without making you chase a moving results list.",
        "The desktop Toolkit window can be dragged up to the actual navigation bar; floating panels and map offsets no longer create an invisible ceiling.",
        "Menu opening and the M shortcut are repaired, including protection from building-filter refresh failures."
      ]
    ],
    [
      "Account, sign-in and settings sync",
      [
        "A more compact Account layout clearly distinguishes signed out, connecting, signed in and syncing, with activity indicators.",
        "Added browser-tab Discord sign-in for Orion alongside the standard sign-in option, with improved callback handling and clearer sign-in errors.",
        "Sign-in status updates automatically during approval; existing Account tabs are reused and the temporary sign-in tab returns to Account.",
        "Saved cloud settings load before this device uploads changes on sign-in or reconnection.",
        "A live Time until sync countdown shows Syncing and Sync complete states, then restarts for the next scheduled sync.",
        "Account now shows your MissionChief UK building totals by type, the game-reported mission capacity and a station-count comparison. Game information can be refreshed without Discord sign-in.",
        "All ordinary Toolkit operations remain available without a Toolkit login or payment; Discord sign-in is for optional syncing."
      ]
    ],
    [
      "Discord reports",
      [
        "Manage one Toolkit Discord webhook in Account for finance reports, transport-sweep summaries and operational briefings.",
        "The destination syncs with your signed-in account across devices and is managed separately from normal settings exports.",
        "Post to Discord sends the selected report to your saved destination without the previous separate draft-and-send workflow.",
        "The webhook editor supports a label, replacement, removal and a connection check that sends no message. The saved secret URL is not displayed.",
        "Saved-destination status now refreshes after sign-in and sync, with older responses prevented from overwriting newly restored state.",
        "Report sending verifies the selected destination and avoids automatically retrying an uncertain send."
      ]
    ],
    [
      "Awards dashboard",
      [
        "The native Awards page gains a medal collection overview, progress summaries and everyday targets.",
        "Search awards, filter and sort the collection, and pin goals locally.",
        "Choose Showcase or Compact layouts, or Show original page. The enhanced view supports full pages and game frames."
      ]
    ],
    [
      "Tasks and Events dashboard",
      [
        "New overview with ready-to-claim counts and deadline highlights.",
        "Search and filter tasks, then sort by readiness, progress, deadline or credit rewards.",
        "Native categories, claim buttons, restrictions and timers stay available; Show original page restores the game layout."
      ]
    ],
    [
      "Player profiles",
      [
        "New black/red profile overview with lifetime earnings, account age, lifetime daily average and the next credit milestone.",
        "Browse the trophy gallery with award search and tier counts.",
        "Search buildings already loaded on the profile map and open their markers directly; this directory reflects loaded markers rather than a complete account inventory.",
        "Native biography, map and profile actions remain available, with a Show original page option."
      ]
    ],
    [
      "Chat, panels, alliance and inbox",
      [
        "Alliance chat has compact black/red styling and search across loaded messages by player or text.",
        "Hide or restore the alliance announcement; changed announcements reappear automatically.",
        "Collapse chat to its header and see a count of new messages received while it is collapsed.",
        "Missions, Stations and Radio also gain collapse/reopen controls that preserve their original window sizes.",
        "Panel and chat preferences are saved on this device and scoped to the game account when it can be identified.",
        "Alliance pages gain resource shortcuts, improved presentation and filtering of loaded members by name or role, with an original-page option.",
        "Inbox search filters conversations on the current page, keeps selected messages visible and improves table/message styling while retaining native compose and message controls."
      ]
    ],
    [
      "Dispatch dashboard and top navigation",
      [
        "Open Dispatch dashboard from the Stations header and load an on-demand snapshot.",
        "Compare buildings, vehicles and available staffing information across dispatch centres; expand a centre for building links and reported staffing targets.",
        "Missing staffing information is shown as unavailable rather than zero; partial snapshots are not presented as complete totals.",
        "The top navigation uses black/charcoal styling, restrained red accents and matching dropdowns, with the Toolkit two-bar mark on the Home link.",
        "Five compact building toggles provide Fire Stations, Ambulance Stations, Police Stations, Home Responses and Hospitals. Fire, ambulance and police groups include their small variants.",
        "Toggles reflect native visibility, including mixed states, and support keyboard use. They hide when space is too tight; the existing Buildings menu remains available."
      ]
    ],
    [
      "London time and update notes",
      [
        "Toolkit display times and its timestamp-based finance periods use Europe/London, automatically switching between GMT and BST.",
        "London date boundaries are used for daily transaction grouping and period calculations, including the spring and autumn clock changes.",
        "Native game daily totals retain the game’s UTC reporting boundaries and are explicitly labelled Game reporting day (UTC).",
        "The retired userscript update briefing is removed. This one-off 2.0.0 overview covers changes since store version 1.8.2; future updates return to shorter release-specific notes.",
        "Dismiss this overview once with Got it, and reopen it whenever needed from the extension popup’s What’s New link."
      ]
    ]
  ]
};
