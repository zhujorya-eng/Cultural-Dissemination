import * as THREE from 'three';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { XRControllerModelFactory } from 'three/examples/jsm/webxr/XRControllerModelFactory.js';
import { AudioManager } from './core/AudioManager.js';
import { HUD } from './ui/HUD.js';
import {
  createPetals,
  updatePetals,
  createChineseStage,
  createPipa,
  createPerformer,
  createTeaHouse,
  createGarden,
  createDigitalTheater,
  createScroll,
  createStageFrame,
} from './utils/sceneAssets.js';

const SCENES = [
  { id: 'mr-open', name: 'MR 开场', mode: '混合现实', progress: 0 },
  { id: 'opera', name: '清代戏园', mode: '纯 VR', progress: 16 },
  { id: 'tea', name: '民国茶楼', mode: '纯 VR', progress: 33 },
  { id: 'garden', name: '园林实景', mode: '纯 VR', progress: 50 },
  { id: 'digital', name: '数字剧场', mode: '纯 VR', progress: 66 },
  { id: 'mr-close', name: 'MR 结尾', mode: '混合现实', progress: 100 },
];

export class TheaterApp {
  constructor(canvas) {
    this.canvas = canvas;
    this.clock = new THREE.Clock();
    this.audio = new AudioManager();
    this.hud = new HUD(document.getElementById('hud'));

    this.stats = {
      interactions: 0,
      scenesUnlocked: 0,
      startTime: null,
      performance: 0,
    };

    this.currentSceneIndex = 0;
    this.started = false;
    this.interactiveObjects = [];
    this.petals = null;
    this.performer = null;
    this.videoTexture = null;
    this.videoEl = null;
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.moveState = { forward: false, backward: false, left: false, right: false };
    this.velocity = new THREE.Vector3();
    this.isPointerLocked = false;
    this.config = {
      narrative: 'interactive',
      immersion: 'participatory',
      interpretation: 'npc-guided',
    };

    this.initRenderer();
    this.initScene();
    this.initCamera();
    this.initLights();
    this.initXR();
    this.bindEvents();
    this.bindHUD();
    this.animate();
  }

  initRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.shadowMap.enabled = true;
    this.renderer.xr.enabled = true;
    document.body.appendChild(VRButton.createButton(this.renderer));
  }

  initScene() {
    this.scene = new THREE.Group();
    this.world = new THREE.Scene();
    this.world.add(this.scene);
    this.world.background = new THREE.Color(0x0a0608);
    this.world.fog = new THREE.FogExp2(0x0a0608, 0.035);
  }

  initCamera() {
    this.camera = new THREE.PerspectiveCamera(
      70,
      window.innerWidth / window.innerHeight,
      0.1,
      100
    );
    this.camera.position.set(0, 1.6, 6);
  }

  initLights() {
    this.ambient = new THREE.AmbientLight(0xfff0e0, 0.4);
    this.world.add(this.ambient);
    this.keyLight = new THREE.DirectionalLight(0xffe4c4, 1.2);
    this.keyLight.position.set(5, 10, 5);
    this.keyLight.castShadow = true;
    this.world.add(this.keyLight);
  }

  initXR() {
    this.controllerModelFactory = new XRControllerModelFactory();
    this.controllers = [];

    for (let i = 0; i < 2; i++) {
      const controller = this.renderer.xr.getController(i);
      controller.addEventListener('selectstart', () => this.onXRSelect(controller));
      this.world.add(controller);

      const grip = this.renderer.xr.getControllerGrip(i);
      grip.add(
        this.controllerModelFactory.createControllerModel(grip)
      );
      this.world.add(grip);
      this.controllers.push(controller);
    }
  }

  bindEvents() {
    window.addEventListener('resize', () => this.onResize());
    document.addEventListener('keydown', (e) => this.onKey(e, true));
    document.addEventListener('keyup', (e) => this.onKey(e, false));
    document.addEventListener('click', (e) => this.onClick(e));
    document.addEventListener('mousemove', (e) => this.onMouseMove(e));
    document.addEventListener('pointerlockchange', () => {
      this.isPointerLocked = document.pointerLockElement === this.canvas;
    });
  }

  bindHUD() {
    this.hud.onAction = (action) => {
      if (action === 'start') this.startExperience();
      if (action === 'vr') this.renderer.xr.getSession()?.end();
      if (action === 'help') this.showHelp();
      if (action === 'restart') this.restart();
    };
    this.hud.onChoice = (choice) => this.handleChoice(choice);

    this.hud.showSubtitle({
      text: '欢迎来到昆曲 VR 剧场。点击「开始体验」，开启 MR-VR-MR 虚实之旅。',
      hint: '桌面端：点击画面锁定鼠标 · WASD 移动 · 点击物体交互 · 支持 WebXR VR 头显',
    });
  }

  showHelp() {
    this.hud.showSubtitle({
      speaker: '操作说明',
      text: 'WASD 移动 · 鼠标环顾 · 点击交互对象（琵琶、茶席、演员、游园帖）',
      hint: 'VR 模式：使用手柄射线选择 · 体验含六个场景自动切换',
      duration: 8000,
    });
  }

  async startExperience() {
    await this.audio.resume();
    this.hud.setStarted();
    this.started = true;
    this.stats.startTime = Date.now();
    this.stats.interactions = 0;
    this.stats.scenesUnlocked = 0;
    this.stats.performance = 0;
    this.currentSceneIndex = 0;
    await this.loadScene(0);
    this.canvas.requestPointerLock?.();
  }

  restart() {
    this.clearScene();
    this.startExperience();
  }

  async loadScene(index) {
    this.clearScene();
    this.currentSceneIndex = index;
    const meta = SCENES[index];
    this.hud.setScene(meta.name, meta.mode);
    this.hud.setProgress(meta.progress);
    this.hud.hideChoices();

    switch (meta.id) {
      case 'mr-open':
        await this.buildMROpening();
        break;
      case 'opera':
        await this.buildOperaGarden();
        break;
      case 'tea':
        await this.buildTeaHouse();
        break;
      case 'garden':
        await this.buildGarden();
        break;
      case 'digital':
        await this.buildDigitalTheater();
        break;
      case 'mr-close':
        await this.buildMRClose();
        break;
    }

    if (index > 0 && index < 5) {
      this.stats.scenesUnlocked = Math.max(this.stats.scenesUnlocked, index);
      this.updateStatsDisplay();
    }
  }

  clearScene() {
    while (this.scene.children.length) {
      const child = this.scene.children[0];
      this.scene.remove(child);
      child.traverse?.((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (Array.isArray(obj.material)) obj.material.forEach((m) => m.dispose());
          else obj.material.dispose();
        }
      });
    }
    this.interactiveObjects = [];
    this.petals = null;
    this.performer = null;
    this.audio.stopAmbient();
  }

  async setupWebcamBackground() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      });
      this.videoEl = document.createElement('video');
      this.videoEl.srcObject = stream;
      this.videoEl.playsInline = true;
      await this.videoEl.play();
      this.videoTexture = new THREE.VideoTexture(this.videoEl);
      this.videoTexture.colorSpace = THREE.SRGBColorSpace;
      this.world.background = this.videoTexture;
      this.world.fog = null;
    } catch {
      this.world.background = new THREE.Color(0x1a1018);
      this.world.fog = new THREE.FogExp2(0x1a1018, 0.02);
    }
  }

  async buildMROpening() {
    await this.setupWebcamBackground();
    this.audio.startAmbient('mr');
    this.camera.position.set(0, 1.6, 0);

    const frame = createStageFrame();
    this.scene.add(frame);

    this.petals = createPetals(40);
    this.scene.add(this.petals);

    const scroll = createScroll();
    scroll.position.set(0, 1.4, -1.5);
    scroll.userData.onInteract = () => this.onScrollTaken();
    this.scene.add(scroll);
    this.interactiveObjects.push(scroll);

    this.hud.showSubtitle({
      speaker: '引路人 · 杜丽娘',
      text: '请接取「游园帖」，穿越百年昆曲流变。',
      hint: '点击发光的游园帖进入 VR 戏园',
    });
  }

  onScrollTaken() {
    this.recordInteraction('接取游园帖', 10);
    this.hud.showToast('已接取游园帖');
    setTimeout(() => this.nextScene(), 1500);
  }

  async buildOperaGarden() {
    this.world.background = new THREE.Color(0x120810);
    this.world.fog = new THREE.FogExp2(0x120810, 0.025);
    this.audio.startAmbient('opera');
    this.camera.position.set(0, 1.6, 5);

    const stage = createChineseStage();
    this.scene.add(stage);

    this.performer = createPerformer();
    this.performer.position.set(0, 0, -2);
    this.scene.add(this.performer);

    const pipa = createPipa();
    pipa.position.set(1.2, 1, 2);
    pipa.rotation.y = -0.6;
    pipa.userData.onInteract = () => this.onPipaPlay();
    this.scene.add(pipa);
    this.interactiveObjects.push(pipa);

    this.petals = createPetals(60);
    this.scene.add(this.petals);

    this.hud.showSubtitle({
      speaker: '清代戏园 · 1790s',
      text: '《牡丹亭》正在上演。你可拨弄琵琶为演出伴奏。',
      hint: '点击琵琶弦 · 按 N 进入下一场景',
    });

    if (this.config.interpretation === 'npc-guided') {
      setTimeout(() => {
        this.hud.showSubtitle({
          speaker: '文化讲解',
          text: '昆班行会制度：清代昆曲以苏州为中心，戏园是市民文化核心空间。',
          duration: 6000,
        });
      }, 4000);
    }
  }

  onPipaPlay() {
    const note = this.stats.interactions % 6;
    this.audio.playPipaNote(note);
    this.audio.playDrum();
    this.recordInteraction('琵琶伴奏', 8);
    this.hud.showToast(`琵琶伴奏 · 第 ${note + 1} 弦`);

    if (this.performer) {
      this.performer.children
        .filter((c) => c.name === 'sleeve')
        .forEach((sleeve, i) => {
          sleeve.rotation.z = i === 0 ? 0.6 : -0.6;
          setTimeout(() => {
            sleeve.rotation.z = 0;
          }, 800);
        });
    }
  }

  async buildTeaHouse() {
    this.world.background = new THREE.Color(0x1a1410);
    this.world.fog = new THREE.FogExp2(0x1a1410, 0.028);
    this.audio.startAmbient('tea');
    this.camera.position.set(0, 1.6, 5);

    const house = createTeaHouse();
    this.scene.add(house);

    house.userData.seats.forEach((seat) => {
      seat.userData.onInteract = () => this.onSeatSelect(seat);
      this.interactiveObjects.push(seat);
      seat.traverse((c) => {
        if (c.userData?.type === 'tea') {
          c.userData.onInteract = () => this.onTeaDrink();
          this.interactiveObjects.push(c);
        }
      });
    });

    this.hud.showSubtitle({
      speaker: '民国茶楼 · 1920s',
      text: '江南茶楼，昆曲与评弹并置。请选择茶席入座。',
      hint: '点击茶桌就座 · 点击茶盏品茗',
    });

    if (this.config.narrative === 'interactive') {
      setTimeout(() => {
        this.hud.showChoices([
          { label: '入座观戏', action: 'watch' },
          { label: '走向后台', action: 'backstage' },
        ]);
      }, 3000);
    }
  }

  handleChoice(choice) {
    if (choice.action === 'watch') {
      this.hud.showSubtitle({ text: '你选择了入座观戏，沉浸于折子戏演出。', duration: 4000 });
    } else if (choice.action === 'backstage') {
      this.recordInteraction('后台探索', 12);
      this.hud.showSubtitle({
        text: '后台：妆造与行头整理，昆曲"生旦净丑"行当一目了然。',
        duration: 5000,
      });
    } else if (choice.action === 'duet') {
      this.onDuet();
    } else if (choice.action === 'decline') {
      this.hud.showSubtitle({ text: '你静静欣赏《游园·惊梦》的水磨腔。', duration: 4000 });
    }
  }

  onSeatSelect(seat) {
    this.recordInteraction(`就座·${seat.userData.label}`, 5);
    this.camera.position.copy(seat.userData.cameraPos);
    this.hud.showToast(`已就座：${seat.userData.label}`);
    this.audio.playDrum();
  }

  onTeaDrink() {
    this.recordInteraction('品茗', 3);
    this.hud.showToast('茶香袅袅，边品茗边看戏');
  }

  async buildGarden() {
    this.world.background = new THREE.Color(0x0a1810);
    this.world.fog = new THREE.FogExp2(0x0a1810, 0.02);
    this.audio.startAmbient('garden');
    this.camera.position.set(0, 1.6, 8);

    const garden = createGarden();
    this.scene.add(garden);

    garden.traverse((obj) => {
      if (obj.userData?.interactive) {
        if (obj.userData.type === 'duet') {
          obj.userData.onInteract = () => this.promptDuet();
        }
        if (obj.userData.type === 'bridge') {
          obj.userData.onInteract = () => {
            this.recordInteraction('曲桥漫游', 4);
            this.hud.showToast('曲径通幽');
          };
        }
        this.interactiveObjects.push(obj);
      }
    });

    this.petals = createPetals(50);
    this.scene.add(this.petals);

    this.hud.showSubtitle({
      speaker: '园林实景 · 《游园·惊梦》',
      text: '亭榭水榭，天然舞台。杜丽娘正在梦中游园…',
      hint: '点击演员参与对唱 · 按 N 继续',
    });
  }

  promptDuet() {
    if (this.config.immersion === 'passive') {
      this.hud.showSubtitle({ text: '（纯观赏模式）静观杜丽娘游园唱段。', duration: 4000 });
      return;
    }
    this.hud.showChoices([
      { label: '参与对唱', action: 'duet' },
      { label: '静静欣赏', action: 'decline' },
    ]);
  }

  onDuet() {
    this.audio.playVoiceTone();
    this.recordInteraction('惊梦对唱', 15);
    this.hud.showToast('「不到园林，怎知春色如许」');
    this.hud.showSubtitle({
      speaker: '双轨表演',
      text: '你成为了梦中人，与杜丽娘虚实融合，共唱《游园·惊梦》。',
      duration: 5000,
    });
  }

  async buildDigitalTheater() {
    this.world.background = new THREE.Color(0x050208);
    this.world.fog = new THREE.FogExp2(0x050208, 0.015);
    this.audio.startAmbient('digital');
    this.camera.position.set(0, 2, 10);

    const theater = createDigitalTheater();
    this.scene.add(theater);

    theater.userData.particles.userData.onInteract = () => {
      this.recordInteraction('驱动粒子', 6);
      this.hud.showToast('唱腔化为粒子流');
    };
    this.interactiveObjects.push(theater.userData.particles);

    this.hud.showSubtitle({
      speaker: '数字剧场 · 2020s',
      text: '水袖化为光带，昆曲进入数字传承时代。移动鼠标驱动意象变形。',
      hint: '点击粒子群 · 按 N 进入 MR 结尾',
    });
  }

  async buildMRClose() {
    await this.setupWebcamBackground();
    this.audio.startAmbient('mr');
    this.camera.position.set(0, 1.6, 0);

    const frame = createStageFrame();
    frame.scale.set(0.8, 0.8, 0.8);
    this.scene.add(frame);

    const scroll = createScroll();
    scroll.position.set(-0.8, 1.2, -1.2);
    scroll.rotation.y = 0.3;
    this.scene.add(scroll);

    setTimeout(() => {
      const time = this.formatTime(Date.now() - this.stats.startTime);
      this.hud.hideSubtitle();
      this.hud.showImprintCard({
        time,
        interactions: this.stats.interactions,
        scenes: this.stats.scenesUnlocked,
        performance: Math.min(100, this.stats.performance),
      });
    }, 2000);

    this.hud.showSubtitle({
      speaker: '引路人',
      text: '体验结束，虚拟道具留存于现实。你的昆曲印记已生成。',
      duration: 4000,
    });
  }

  recordInteraction(label, perfPoints) {
    this.stats.interactions += 1;
    this.stats.performance = Math.min(100, this.stats.performance + perfPoints);
    this.updateStatsDisplay();
  }

  updateStatsDisplay() {
    const elapsed = this.stats.startTime
      ? Date.now() - this.stats.startTime
      : 0;
    this.hud.updateStats({
      interactions: this.stats.interactions,
      scenes: this.stats.scenesUnlocked,
      time: this.formatTime(elapsed),
    });
  }

  formatTime(ms) {
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    return `${m}:${String(s % 60).padStart(2, '0')}`;
  }

  nextScene() {
    if (this.currentSceneIndex < SCENES.length - 1) {
      this.loadScene(this.currentSceneIndex + 1);
    }
  }

  onKey(e, down) {
    if (!this.started) return;
    const map = {
      KeyW: 'forward',
      KeyS: 'backward',
      KeyA: 'left',
      KeyD: 'right',
    };
    if (map[e.code]) this.moveState[map[e.code]] = down;
    if (down && e.code === 'KeyN') this.nextScene();
  }

  onMouseMove(e) {
    if (!this.isPointerLocked || this.renderer.xr.isPresenting) return;
    this.camera.rotation.order = 'YXZ';
    this.camera.rotation.y -= e.movementX * 0.002;
    this.camera.rotation.x -= e.movementY * 0.002;
    this.camera.rotation.x = Math.max(-1.2, Math.min(1.2, this.camera.rotation.x));
  }

  onClick(e) {
    if (!this.started || e.target.closest('#hud')) return;
    if (!this.isPointerLocked) {
      this.canvas.requestPointerLock?.();
      return;
    }
    this.pointer.x = 0;
    this.pointer.y = 0;
    this.tryInteract(this.camera);
  }

  onXRSelect(controller) {
    if (!this.started) return;
    this.raycaster.setFromXRController(controller);
    this.tryInteract(null, controller);
  }

  tryInteract(fallbackCamera, controller) {
    if (controller) {
      const hits = this.raycaster.intersectObjects(this.interactiveObjects, true);
      if (hits.length) {
        this.triggerInteract(hits[0].object);
        return;
      }
    } else {
      this.raycaster.setFromCamera(this.pointer, this.camera);
      const hits = this.raycaster.intersectObjects(this.interactiveObjects, true);
      if (hits.length) this.triggerInteract(hits[0].object);
    }
  }

  triggerInteract(object) {
    let target = object;
    while (target && !target.userData?.onInteract) {
      target = target.parent;
    }
    target?.userData?.onInteract?.();
  }

  updateMovement(delta) {
    if (this.renderer.xr.isPresenting) return;
    const speed = 2.5 * delta;
    const direction = new THREE.Vector3();
    this.camera.getWorldDirection(direction);
    direction.y = 0;
    direction.normalize();
    const right = new THREE.Vector3().crossVectors(direction, new THREE.Vector3(0, 1, 0));

    if (this.moveState.forward) this.camera.position.addScaledVector(direction, speed);
    if (this.moveState.backward) this.camera.position.addScaledVector(direction, -speed);
    if (this.moveState.left) this.camera.position.addScaledVector(right, -speed);
    if (this.moveState.right) this.camera.position.addScaledVector(right, speed);
  }

  updateAnimations(delta) {
    if (this.petals) updatePetals(this.petals, delta);

    if (this.performer) {
      this.performer.rotation.y = Math.sin(this.clock.elapsedTime * 0.5) * 0.15;
      this.performer.children
        .filter((c) => c.name === 'sleeve')
        .forEach((sleeve, i) => {
          sleeve.rotation.z = Math.sin(this.clock.elapsedTime * 2 + i) * 0.3;
        });
    }

    this.scene.traverse((obj) => {
      if (obj.name === 'ribbon') {
        obj.rotation.x += delta * 0.3;
        obj.rotation.y += delta * 0.5;
      }
      if (obj.name === 'digital-particles') {
        const pos = obj.geometry.attributes.position;
        for (let i = 0; i < pos.count; i++) {
          pos.array[i * 3 + 1] += Math.sin(this.clock.elapsedTime + i) * 0.002;
        }
        pos.needsUpdate = true;
        obj.rotation.y += delta * 0.1;
      }
      if (obj.name === 'scroll') {
        obj.position.y = 1.4 + Math.sin(this.clock.elapsedTime * 1.5) * 0.05;
      }
    });

    if (this.stats.startTime) this.updateStatsDisplay();
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  animate() {
    this.renderer.setAnimationLoop(() => {
      const delta = this.clock.getDelta();
      if (this.started) {
        this.updateMovement(delta);
        this.updateAnimations(delta);
      }
      this.renderer.render(this.world, this.camera);
    });
  }
}
