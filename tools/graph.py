"""Knowledge graph: key circuits, parameters, tests and process items across the site,
and how they relate. build.py calls refresh() to write the data, the page-link map and
the connection table into radar77-knowledge-graph.html, and to list where each item is
mentioned on the other pages.

Node: (id, label, type, 'page#anchor', description, [extra aliases for the mention scan])
Edge: (from, relation, to), read as "from <relation> to".
"""
import io, json, re
from bs4 import BeautifulSoup

GRAPH = 'radar77-knowledge-graph.html'
PAGES = {
    'sc': ('radar77-signal-chain.html', 'Signal chain'),
    'pll': ('radar77-synthesizer.html', 'Synthesizer'),
    'pwr': ('radar77-power.html', 'Power'),
    'rf': ('radar77-rf-frontend.html', 'RF front end'),
    'bist': ('radar77-bist-loopback.html', 'BIST & loopback'),
    'cont': ('radar77-continuity.html', 'Open/short & Cres'),
    'dft': ('radar77-dft-stress.html', 'DFT & stress'),
    'flow': ('radar77-test-flow.html', 'Test flow'),
    'pcm': ('radar77-pcm-wat-spc.html', 'PCM / WAT'),
    'wm': ('radar77-wafer-map.html', 'Wafer maps'),
    'pkg': ('radar77-package.html', 'Package'),
    'ifadc': ('radar77-if-adc.html', 'IF &amp; ADC'),
    'dsp': ('radar77-dsp.html', 'DSP'),
    'fusa': ('radar77-safety.html', 'Functional safety'),
    'esd': ('radar77-esd.html', 'ESD'),
    'rel': ('radar77-reliability.html', 'Reliability'),
    'char': ('radar77-characterization.html', 'Characterization'),
    'yield': ('radar77-yield.html', 'Yield'),
    'reg': ('radar77-regulation.html', 'Regulations'),
    'app': ('radar77-applications.html', 'Applications'),
    'otp': ('radar77-efuse-otp.html', 'eFuse &amp; OTP'),
}
TYPES = [('c', 'Circuit'), ('p', 'Parameter'), ('t', 'Test'), ('f', 'Fab & package'), ('s', 'System')]

N = [
    # circuits
    ('ant', 'Antenna', 'c', 'sc#antenna', 'Tx and Rx antennas and the chip-to-antenna transition; its loss adds straight to the noise figure and subtracts from Tx power.', ['antenna', 'antennas']),
    ('pa', 'PA', 'c', 'rf#pa', 'Power amplifier: drives the chirp into the Tx antenna through a transformer balun.', ['power amplifier']),
    ('lna', 'LNA', 'c', 'rf#lna', 'Low-noise amplifier: first gain stage of the receiver; its noise and gain set the receiver noise figure.', ['low-noise amplifier']),
    ('mixer', 'Mixer + TIA', 'c', 'rf#mixer', 'Passive double-balanced mixer with a transimpedance amplifier: multiplies the echo by the LO to give the IF beat signal.', ['mixer', 'mixers', 'TIA']),
    ('hpf', 'IF filter / HPF', 'c', 'ifadc#hpf', 'High-pass and anti-alias filters in the IF chain: suppress close-in leakage and set the IF band before the ADC.', ['HPF', 'anti-alias', 'IF filter']),
    ('vga', 'VGA / PGA', 'c', 'rf#vga', 'Programmable IF gain amplifier with switched feedback resistors; sets the signal level for the ADC.', ['VGA', 'PGA']),
    ('adc', 'ADC', 'c', 'ifadc#adc', 'Converts the IF beat signal to digital; also used by BIST to measure on-chip detectors.', []),
    ('dfe', 'DFE', 'c', 'sc#dfe', 'Digital front end: decimation, filtering and data formatting before the radar processing.', ['decimation']),
    ('dsp', 'Radar DSP (FFT)', 'c', 'dsp#dsp', 'Range and Doppler FFTs, CFAR detection and angle estimation.', ['FFT', 'CFAR']),
    ('rot', 'Phase rotator', 'c', 'sc#rotator', 'Sets the phase of each Tx channel for beam steering and MIMO coding; built from I/Q vector summing.', ['phase rotator', 'phase shifter']),
    ('dac', 'Rotator DAC', 'c', 'sc#dac-bow', 'Current DACs that weight the I and Q vectors of the phase rotator; their INL/DNL and bow set phase accuracy.', ['DAC', 'DACs']),
    ('pdet', 'Power detector', 'c', 'sc#txpower', 'Diode or square-law detector on the Tx output coupler; its DC output tells the chip the Tx power.', ['power detector', 'PDET']),
    ('pfd', 'PFD + charge pump', 'c', 'pll#blocks', 'Phase-frequency detector and charge pump: compare reference and divided VCO and pump current into the loop filter.', ['PFD', 'charge pump']),
    ('lf', 'Loop filter', 'c', 'pll#blocks', 'RC network that turns charge-pump current into the VCO tuning voltage and sets loop bandwidth and stability.', ['loop filter']),
    ('vco', 'VCO', 'c', 'pll#vco', 'LC-tank voltage-controlled oscillator (about 19–20 GHz, then ×4) with switched-capacitor sub-bands.', ['LC tank', 'varactor']),
    ('div', 'Divider / ΣΔ', 'c', 'pll#blocks', 'Multi-modulus divider driven by a sigma-delta modulator for fractional-N division.', ['divider', 'sigma-delta', 'ΣΔ']),
    ('ramp', 'Ramp generator', 'c', 'pll#pll', 'Digital chirp generator that steps the fractional divide ratio to sweep the frequency.', ['ramp generator', 'chirp generator']),
    ('mult', '×4 multiplier', 'c', 'pll#blocks', 'Frequency multiplier from the VCO band to 76–81 GHz.', ['multiplier', 'quadrupler']),
    ('lod', 'LO distribution', 'c', 'sc#lo', 'Buffers and lines that carry the 77 GHz LO to every Tx rotator and Rx mixer.', ['LO distribution', 'LO buffer']),
    ('ldo', 'LDO', 'c', 'pwr#ldo', 'Low-dropout regulators that give each block a clean, local supply.', ['regulator', 'regulators']),
    ('bg', 'Bandgap', 'c', 'pwr#bg', 'Temperature-stable voltage reference for LDOs, monitors, ADC and bias currents.', ['bandgap', 'reference voltage']),
    ('uvov', 'UV / OV monitor', 'c', 'pwr#uvov', 'Window comparators that flag under- and over-voltage on each supply for functional safety.', ['UV/OV', 'undervoltage', 'overvoltage', 'UV', 'OV']),
    ('por', 'POR & sequencing', 'c', 'pwr#seq', 'Power-on reset and the order in which supplies, references and clocks come up.', ['POR', 'power-on reset', 'sequencing']),
    ('esd', 'ESD diodes', 'c', 'esd#network', 'Protection diodes on every pin; open/short test forward-biases them to check continuity.', ['ESD']),
    ('scan', 'Scan chains', 'c', 'dft#scan', 'Flip-flops linked into shift registers so the digital logic can be controlled and observed by the tester.', ['scan chain', 'scan chains', 'scan']),
    ('mbist', 'Memory BIST', 'c', 'dft#mbist', 'On-chip March-algorithm tester for the radar data memories.', ['MBIST', 'memory BIST']),
    ('lbist', 'Logic BIST', 'c', 'dft#lbist', 'Pseudo-random self-test of the logic, also run in the field at key-on.', ['LBIST', 'logic BIST']),
    ('jtag', 'JTAG / IJTAG', 'c', 'dft#jtag', 'Test access port and instrument network that reach scan, BIST and trim registers.', ['JTAG', 'IJTAG']),
    ('atb', 'Test mux / ATB', 'c', 'bist#mux', 'Analog test muxes and the analog test bus: connect each sub-block node to the aux ADC, main ADC or a test pin.', ['test mux', 'analog test bus', 'ATB', 'MUX']),
    ('lbsw', 'Loopback switches', 'c', 'bist#mux', 'RF SP4T switches and splitter that choose which Tx feeds which Rx in the loopback.', ['loopback switch', 'SP4T', 'SPDT']),
    ('dmux', 'Digital test muxes', 'c', 'dft#muxes', 'Scan, clock, reset, bypass and pin-sharing muxes that test mode controls.', ['clock mux', 'bypass', 'pin-sharing']),
    ('bistc', 'BIST controller', 'c', 'bist#arch', 'On-chip sequencer that sets up loopback paths, runs measurements and compares results with limits.', ['BIST controller', 'BIST engine']),
    # parameters
    ('nf', 'Noise figure', 'p', 'rf#lna', 'How much noise the receiver adds; set mostly by input loss and the LNA (Friis).', ['NF', 'noise figure']),
    ('gain', 'Rx gain', 'p', 'rf#cascade', 'Total receive-chain gain from antenna to ADC; high LNA gain hides later noise.', ['conversion gain', 'Rx gain']),
    ('iip3', 'IIP3 / P1dB', 'p', 'rf#cascade', 'Linearity of the receive chain; late stages (mixer, VGA) usually limit it.', ['IIP3', 'P1dB', 'linearity']),
    ('pout', 'Tx output power', 'p', 'rf#pa', 'Power at the Tx ball, typically 10–14 dBm per channel.', ['output power', 'Tx power', 'Pout', 'Psat']),
    ('pae', 'PAE', 'p', 'rf#pa', 'Power-added efficiency of the PA; sets heat and supply current.', ['efficiency']),
    ('pn', 'Phase noise', 'p', 'pll#specs', 'Noise on the LO phase; limits detection of weak targets next to strong ones.', ['phase noise']),
    ('lin', 'Chirp linearity', 'p', 'pll#specs', 'How straight the frequency ramp is; nonlinearity smears range peaks.', ['chirp linearity', 'linearity error']),
    ('lock', 'Lock time / lock detect', 'p', 'pll#lock', 'How fast the PLL settles and how the chip knows it is locked.', ['lock time', 'lock detect', 'locked']),
    ('kvco', 'KVCO / tuning range', 'p', 'pll#vco', 'VCO gain (MHz/V) and the frequency span of each sub-band.', ['KVCO', 'tuning range', 'sub-band']),
    ('iqimb', 'I/Q imbalance', 'p', 'sc#iq', 'Gain and phase mismatch between I and Q paths; creates image (ghost) targets.', ['I/Q imbalance', 'IQ imbalance', 'image rejection']),
    ('enob', 'ADC SNR / ENOB', 'p', 'ifadc#adc', 'Effective resolution of the ADC; sets the dynamic range at the digital side.', ['ENOB', 'SNDR']),
    ('inl', 'DAC INL / DNL', 'p', 'sc#rotator', 'Linearity of the rotator DACs; bow (2nd-order INL) becomes phase and amplitude error.', ['INL', 'DNL', 'bow']),
    ('psrr', 'PSRR', 'p', 'pwr#ldo', 'How well a regulator or circuit rejects supply noise; poor PSRR shows up as spurs.', ['PSRR', 'ripple']),
    ('drop', 'Dropout / load regulation', 'p', 'pwr#ldo', 'Minimum headroom across the LDO and its output change with load current.', ['dropout', 'load regulation']),
    ('vth', 'Vth', 'p', 'pcm#params', 'Transistor threshold voltage; shifts speed, bias points and leakage.', ['threshold voltage', 'Vt', 'Vtlin', 'Vtsat']),
    ('ft', 'fT / fmax', 'p', 'pcm#small', 'Transistor cut-off and maximum oscillation frequencies; set the headroom at 77 GHz.', ['fT', 'fmax']),
    ('gm', 'gm / Idsat', 'p', 'pcm#large', 'Transconductance and saturation current: the drive strength of the transistor.', ['gm', 'Idsat', 'transconductance']),
    ('ioff', 'Ioff / leakage', 'p', 'pcm#params', 'Off-state transistor current; sets standby and IDDQ baseline.', ['Ioff', 'leakage']),
    ('bv', 'Breakdown voltage', 'p', 'pcm#bv', 'Junction, oxide and drain breakdown limits; cap PA swing and stress-test levels.', ['breakdown', 'BVdss', 'BVox', 'TDDB']),
    ('rs', 'Sheet R / matching', 'p', 'pcm#params', 'Resistor and capacitor values and their matching; set gain steps, filter corners and trim range.', ['sheet resistance', 'matching', 'mismatch']),
    ('cres', 'Contact resistance', 'p', 'cont#cres', 'Probe or socket contact resistance; drifts as needles wear and falsely fails parametric tests.', ['Cres', 'contact resistance']),
    ('range', 'Max range / SNR', 'p', 'sc#spec', 'Detection range from the radar equation: Tx power, antenna gain, NF and integration time.', ['maximum range', 'max range', 'SNR']),
    ('res', 'Range resolution', 'p', 'sc#spec', 'c / 2B: set by the chirp bandwidth.', ['range resolution', 'bandwidth']),
    ('cpk', 'Cpk', 'p', 'pcm#cpk', 'Process capability: distance from the mean to the nearest limit in units of 3σ.', ['Cp', 'Cpk']),
    # tests
    ('os', 'Open / short test', 't','cont#method', 'Forces current into each pin through its ESD diode to find opens and shorts before any other test.', ['open/short', 'continuity']),
    ('walkz', 'Walking-Z', 't', 'cont#walkz', 'Tri-states pins one at a time to find pin-to-pin shorts and leakage.', ['walking-Z', 'walking Z']),
    ('iddq', 'IDDQ', 't', 'dft#iddq', 'Quiescent supply current in several scan states; a raised value reveals bridges and gate-oxide defects.', ['IDDQ', 'quiescent current']),
    ('ats', 'At-speed test', 't', 'dft#atspeed', 'Transition and path-delay scan patterns at the functional clock to catch slow paths.', ['at-speed', 'transition fault', 'path delay']),
    ('stress', 'HVST / burn-in', 't', 'dft#stress', 'High-voltage stress and burn-in accelerate weak oxide and metal defects to failure before shipment.', ['HVST', 'burn-in', 'stress test']),
    ('vlv', 'VLV / Vmin', 't', 'dft#stress', 'Very-low-voltage test: runs logic and memory below nominal supply to expose marginal cells and resistive defects.', ['VLV', 'Vmin']),
    ('loop', 'RF loopback', 't', 'bist#arch', 'Routes the Tx signal back into the Rx on-chip so the whole RF path is tested without mmWave instruments.', ['loopback', 'loop-back']),
    ('bism', 'On-chip measurement', 't', 'bist#meas', 'Detectors, counters and the ADC measure power, frequency, gain and phase inside the chip (BISM).', ['BISM', 'self-measurement']),
    ('trim', 'Trim & calibration', 't', 'bist#feedback', 'Measured errors are written back as trim codes: bandgap, LDO, VCO band, I/Q, phase, gain.', ['trim', 'calibration', 'e-fuse', 'OTP']),
    ('wat', 'PCM / WAT', 't', 'pcm#pcm', 'Scribe-line test structures measured on every wafer before sort: Vth, Idsat, leakage, sheet R, breakdown.', ['WAT', 'PCM', 'scribe']),
    ('spc', 'SPC', 't', 'pcm#spc', 'Control charts and run rules that keep each WAT parameter in control.', ['SPC', 'control chart', 'run rules']),
    ('pat', 'PAT / GDBN', 't', 'dft#stress', 'Outlier screens: part-average testing and good-die-in-bad-neighbourhood removal for zero-defect automotive.', ['PAT', 'GDBN', 'outlier']),
    ('qual', 'AEC-Q100', 't', 'dft#qual', 'Automotive qualification: HTOL, temperature cycling, ESD, latch-up and more.', ['AEC-Q100', 'HTOL', 'qualification']),
    ('flow', 'Production test flow', 't', 'flow#flow', 'The order of test insertions from wafer sort to final test and system test.', ['test flow', 'wafer sort', 'final test']),
    ('bins', 'Fail bins', 't', 'flow#bins', 'Where each failing die is sorted; bin data drives yield analysis.', ['bin', 'bins']),
    # fab & package
    ('corner', 'Corners & mismatch', 'f', 'pcm#corners', 'Process corners (SS/FF/SF/FS) and local mismatch that designs must survive.', ['corner', 'corners', 'Monte Carlo']),
    ('wmap', 'Wafer map signature', 'f', 'wm#maps', 'Spatial patterns of failing die that point to a process tool or setting.', ['wafer map', 'signature']),
    ('cmp', 'CMP', 'f', 'wm#table', 'Chemical-mechanical polishing: centre/edge rings from pad wear, slurry or pressure zones.', ['CMP', 'polishing', 'dishing']),
    ('litho', 'Reticle / litho', 'f', 'wm#table', 'Exposure and reticle issues that repeat in every shot on the wafer.', ['reticle', 'lithography', 'litho']),
    ('ewlb', 'Fan-out (eWLB)', 'f', 'pkg#types', 'Fan-out wafer-level package common for 77 GHz radar: low-loss RDL, no bond wires.', ['eWLB', 'fan-out', 'FOWLP']),
    ('aip', 'Antenna in package', 'f', 'pkg#types', 'Antennas built into the package, removing the PCB RF launch.', ['AiP', 'antenna-in-package', 'launch-on-package']),
    ('rdl', 'RDL', 'f', 'pkg#dims', 'Redistribution layers that route die pads to balls and carry the mmWave transitions.', ['redistribution layer']),
    ('bump', 'Bump / ball', 'f', 'pkg#dims', 'Solder bumps and balls: pitch, height and under-bump metallurgy.', ['bump', 'bumps', 'solder ball', 'BGA']),
    ('solder', 'Solder fatigue', 'f', 'pkg#failures', 'Thermal cycling cracks the solder joints; the leading package failure in automotive.', ['solder fatigue', 'solder joint', 'crack']),
    ('tc', 'Temperature cycling', 'f', 'pkg#detect', 'Cycling −40/+125 °C (or −55/+150 °C) accelerates fatigue and delamination.', ['temperature cycling', 'thermal cycling']),
    # added with the IF/ADC, DSP, safety, ESD, reliability, characterization, yield and regulation pages
    ('aaf', 'Anti-alias filter', 'c', 'ifadc#aaf', 'Low-pass filter before the ADC that stops signals near fs from folding into the band; relaxed with a CT-ΣΔ ADC.', ['AAF', 'anti-alias filter']),
    ('decim', 'Decimation filter', 'c', 'ifadc#decim', 'CIC and half-band FIR stages that turn the ΣΔ bit stream into 16-bit samples at 2× the IF bandwidth.', ['decimation filter', 'CIC', 'half-band']),
    ('efuse', 'eFuse / OTP', 'c', 'otp#cell', 'One-time-programmable bits (poly eFuse, antifuse) that store trim codes, die ID and repair for life.', ['eFuse', 'OTP', 'antifuse', 'fuse']),
    ('shadow', 'Shadow registers', 'c', 'otp#cell', 'Registers loaded from the fuses at boot; they drive the trim DACs and allow soft trim during test.', ['shadow register', 'soft trim']),
    ('acc', 'ACC', 's', 'app#functions', 'Adaptive cruise control: keeps a time gap to the car ahead using the front long-range radar.', ['ACC', 'adaptive cruise']),
    ('aeb', 'AEB', 's', 'app#functions', 'Automatic emergency braking for cars, pedestrians and cyclists, from time-to-collision.', ['AEB', 'emergency braking']),
    ('bsd', 'BSD / LCA', 's', 'app#functions', 'Blind-spot detection and lane-change assist from the rear corner radars.', ['BSD', 'LCA', 'blind spot']),
    ('rcta', 'RCTA / RCTB', 's', 'app#functions', 'Rear cross-traffic alert and braking when reversing.', ['RCTA', 'RCTB', 'cross-traffic']),
    ('img4d', '4D imaging radar', 's', 'app#classes', 'High-channel radar that also measures elevation, for L2+ and L3 driving.', ['4D imaging', 'imaging radar']),
    ('satdet', 'Saturation detector', 'c', 'ifadc#sat', 'Window comparators, peak detectors and ADC over-range flags that report clipping in each receive stage.', ['saturation detector', 'saturation', 'clipping', 'over-range']),
    ('jit', 'Clock jitter', 'p', 'ifadc#adc', 'Timing noise of the ADC clock; limits SNR at high IF frequencies.', ['jitter']),
    ('cube', 'Radar cube memory', 'c', 'dsp#cube', 'On-chip SRAM holding range × chirp × channel data for the Doppler and angle processing.', ['radar cube', 'cube']),
    ('cfar', 'CFAR detection', 's', 'dsp#cfar', 'Adaptive threshold that finds targets at a constant false-alarm rate.', ['CFAR', 'OS-CFAR', 'CA-CFAR']),
    ('angle', 'Angle estimation', 's', 'dsp#angle', 'Direction of arrival over the virtual array: FFT beamforming or super-resolution.', ['angle estimation', 'DoA', 'DBF']),
    ('iface', 'Data interface', 'c', 'dsp#iface', 'CSI-2, automotive Ethernet, SPI or CAN-FD link to the host.', ['CSI-2', 'Ethernet', 'CAN-FD']),
    ('ftti', 'FTTI', 'p', 'fusa#ftti', 'Fault-tolerant time interval: detection and reaction must finish within it.', ['FTTI', 'fault-tolerant time']),
    ('spfm', 'SPFM / LFM / PMHF', 'p', 'fusa#metrics', 'ISO 26262 hardware metrics that the FMEDA must meet for the ASIL.', ['SPFM', 'LFM', 'PMHF', 'FMEDA']),
    ('keyon', 'Key-on tests', 't', 'fusa#keyon', 'Start-up self-tests of logic, memories and the monitors themselves, for latent faults.', ['key-on', 'start-up test']),
    ('clamp', 'ESD power clamp', 'c', 'esd#network', 'RC-triggered large NMOS between supply rails that carries the ESD current.', ['power clamp', 'RC clamp', 'GGNMOS']),
    ('hbm', 'HBM / CDM', 't', 'esd#models', 'ESD qualification stresses: human-body and charged-device models.', ['HBM', 'CDM']),
    ('latch', 'Latch-up', 'f', 'esd#latchup', 'Parasitic thyristor turning on and shorting the supplies.', ['latch-up', 'latchup']),
    ('hci', 'HCI', 'f', 'rel#mech', 'Hot-carrier injection: drain-side damage that lowers gain and output power over life.', ['HCI', 'hot-carrier']),
    ('bti', 'NBTI / PBTI', 'f', 'rel#mech', 'Threshold shift under gate bias at high temperature; slows logic and shifts analog bias.', ['NBTI', 'PBTI', 'BTI']),
    ('tddb', 'TDDB', 'f', 'rel#mech', 'Time-dependent gate-oxide breakdown.', ['TDDB']),
    ('em', 'Electromigration', 'f', 'rel#mech', 'Metal atoms pushed by current density; opens and shorts in supply lines.', ['electromigration', 'EM']),
    ('htol', 'HTOL / FIT', 't', 'rel#accel', 'High-temperature operating life test and the failure rate derived from it.', ['HTOL', 'FIT', 'ELFR']),
    ('mission', 'Mission profile', 's', 'rel#mission', '15-year temperature, voltage and on-time profile that sets the aging and FIT budget.', ['mission profile']),
    ('gband', 'Guard band / test limits', 'p', 'char#gb', 'Margin between spec and test limit for measurement error, temperature and aging.', ['guard band', 'test limit']),
    ('corrl', 'Lab–ATE correlation', 't', 'char#corr', 'Golden units measured in the lab and on the tester to align production results.', ['correlation', 'golden unit']),
    ('grr', 'Gage R&R', 't', 'char#msa', 'Repeatability and reproducibility of the measurement system.', ['GRR', 'MSA']),
    ('dy', 'Die yield (D0)', 'p', 'yield#components', 'Share of good dies, set by defect density and area plus parametric margin.', ['die yield', 'D0', 'defect density']),
    ('dppm', 'DPPM / escapes', 'p', 'yield#dppm', 'Defective parts per million that pass test; automotive goal below 1.', ['DPPM', 'escape', 'escapes']),
    ('syl', 'SYL / SBL', 't', 'yield#limits', 'Statistical yield and bin limits that hold abnormal lots.', ['SYL', 'SBL', 'maverick']),
    ('fa', 'Failure analysis / 8D', 't', 'yield#rma', 'Root-cause analysis of returns and the 8D corrective-action process.', ['8D', 'RMA', 'failure analysis']),
    ('eirp', 'EIRP / band limits', 'p', 'reg#bands', 'Regulatory power and band-edge limits in each market.', ['EIRP', 'ETSI', 'FCC']),
    ('interf', 'Radar interference', 's', 'reg#interf', 'Other radars crossing the chirp; raises the noise floor or creates ghosts.', ['interference', 'interferer']),
    # system
    ('fmcw', 'FMCW chirp', 's', 'sc#chain', 'A linear frequency ramp; the beat frequency between Tx and echo gives range.', ['FMCW', 'chirp', 'chirps']),
    ('beam', 'Beam steering / MIMO', 's', 'sc#rotator', 'Tx phases steer the beam or code the channels so the receiver can separate them (virtual array).', ['beam steering', 'MIMO', 'beamforming']),
    ('txl', 'Tx power loop', 's', 'sc#txpower', 'Detector, ADC and digital control that hold the Tx power constant over temperature and ageing.', ['Tx power loop', 'power control']),
    ('agc', 'AGC', 's', 'sc#if', 'Automatic gain control: picks the VGA gain so strong echoes do not clip the ADC.', ['automatic gain control']),
    ('supply', 'Supply tree', 's', 'pwr#pwr', 'Battery or PMIC rails split into domains and local LDOs.', ['supply tree', 'PMIC', 'power domain']),
    ('safety', 'Functional safety', 's', 'fusa#fusa', 'ISO 26262 / ASIL: in-field monitors and self-tests that detect faults within the fault-tolerant time.', ['ISO 26262', 'ASIL', 'safety mechanism']),
    ('timing', 'Digital timing', 's', 'pcm#digital', 'Setup and hold margins of the logic; corners and mismatch can break them.', ['setup', 'hold time', 'timing']),
]

E = [
    # Rx chain
    ('ant', 'feeds the echo to', 'lna'), ('lna', 'amplifies into', 'mixer'), ('mixer', 'IF output to', 'hpf'),
    ('hpf', 'filters for', 'vga'), ('vga', 'sets the level for', 'adc'), ('adc', 'samples for', 'dfe'), ('dfe', 'decimates for', 'dsp'),
    # LO and Tx chain
    ('vco', 'output is multiplied by', 'mult'), ('mult', 'drives', 'lod'), ('lod', 'LO for', 'mixer'), ('lod', 'LO for', 'rot'),
    ('rot', 'drives', 'pa'), ('pa', 'radiates through', 'ant'), ('dac', 'sets the phase of', 'rot'), ('rot', 'enables', 'beam'),
    ('pa', 'is sampled by', 'pdet'), ('pdet', 'feeds', 'txl'), ('txl', 'adjusts the drive of', 'pa'), ('txl', 'regulates', 'pout'),
    ('pdet', 'is read by', 'adc'),
    # PLL loop
    ('ramp', 'modulates', 'div'), ('div', 'feeds back to', 'pfd'), ('pfd', 'pumps charge into', 'lf'), ('lf', 'tunes', 'vco'),
    ('vco', 'is divided by', 'div'), ('fmcw', 'is generated by', 'ramp'),
    # parameters of circuits
    ('lna', 'dominates', 'nf'), ('lna', 'sets most of', 'gain'), ('mixer', 'contributes to', 'iip3'), ('vga', 'often limits', 'iip3'),
    ('mixer', 'mismatch causes', 'iqimb'), ('lod', 'quadrature error causes', 'iqimb'), ('adc', 'is rated by', 'enob'),
    ('dac', 'is limited by', 'inl'), ('pa', 'sets', 'pout'), ('pa', 'is rated by', 'pae'), ('vco', 'sets far-out', 'pn'),
    ('lf', 'bandwidth sets close-in', 'pn'), ('lf', 'bandwidth sets', 'lock'), ('lf', 'bandwidth limits', 'lin'),
    ('vco', 'is characterised by', 'kvco'), ('ramp', 'determines', 'lin'), ('ldo', 'is rated by', 'psrr'), ('ldo', 'is rated by', 'drop'),
    # system-level consequences
    ('nf', 'limits', 'range'), ('pout', 'sets', 'range'), ('ant', 'loss reduces', 'range'), ('pn', 'masks weak targets, limiting', 'range'),
    ('fmcw', 'bandwidth sets', 'res'), ('lin', 'smears peaks, degrading', 'res'), ('iqimb', 'creates ghost targets in', 'dsp'),
    ('inl', 'becomes phase error in', 'beam'), ('enob', 'limits dynamic range of', 'range'), ('agc', 'controls', 'vga'),
    ('agc', 'prevents clipping in', 'adc'), ('iip3', 'decides when strong echoes need', 'agc'), ('hpf', 'removes close-in leakage before', 'agc'),
    # device parameters
    ('ft', 'limits gain and noise of', 'lna'), ('ft', 'limits output power of', 'pa'), ('ft', 'limits tuning of', 'vco'), ('ft', 'sets the floor of', 'nf'),
    ('gm', 'with Cgs sets', 'ft'), ('vth', 'shifts', 'gm'), ('vth', 'is spread by', 'corner'), ('corner', 'shifts the band of', 'kvco'),
    ('corner', 'can break', 'timing'), ('corner', 'shifts', 'iqimb'), ('ioff', 'sets the baseline of', 'iddq'), ('ioff', 'rises at FF corner in', 'corner'),
    ('rs', 'sets gain steps of', 'vga'), ('rs', 'sets trim range of', 'bg'), ('rs', 'sets corners of', 'hpf'), ('rs', 'mismatch limits', 'inl'),
    ('bv', 'caps the swing of', 'pa'), ('bv', 'sets the level of', 'stress'),
    # fab monitoring
    ('wat', 'measures', 'vth'), ('wat', 'measures', 'ioff'), ('wat', 'measures', 'gm'), ('wat', 'measures', 'rs'), ('wat', 'measures', 'bv'),
    ('wat', 'is modelled for', 'ft'), ('wat', 'is monitored by', 'spc'), ('spc', 'reports capability as', 'cpk'),
    ('wat', 'correlates with', 'wmap'), ('cmp', 'makes rings in', 'wmap'), ('litho', 'makes repeats in', 'wmap'), ('cmp', 'thickness shifts', 'rs'),
    ('litho', 'CD shifts', 'vth'), ('wmap', 'feeds', 'pat'), ('flow', 'starts after', 'wat'),
    # power
    ('supply', 'branches into', 'ldo'), ('bg', 'is the reference for', 'ldo'), ('bg', 'sets thresholds of', 'uvov'), ('uvov', 'reports faults to', 'safety'),
    ('por', 'sequences', 'ldo'), ('por', 'waits for', 'bg'), ('ldo', 'supplies', 'vco'), ('ldo', 'supplies', 'pa'), ('ldo', 'supplies', 'lna'),
    ('psrr', 'supply noise becomes spurs in', 'pn'), ('drop', 'limits headroom of', 'pa'), ('uvov', 'watches', 'supply'),
    # BIST and on-chip measurement
    ('bistc', 'sets up', 'loop'), ('bistc', 'runs', 'bism'), ('loop', 'tests the Rx path of', 'lna'), ('loop', 'tests the Tx path of', 'pa'),
    ('loop', 'checks', 'iqimb'), ('bism', 'uses', 'pdet'), ('bism', 'measures with', 'adc'), ('bism', 'counts the frequency of', 'vco'),
    ('bism', 'result drives', 'trim'), ('trim', 'calibrates', 'dac'), ('trim', 'corrects', 'iqimb'), ('trim', 'trims', 'bg'),
    ('trim', 'selects the sub-band of', 'vco'), ('bism', 'checks', 'lock'), ('bistc', 'provides in-field monitoring for', 'safety'),
    ('lbist', 'provides in-field test for', 'safety'), ('mbist', 'provides in-field test for', 'safety'), ('jtag', 'controls', 'bistc'),
    ('txl', 'is checked by', 'bism'),
    # new pages
    ('hpf', 'feeds', 'aaf'), ('aaf', 'protects', 'adc'), ('adc', 'streams into', 'decim'), ('decim', 'hands samples to', 'dfe'),
    ('jit', 'limits', 'enob'), ('rs', 'sets corners of', 'aaf'), ('dsp', 'reads and writes', 'cube'), ('mbist', 'tests', 'cube'),
    ('dsp', 'runs', 'cfar'), ('dsp', 'runs', 'angle'), ('cfar', 'sets the false-alarm rate for', 'range'), ('angle', 'relies on channel calibration of', 'beam'),
    ('dsp', 'sends the point cloud through', 'iface'), ('safety', 'must react within', 'ftti'), ('safety', 'is proven by', 'spfm'),
    ('keyon', 'finds latent faults for', 'spfm'), ('lbist', 'runs as part of', 'keyon'), ('uvov', 'is self-tested by', 'keyon'),
    ('esd', 'discharges through', 'clamp'), ('hbm', 'stresses', 'clamp'), ('bv', 'sets the design window of', 'clamp'), ('hbm', 'is part of', 'qual'),
    ('latch', 'is tested in', 'qual'), ('esd', 'adds capacitance to the match of', 'lna'),
    ('hci', 'lowers the power of', 'pa'), ('bti', 'shifts', 'vco'), ('bti', 'slows', 'timing'), ('tddb', 'shows up in', 'iddq'), ('em', 'limits current in', 'ldo'),
    ('htol', 'accelerates', 'hci'), ('htol', 'accelerates', 'bti'), ('mission', 'sets the stress of', 'htol'), ('htol', 'is part of', 'qual'), ('bv', 'sets the TDDB margin for', 'tddb'),
    ('gband', 'protects', 'dppm'), ('corrl', 'sets the uncertainty in', 'gband'), ('grr', 'feeds', 'gband'), ('gband', 'uses the spread from', 'cpk'),
    ('bism', 'is aligned to the lab by', 'corrl'), ('dy', 'is lost in', 'bins'), ('wmap', 'explains', 'dy'), ('pat', 'reduces', 'dppm'),
    ('syl', 'holds lots flagged by', 'bins'), ('fa', 'feeds corrective action into', 'flow'), ('dppm', 'is investigated by', 'fa'),
    ('eirp', 'caps', 'pout'), ('lin', 'keeps the chirp inside', 'eirp'), ('interf', 'raises the noise floor for', 'cfar'), ('interf', 'is detected in', 'dfe'),
    ('ramp', 'randomises chirps against', 'interf'),
    ('trim', 'stores codes in', 'efuse'), ('efuse', 'loads at boot into', 'shadow'), ('shadow', 'sets', 'bg'), ('shadow', 'sets', 'ldo'),
    ('em', 'is the mechanism that programs', 'efuse'), ('tddb', 'is the mechanism of antifuse', 'efuse'), ('keyon', 'checks the CRC of', 'efuse'),
    ('mbist', 'stores repair addresses in', 'efuse'), ('htol', 'qualifies retention of', 'efuse'),
    ('acc', 'needs long', 'range'), ('acc', 'assigns lanes with', 'angle'), ('aeb', 'must react within', 'ftti'), ('aeb', 'needs fine', 'res'),
    ('aeb', 'detects with', 'cfar'), ('bsd', 'needs wide-FoV', 'ant'), ('rcta', 'needs wide-angle', 'angle'), ('img4d', 'needs many channels for', 'beam'),
    ('img4d', 'streams data through', 'iface'), ('interf', 'degrades', 'aeb'), ('safety', 'covers', 'aeb'), ('satdet', 'protects pedestrian detection in', 'aeb'),
    ('satdet', 'flags clipping in', 'adc'), ('satdet', 'watches the output of', 'vga'), ('satdet', 'tells', 'agc'), ('satdet', 'reports a blind receiver to', 'safety'),
    ('interf', 'trips', 'satdet'), ('keyon', 'self-tests', 'satdet'), ('iip3', 'sets the level that trips', 'satdet'),
    # test muxes
    ('bistc', 'sets the selects of', 'atb'), ('atb', 'brings nodes to', 'adc'), ('atb', 'reads', 'bg'), ('atb', 'reads', 'ldo'),
    ('atb', 'reads the tuning voltage of', 'vco'), ('atb', 'reads', 'pdet'), ('atb', 'copies the bias current of', 'lna'),
    ('ioff', 'leakage limits the accuracy of', 'atb'), ('atb', 'is locked off in the field for', 'safety'), ('bism', 'is routed by', 'atb'),
    ('loop', 'is routed by', 'lbsw'), ('lbsw', 'taps the output of', 'pa'),
    ('dmux', 'builds', 'scan'), ('dmux', 'switches the test clocks for', 'ats'), ('dmux', 'brings out', 'lock'), ('jtag', 'sets', 'dmux'),
    # digital test
    ('jtag', 'accesses', 'scan'), ('scan', 'tests the logic for', 'timing'), ('ats', 'uses', 'scan'), ('ats', 'catches slow paths in', 'timing'),
    ('iddq', 'uses scan states from', 'scan'), ('vlv', 'finds marginal', 'timing'), ('stress', 'is followed by', 'pat'), ('lbist', 'reuses', 'scan'),
    ('stress', 'accelerates oxide defects seen by', 'iddq'),
    # continuity
    ('os', 'forward-biases', 'esd'), ('walkz', 'extends', 'os'), ('os', 'is guarded by', 'cres'), ('os', 'finds opens in', 'bump'),
    ('flow', 'begins with', 'os'), ('flow', 'runs', 'scan'), ('flow', 'runs', 'loop'), ('flow', 'sorts dies into', 'bins'),
    ('flow', 'includes', 'stress'), ('pat', 'moves outliers into', 'bins'), ('cres', 'is logged per', 'bins'),
    # package
    ('ewlb', 'routes through', 'rdl'), ('rdl', 'connects to', 'bump'), ('bump', 'fails by', 'solder'), ('tc', 'accelerates', 'solder'),
    ('aip', 'integrates', 'ant'), ('aip', 'is built on', 'ewlb'), ('rdl', 'transition loss reduces', 'range'), ('qual', 'includes', 'tc'),
    ('qual', 'includes', 'stress'), ('ewlb', 'is qualified by', 'qual'),
]


def _href_ok(docs_read, page, anchor):
    return re.search(r'id="%s"' % re.escape(anchor), docs_read(PAGES[page][0])) is not None


def _mentions(docs_read, nodes):
    """Where each node's label/aliases appear, per section or h3 subsection of every other page."""
    blocks = []  # (page key, anchor, heading, text)
    for k, (f, _) in PAGES.items():
        soup = BeautifulSoup(docs_read(f), 'html.parser')
        for sec in soup.select('main section'):
            sid = sec.get('id') or ''
            if sid == 'glossary':
                continue
            h2 = sec.find('h2')
            cur = [sid, h2.get_text(' ', strip=True) if h2 else sid, []]
            parts = [cur]
            for el in sec.children:
                if getattr(el, 'name', None) == 'h3' and el.get('id'):
                    cur = [el['id'], el.get_text(' ', strip=True), []]
                    parts.append(cur)
                elif getattr(el, 'name', None) not in (None, 'script', 'style'):
                    cur[2].append(el.get_text(' '))
            for a, h, t in parts:
                blocks.append((k, a, h, re.sub(r'\s+', ' ', ' '.join(t))))
    out = {}
    for n in nodes:
        terms = [n[1]] + n[5]
        pats = []
        for t in terms:
            flags = 0 if t == t.upper() or len(t) <= 4 else re.I
            pats.append(re.compile(r'(?<![\w-])%s(?![\w-])' % re.escape(t), flags))
        hits = []
        for k, a, h, t in blocks:
            c = sum(len(p.findall(t)) for p in pats)
            if c and '%s#%s' % (k, a) != n[3]:
                hits.append((c, k, a, h))
        hits.sort(key=lambda x: -x[0])
        out[n[0]] = [[k, a, h, c] for c, k, a, h in hits[:8]]
    return out


def _esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def refresh(docs_read, docs_write):
    ids = [n[0] for n in N]
    assert len(ids) == len(set(ids)), 'duplicate node id'
    tkeys = [t for t, _ in TYPES]
    for n in N:
        assert n[2] in tkeys, n
    nodes = N
    for n in nodes:
        p, a = n[3].split('#')
        assert p in PAGES and _href_ok(docs_read, p, a), 'graph: bad link %s for %s' % (n[3], n[0])
    seen = set()
    for a, r, b in E:
        assert a in ids and b in ids, 'graph: unknown node in edge %s' % ((a, r, b),)
        assert (a, b) not in seen, 'graph: duplicate edge %s → %s' % (a, b)
        seen.add((a, b))
    men = _mentions(docs_read, nodes)
    data = {'types': TYPES, 'pt': {k: t for k, (_, t) in PAGES.items()},
            'nodes': [{'id': n[0], 'l': n[1], 't': n[2], 'h': n[3], 'd': n[4], 'm': men[n[0]]} for n in nodes],
            'edges': [[a, r, b] for a, r, b in E]}
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    lab = {n[0]: n[1] for n in nodes}
    tname = dict(TYPES)
    pages = ''.join('<a data-p="%s" href="%s"></a>' % (k, f) for k, (f, _) in PAGES.items())
    rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (_esc(lab[a]), _esc(r), _esc(lab[b])) for a, r, b in E)
    items = ''.join('<tr><td><a href="%s#%s">%s</a></td><td>%s</td><td>%s</td></tr>'
                    % (PAGES[n[3].split('#')[0]][0], n[3].split('#')[1], _esc(n[1]), tname[n[2]], _esc(n[4])) for n in nodes)
    s = docs_read(GRAPH)
    rep = [
        ('graph-data', '<script type="application/json" id="gData">%s</script>' % blob),
        ('graph-pages', '<div id="gPages" hidden>%s</div>' % pages),
        ('graph-count', '%d items and %d connections' % (len(nodes), len(E))),
        ('graph-items', '<tbody>%s</tbody>' % items),
        ('graph-table', '<tbody>%s</tbody>' % rows),
    ]
    for k, v in rep:
        s, c = re.subn(r'<!--%s-->.*?<!--/%s-->' % (k, k), lambda m: '<!--%s-->%s<!--/%s-->' % (k, v, k), s, count=1, flags=re.S)
        assert c == 1, 'graph page marker %s missing' % k
    docs_write(GRAPH, s)
    return len(nodes), len(E)
