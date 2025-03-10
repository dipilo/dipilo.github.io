var running = !1;
let pixiApp, graphRenderer, batchFraction = 1, minBatchFraction = .3, dt = 1, targetFPS = 40, startingCameraRect = { minX: -1, minY: -1, maxX: 1, maxY: 1 }, mouseWorldPos = { x: void 0, y: void 0 }, scrollVelocity = 0, averageFPS = 2 * targetFPS;

class GraphAssembly {
  static nodeCount = 0;
  static linkCount = 0;
  static hoveredNode = -1;
  static #e = 0;
  static #r = 0;
  static #t = 0;
  static #a = 0;
  static #s = 0;
  static linkSources = new Int32Array(0);
  static linkTargets = new Int32Array(0);
  static radii = new Float32Array(0);
  static maxRadius = 0;
  static averageRadius = 0;
  static minRadius = 0;

  static init(e) {
    GraphAssembly.nodeCount = e.nodeCount;
    GraphAssembly.linkCount = e.linkCount;
    let r = new Float32Array(2 * GraphAssembly.nodeCount);
    GraphAssembly.radii = new Float32Array(e.radii);
    GraphAssembly.linkSources = new Int32Array(e.linkSources);
    GraphAssembly.linkTargets = new Int32Array(e.linkTargets);
    GraphAssembly.#e = Module._malloc(r.byteLength);
    GraphAssembly.#r = r.byteLength;
    GraphAssembly.#t = Module._malloc(GraphAssembly.radii.byteLength);
    GraphAssembly.#a = Module._malloc(GraphAssembly.linkSources.byteLength);
    GraphAssembly.#s = Module._malloc(GraphAssembly.linkTargets.byteLength);
    GraphAssembly.maxRadius = GraphAssembly.radii.reduce(((e, r) => Math.max(e, r)), 0);
    GraphAssembly.averageRadius = GraphAssembly.radii.reduce(((e, r) => e + r), 0) / (GraphAssembly.radii.length || 1);
    GraphAssembly.minRadius = GraphAssembly.radii.reduce(((e, r) => Math.min(e, r)), Infinity);
    r = this.loadState();
    Module.HEAP32.set(new Int32Array(r.buffer), GraphAssembly.#e / r.BYTES_PER_ELEMENT);
  }

  static get positions() {
    return Module.HEAP32.buffer.slice(GraphAssembly.#e, GraphAssembly.#e + GraphAssembly.#r);
  }

  static saveState(e) {
    localStorage.setItem("positions", JSON.stringify(new Float32Array(GraphAssembly.positions).map((e => Math.round(e)))));
  }

  static loadState() {
    let e = localStorage.getItem("positions"), r = null;
    if (e && (r = new Float32Array(Object.values(JSON.parse(e)))), !r || !e || r.length != 2 * GraphAssembly.nodeCount) {
      r = new Float32Array(2 * GraphAssembly.nodeCount);
      let e = GraphAssembly.averageRadius * Math.sqrt(GraphAssembly.nodeCount) * 2;
      for (let t = 0; t < GraphAssembly.nodeCount; t++) {
        let a = (1 - GraphAssembly.radii[t] / GraphAssembly.maxRadius) * e;
        r[2 * t] = Math.cos(t / GraphAssembly.nodeCount * 7.41 * 2 * Math.PI) * a;
        r[2 * t + 1] = Math.sin(t / GraphAssembly.nodeCount * 7.41 * 2 * Math.PI) * a;
      }
    }
    let t = 1 / 0, a = -1 / 0, s = 1 / 0, i = -1 / 0;
    for (let e = 0; e < GraphAssembly.nodeCount - 1; e += 2) {
      let o = { x: r[e], y: r[e + 1] };
      t = Math.min(t, o.x);
      a = Math.max(a, o.x);
      s = Math.min(s, o.y);
      i = Math.max(i, o.y);
    }
    return startingCameraRect = { minX: t - 50, minY: s - 50, maxX: a + 50, maxY: i + 50 }, r;
  }

  static update(e, r, t) {
    GraphAssembly.hoveredNode = Module._Update(e.x, e.y, r, t);
  }

  static free() {
    Module._free(GraphAssembly.#e);
    Module._free(GraphAssembly.#t);
    Module._free(GraphAssembly.#a);
    Module._free(GraphAssembly.#s);
    Module._FreeMemory();
  }

  static set batchFraction(e) {
    Module._SetBatchFractionSize(e);
  }

  static set attractionForce(e) {
    Module._SetAttractionForce(e);
  }

  static set repulsionForce(e) {
    Module._SetRepulsionForce(e);
  }

  static set centralForce(e) {
    Module._SetCentralForce(e);
  }

  static set linkLength(e) {
    Module._SetLinkLength(e);
  }

  static set dt(e) {
    Module._SetDt(e);
  }
}

class GraphRenderWorker {
  #i;
  #o;
  #n;
  #h;
  #d;
  #l;
  #c;

  constructor() {
    this.canvas = document.querySelector("#graph-canvas");
    this.canvasSidebar = void 0;
    try {
      this.canvasSidebar = document.querySelector(".sidebar:has(#graph-canvas)");
    } catch (e) {
      console.log("Error: " + e + "\n\n Using fallback.");
    }
    this.view = this.canvas.transferControlToOffscreen();
    this.worker = new Worker("lib/scripts/graph-render-worker.js"); // Use relative path
    this.#i = { x: 0, y: 0 };
    this.#o = 1;
    this.#n = -1;
    this.#h = -1;
    this.#d = { background: 0, link: 0, node: 0, outline: 0, text: 0, accent: 0 };
    this.#l = 0;
    this.#c = 0;
    this.cameraOffset = { x: this.canvas.width / 2, y: this.canvas.height / 2 };
    this.cameraScale = 1;
    this.hoveredNode = -1;
    this.grabbedNode = -1;
    this.resampleColors();
    this.#p();
    this.width = this.canvas.width;
    this.height = this.canvas.height;
    this.autoResizeCanvas();
    this.fitToRect(startingCameraRect);
  }

  #p() {
    let { width: e, height: r } = this.view;
    this.worker.postMessage({
      type: "init",
      linkCount: GraphAssembly.linkCount,
      linkSources: GraphAssembly.linkSources,
      linkTargets: GraphAssembly.linkTargets,
      nodeCount: GraphAssembly.nodeCount,
      radii: GraphAssembly.radii,
      labels: graphData.labels,
      linkLength: graphData.graphOptions.linkLength,
      edgePruning: graphData.graphOptions.edgePruning,
      options: { width: e, height: r, view: this.view }
    }, [this.view]);
  }

  fitToRect(e) {
    let r = e.minX, t = e.minY, a = e.maxX - r, s = e.maxY - t, i = 1 / Math.min(a / this.width, s / this.height);
    this.cameraScale = i;
    this.cameraOffset = { x: this.width / 2 - (e.minX + a / 2) * i, y: this.height / 2 - (e.minY + s / 2) * i };
  }

  fitToNodes() {
    this.fitToRect(startingCameraRect);
  }

  sampleColor(e) {
    let r = document.createElement("div");
    document.body.appendChild(r);
    r.style.setProperty("display", "none");
    r.style.setProperty("color", "var(" + e + ")");
    let t = getComputedStyle(r).color, a = getComputedStyle(r).opacity;
    r.remove();
    let s = (i = t.match(/rgb?\((\d+),\s*(\d+),\s*(\d+)\)/)) ? { red: parseInt(i[1]), green: parseInt(i[2]), blue: parseInt(i[3]), alpha: 1 } : null;
    var i;
    return { a: parseFloat(a) * s?.alpha ?? 1 ?? 1, rgb: s?.red << 16 | s?.green << 8 | s?.blue ?? 8947848 };
  }

  resampleColors() {
    this.colors = {
      background: this.sampleColor("--background-secondary").rgb,
      link: this.sampleColor("--graph-line").rgb,
      node: this.sampleColor("--graph-node").rgb,
      outline: this.sampleColor("--graph-line").rgb,
      text: this.sampleColor("--graph-text").rgb,
      accent: this.sampleColor("--interactive-accent").rgb
    };
  }

  draw(e) {
    this.worker.postMessage({ type: "draw", positions: e }, [e]);
  }

  resizeCanvas(e, r) {
    this.worker.postMessage({ type: "resize", width: e, height: r });
    this.#l = e;
    this.#c = r;
  }

  autoResizeCanvas() {
    this.width == this.canvas.offsetWidth && this.height == this.canvas.offsetHeight || (this.centerCamera(), this.resizeCanvas(this.canvas.offsetWidth, this.canvas.offsetHeight));
  }

  centerCamera() {
    this.cameraOffset = { x: this.width / 2, y: this.height / 2 };
  }

  #m(e, r) {
    let t = { type: "update_interaction", hoveredNode: e, grabbedNode: r };
    this.worker.postMessage(t);
  }

  #g(e, r) {
    this.worker.postMessage({ type: "update_camera", cameraOffset: e, cameraScale: r });
  }

  #u(e) {
    this.worker.postMessage({ type: "update_colors", colors: e });
  }

  set cameraOffset(e) {
    this.#i = e;
    this.#g(e, this.cameraScale);
  }

  set cameraScale(e) {
    this.#o = e;
    this.#g(this.cameraOffset, e);
  }

  get cameraOffset() {
    return this.#i;
  }

  get cameraScale() {
    return this.#o;
  }

  set hoveredNode(e) {
    this.#n = e;
    this.#m(e, this.#h);
  }

  set grabbedNode(e) {
    this.#h = e;
    this.#m(this.#n, e);
  }

  set activeNode(e) {
    this.worker.postMessage({ type: "set_active", active: e });
  }

  get hoveredNode() {
    return this.#n;
  }

  get grabbedNode() {
    return this.#h;
  }

  set colors(e) {
    this.#d = e;
    this.#u(e);
  }

  get colors() {
    return this.#d;
  }

  set width(e) {
    this.#l = e;
    this.resizeCanvas(e, this.#c);
  }

  set height(e) {
    this.#c = e;
    this.resizeCanvas(this.#l, e);
  }

  get height() {
    return this.#c;
  }

  get width() {
    return this.#l;
  }

  toScreenSpace(e, r, t = !0) {
    return t ? { x: Math.floor(e * this.cameraScale + this.cameraOffset.x), y: Math.floor(r * this.cameraScale + this.cameraOffset.y) } : { x: e * this.cameraScale + this.cameraOffset.x, y: r * this.cameraScale + this.cameraOffset.y };
  }

  vecToScreenSpace(e, r = !0) {
    return this.toScreenSpace(e.x, e.y, r);
  }

  toWorldspace(e, r) {
    return { x: (e - this.cameraOffset.x) / this.cameraScale, y: (r - this.cameraOffset.y) / this.cameraScale };
  }

  vecToWorldspace(e) {
    return this.toWorldspace(e.x, e.y);
  }

  setCameraCenterWorldspace({ x: e, y: r }) {
    this.cameraOffset = { x: this.width / 2 - e * this.cameraScale, y: this.height / 2 - r * this.cameraScale };
  }

  getCameraCenterWorldspace() {
    return this.toWorldspace(this.width / 2, this.height / 2);
  }
}

async function initializeGraphView(graphData) {
  if (!running) {
    running = !0;
    graphData.graphOptions.repulsionForce /= batchFraction;
    pixiApp = new PIXI.Application({ view: document.querySelector("#graph-canvas") });
    console.log("Module Ready");
    GraphAssembly.init(graphData);
    graphRenderer = new GraphRenderWorker;
    window.graphRenderer = graphRenderer;
    initializeGraphEvents();
    pixiApp.ticker.maxFPS = targetFPS;
    pixiApp.ticker.add(updateGraph);
    setInterval(() => {
      try {
        var e = graphRenderer.canvasSidebar.classList.contains("is-collapsed");
      } catch (e) {
        return;
      }
      running && e ? running = !1 : running || e || (running = !0, graphRenderer.autoResizeCanvas(), graphRenderer.centerCamera());
    }, 1e3);
  }
}

let firstUpdate = !0;

function updateGraph() {
  if (running && !graphRenderer.canvasSidebar.classList.contains("is-collapsed")) {
    firstUpdate && (setTimeout(() => graphRenderer?.canvas?.classList.remove("hide"), 500), firstUpdate = !1);
    GraphAssembly.update(mouseWorldPos, graphRenderer.grabbedNode, graphRenderer.cameraScale);
    GraphAssembly.hoveredNode != graphRenderer.hoveredNode && (graphRenderer.hoveredNode = GraphAssembly.hoveredNode, graphRenderer.canvas.style.cursor = -1 == GraphAssembly.hoveredNode ? "default" : "pointer");
    graphRenderer.autoResizeCanvas();
    graphRenderer.draw(GraphAssembly.positions);
    averageFPS = .95 * averageFPS + .05 * pixiApp.ticker.FPS;
    averageFPS < .8 * targetFPS && batchFraction > minBatchFraction && (batchFraction = Math.max(batchFraction - .5 / targetFPS, minBatchFraction), GraphAssembly.batchFraction = batchFraction, GraphAssembly.repulsionForce = graphData.graphOptions.repulsionForce / batchFraction);
    averageFPS > 1.2 * targetFPS && batchFraction < 1 && (batchFraction = Math.min(batchFraction + .5 / targetFPS, 1), GraphAssembly.batchFraction = batchFraction, GraphAssembly.repulsionForce = graphData.graphOptions.repulsionForce / batchFraction);
    0 != scrollVelocity && (graphRenderer.getCameraCenterWorldspace(), Math.abs(scrollVelocity) < .001 && (scrollVelocity = 0), zoomGraphViewAroundPoint(mouseWorldPos, scrollVelocity), scrollVelocity *= .65);
  }
}

function zoomGraphViewAroundPoint(e, r, t = .15, a = 15) {
  let s = graphRenderer.getCameraCenterWorldspace();
  if (graphRenderer.cameraScale = Math.max(Math.min(graphRenderer.cameraScale + r * graphRenderer.cameraScale, a), t), graphRenderer.cameraScale != t && graphRenderer.cameraScale != a && scrollVelocity > 0 && null != mouseWorldPos.x && null != mouseWorldPos.y) {
    let t = { x: e.x - s.x, y: e.y - s.y }, a = { x: s.x + t.x * r, y: s.y + t.y * r };
    graphRenderer.setCameraCenterWorldspace(a);
  } else graphRenderer.setCameraCenterWorldspace(s);
}

function scaleGraphViewAroundPoint(e, r, t = .15, a = 15) {
  let s = graphRenderer.getCameraCenterWorldspace(), i = graphRenderer.cameraScale;
  graphRenderer.cameraScale = Math.max(Math.min(r * graphRenderer.cameraScale, a), t);
  let o = (i - graphRenderer.cameraScale) / i;
  if (graphRenderer.cameraScale != t && graphRenderer.cameraScale != a && 0 != r) {
    let r = { x: e.x - s.x, y: e.y - s.y }, t = { x: s.x - r.x * o, y: s.y - r.y * o };
    graphRenderer.setCameraCenterWorldspace(t);
  } else graphRenderer.setCameraCenterWorldspace(s);
}

function initializeGraphEvents() {
  const canvas = document.querySelector("#graph-canvas");
  canvas.addEventListener("wheel", function (e) {
    let r = .09;
    e.deltaY > 0 ? (scrollVelocity >= -.09 && (scrollVelocity = -.09), scrollVelocity *= 1.4) : (scrollVelocity <= r && (scrollVelocity = r), scrollVelocity *= 1.4);
  }, { passive: true });

  canvas.addEventListener("dblclick", function (e) {
    graphRenderer.fitToNodes();
  });

  document.querySelector(".theme-toggle-input")?.addEventListener("change", e => {
    setTimeout(() => graphRenderer.resampleColors(), 0);
  });
}

function waitLoadScripts(scripts, callback) {
  let loadedScripts = 0;
  scripts.forEach(script => {
    const scriptElement = document.createElement('script');
    scriptElement.src = `lib/scripts/${script}.js`;
    scriptElement.onload = () => {
      loadedScripts++;
      if (loadedScripts === scripts.length) {
        callback();
      }
    };
    document.head.appendChild(scriptElement);
  });
}

window.addEventListener("load", () => {
  waitLoadScripts(["pixi", "graph-render-worker", "graph-wasm"], () => {
    Module.onRuntimeInitialized = () => initializeGraphView(graphData);
    setTimeout(() => Module.onRuntimeInitialized(), 300);
  });
});