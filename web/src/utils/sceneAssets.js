import * as THREE from 'three';

export function createPetals(count = 80) {
  const group = new THREE.Group();
  const geo = new THREE.PlaneGeometry(0.08, 0.08);
  const mat = new THREE.MeshBasicMaterial({
    color: 0xffb7c5,
    transparent: true,
    opacity: 0.85,
    side: THREE.DoubleSide,
    depthWrite: false,
  });

  for (let i = 0; i < count; i++) {
    const petal = new THREE.Mesh(geo, mat.clone());
    petal.position.set(
      (Math.random() - 0.5) * 12,
      Math.random() * 8 + 2,
      (Math.random() - 0.5) * 12
    );
    petal.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
    petal.userData = {
      speed: 0.003 + Math.random() * 0.008,
      sway: Math.random() * Math.PI * 2,
    };
    group.add(petal);
  }
  return group;
}

export function updatePetals(group, delta) {
  group.children.forEach((petal) => {
    petal.position.y -= petal.userData.speed * 60 * delta;
    petal.position.x += Math.sin(petal.userData.sway + performance.now() * 0.001) * 0.002;
    petal.rotation.z += delta * 0.5;
    if (petal.position.y < 0) {
      petal.position.y = 8 + Math.random() * 2;
      petal.position.x = (Math.random() - 0.5) * 12;
    }
  });
}

export function createChineseStage() {
  const stage = new THREE.Group();

  const floorGeo = new THREE.BoxGeometry(14, 0.2, 10);
  const floorMat = new THREE.MeshStandardMaterial({ color: 0x3d2018, roughness: 0.8 });
  const floor = new THREE.Mesh(floorGeo, floorMat);
  floor.position.y = -0.1;
  stage.add(floor);

  const pillarMat = new THREE.MeshStandardMaterial({
    color: 0x8b1a2d,
    metalness: 0.2,
    roughness: 0.6,
  });
  [[-5.5, -4], [5.5, -4], [-5.5, 4], [5.5, 4]].forEach(([x, z]) => {
    const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.3, 5, 12), pillarMat);
    pillar.position.set(x, 2.5, z);
    stage.add(pillar);
  });

  const archShape = new THREE.Shape();
  archShape.moveTo(-6, 0);
  archShape.lineTo(-6, 4.5);
  archShape.quadraticCurveTo(0, 6.5, 6, 4.5);
  archShape.lineTo(6, 0);
  const archGeo = new THREE.ExtrudeGeometry(archShape, { depth: 0.3, bevelEnabled: false });
  const arch = new THREE.Mesh(
    archGeo,
    new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.4, roughness: 0.5 })
  );
  arch.position.set(0, 0, -4.8);
  stage.add(arch);

  const curtain = new THREE.Mesh(
    new THREE.PlaneGeometry(10, 5),
    new THREE.MeshStandardMaterial({
      color: 0xc41e3a,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.92,
    })
  );
  curtain.position.set(0, 2.5, -4.2);
  stage.add(curtain);

  const stageLight = new THREE.PointLight(0xffd4a0, 2, 20);
  stageLight.position.set(0, 6, 2);
  stage.add(stageLight);

  return stage;
}

export function createPipa() {
  const pipa = new THREE.Group();
  pipa.name = 'pipa';

  const body = new THREE.Mesh(
    new THREE.SphereGeometry(0.35, 16, 12),
    new THREE.MeshStandardMaterial({ color: 0x5c3317, roughness: 0.7 })
  );
  body.scale.set(1, 1.3, 0.5);
  pipa.add(body);

  const neck = new THREE.Mesh(
    new THREE.CylinderGeometry(0.04, 0.06, 0.8, 8),
    new THREE.MeshStandardMaterial({ color: 0x3d2010 })
  );
  neck.rotation.z = -0.5;
  neck.position.set(0.2, 0.5, 0);
  pipa.add(neck);

  for (let i = 0; i < 4; i++) {
    const string = new THREE.Mesh(
      new THREE.CylinderGeometry(0.003, 0.003, 0.7, 4),
      new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.8 })
    );
    string.rotation.z = -0.5;
    string.position.set(-0.08 + i * 0.05, 0.15, 0.05);
    string.userData.stringIndex = i;
    string.name = 'pipa-string';
    pipa.add(string);
  }

  pipa.userData.interactive = true;
  pipa.userData.type = 'pipa';
  return pipa;
}

export function createPerformer() {
  const performer = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.CylinderGeometry(0.25, 0.35, 1.2, 8),
    new THREE.MeshStandardMaterial({ color: 0x1a5080 })
  );
  body.position.y = 0.6;
  performer.add(body);

  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.2, 12, 12),
    new THREE.MeshStandardMaterial({ color: 0xf5d0c5 })
  );
  head.position.y = 1.4;
  performer.add(head);

  const sleeveL = new THREE.Mesh(
    new THREE.PlaneGeometry(0.8, 0.3),
    new THREE.MeshStandardMaterial({ color: 0xffffff, side: THREE.DoubleSide })
  );
  sleeveL.position.set(-0.5, 0.9, 0.2);
  sleeveL.rotation.y = 0.4;
  sleeveL.name = 'sleeve';
  performer.add(sleeveL);

  const sleeveR = sleeveL.clone();
  sleeveR.position.set(0.5, 0.9, 0.2);
  sleeveR.rotation.y = -0.4;
  performer.add(sleeveR);

  return performer;
}

export function createTeaHouse() {
  const house = new THREE.Group();

  const floor = new THREE.Mesh(
    new THREE.BoxGeometry(16, 0.15, 14),
    new THREE.MeshStandardMaterial({ color: 0x4a3728 })
  );
  house.add(floor);

  const wallMat = new THREE.MeshStandardMaterial({ color: 0x8b7355 });
  const backWall = new THREE.Mesh(new THREE.BoxGeometry(16, 4, 0.2), wallMat);
  backWall.position.set(0, 2, -7);
  house.add(backWall);

  const seats = [];
  const seatPositions = [
    { pos: [-3, 0, -2], label: '雅座' },
    { pos: [3, 0, -2], label: '散座' },
    { pos: [0, 0, 2], label: '临窗' },
  ];

  seatPositions.forEach(({ pos, label }, i) => {
    const table = new THREE.Group();
    table.position.set(...pos);

    const tabletop = new THREE.Mesh(
      new THREE.CylinderGeometry(0.6, 0.65, 0.08, 16),
      new THREE.MeshStandardMaterial({ color: 0x5c4033 })
    );
    tabletop.position.y = 0.75;
    table.add(tabletop);

    const cup = new THREE.Mesh(
      new THREE.CylinderGeometry(0.06, 0.05, 0.1, 8),
      new THREE.MeshStandardMaterial({ color: 0xf5f5dc })
    );
    cup.position.set(0.15, 0.85, 0.1);
    cup.userData.type = 'tea';
    cup.userData.interactive = true;
    table.add(cup);

    const chair = new THREE.Mesh(
      new THREE.BoxGeometry(0.5, 0.5, 0.5),
      new THREE.MeshStandardMaterial({ color: 0x3d2817 })
    );
    chair.position.set(0, 0.25, 0.8);
    table.add(chair);

    table.userData.interactive = true;
    table.userData.type = 'seat';
    table.userData.seatIndex = i;
    table.userData.label = label;
    table.userData.cameraPos = new THREE.Vector3(pos[0], 1.5, pos[2] + 1.2);
    table.userData.lookAt = new THREE.Vector3(0, 1.5, -5);
    seats.push(table);
    house.add(table);
  });

  const miniStage = createChineseStage();
  miniStage.scale.set(0.6, 0.6, 0.6);
  miniStage.position.set(0, 0, -5.5);
  house.add(miniStage);

  house.userData.seats = seats;
  return house;
}

export function createGarden() {
  const garden = new THREE.Group();

  const ground = new THREE.Mesh(
    new THREE.CircleGeometry(18, 32),
    new THREE.MeshStandardMaterial({ color: 0x2d4a2d })
  );
  ground.rotation.x = -Math.PI / 2;
  garden.add(ground);

  const pond = new THREE.Mesh(
    new THREE.CircleGeometry(4, 32),
    new THREE.MeshStandardMaterial({
      color: 0x1a3a4a,
      metalness: 0.8,
      roughness: 0.1,
    })
  );
  pond.rotation.x = -Math.PI / 2;
  pond.position.y = 0.02;
  garden.add(pond);

  const pavilion = new THREE.Group();
  const roof = new THREE.Mesh(
    new THREE.ConeGeometry(3, 1.2, 4),
    new THREE.MeshStandardMaterial({ color: 0x2a2a2a })
  );
  roof.position.y = 3.2;
  roof.rotation.y = Math.PI / 4;
  pavilion.add(roof);

  const columns = new THREE.MeshStandardMaterial({ color: 0x8b1a2d });
  [[-1.5, -1.5], [1.5, -1.5], [-1.5, 1.5], [1.5, 1.5]].forEach(([x, z]) => {
    const col = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 2.8, 8), columns);
    col.position.set(x, 1.4, z);
    pavilion.add(col);
  });
  pavilion.position.set(0, 0, -3);
  garden.add(pavilion);

  for (let i = 0; i < 8; i++) {
    const tree = new THREE.Group();
    const trunk = new THREE.Mesh(
      new THREE.CylinderGeometry(0.08, 0.12, 1.5, 6),
      new THREE.MeshStandardMaterial({ color: 0x4a3020 })
    );
    trunk.position.y = 0.75;
    tree.add(trunk);
    const foliage = new THREE.Mesh(
      new THREE.SphereGeometry(0.6, 8, 8),
      new THREE.MeshStandardMaterial({ color: 0x1a5c1a })
    );
    foliage.position.y = 1.8;
    tree.add(foliage);
    const angle = (i / 8) * Math.PI * 2;
    tree.position.set(Math.cos(angle) * 8, 0, Math.sin(angle) * 8);
    garden.add(tree);
  }

  const bridge = new THREE.Mesh(
    new THREE.BoxGeometry(5, 0.15, 1),
    new THREE.MeshStandardMaterial({ color: 0x6b4c30 })
  );
  bridge.position.set(0, 0.3, 2);
  bridge.userData.interactive = true;
  bridge.userData.type = 'bridge';
  garden.add(bridge);

  const performer = createPerformer();
  performer.position.set(0, 0, -3);
  performer.scale.set(1.2, 1.2, 1.2);
  performer.userData.type = 'duet';
  performer.userData.interactive = true;
  garden.add(performer);

  return garden;
}

export function createDigitalTheater() {
  const theater = new THREE.Group();

  const particles = new THREE.BufferGeometry();
  const count = 2000;
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 20;
    positions[i * 3 + 1] = Math.random() * 10;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 20;
    colors[i * 3] = 0.8 + Math.random() * 0.2;
    colors[i * 3 + 1] = 0.2 + Math.random() * 0.3;
    colors[i * 3 + 2] = 0.3 + Math.random() * 0.2;
  }
  particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particles.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const particleMat = new THREE.PointsMaterial({
    size: 0.08,
    vertexColors: true,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const points = new THREE.Points(particles, particleMat);
  points.name = 'digital-particles';
  theater.add(points);

  for (let i = 0; i < 5; i++) {
    const ribbon = new THREE.Mesh(
      new THREE.TorusKnotGeometry(0.8, 0.06, 100, 16),
      new THREE.MeshStandardMaterial({
        color: i % 2 === 0 ? 0xc41e3a : 0xd4af37,
        emissive: i % 2 === 0 ? 0x440010 : 0x332200,
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.7,
      })
    );
    ribbon.position.set((i - 2) * 2.5, 2 + i * 0.5, -2);
    ribbon.name = 'ribbon';
    theater.add(ribbon);
  }

  theater.userData.particles = points;
  return theater;
}

export function createScroll() {
  const scroll = new THREE.Group();
  scroll.name = 'scroll';

  const paper = new THREE.Mesh(
    new THREE.PlaneGeometry(0.6, 0.9),
    new THREE.MeshStandardMaterial({
      color: 0xf5e6d3,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.95,
    })
  );
  scroll.add(paper);

  const rodMat = new THREE.MeshStandardMaterial({ color: 0x5c3317 });
  const rodTop = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.7, 8), rodMat);
  rodTop.rotation.z = Math.PI / 2;
  rodTop.position.y = 0.48;
  scroll.add(rodTop);
  const rodBot = rodTop.clone();
  rodBot.position.y = -0.48;
  scroll.add(rodBot);

  scroll.userData.interactive = true;
  scroll.userData.type = 'scroll';
  return scroll;
}

export function createStageFrame() {
  const frame = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({
    color: 0xc41e3a,
    transparent: true,
    opacity: 0.55,
    emissive: 0x440010,
    emissiveIntensity: 0.3,
  });

  const left = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.5, 0.08), mat);
  left.position.set(-1.5, 1.25, -2);
  frame.add(left);
  const right = left.clone();
  right.position.x = 1.5;
  frame.add(right);
  const top = new THREE.Mesh(new THREE.BoxGeometry(3.08, 0.08, 0.08), mat);
  top.position.set(0, 2.5, -2);
  frame.add(top);

  return frame;
}
