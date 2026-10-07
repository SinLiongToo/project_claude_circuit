"""Site changelog. Add a line at the top for every published version; build.py renders it
into radar77-changelog.html. Minor version = new content, patch = fixes."""

LOG = [
    ('1.23.0', '2026-10-08', ['ESD page: CDM test subsection — field-induced CDM setup, discharge waveforms by package size, test procedure, JS-002 classes and automotive requirements, package factors, design for CDM and failure signatures; linked from the qualification and assembly pages.']),
    ('1.22.1', '2026-10-07', ['Qualification page: temperature-cycling profile, Coffin–Manson test-vs-field chart, read-point drift chart and a solder-ball cross-section drawing.']),
    ('1.22.0', '2026-10-07', ['New package qualification &amp; physical analysis page: AEC-Q100 grades, stress tests with conditions and sample sizes, setting conditions from the mission profile (with calculator), read-points, pass criteria, CSAM / X-ray / cross-section / SEM analysis, failure analysis and re-qualification; linked from the package and reliability pages.']),
    ('1.21.0', '2026-10-07', ['New assembly-flow page: flip-chip and fan-out flows, RDL build-up, bumps and balls, 77 GHz specifics, in-line inspection, assembly defects, MSL and test points, with an RDL microstrip calculator; linked from the package page. claude.ai mirrors removed; the site is published on GitHub Pages only.']),
    ('1.20.0', '2026-10-06', ['Six new pages: bench bring-up &amp; lab test, antenna &amp; radar module, thermal design, EMC &amp; power integrity, design flow &amp; verification, and test cost model; each with a calculator (OTA/reflector, MIMO array, junction temperature, ripple-to-spur, cost per good die), new knowledge-graph items and glossary terms.']),
    ('1.19.0', '2026-10-06', ['New eFuse, OTP &amp; trim page: NVM types, eFuse bit cell with sense amplifier and shadow register, trim flow, trim-word map, trim-bit calculator, reliability, safety and failure modes; linked from the BIST, reliability and worked-example pages.']),
    ('1.18.0', '2026-10-02', ['New ADAS applications page: animated ACC, pedestrian AEB, BSD/LCA and RCTA scenarios with live point-cloud output and video export; functions, sensor classes, application-to-chip requirements, regulations and market trends.']),
    ('1.17.0', '2026-10-02', ['IF &amp; ADC page: saturation detectors (where they sit, circuits, specifications, testing, problems); linked from the safety page and the knowledge graph.']),
    ('1.16.1', '2026-09-29', ['Knowledge graph: one-click full-screen button.']),
    ('1.16.0', '2026-09-28', [
        'New pages: IF chain &amp; ADC circuits, radar DSP &amp; data path, functional safety (ISO 26262), ESD &amp; latch-up, reliability &amp; aging, characterization &amp; correlation, yield &amp; quality analytics, regulations &amp; interference, standards &amp; references, worked example, and this changelog.',
        'Calculators: ADC SNR budget, radar-cube memory, acceleration factor and FIT, guard-band escapes, die yield.',
        'Knowledge graph: items from the new pages; every page has a "Knowledge graph" tab that opens the graph on that page\'s items.',
        'Print layout: printing a page hides the controls, uses light colours and opens every collapsed table.',
    ]),
    ('1.15.0', '2026-09-28', ['Synthesizer: why the PLL won\'t lock, with causes, Vtune patterns and a debug flow.']),
    ('1.14.1', '2026-09-28', ['Main page: removed duplicate Knowledge Graph cards.']),
    ('1.14.0', '2026-09-28', ['BIST page: test muxes and the analog test bus; DFT page: muxes in the digital test logic.']),
    ('1.13.2', '2026-09-28', ['Knowledge graph: colours for fab &amp; package and system items.']),
    ('1.13.1', '2026-09-28', ['Knowledge graph: Focus prompts for an item and shows what it is showing.']),
    ('1.13.0', '2026-09-28', ['Knowledge graph page linking key items across all pages.']),
    ('1.12.0', '2026-09-27', ['RF front-end circuits page: LNA, mixer, PA, VGA and a cascade calculator.']),
    ('1.11.0', '2026-09-26', ['Power management page: LDO, bandgap, UV/OV, sequencing.']),
    ('1.10.0', '2026-09-26', ['Synthesizer: circuit-level blocks (charge pump, loop filter, LC tank, ×4).']),
    ('1.9.0', '2026-09-26', ['Frequency synthesizer (PLL) page.']),
    ('1.8.1', '2026-09-26', ['PCM / WAT: digital impact of corners and mismatch.']),
    ('1.8.0', '2026-09-26', ['PCM / WAT: transistor, large- and small-signal models.']),
    ('1.7.1', '2026-09-25', ['Collapsible contents panel on every page.']),
    ('1.7.0', '2026-09-25', ['Package &amp; failure modes page.']),
    ('1.6.0', '2026-09-25', ['Dark / light mode switch on every page.']),
    ('1.5.0', '2026-09-25', ['Wafer map signatures page.']),
    ('1.4.0', '2026-09-25', ['Breakdown voltages on the PCM / WAT page.']),
    ('1.3.0', '2026-09-25', ['PCM / WAT &amp; SPC page; "Main page" tab on every page.']),
    ('1.2.0–1.2.4', '2026-09-25', ['Production test flow page with a Mermaid flowchart (and where it lives).']),
    ('1.1.0', '2026-09-24', ['Tx power control: detector, VGA and predistortion.']),
    ('1.0.0', '2026-09-24', ['Signal chain, BIST &amp; loopback, DFT &amp; stress, and open/short &amp; Cres pages; site search, glossary, landing page with version stamp.']),
]


def render():
    return ''.join('\n  <h3 id="v%s">Version %s <span style="font:12px var(--mono);color:var(--muted)">· %s</span></h3>\n  <ul>%s</ul>'
                   % (v.replace('.', '-').replace('–', '-'), v, d, ''.join('<li>%s</li>' % i for i in items)) for v, d, items in LOG) + '\n'
