export class AudioManager {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.ambientNodes = [];
    this.enabled = false;
  }

  async init() {
    if (this.ctx) return;
    this.ctx = new AudioContext();
    this.master = this.ctx.createGain();
    this.master.gain.value = 0.6;
    this.master.connect(this.ctx.destination);
    this.enabled = true;
  }

  async resume() {
    await this.init();
    if (this.ctx.state === 'suspended') await this.ctx.resume();
  }

  playPipaNote(index = 0) {
    if (!this.enabled) return;
    const freqs = [293.66, 329.63, 369.99, 392.0, 440.0, 493.88];
    const freq = freqs[index % freqs.length];
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.001, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.35, this.ctx.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 1.2);
    osc.connect(gain);
    gain.connect(this.master);
    osc.start();
    osc.stop(this.ctx.currentTime + 1.3);
  }

  playDrum() {
    if (!this.enabled) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(180, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(60, this.ctx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.5, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.4);
    osc.connect(gain);
    gain.connect(this.master);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.45);
  }

  playVoiceTone() {
    if (!this.enabled) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(520, this.ctx.currentTime);
    osc.frequency.linearRampToValueAtTime(680, this.ctx.currentTime + 0.8);
    gain.gain.setValueAtTime(0.001, this.ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.12, this.ctx.currentTime + 0.1);
    gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 1.5);
    osc.connect(gain);
    gain.connect(this.master);
    osc.start();
    osc.stop(this.ctx.currentTime + 1.6);
  }

  startAmbient(type = 'opera') {
    this.stopAmbient();
    if (!this.enabled) return;

    const configs = {
      opera: { freq: 110, mod: 0.08, filter: 400 },
      tea: { freq: 146, mod: 0.05, filter: 600 },
      garden: { freq: 98, mod: 0.06, filter: 350 },
      digital: { freq: 220, mod: 0.12, filter: 800 },
      mr: { freq: 130, mod: 0.03, filter: 500 },
    };
    const cfg = configs[type] || configs.opera;

    const osc = this.ctx.createOscillator();
    const lfo = this.ctx.createOscillator();
    const lfoGain = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = cfg.freq;
    lfo.type = 'sine';
    lfo.frequency.value = 0.15;
    lfoGain.gain.value = cfg.freq * cfg.mod;
    filter.type = 'lowpass';
    filter.frequency.value = cfg.filter;
    gain.gain.value = 0.08;

    lfo.connect(lfoGain);
    lfoGain.connect(osc.frequency);
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.master);

    osc.start();
    lfo.start();
    this.ambientNodes.push(osc, lfo);
  }

  stopAmbient() {
    this.ambientNodes.forEach((n) => {
      try {
        n.stop();
      } catch {
        /* already stopped */
      }
    });
    this.ambientNodes = [];
  }
}
