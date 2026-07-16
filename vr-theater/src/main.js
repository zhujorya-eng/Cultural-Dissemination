import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { KunquStage } from './stage.js';
import { getScene } from './subtitles.js';

class KunquVRTheater {
  constructor() {
    this.canvas = document.getElementById('canvas');
    this.loading = document.getElementById('loading');
    this.hud = document.getElementById('hud');

    this.sceneIndex = 0;
    this.lineIndex = 0;
    this.lang = 'both';
    this.subtitlesOn = true;
    this.lineTimer = 0;
    this.lineInterval = 6;

    this.initRenderer();
    this.initScene();
    this.initControls();
    this.initUI();
    this.applyScene(0);
    this.animate();

    this.loading.classList.add('hidden');
    this.hud.classList.remove('hidden');
  }

  initRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: false,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.xr.enabled = true;

    document.body.appendChild(VRButton.createButton(this.renderer));

    window.addEventListener('resize', () => this.onResize());
  }

  initScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0d0908);
    this.scene.fog = new THREE.FogExp2(0x0d0908, 0.035);

    this.camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      100,
    );
    this.camera.position.set(0, 2.2, 7);

    const ambient = new THREE.AmbientLight(0x403020, 0.4);
    this.scene.add(ambient);

    const hemi = new THREE.HemisphereLight(0xffe8c0, 0x1a1008, 0.35);
    this.scene.add(hemi);

    this.stage = new KunquStage();
    this.stage.attachSpotLight(this.scene);
    this.scene.add(this.stage.group);

    this.vrRig = new THREE.Group();
    this.vrRig.position.set(0, 0, 5);
    this.scene.add(this.vrRig);
  }

  initControls() {
    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.target.set(0, 1.5, -1);
    this.controls.maxPolarAngle = Math.PI * 0.48;
    this.controls.minDistance = 3;
    this.controls.maxDistance = 14;

    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space') {
        e.preventDefault();
        this.stage.toggleCurtain();
      }
    });
  }

  initUI() {
    const btnVr = document.getElementById('btn-vr');
    btnVr.addEventListener('click', () => {
      const vrBtn = document.querySelector('#VRButton');
      if (vrBtn) vrBtn.click();
    });

    document.getElementById('btn-lang').addEventListener('click', (e) => {
      const modes = ['both', 'zh', 'en'];
      const idx = (modes.indexOf(this.lang) + 1) % modes.length;
      this.lang = modes[idx];
      e.target.textContent = this.lang === 'both' ? '双语' : this.lang.toUpperCase();
      this.updateSubtitleDisplay();
    });

    document.getElementById('btn-sub').addEventListener('click', (e) => {
      this.subtitlesOn = !this.subtitlesOn;
      e.target.classList.toggle('active', this.subtitlesOn);
      document.getElementById('subtitle-panel').classList.toggle('hidden', !this.subtitlesOn);
    });

    document.querySelectorAll('.tab').forEach((tab) => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        this.applyScene(Number(tab.dataset.scene));
      });
    });
  }

  applyScene(index) {
    this.sceneIndex = index;
    this.lineIndex = 0;
    this.lineTimer = 0;
    const data = getScene(index);
    this.stage.setSceneColors(data.stageColor, data.lightColor);
    this.updateSubtitleDisplay();
  }

  updateSubtitleDisplay() {
    const data = getScene(this.sceneIndex);
    const line = data.lines[this.lineIndex];

    document.getElementById('emotion-tag').textContent =
      `${data.emotion.en} · ${data.emotion.zh}`;

    const cnEl = document.getElementById('subtitle-cn');
    const enEl = document.getElementById('subtitle-en');
    const noteEl = document.getElementById('subtitle-note');

    cnEl.style.display = this.lang === 'en' ? 'none' : 'block';
    enEl.style.display = this.lang === 'zh' ? 'none' : 'block';

    cnEl.textContent = line.cn;
    enEl.textContent = line.en;
    noteEl.textContent = `《${data.title.zh}》— ${line.note}`;
  }

  advanceLine(delta) {
    this.lineTimer += delta;
    if (this.lineTimer >= this.lineInterval) {
      this.lineTimer = 0;
      const data = getScene(this.sceneIndex);
      this.lineIndex = (this.lineIndex + 1) % data.lines.length;
      this.updateSubtitleDisplay();
    }
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  animate() {
    this.renderer.setAnimationLoop((time, frame) => {
      const delta = 0.016;
      const t = time * 0.001;

      this.stage.update(t, delta);
      this.advanceLine(delta);

      const inVR = this.renderer.xr.isPresenting;
      this.controls.enabled = !inVR;

      if (!inVR) {
        this.controls.update();
      }

      this.renderer.render(this.scene, this.camera);
    });
  }
}

new KunquVRTheater();
