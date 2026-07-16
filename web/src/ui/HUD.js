export class HUD {
  constructor(root) {
    this.root = root;
    this.onChoice = null;
    this.onAction = null;
    this.render();
  }

  render() {
    this.root.innerHTML = `
      <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
      <div class="hud-top">
        <div class="scene-badge" id="scene-badge">昆曲 VR 剧场</div>
        <div class="hud-actions">
          <button class="btn" id="btn-help">操作说明</button>
          <button class="btn" id="btn-vr">进入 VR</button>
          <button class="btn btn-primary" id="btn-start">开始体验</button>
        </div>
      </div>
      <div class="stats-panel" id="stats-panel">
        <div>互动次数：<span id="stat-interactions">0</span></div>
        <div>解锁场景：<span id="stat-scenes">0</span>/4</div>
        <div>体验时长：<span id="stat-time">0:00</span></div>
      </div>
      <div class="crosshair" id="crosshair"></div>
      <div id="subtitle-container"></div>
      <div id="choice-container"></div>
      <div id="card-container"></div>
    `;

    this.progressBar = this.root.querySelector('#progress-bar');
    this.sceneBadge = this.root.querySelector('#scene-badge');
    this.subtitleContainer = this.root.querySelector('#subtitle-container');
    this.choiceContainer = this.root.querySelector('#choice-container');
    this.cardContainer = this.root.querySelector('#card-container');
    this.statInteractions = this.root.querySelector('#stat-interactions');
    this.statScenes = this.root.querySelector('#stat-scenes');
    this.statTime = this.root.querySelector('#stat-time');

    this.root.querySelector('#btn-start').addEventListener('click', () =>
      this.onAction?.('start')
    );
    this.root.querySelector('#btn-vr').addEventListener('click', () =>
      this.onAction?.('vr')
    );
    this.root.querySelector('#btn-help').addEventListener('click', () =>
      this.onAction?.('help')
    );
  }

  setProgress(pct) {
    this.progressBar.style.width = `${pct}%`;
  }

  setScene(name, mode) {
    this.sceneBadge.textContent = `${name} · ${mode}`;
  }

  showSubtitle({ speaker, text, hint, duration = 0 }) {
    this.subtitleContainer.innerHTML = `
      <div class="subtitle-panel">
        ${speaker ? `<div class="speaker">${speaker}</div>` : ''}
        <div class="text">${text}</div>
        ${hint ? `<div class="hint">${hint}</div>` : ''}
      </div>
    `;
    if (duration > 0) {
      clearTimeout(this.subtitleTimer);
      this.subtitleTimer = setTimeout(() => this.hideSubtitle(), duration);
    }
  }

  hideSubtitle() {
    this.subtitleContainer.innerHTML = '';
  }

  showChoices(choices) {
    this.choiceContainer.innerHTML = `<div class="choice-panel">${choices
      .map(
        (c, i) =>
          `<button class="choice-btn" data-index="${i}">${c.label}</button>`
      )
      .join('')}</div>`;
    this.choiceContainer.querySelectorAll('.choice-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const idx = Number(btn.dataset.index);
        this.hideChoices();
        this.onChoice?.(choices[idx]);
      });
    });
  }

  hideChoices() {
    this.choiceContainer.innerHTML = '';
  }

  showToast(msg) {
    const el = document.createElement('div');
    el.className = 'interaction-toast';
    el.textContent = msg;
    this.root.appendChild(el);
    setTimeout(() => el.remove(), 2000);
  }

  showImprintCard(stats) {
    this.cardContainer.innerHTML = `
      <div class="card-panel">
        <div class="imprint-card">
          <h2>昆曲印记</h2>
          <p>感谢您完成虚实融合的昆曲之旅</p>
          <div class="stats">
            <div>体验时长：${stats.time}</div>
            <div>互动次数：${stats.interactions}</div>
            <div>解锁场景：${stats.scenes}/4</div>
            <div>表演贡献：${stats.performance}%</div>
          </div>
          <button class="btn btn-primary" id="btn-restart">再次体验</button>
        </div>
      </div>
    `;
    this.cardContainer.querySelector('#btn-restart').addEventListener('click', () => {
      this.hideImprintCard();
      this.onAction?.('restart');
    });
  }

  hideImprintCard() {
    this.cardContainer.innerHTML = '';
  }

  updateStats({ interactions, scenes, time }) {
    if (interactions !== undefined) this.statInteractions.textContent = interactions;
    if (scenes !== undefined) this.statScenes.textContent = scenes;
    if (time !== undefined) this.statTime.textContent = time;
  }

  setStarted() {
    this.root.querySelector('#btn-start').style.display = 'none';
  }
}
