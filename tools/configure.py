# Applies the whole Arc-style setup to a running Vivaldi (started with --remote-debugging-port=9333).
import base64, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD_DIR = os.path.expanduser("~/Library/Application Support/VivalArc/mod")
SAGE_ID = "5a6e0c1f-8d2b-4e7a-9c3d-a5bf9e5a6e01"  # arc-sage.css targets this id

THEMES_DIR = os.environ.get("VIVALARC_THEMES", f"{ROOT}/themes")  # setup.sh downloads them

themes = {name: base64.b64encode(open(f"{THEMES_DIR}/theme-{name}.zip", "rb").read()).decode()
          for name in ("ArcLight", "ArcDark")}

prefs = {
    "vivaldi.tabs.bar.position": "left",
    "vivaldi.tabs.bar.width": 240,
    "vivaldi.tabs.stacking.mode": "accordion",
    "vivaldi.tabs.new_placement": "alwayslast",
    "vivaldi.address_bar.visible": False,
    "vivaldi.status_bar.display": "overlay",
    "vivaldi.panels.as_overlay.enabled": True,
    "vivaldi.panels.window_defaults": {"barVisible": False, "contentVisible": False, "width": 0},
    "vivaldi.tabs.tiling.collapse_border": True,
    "vivaldi.tabs.tiling.show_titlebar": False,
    "vivaldi.appearance.css_ui_mods_directory": MOD_DIR,
    "vivaldi.auto_hide.enabled": True,
    "vivaldi.auto_hide.tab_bar": True,
    "vivaldi.auto_hide.panel": False,
    "vivaldi.auto_hide.address_bar": True,
    "vivaldi.auto_hide.status_bar": False,
    "vivaldi.auto_hide.bookmarks_bar": True,
    "vivaldi.auto_hide.show_introduction": False,
    # URL bar and extension buttons at the top of the sidebar (the address bar is hidden,
    # so extension buttons left there would be unreachable)
    "vivaldi.toolbars.tabbar_before": ["Back", "Forward", "Reload", "FlexibleSpacer", "Extensions",
                                       "AddressField", "WorkspaceButton"],
    "vivaldi.toolbars.navigation": ["PanelToggle", "PanelWidthSpacer", "Spacer",
                                    "VPNButton", "UpdateButton", "AccountButton"],
    "vivaldi.startup.has_seen_welcome_page": True,
    "vivaldi.quick_commands.open_url_in_new_tab": True,
    "vivaldi.quick_commands.first_run_tip_dismissed": True,
    "vivaldi.quick_commands.search_priority": [
        "KEYWORD_SEARCH", "OPEN_TABS", "BOOKMARK_ITEM_OR_FOLDER", "HISTORY", "CALCULATOR", "WORKSPACES",
        "NORMAL_COMMAND", "COMMAND_CHAIN", "READING_LIST", "NOTES_SEARCH", "EXTENSIONS", "PAGE_ACTIONS",
        "CLOSED_TABS", "SYNCED_TABS", "SEND_TAB_TO_SELF", "NAMED_TAB_GROUPS"],
}

# macOS shortcuts; any other command using the same keys loses them
shortcuts = {
    "COMMAND_SHOW_QUICK_COMMANDS": ["meta+t", "meta+e", "f2"],  # Arc command bar
    "COMMAND_NEW_TAB": ["meta+shift+alt+t"],
    "COMMAND_TOGGLE_AUTO_HIDE_TAB_BAR": ["meta+s"],             # Arc: pin / unpin sidebar
    "COMMAND_MAIN_TOGGLE_TAB_BAR": [],
    "COMMAND_PIN_TAB": ["meta+d"],
    "COMMAND_PAGE_COPY_URL": ["meta+shift+c"],
    "COMMAND_MAIN_TOGGLE_ADDRESS_BAR": ["meta+b"],
    "COMMAND_TOGGLE_PANEL": ["meta+p", "alt+meta+p", "f4"],
    "COMMAND_SAVE_PAGE": ["meta+shift+alt+s"],
    "COMMAND_ADD_BOOKMARK": ["meta+shift+alt+d"],
    "COMMAND_PRINT_PAGE": ["meta+shift+alt+p"],
}

sage_colors = {"name": "Arc Sage", "id": SAGE_ID, "url": "", "backgroundImage": "",
               "colorWindowBg": "#a5bf9e", "colorAccentBg": "#a5bf9e", "colorBg": "#eef2ec",
               "colorFg": "#2f4529", "colorHighlightBg": "#3f6b36", "accentOnWindow": False,
               "transparencyTabBar": True, "transparencyTabs": True, "radius": 12}

ublock_lists = [f"https://ublockorigin.github.io/uAssets/filters/{n}.txt"
                for n in ("filters", "privacy", "badware", "quick-fixes", "unbreak", "resource-abuse")]

js = f"""(async () => {{ try {{
  const P = vivaldi.prefs, C = vivaldi.contentBlocking, S = vivaldi.searchEngines, log = {{}};
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  for (const [path, value] of Object.entries({json.dumps(prefs)})) await P.set({{path, value}});
  log.prefs = 'ok';

  const actions = (await P.get('vivaldi.actions')).value, mac = actions[0];
  const wanted = {json.dumps(shortcuts)}, taken = new Set(Object.values(wanted).flat());
  for (const [cmd, v] of Object.entries(mac))
    if (!(cmd in wanted) && v && v.shortcuts) v.shortcuts = v.shortcuts.filter(s => !taken.has(s));
  for (const [cmd, keys] of Object.entries(wanted)) mac[cmd] = Object.assign(mac[cmd] || {{}}, {{shortcuts: keys}});
  await P.set({{path: 'vivaldi.actions', value: actions}});
  log.shortcuts = 'ok';

  // themes: import only previews them, so save each preview as a user theme
  let base;
  for (const [name, b64] of Object.entries({json.dumps(themes)})) {{
    await P.set({{path: 'vivaldi.themes.preview', value: []}});
    const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    const r = await vivaldi.themePrivate.import({{dataBlob: bin.buffer}});
    if (r.error) throw new Error(name + ': ' + JSON.stringify(r.error));
    let t;
    for (let i = 0; i < 50; i++) {{
      t = (await P.get('vivaldi.themes.preview')).value[0];
      if (t && t.name === name) break;
      await sleep(200);
    }}
    if (!t || t.name !== name) throw new Error('theme preview missing: ' + name);
    const user = (await P.get('vivaldi.themes.user')).value.filter(u => u.id !== t.id);
    user.push(t);
    await P.set({{path: 'vivaldi.themes.user', value: user}});
    base = base || t;
  }}
  await P.set({{path: 'vivaldi.themes.preview', value: []}});
  const sage = {{...base, ...{json.dumps(sage_colors)}}};
  const user = (await P.get('vivaldi.themes.user')).value.filter(u => u.id !== sage.id);
  user.push(sage);
  await P.set({{path: 'vivaldi.themes.user', value: user}});
  await P.set({{path: 'vivaldi.theme.schedule.enabled', value: 'system'}});
  await P.set({{path: 'vivaldi.theme.schedule.o_s', value: {{light: sage.id, dark: sage.id}}}});
  await P.set({{path: 'vivaldi.themes.current', value: sage.id}});
  log.themes = (await P.get('vivaldi.themes.user')).value.map(u => u.name);

  const tu = await S.getTemplateUrls();
  const google = tu.templateUrls.find(t => /google\\./.test(t.url) && t.keyword === 'g')
              || tu.templateUrls.find(t => t.name === 'Google');
  for (const type of Object.values(S.DefaultType)) await S.setDefault(type, google.guid);
  log.search = google.name;

  await C.setActiveExceptionsList('tracking', 'exempt_list');
  await C.setActiveExceptionsList('ad_blocking', 'exempt_list');
  const enable = async (group, re) => {{
    for (const s of await C.getRuleSources(group)) if (re.test(s.source_location) && !s.loaded) await C.enableSource(group, s.id);
  }};
  await enable('tracking', /easyprivacy/);
  await enable('ad_blocking', /liste_fr\\.txt/);
  const have = new Set((await C.getRuleSources('ad_blocking')).map(s => s.source_location));
  for (const u of {json.dumps(ublock_lists)})
    if (!have.has(u)) await C.addKnownSourceFromURL('ad_blocking', u,
      {{allow_abp_snippets: false, naked_hostname_is_pure_host: true, use_whole_document_allow: true}});
  log.blocking = 'ok';
  return log;
}} catch (e) {{ return 'ERROR ' + e.stack; }} }})()"""

with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
    f.write(js)
try:
    out = subprocess.run([sys.executable, "-I", f"{HERE}/cdp.py", "-f", f.name],
                         env={**os.environ, "TGT": "main.html"}, capture_output=True, text=True)
finally:
    os.unlink(f.name)
print(out.stdout.strip() or out.stderr.strip())
sys.exit(1 if "ERROR" in out.stdout or out.returncode else 0)
