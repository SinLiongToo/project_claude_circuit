# Glossary data + injection of the glossary section and auto-link script. Used by build.py.
import io, re, html, sys

G = [
("Radar system & ADAS", [
 ("ACC","Adaptive Cruise Control","Keeps distance to the car ahead; uses long-range front radar."),
 ("ADAS","Advanced Driver-Assistance Systems","The vehicle functions the radar serves."),
 ("AEB","Autonomous Emergency Braking","Brakes automatically when a collision is imminent."),
 ("BSD","Blind-Spot Detection","Corner-radar function."),
 ("LCA","Lane-Change Assist","Corner-radar function that warns of fast approaching vehicles."),
 ("RCTA","Rear Cross-Traffic Alert","Rear corner-radar function when reversing."),
 ("L2","SAE automation Level 2 (L3 = Level 3)","Partial (L2) and conditional (L3) driving automation."),
 ("FMCW","Frequency-Modulated Continuous Wave","A linear chirp; range comes from the beat frequency f_b = S·2R/c."),
 ("FoV","Field of View","Angular coverage in azimuth and elevation."),
 ("RCS","Radar Cross Section","Target reflectivity in dBsm (car ≈ 10, pedestrian ≈ −10…0)."),
 ("dBsm","Decibels relative to 1 m²","Unit of RCS."),
 ("EIRP","Effective Isotropic Radiated Power","Tx power + antenna gain; limited by regulations."),
 ("MIMO","Multiple-Input Multiple-Output","N_tx × N_rx channels form a larger virtual array."),
 ("TDM","Time-Division Multiplexing","One Tx per chirp; v_max falls by a factor of N_tx."),
 ("BPM","Binary Phase Modulation","0/180° codes across chirps separate the Tx signals."),
 ("DDMA","Doppler-Division Multiple Access","Each Tx gets a slow-time phase ramp and separates in Doppler."),
 ("DoA","Direction of Arrival","Angle estimation over the virtual array."),
 ("DBF","Digital Beamforming","FFT or matched steering over array channels."),
 ("CFAR","Constant False Alarm Rate","Adaptive detection threshold (CA = cell-averaging, OS = ordered-statistic)."),
 ("FFT","Fast Fourier Transform","Range, Doppler and angle FFTs build the radar cube."),
 ("SNR","Signal-to-Noise Ratio",""),
 ("MUSIC","MUltiple SIgnal Classification","Subspace super-resolution DoA algorithm."),
 ("ESPRIT","Estimation of Signal Parameters via Rotational Invariance Techniques","Super-resolution DoA algorithm."),
 ("IAA","Iterative Adaptive Approach","Super-resolution spectral / DoA estimator."),
 ("DBSCAN","Density-Based Spatial Clustering of Applications with Noise","Groups detections into objects."),
 ("EKF","Extended Kalman Filter","Nonlinear tracking filter."),
 ("UKF","Unscented Kalman Filter","Nonlinear tracking filter using sigma points."),
 ("IMM","Interacting Multiple Model","Tracker that mixes several motion models."),
 ("HWA","Hardware Accelerator","On-chip FFT / radar processing engine."),
 ("RTS","Radar Target Simulator","Echo generator for HIL and EOL testing."),
 ("HIL","Hardware-in-the-Loop","Testing the real sensor against simulated scenarios."),
 ("EOL","End-of-Line","Final production test of a module or vehicle."),
]),
("RF & analog front end", [
 ("RF","Radio Frequency","Here the 76–81 GHz signal."),
 ("LO","Local Oscillator","The chirp signal that drives the Tx and the Rx mixers."),
 ("IF","Intermediate Frequency","The beat / baseband signal after the mixer, DC–20 MHz."),
 ("PA","Power Amplifier","Tx output stage, 12–14 dBm."),
 ("LNA","Low-Noise Amplifier","First Rx stage; sets most of the NF."),
 ("NF","Noise Figure","Noise the receiver adds, in dB."),
 ("VGA","Variable-Gain Amplifier","Programmable-gain stage (IF), or signed VGAs in the phase rotator."),
 ("TIA","Transimpedance Amplifier","Current-to-voltage stage after a passive mixer."),
 ("HPF","High-Pass Filter","In IF: removes leakage and DC, and equalises R⁻⁴."),
 ("LPF","Low-Pass Filter",""),
 ("AAF","Anti-Aliasing Filter","Low-pass filter in front of the ADC."),
 ("PPF","Polyphase Filter","RC-CR network that generates I/Q."),
 ("I/Q","In-phase / Quadrature","Two copies of a signal 90° apart."),
 ("IRR","Image Rejection Ratio","How well an I/Q path suppresses the mirror frequency."),
 ("SSB","Single Sideband","A frequency shift in one direction only, e.g. the loopback offset."),
 ("BPSK","Binary Phase-Shift Keying","0/180° switching; produces ±f_m sidebands."),
 ("VM","Vector Modulator","I/Q-weighted phase rotator."),
 ("RTPS","Reflection-Type Phase Shifter","Hybrid coupler terminated by tunable loads."),
 ("P1dB","1 dB compression point","Input (or output) level where gain drops by 1 dB."),
 ("HD2","2nd-order Harmonic Distortion (HD3 = 3rd)","Harmonics show up as ghost targets at 2×/3× range."),
 ("AM/PM","Amplitude-to-phase conversion","Phase change caused by amplitude or supply changes."),
 ("RL","Return Loss","Match quality, in dB."),
 ("Cpl","Coupler (directional coupler)","Taps a small, known fraction (−15…−20 dB) of a signal for detection or loopback."),
 ("PD","Power Detector","Diode or square-law RF-to-DC converter."),
 ("APC","Automatic Power Control","Closed loop from the power detector to the VGA/PA gain code."),
 ("DPD","Digital Predistortion","Wideband PA linearisation used in comms; radar uses static gain/phase LUTs instead."),
 ("VSWR","Voltage Standing-Wave Ratio","Mismatch at the antenna/load; changes the delivered power."),
 ("CW","Continuous Wave","An unmodulated single-frequency tone."),
 ("ENR","Excess Noise Ratio","Calibrated output level of a noise source."),
 ("SiGe","Silicon-Germanium (BiCMOS)","Bipolar-plus-CMOS process used for earlier radar chips."),
 ("CMOS","Complementary Metal-Oxide-Semiconductor","RFCMOS = CMOS process with RF / mmWave capability."),
 ("RFCMOS","RF-capable CMOS","Today's single-chip radar process (e.g. 45/40/28/22 nm)."),
 ("NMOS","N-channel MOS transistor (PMOS = P-channel)",""),
 ("PTAT","Proportional To Absolute Temperature","Voltage or current used by temperature sensors."),
 ("BG","Bandgap reference","Temperature-stable voltage reference (BG1/BG2 = two independent ones)."),
 ("PVT","Process, Voltage, Temperature","Variation corners a design must cover."),
]),
("LO, clock & synthesis", [
 ("PLL","Phase-Locked Loop","Locks the VCO to the crystal and generates the ramp."),
 ("ADPLL","All-Digital PLL","PLL with a TDC and a digital loop filter."),
 ("VCO","Voltage-Controlled Oscillator","≈ 19–20.25 GHz, multiplied ×4 to 77 GHz."),
 ("PFD","Phase-Frequency Detector","Compares the divided VCO with the reference."),
 ("CP","Charge Pump; also Chip Probe","In a PLL: converts PFD pulses into loop-filter current. In test flows: wafer-level probe test."),
 ("TDC","Time-to-Digital Converter","Digital phase detector of an ADPLL."),
 ("XTAL","Crystal (reference oscillator)","40/50 MHz reference for PLL, ADC and digital."),
 ("DDS","Direct Digital Synthesizer","Digitally generated tone (IF test tone)."),
]),
("Data conversion & digital", [
 ("ADC","Analog-to-Digital Converter","Main Rx ADCs (ΣΔ) and the aux SAR ADC."),
 ("DAC","Digital-to-Analog Converter","Rotator I/Q weights, bias, trim, test-tone generation."),
 ("SAR","Successive-Approximation Register ADC","Slow, precise ADC used for monitoring."),
 ("CT","Continuous-Time (CT-ΣΔ)","Sigma-delta ADC with a continuous-time loop filter."),
 ("ENOB","Effective Number of Bits",""),
 ("SFDR","Spurious-Free Dynamic Range","Tone relative to the largest spur."),
 ("THD","Total Harmonic Distortion",""),
 ("DR","Dynamic Range",""),
 ("INL","Integral Nonlinearity","Deviation from the ideal transfer line."),
 ("DNL","Differential Nonlinearity","Deviation of each step from 1 LSB."),
 ("LSB","Least Significant Bit (MSB = most significant)",""),
 ("DFE","Digital Front End","Decimation, DC and I/Q correction, interference handling."),
 ("CIC","Cascaded Integrator-Comb","Multiplier-free decimation filter."),
 ("FIR","Finite Impulse Response filter",""),
 ("DSP","Digital Signal Processor",""),
 ("MCU","Microcontroller Unit",""),
 ("CPU","Central Processing Unit","E.g. the RF control CPU that runs chirps and monitors."),
 ("SoC","System-on-Chip",""),
 ("ECU","Electronic Control Unit","Vehicle computer that receives radar data."),
 ("SRAM","Static RAM (RAM = random-access memory)",""),
 ("ECC","Error-Correcting Code","Memory protection for functional safety."),
 ("DMA","Direct Memory Access",""),
 ("LUT","Look-Up Table","E.g. phase-code → (I, Q) DAC codes, Tx power vs. temperature."),
 ("FW","Firmware (SW = software)",""),
 ("OTP","One-Time Programmable memory","Holds trims and IDs, like eFuse."),
 ("SPI","Serial Peripheral Interface","Configuration / test bus from host or ATE."),
 ("CAN","Controller Area Network (CAN-FD = Flexible Data-rate)","Vehicle bus for object lists."),
 ("ETH","Ethernet (100/1000BASE-T1)","Automotive single-pair Ethernet."),
 ("CSI","Camera Serial Interface (MIPI CSI-2)","Streams raw radar data to a central SoC."),
 ("LVDS","Low-Voltage Differential Signaling","Raw-data debug / streaming interface."),
 ("GPIO","General-Purpose Input/Output",""),
 ("IO","Input/Output",""),
]),
("Power", [
 ("LDO","Low-Dropout regulator","Linear regulator; one per noise-sensitive domain."),
 ("PMIC","Power-Management IC","External bucks, supervisors and watchdog."),
 ("PSRR","Power-Supply Rejection Ratio","How much supply ripple an LDO (or circuit) blocks."),
 ("UV","Under-Voltage (OV = Over-Voltage)","Supply monitors, a safety mechanism."),
 ("GND","Ground",""),
]),
("Test & production", [
 ("BIST","Built-In Self-Test","On-chip stimulus + measurement; result is pass/fail or a value checked against a limit."),
 ("BISM","Built-In Self-Measurement","Same on-chip hardware, but the result is a calibrated value (dB, °, MHz) used for trim, calibration and trend."),
 ("DFT","Design for Test",""),
 ("ATE","Automatic Test Equipment","Production tester."),
 ("ATPG","Automatic Test Pattern Generation","Scan patterns for digital logic."),
 ("IDDQ","Quiescent supply-current test","Detects leakage defects."),
 ("PMU","Parametric Measurement Unit","ATE DC source/measure channel."),
 ("Cres","Contact resistance","Probe or socket contact resistance; measured with the Kelvin or two-current method."),
 ("FIMV","Force Current, Measure Voltage","PMU mode used for open/short (diode) tests."),
 ("FVMI","Force Voltage, Measure Current","PMU mode used for leakage and power-short tests."),
 ("IIL","Input leakage current, input Low (IIH = input High)","Leakage limit per IO pin, typically |I| < 1 µA."),
 ("IIH","Input leakage current, input High",""),
 ("ESD","Electrostatic Discharge","Pad protection diodes / clamps; the diode method uses them for continuity."),
 ("VDD","Positive supply rail (VSS = ground / negative rail)",""),
 ("VSS","Ground / negative supply rail",""),
 ("DCR","DC Resistance","E.g. of an RF shunt inductor, 0.5–3 Ω."),
 ("Hi-Z","High impedance (Z)","Output driver switched off; the pin floats."),
 ("OE","Output Enable","Control that switches an output between driving and Hi-Z."),
 ("IOZ","Off-state output leakage (IOZH at VDDIO, IOZL at 0 V)","Measured on a pin in Hi-Z; typically |I| < 1–10 µA."),
 ("VOH","Output High voltage threshold (VOL = Output Low)","Tester comparator levels that decide 1 / Z / 0."),
 ("VOL","Output Low voltage threshold",""),
 ("HIGHZ","IEEE 1149.1 instruction that puts all outputs in Hi-Z",""),
 ("EXTEST","IEEE 1149.1 external test instruction","Boundary cells drive and sample the pins; used for interconnect and walking-Z tests."),
 ("RPCT","Reduced Pin-Count Testing","Testing through JTAG / a few pins, so more sites fit on one tester."),
 ("BICS","Built-In Current Sensor","On-chip current monitor for IDDQ per power domain."),
 ("SPC","Statistical Process Control",""),
 ("VNA","Vector Network Analyzer","Lab instrument for S-parameters."),
 ("AWG","Arbitrary Waveform Generator",""),
 ("DMM","Digital Multimeter",""),
 ("GPIB","General-Purpose Interface Bus","Instrument control bus (like LAN)."),
]),
("Safety, standards & regulation", [
 ("ASIL","Automotive Safety Integrity Level","ISO 26262 risk class A–D; radar typically ASIL-B."),
 ("ISO","ISO 26262 / ISO/SAE 21434 / ISO 11452","Functional safety / cybersecurity / EMC immunity."),
 ("FTTI","Fault-Tolerant Time Interval","Time from fault to hazard; monitors must react within it."),
 ("FMEDA","Failure Modes, Effects and Diagnostic Analysis",""),
 ("SPFM","Single-Point Fault Metric","ISO 26262 coverage metric."),
 ("LFM","Latent Fault Metric","ISO 26262 coverage metric."),
 ("AEC","Automotive Electronics Council (AEC-Q100 / Q200)","Qualification of ICs / passives."),
 ("ETSI","European Telecommunications Standards Institute","EN 301 091 / EN 303 396 radar standards."),
 ("FCC","Federal Communications Commission","US rules, Part 95M for 76–81 GHz."),
 ("EMC","Electromagnetic Compatibility",""),
 ("CISPR","Comité International Spécial des Perturbations Radioélectriques","CISPR 25: vehicle-component emissions."),
 ("OOB","Out-of-Band (emission)",""),
]),
("Digital DFT, stress & reliability", [
 ("SE","Scan Enable","Selects shift (SE = 1) or functional capture (SE = 0) in scan flops."),
 ("SAF","Stuck-At Fault","Node permanently 0 or 1."),
 ("TDF","Transition Delay Fault","Node slow to rise or fall; needs at-speed test."),
 ("STA","Static Timing Analysis","Finds the longest paths for timing-aware ATPG."),
 ("OCC","On-Chip Clock Controller","Gates exact launch/capture pulses from the PLL for at-speed test."),
 ("LOC","Launch-On-Capture","At-speed scheme; also called broadside."),
 ("LOS","Launch-On-Shift","At-speed scheme; SE must switch at speed."),
 ("EDT","Embedded Deterministic Test","Scan compression (decompressor + compactor)."),
 ("LFSR","Linear-Feedback Shift Register","Pseudo-random sequence generator."),
 ("PRPG","Pseudo-Random Pattern Generator","LFSR that feeds the scan chains in LBIST."),
 ("MISR","Multiple-Input Signature Register","Compresses responses into one signature."),
 ("STUMPS","Self-Test Using MISR and Parallel Shift-register sequence generator","Standard LBIST architecture."),
 ("LBIST","Logic BIST","On-chip random-pattern scan test; used at key-on."),
 ("MBIST","Memory BIST","On-chip March-algorithm test of SRAMs."),
 ("BIRA","Built-In Redundancy Analysis","Computes which spare rows/columns repair a memory."),
 ("BISR","Built-In Self-Repair","Loads the repair from eFuse at boot."),
 ("IR","IR drop","Supply voltage drop (current × resistance), high during scan shift."),
 ("JTAG","Joint Test Action Group (IEEE 1149.1)","Boundary scan and test access port."),
 ("TAP","Test Access Port","JTAG pins TCK, TMS, TDI, TDO, TRST."),
 ("BSDL","Boundary Scan Description Language","Describes a chip's JTAG boundary-scan cells."),
 ("IJTAG","Internal JTAG (IEEE 1687)","Network for accessing on-chip instruments."),
 ("ICL","Instrument Connectivity Language (PDL = Procedural Description Language)","IJTAG description files."),
 ("ECID","Electronic Chip ID","Unique per-die ID for traceability."),
 ("HVST","High-Voltage Stress Test","Short over-voltage on the core rail to activate latent oxide defects."),
 ("VLV","Very-Low-Voltage test","Test below nominal V to expose resistive defects."),
 ("Vmin","Minimum operating voltage","The pass/fail edge in a shmoo; an outlier Vmin flags a defect."),
 ("PAT","Part Average Testing (AEC-Q001)","Outlier limits at robust μ ± 6σ."),
 ("DPAT","Dynamic Part Average Testing","PAT limits recalculated per lot or wafer."),
 ("GDBN","Good Die in Bad Neighbourhood","Wafer-map screen that rejects dies in defect clusters."),
 ("NNR","Nearest-Neighbour Residual","Compares a die's parameter with its wafer neighbours."),
 ("DPPM","Defective Parts Per Million","Shipped-quality metric; automotive target ≪ 1."),
 ("FT","Final Test","Package-level production test."),
 ("SLT","System-Level Test","Functional test by booting the application."),
 ("PCM","Process Control Monitor","Test structures in the scribe lines, measured by the fab (see WAT)."),
 ("WAT","Wafer Acceptance Test","Fab's electrical test of PCM structures before shipping wafers."),
 ("OSAT","Outsourced Semiconductor Assembly and Test","Company that packages and tests the dies."),
 ("QA","Quality Assurance","Sample-based outgoing inspection and audits."),
 ("HTOL","High-Temperature Operating Life","≈ 1000 h biased at max temperature (AEC-Q100)."),
 ("ELFR","Early Life Failure Rate","Short high-temperature operation of a large sample."),
 ("TC","Temperature Cycling","Package and interconnect fatigue test."),
 ("THB","Temperature-Humidity-Bias","85 °C / 85% RH with bias."),
 ("HAST","Highly Accelerated Stress Test","130 °C / 85% RH with bias."),
 ("RH","Relative Humidity",""),
 ("HTSL","High-Temperature Storage Life","Unbiased bake."),
 ("HBM","Human-Body Model (ESD)",""),
 ("CDM","Charged-Device Model (ESD)",""),
 ("LU","Latch-Up","JESD78 test."),
 ("EM","Electromigration","Metal wear-out under current (wafer-level reliability)."),
 ("TDDB","Time-Dependent Dielectric Breakdown","Gate-oxide wear-out."),
 ("HCI","Hot-Carrier Injection","Transistor degradation mechanism."),
 ("NBTI","Negative-Bias Temperature Instability","PMOS threshold drift."),
]),
("PCB, package & materials", [
 ("PCB","Printed Circuit Board",""),
 ("BGA","Ball Grid Array","FC-BGA = flip-chip BGA."),
 ("eWLB","embedded Wafer-Level Ball-grid-array","Fan-out package with low RF loss."),
 ("AoP","Antenna-on-Package",""),
 ("LoP","Launch-on-Package","RF launched from package into waveguide / antenna."),
 ("GCPW","Grounded Coplanar Waveguide","PCB transmission line at the ball launch."),
 ("SIW","Substrate-Integrated Waveguide","Waveguide formed with via fences in the PCB."),
 ("FR4","Flame-Retardant epoxy-glass laminate","Standard low-cost PCB material."),
 ("ENEPIG","Electroless Nickel, Electroless Palladium, Immersion Gold","PCB surface finish."),
 ("ImAg","Immersion Silver","PCB surface finish."),
 ("HASL","Hot-Air Solder Leveling","Surface finish; too rough/uneven for 77 GHz."),
 ("PBT","Polybutylene terephthalate (PC = polycarbonate)","Radome plastics."),
 ("HFSS","High-Frequency Structure Simulator (Ansys)","3D EM simulator (CST = Dassault's equivalent)."),
]),
]

def gid(a): return "g-" + re.sub(r'[^A-Za-z0-9]+', '-', a).strip('-')

def section():
    out = ['<section id="glossary">',
           '  <div class="sec-head"><span class="num">--</span><h2>Glossary of abbreviations</h2></div>',
           '  <p>Abbreviations are underlined with dots the first time they appear in each section. Hover to see the meaning; click to jump here. Use Search (Ctrl+K) to find an abbreviation anywhere on the page.</p>']
    for cat, rows in G:
        out.append('  <h3>%s</h3>' % html.escape(cat))
        out.append('  <div class="tbl"><table class="gl-tbl">')
        out.append('    <thead><tr><th>Abbr.</th><th>Stands for</th><th>Note</th></tr></thead>')
        out.append('    <tbody>')
        for a, full, note in rows:
            out.append('      <tr id="%s" data-abbr="%s" data-full="%s"><td class="v">%s</td><td>%s</td><td>%s</td></tr>' % (
                gid(a), html.escape(a, True), html.escape(full + (" (" + note + ")" if note else ""), True),
                html.escape(a), html.escape(full), html.escape(note)))
        out.append('    </tbody>')
        out.append('  </table></div>')
    out.append('</section>')
    return "\n".join(out) + "\n"

CSS = """/* glossary */
.gl-tbl td.v{font-weight:600;color:var(--rf);white-space:nowrap}
.gl-tbl td:first-child{width:90px}
a.gl{color:inherit;text-decoration:underline dotted;text-decoration-color:var(--muted);text-underline-offset:3px;cursor:help}
a.gl:hover{color:var(--rf);text-decoration-color:var(--rf)}
"""

JS = r"""<script>
(function(){
  const rows=[...document.querySelectorAll("#glossary tr[data-abbr]")];
  if(!rows.length)return;
  const map={};rows.forEach(r=>{map[r.dataset.abbr]=r});
  const keys=Object.keys(map).sort((a,b)=>b.length-a.length);
  const re=new RegExp("(?<![\\w/-])("+keys.map(k=>k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|")+")(?:s)?(?![\\w])","g");
  const SKIP="svg,script,style,a,h1,h2,h3,th,.eq,code,kbd,form,.out,.find-ov,#glossary,nav,.num,.domain,button,mark,pre,.mermaid";
  document.querySelectorAll("main section").forEach(sec=>{
    if(sec.id==="glossary")return;
    const seen=new Set(), nodes=[];
    const w=document.createTreeWalker(sec,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentNode.closest(SKIP)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
    while(w.nextNode())nodes.push(w.currentNode);
    nodes.forEach(n=>{
      const s=n.nodeValue;re.lastIndex=0;let m,last=0,f=null;
      while((m=re.exec(s))){
        const k=m[1];if(seen.has(k))continue;seen.add(k);
        f=f||document.createDocumentFragment();
        f.appendChild(document.createTextNode(s.slice(last,m.index)));
        const a=document.createElement("a");a.className="gl";a.href="#"+map[k].id;a.title=k+" — "+map[k].dataset.full;a.textContent=m[0];
        f.appendChild(a);last=m.index+m[0].length;
      }
      if(f){f.appendChild(document.createTextNode(s.slice(last)));n.parentNode.replaceChild(f,n)}
    });
  });
  const reduce=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.addEventListener("click",e=>{
    const a=e.target.closest("a.gl");if(!a)return;
    const r=document.getElementById(a.getAttribute("href").slice(1));if(!r)return;
    e.preventDefault();
    r.scrollIntoView({behavior:reduce?"auto":"smooth",block:"center"});
    r.classList.remove("find-flash");void r.offsetWidth;r.classList.add("find-flash");
    setTimeout(()=>r.classList.remove("find-flash"),1900);
  });
})();
</script>
"""

def inject(path, after_section_id, toc_after):
    s = io.open(path, encoding='utf-8').read()
    # section: replace in place if present, else append as last section inside <main>
    if 'id="glossary"' in s:
        s = re.sub(r'<section id="glossary">.*?</section>\n', lambda m: section(), s, count=1, flags=re.S)
    else:
        i = s.index('</main>')
        s = s[:i] + "\n" + section() + s[i:]
    if 'href="#glossary"' not in s:
        assert s.count(toc_after) == 1, toc_after
        s = s.replace(toc_after, toc_after + '\n    <li><a href="#glossary">Glossary</a></li>')
    if '/* glossary */' not in s:
        i = s.index('</style>'); s = s[:i] + CSS + s[i:]
    if 'a.className="gl"' not in s:
        s = s.rstrip('\n') + '\n' + JS
    # renumber
    n = [0]
    def r(m):
        v = "%02d" % n[0]; n[0] += 1; return '<span class="num">%s</span>' % v
    s = re.sub(r'<span class="num">[^<]*</span>', r, s)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
    print(path, "sections", n[0], "entries", sum(len(r) for _, r in G))

