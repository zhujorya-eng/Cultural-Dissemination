import * as THREE from 'three';

const CRIMSON = 0x8b1a2b;
const GOLD = 0xc9a44c;
const WOOD = 0x4a3020;
const DARK = 0x1a1410;

export class KunquStage {
  constructor() {
    this.group = new THREE.Group();
    this.curtainLeft = null;
    this.curtainRight = null;
    this.curtainOpen = 0.85;
    this.performer = null;
    this.sleeves = [];
    this.lanterns = [];
    this.spotLight = null;
    this.ambientParticles = null;
    this.build();
  }

  build() {
    this.buildHall();
    this.buildStagePlatform();
    this.buildRoof();
    this.buildPillars();
    this.buildCurtains();
    this.buildProps();
    this.buildPerformer();
    this.buildLanterns();
    this.buildAudience();
    this.buildParticles();
  }

  buildHall() {
    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(30, 24),
      new THREE.MeshStandardMaterial({ color: 0x2a1810, roughness: 0.9 }),
    );
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = 0;
    floor.receiveShadow = true;
    this.group.add(floor);

    const backWall = new THREE.Mesh(
      new THREE.PlaneGeometry(30, 10),
      new THREE.MeshStandardMaterial({ color: DARK, roughness: 0.95 }),
    );
    backWall.position.set(0, 5, -8);
    this.group.add(backWall);

    const sideMat = new THREE.MeshStandardMaterial({ color: 0x241810, roughness: 0.9 });
    [-1, 1].forEach((side) => {
      const wall = new THREE.Mesh(new THREE.PlaneGeometry(24, 10), sideMat);
      wall.position.set(side * 15, 5, 0);
      wall.rotation.y = (-Math.PI / 2) * side;
      this.group.add(wall);
    });
  }

  buildStagePlatform() {
    const platform = new THREE.Mesh(
      new THREE.BoxGeometry(10, 0.5, 6),
      new THREE.MeshStandardMaterial({ color: WOOD, roughness: 0.7, metalness: 0.05 }),
    );
    platform.position.set(0, 0.25, -2);
    platform.castShadow = true;
    platform.receiveShadow = true;
    this.group.add(platform);

    const frontEdge = new THREE.Mesh(
      new THREE.BoxGeometry(10.2, 0.15, 0.2),
      new THREE.MeshStandardMaterial({ color: CRIMSON, roughness: 0.5 }),
    );
    frontEdge.position.set(0, 0.55, 1.05);
    this.group.add(frontEdge);

    const goldTrim = new THREE.Mesh(
      new THREE.BoxGeometry(10.4, 0.06, 0.08),
      new THREE.MeshStandardMaterial({ color: GOLD, metalness: 0.6, roughness: 0.3 }),
    );
    goldTrim.position.set(0, 0.62, 1.12);
    this.group.add(goldTrim);
  }

  buildRoof() {
    const roofGroup = new THREE.Group();
    roofGroup.position.set(0, 6.5, -2);

    const roofGeo = new THREE.ConeGeometry(7.5, 2.5, 4);
    const roofMat = new THREE.MeshStandardMaterial({ color: 0x2a1510, roughness: 0.8 });
    const roof = new THREE.Mesh(roofGeo, roofMat);
    roof.rotation.y = Math.PI / 4;
    roofGroup.add(roof);

    const eaves = new THREE.Mesh(
      new THREE.TorusGeometry(5.2, 0.12, 8, 4),
      new THREE.MeshStandardMaterial({ color: GOLD, metalness: 0.5, roughness: 0.4 }),
    );
    eaves.rotation.x = Math.PI / 2;
    eaves.rotation.z = Math.PI / 4;
    eaves.position.y = -0.8;
    roofGroup.add(eaves);

    const sign = this.createTextPlane('昆曲', 0.9, CRIMSON);
    sign.position.set(0, -0.5, 0);
    roofGroup.add(sign);

    this.group.add(roofGroup);
  }

  buildPillars() {
    const pillarMat = new THREE.MeshStandardMaterial({ color: CRIMSON, roughness: 0.6 });
    const positions = [
      [-4.5, -2], [4.5, -2], [-4.5, 1.5], [4.5, 1.5],
    ];
    positions.forEach(([x, z]) => {
      const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 5.5, 12), pillarMat);
      pillar.position.set(x, 3.25, z);
      pillar.castShadow = true;
      this.group.add(pillar);

      const cap = new THREE.Mesh(
        new THREE.CylinderGeometry(0.28, 0.22, 0.15, 12),
        new THREE.MeshStandardMaterial({ color: GOLD, metalness: 0.5 }),
      );
      cap.position.set(x, 6.0, z);
      this.group.add(cap);
    });
  }

  buildCurtains() {
    const curtainMat = new THREE.MeshStandardMaterial({
      color: CRIMSON,
      roughness: 0.85,
      side: THREE.DoubleSide,
    });

    this.curtainLeft = new THREE.Mesh(new THREE.PlaneGeometry(2.5, 4.5, 8, 16), curtainMat);
    this.curtainLeft.position.set(-1.25, 3.0, 0.8);
    this.group.add(this.curtainLeft);

    this.curtainRight = new THREE.Mesh(new THREE.PlaneGeometry(2.5, 4.5, 8, 16), curtainMat);
    this.curtainRight.position.set(1.25, 3.0, 0.8);
    this.group.add(this.curtainRight);

    const valance = new THREE.Mesh(
      new THREE.BoxGeometry(6, 0.3, 0.15),
      new THREE.MeshStandardMaterial({ color: GOLD, metalness: 0.4 }),
    );
    valance.position.set(0, 5.4, 0.85);
    this.group.add(valance);
  }

  buildProps() {
    const table = new THREE.Mesh(
      new THREE.BoxGeometry(1.2, 0.08, 0.7),
      new THREE.MeshStandardMaterial({ color: 0x3d2817, roughness: 0.7 }),
    );
    table.position.set(0, 0.65, -1.5);
    this.group.add(table);

    [-0.8, 0.8].forEach((x) => {
      const chair = new THREE.Mesh(
        new THREE.BoxGeometry(0.35, 0.7, 0.35),
        new THREE.MeshStandardMaterial({ color: 0x3d2817 }),
      );
      chair.position.set(x, 0.85, -0.5);
      this.group.add(chair);
    });
  }

  buildPerformer() {
    this.performer = new THREE.Group();
    this.performer.position.set(0, 0.55, 0.2);

    const bodyMat = new THREE.MeshStandardMaterial({ color: 0xf5e6d0, roughness: 0.8 });
    const robeMat = new THREE.MeshStandardMaterial({ color: CRIMSON, roughness: 0.7 });

    const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.28, 0.7, 12), robeMat);
    torso.position.y = 0.85;
    this.performer.add(torso);

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 16, 16), bodyMat);
    head.position.y = 1.35;
    this.performer.add(head);

    const headdress = new THREE.Mesh(
      new THREE.ConeGeometry(0.15, 0.25, 8),
      new THREE.MeshStandardMaterial({ color: GOLD, metalness: 0.6 }),
    );
    headdress.position.y = 1.55;
    this.performer.add(headdress);

    this.sleeves = [];
    [-1, 1].forEach((side) => {
      const sleeve = new THREE.Mesh(
        new THREE.PlaneGeometry(0.15, 1.8, 4, 8),
        new THREE.MeshStandardMaterial({
          color: 0xf0d8e8,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.92,
        }),
      );
      sleeve.position.set(side * 0.35, 0.95, 0.1);
      sleeve.rotation.z = side * 0.4;
      this.performer.add(sleeve);
      this.sleeves.push({ mesh: sleeve, side });
    });

    this.group.add(this.performer);
  }

  buildLanterns() {
    const positions = [
      [-3, 4.5, 0.5], [3, 4.5, 0.5], [-2, 4.5, -3], [2, 4.5, -3],
    ];
    positions.forEach(([x, y, z]) => {
      const lantern = new THREE.Group();
      const body = new THREE.Mesh(
        new THREE.SphereGeometry(0.25, 12, 12),
        new THREE.MeshStandardMaterial({
          color: CRIMSON,
          emissive: 0xff6030,
          emissiveIntensity: 0.6,
          transparent: true,
          opacity: 0.9,
        }),
      );
      lantern.add(body);

      const light = new THREE.PointLight(0xff8040, 0.8, 6);
      lantern.add(light);

      lantern.position.set(x, y, z);
      this.lanterns.push({ group: lantern, light, phase: Math.random() * Math.PI * 2 });
      this.group.add(lantern);
    });
  }

  buildAudience() {
    const seatMat = new THREE.MeshStandardMaterial({ color: 0x1a1008, roughness: 0.95 });
    for (let row = 0; row < 4; row++) {
      for (let col = -4; col <= 4; col++) {
        const seat = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.4, 0.6), seatMat);
        seat.position.set(col * 0.85, 0.2, 4 + row * 1.1);
        this.group.add(seat);
      }
    }
  }

  buildParticles() {
    const count = 200;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 8;
      positions[i * 3 + 1] = Math.random() * 5 + 0.5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 4 - 1;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({
      color: GOLD,
      size: 0.04,
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
    });
    this.ambientParticles = new THREE.Points(geo, mat);
    this.group.add(this.ambientParticles);
  }

  createTextPlane(text, scale, bgColor) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = `#${bgColor.toString(16).padStart(6, '0')}`;
    ctx.fillRect(0, 0, 256, 128);
    ctx.fillStyle = '#c9a44c';
    ctx.font = 'bold 72px serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 128, 64);
    const tex = new THREE.CanvasTexture(canvas);
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(1.8 * scale, 0.9 * scale),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true }),
    );
    return mesh;
  }

  setSceneColors(stageColor, lightColor) {
    if (this.spotLight) {
      this.spotLight.color.setHex(lightColor);
    }
    this.lanterns.forEach(({ light }) => light.color.setHex(lightColor));
  }

  attachSpotLight(scene) {
    this.spotLight = new THREE.SpotLight(0xffd4a8, 80, 20, Math.PI / 6, 0.4);
    this.spotLight.position.set(0, 8, 3);
    this.spotLight.target.position.set(0, 1, -1);
    this.spotLight.castShadow = true;
    scene.add(this.spotLight);
    scene.add(this.spotLight.target);
  }

  toggleCurtain() {
    this.curtainOpen = this.curtainOpen > 0.5 ? 0.1 : 0.85;
  }

  update(time, delta) {
    const open = THREE.MathUtils.lerp(
      this.curtainLeft.position.x,
      -2.5 * this.curtainOpen,
      delta * 2,
    );
    this.curtainLeft.position.x = open;
    this.curtainRight.position.x = -open;

    if (this.performer) {
      this.performer.position.y = 0.55 + Math.sin(time * 1.2) * 0.03;
      this.performer.rotation.y = Math.sin(time * 0.4) * 0.15;
    }

    this.sleeves.forEach(({ mesh, side }, i) => {
      mesh.rotation.z = side * (0.4 + Math.sin(time * 2 + i) * 0.5);
      mesh.rotation.x = Math.sin(time * 1.5 + i * 0.5) * 0.3;
    });

    this.lanterns.forEach(({ group, light, phase }) => {
      const flicker = 0.7 + Math.sin(time * 3 + phase) * 0.15;
      light.intensity = flicker;
      group.position.y += Math.sin(time * 0.8 + phase) * 0.0005;
    });

    if (this.ambientParticles) {
      this.ambientParticles.rotation.y = time * 0.05;
      const pos = this.ambientParticles.geometry.attributes.position.array;
      for (let i = 0; i < pos.length; i += 3) {
        pos[i + 1] += delta * 0.08;
        if (pos[i + 1] > 6) pos[i + 1] = 0.5;
      }
      this.ambientParticles.geometry.attributes.position.needsUpdate = true;
    }
  }
}
