// Begin Module setup and environment detection
var Module = typeof Module !== 'undefined' ? Module : {};
var moduleOverrides = Object.assign({}, Module);
var arguments_ = [];
var thisProgram = './this.program';
var quit_ = (status, toThrow) => {
  throw toThrow;
};

var ENVIRONMENT_IS_WEB = typeof window === 'object';
var ENVIRONMENT_IS_WORKER = typeof importScripts === 'function';
var ENVIRONMENT_IS_NODE =
  typeof process === 'object' &&
  typeof process.versions === 'object' &&
  typeof process.versions.node === 'string';
var scriptDirectory = '';

function locateFile(path) {
  return Module.locateFile ? Module.locateFile(path, scriptDirectory) : scriptDirectory + path;
}

if (ENVIRONMENT_IS_NODE) {
  var fs = require('fs');
  var nodePath = require('path');
  scriptDirectory = __dirname + '/';
  read_ = (filename, binary) => {
    filename = isFileURI(filename) ? new URL(filename) : nodePath.normalize(filename);
    return fs.readFileSync(filename, binary ? undefined : 'utf8');
  };
  readBinary = filename => {
    var ret = read_(filename, true);
    return ret.buffer || ret;
  };
  readAsync = (filename, onload, onerror) => {
    filename = isFileURI(filename) ? new URL(filename) : nodePath.normalize(filename);
    fs.readFile(filename, (err, data) => {
      if (err) onerror(err);
      else onload(data.buffer);
    });
  };
  if (process.argv.length > 1) {
    thisProgram = process.argv[1].replace(/\\/g, '/');
  }
  arguments_ = process.argv.slice(2);
  if (typeof module !== 'undefined') {
    module.exports = Module;
  }
  process.on('uncaughtException', ex => {
    if (!(ex instanceof ExitStatus)) {
      throw ex;
    }
  });
  process.on('unhandledRejection', reason => {
    throw reason;
  });
  quit_ = (status, toThrow) => {
    process.exitCode = status;
    throw toThrow;
  };
  Module.inspect = () => '[Emscripten Module object]';
} else if (ENVIRONMENT_IS_WEB || ENVIRONMENT_IS_WORKER) {
  if (ENVIRONMENT_IS_WORKER) {
    scriptDirectory = self.location.href;
  } else if (typeof document !== 'undefined' && document.currentScript) {
    scriptDirectory = document.currentScript.src;
  }
  if (scriptDirectory.indexOf('blob:') !== 0) {
    scriptDirectory = scriptDirectory.substr(0, scriptDirectory.lastIndexOf('/') + 1);
  } else {
    scriptDirectory = '';
  }
  read_ = url => {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, false);
    xhr.send(null);
    return xhr.responseText;
  };
  if (ENVIRONMENT_IS_WORKER) {
    readBinary = url => {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', url, false);
      xhr.responseType = 'arraybuffer';
      xhr.send(null);
      return new Uint8Array(xhr.response);
    };
  }
  readAsync = (url, onload, onerror) => {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'arraybuffer';
    xhr.onload = () => {
      if (xhr.status == 200 || (xhr.status == 0 && xhr.response))
        onload(xhr.response);
      else
        onerror();
    };
    xhr.onerror = onerror;
    xhr.send(null);
  };
  setWindowTitle = title => (document.title = title);
}

// Set up output and error printing
var out = Module.print || console.log.bind(console);
var err = Module.printErr || console.warn.bind(console);

// Wasm binary loading helpers
var wasmBinary;
var noExitRuntime = Module.noExitRuntime || true;
var wasmMemory;
var ABORT = false;
var EXITSTATUS;
var HEAP8, HEAPU8, HEAP16, HEAPU16, HEAP32, HEAPU32, HEAPF32, HEAPF64;
var wasmTable;

function updateMemoryViews() {
  var buffer = wasmMemory.buffer;
  Module.HEAP8 = HEAP8 = new Int8Array(buffer);
  Module.HEAP16 = HEAP16 = new Int16Array(buffer);
  Module.HEAP32 = HEAP32 = new Int32Array(buffer);
  Module.HEAPU8 = HEAPU8 = new Uint8Array(buffer);
  Module.HEAPU16 = HEAPU16 = new Uint16Array(buffer);
  Module.HEAPU32 = HEAPU32 = new Uint32Array(buffer);
  Module.HEAPF32 = HEAPF32 = new Float32Array(buffer);
  Module.HEAPF64 = HEAPF64 = new Float64Array(buffer);
}

// Pre- and post-run callbacks
var __ATPRERUN__ = [];
var __ATINIT__ = [];
var __ATPOSTRUN__ = [];
var runtimeInitialized = false;

function preRun() {
  if (Module.preRun) {
    if (typeof Module.preRun === 'function') Module.preRun = [Module.preRun];
    while (Module.preRun.length) {
      addOnPreRun(Module.preRun.shift());
    }
  }
  callRuntimeCallbacks(__ATPRERUN__);
}
function initRuntime() {
  runtimeInitialized = true;
  callRuntimeCallbacks(__ATINIT__);
}
function postRun() {
  if (Module.postRun) {
    if (typeof Module.postRun === 'function') Module.postRun = [Module.postRun];
    while (Module.postRun.length) {
      addOnPostRun(Module.postRun.shift());
    }
  }
  callRuntimeCallbacks(__ATPOSTRUN__);
}
function addOnPreRun(cb) {
  __ATPRERUN__.unshift(cb);
}
function addOnInit(cb) {
  __ATINIT__.unshift(cb);
}
function addOnPostRun(cb) {
  __ATPOSTRUN__.unshift(cb);
}

var runDependencies = 0;
var runDependencyWatcher = null;
var dependenciesFulfilled = null;
function addRunDependency(id) {
  runDependencies++;
  if (Module.monitorRunDependencies) {
    Module.monitorRunDependencies(runDependencies);
  }
}
function removeRunDependency(id) {
  runDependencies--;
  if (Module.monitorRunDependencies) {
    Module.monitorRunDependencies(runDependencies);
  }
  if (runDependencies == 0) {
    if (runDependencyWatcher !== null) {
      clearInterval(runDependencyWatcher);
      runDependencyWatcher = null;
    }
    if (dependenciesFulfilled) {
      var callback = dependenciesFulfilled;
      dependenciesFulfilled = null;
      callback();
    }
  }
}
function abort(what) {
  if (Module.onAbort) {
    Module.onAbort(what);
  }
  what = 'Aborted(' + what + ')';
  err(what);
  ABORT = true;
  EXITSTATUS = 1;
  what += '. Build with -sASSERTIONS for more info.';
  var e = new WebAssembly.RuntimeError(what);
  throw e;
}

// Utility constants and functions for UTF-8 conversion
var dataURIPrefix = "data:application/octet-stream;base64,";

function isDataURI(filename) {
  return filename.startsWith(dataURIPrefix);
}

// Locate the wasm binary file
var wasmBinaryFile = 'graph-wasm.wasm';
if (!isDataURI(wasmBinaryFile)) {
  wasmBinaryFile = locateFile(wasmBinaryFile);
}

// Utility constants and functions for UTF-8 conversion
var ASM_CONSTS = {
  2304: function (ptr) {
    console.log(UTF8ToString(ptr));
  }
};

function ExitStatus(status) {
  this.name = 'ExitStatus';
  this.message = 'Program terminated with exit(' + status + ')';
  this.status = status;
}

function callRuntimeCallbacks(callbacks) {
  while (callbacks.length > 0) {
    callbacks.shift()(Module);
  }
}

function getValue(ptr, type = 'i8') {
  if (type.endsWith('*')) type = '*';
  switch (type) {
    case 'i1':
    case 'i8':
      return HEAP8[ptr >> 0];
    case 'i16':
      return HEAP16[ptr >> 1];
    case 'i32':
      return HEAP32[ptr >> 2];
    case 'i64':
      return HEAP32[ptr >> 2];
    case 'float':
      return HEAPF32[ptr >> 2];
    case 'double':
      return HEAPF64[ptr >> 3];
    case '*':
      return HEAPU32[ptr >> 2];
    default:
      abort('invalid type for getValue: ' + type);
  }
}

function setValue(ptr, value, type = 'i8') {
  if (type.endsWith('*')) type = '*';
  switch (type) {
    case 'i1':
    case 'i8':
      HEAP8[ptr >> 0] = value;
      break;
    case 'i16':
      HEAP16[ptr >> 1] = value;
      break;
    case 'i32':
      HEAP32[ptr >> 2] = value;
      break;
    case 'i64':
      HEAP32[ptr >> 2] = value;
      break;
    case 'float':
      HEAPF32[ptr >> 2] = value;
      break;
    case 'double':
      HEAPF64[ptr >> 3] = value;
      break;
    case '*':
      HEAPU32[ptr >> 2] = value;
      break;
    default:
      abort('invalid type for setValue: ' + type);
  }
}

function _abort() {
  abort('');
}

var readEmAsmArgsArray = [];
function readEmAsmArgs(sigPtr, buf) {
  var args = [];
  var sigIndex = 0;
  while (1) {
    var ch = HEAPU8[sigPtr++];
    if (!ch) break;
    var chr = String.fromCharCode(ch);
    var type = chr;
    if (type === 'i') {
      args.push(HEAP32[buf >> 2]);
      buf += 4;
    } else if (type === 'f') {
      args.push(HEAPF32[buf >> 2]);
      buf += 4;
    } else if (type === 'd') {
      args.push(HEAPF64[buf >> 3]);
      buf += 8;
    } else {
      abort('invalid type for readEmAsmArgs: ' + type);
    }
  }
  return args;
}

function runEmAsmFunction(index, sigPtr, buf) {
  var args = readEmAsmArgs(sigPtr, buf);
  return ASM_CONSTS[index].apply(null, args);
}

function _emscripten_asm_const_int(index, sigPtr, buf) {
  return runEmAsmFunction(index, sigPtr, buf);
}

function _emscripten_date_now() {
  return Date.now();
}

function _emscripten_memcpy_big(dest, src, num) {
  HEAPU8.copyWithin(dest, src, src + num);
}

function getHeapMax() {
  return 2147483648;
}

function emscripten_realloc_buffer(size) {
  var old = wasmMemory.buffer;
  try {
    wasmMemory.grow(((size - old.byteLength) + 65535) >>> 16);
    updateMemoryViews();
    return 1;
  } catch (e) {
    // Fall through.
  }
}

function _emscripten_resize_heap(requestedSize) {
  var oldSize = HEAPU8.length;
  requestedSize >>>= 0;
  var maxHeapSize = getHeapMax();
  if (requestedSize > maxHeapSize) {
    return false;
  }
  for (var cutDown = 1; cutDown <= 4; cutDown *= 2) {
    var overGrownHeapSize = oldSize * (1 + 0.2 / cutDown);
    overGrownHeapSize = Math.min(overGrownHeapSize, requestedSize + 100663296);
    var newSize = Math.min(maxHeapSize, alignUp(Math.max(requestedSize, overGrownHeapSize), 65536));
    var replacement = emscripten_realloc_buffer(newSize);
    if (replacement) {
      return true;
    }
  }
  return false;
}

function getCFunc(ident) {
  var func = Module['_' + ident];
  return func;
}

function writeArrayToMemory(array, buffer) {
  HEAP8.set(array, buffer);
}

function lengthBytesUTF8(str) {
  var len = 0;
  for (var i = 0; i < str.length; ++i) {
    var c = str.charCodeAt(i);
    if (c <= 127) {
      len++;
    } else if (c <= 2047) {
      len += 2;
    } else if (c >= 55296 && c <= 57343) {
      len += 4;
      ++i;
    } else {
      len += 3;
    }
  }
  return len;
}

function stringToUTF8Array(str, heap, outIdx, maxBytesToWrite) {
  if (!(maxBytesToWrite > 0)) return 0;
  var startIdx = outIdx;
  var endIdx = outIdx + maxBytesToWrite - 1;
  for (var i = 0; i < str.length; ++i) {
    var u = str.charCodeAt(i);
    if (u >= 55296 && u <= 57343) {
      var u1 = str.charCodeAt(++i);
      u = 65536 + ((u & 1023) << 10) | (u1 & 1023);
    }
    if (u <= 127) {
      if (outIdx >= endIdx) break;
      heap[outIdx++] = u;
    } else if (u <= 2047) {
      if (outIdx + 1 >= endIdx) break;
      heap[outIdx++] = 192 | (u >> 6);
      heap[outIdx++] = 128 | (u & 63);
    } else if (u <= 65535) {
      if (outIdx + 2 >= endIdx) break;
      heap[outIdx++] = 224 | (u >> 12);
      heap[outIdx++] = 128 | ((u >> 6) & 63);
      heap[outIdx++] = 128 | (u & 63);
    } else {
      if (outIdx + 3 >= endIdx) break;
      heap[outIdx++] = 240 | (u >> 18);
      heap[outIdx++] = 128 | ((u >> 12) & 63);
      heap[outIdx++] = 128 | ((u >> 6) & 63);
      heap[outIdx++] = 128 | (u & 63);
    }
  }
  heap[outIdx] = 0;
  return outIdx - startIdx;
}

function stringToUTF8(str, outPtr, maxBytesToWrite) {
  return stringToUTF8Array(str, HEAPU8, outPtr, maxBytesToWrite);
}

function stringToUTF8OnStack(str) {
  var size = lengthBytesUTF8(str) + 1;
  var ret = stackAlloc(size);
  stringToUTF8(str, ret, size);
  return ret;
}

var UTF8Decoder = typeof TextDecoder !== 'undefined' ? new TextDecoder('utf8') : undefined;

function UTF8ArrayToString(heap, idx, maxBytesToRead) {
  var endIdx = idx + maxBytesToRead;
  var endPtr = idx;
  while (heap[endPtr] && !(endPtr >= endIdx)) ++endPtr;
  if (endPtr - idx > 16 && heap.buffer && UTF8Decoder) {
    return UTF8Decoder.decode(heap.subarray(idx, endPtr));
  } else {
    var str = '';
    while (idx < endPtr) {
      var u0 = heap[idx++];
      if (!(u0 & 128)) {
        str += String.fromCharCode(u0);
        continue;
      }
      var u1 = heap[idx++] & 63;
      if ((u0 & 224) == 192) {
        str += String.fromCharCode(((u0 & 31) << 6) | u1);
        continue;
      }
      var u2 = heap[idx++] & 63;
      if ((u0 & 240) == 224) {
        u0 = ((u0 & 15) << 12) | (u1 << 6) | u2;
      } else {
        u0 = ((u0 & 7) << 18) | (u1 << 12) | (u2 << 6) | (heap[idx++] & 63);
      }
      if (u0 < 65536) {
        str += String.fromCharCode(u0);
      } else {
        var ch = u0 - 65536;
        str += String.fromCharCode(55296 | (ch >> 10), 56320 | (ch & 1023));
      }
    }
    return str;
  }
}

function UTF8ToString(ptr, maxBytesToRead) {
  return ptr ? UTF8ArrayToString(HEAPU8, ptr, maxBytesToRead) : '';
}

function ccall(ident, returnType, argTypes, args, opts) {
  var toC = {
    'string': function (str) {
      var ret = 0;
      if (str !== null && str !== undefined && str !== 0) {
        var len = (str.length << 2) + 1;
        ret = stackAlloc(len);
        stringToUTF8(str, ret, len);
      }
      return ret;
    },
    'array': function (arr) {
      var ret = stackAlloc(arr.length);
      writeArrayToMemory(arr, ret);
      return ret;
    }
  };
  function convertReturnValue(ret) {
    if (returnType === 'string') return UTF8ToString(ret);
    if (returnType === 'boolean') return Boolean(ret);
    return ret;
  }
  var func = getCFunc(ident);
  var cArgs = [];
  var stack = 0;
  if (args) {
    for (var i = 0; i < args.length; i++) {
      var converter = toC[argTypes[i]];
      if (converter) {
        if (stack === 0) stack = stackSave();
        cArgs[i] = converter(args[i]);
      } else {
        cArgs[i] = args[i];
      }
    }
  }
  var ret = func.apply(null, cArgs);
  ret = convertReturnValue(ret);
  if (stack !== 0) stackRestore(stack);
  return ret;
}

function cwrap(ident, returnType, argTypes, opts) {
  var isSimple = !argTypes || argTypes.every(function(type) {
    return type === "number" || type === "boolean";
  });
  if (returnType !== "string" && isSimple && !opts) {
    return getCFunc(ident);
  }
  return function() {
    return ccall(ident, returnType, argTypes, arguments, opts);
  };
}

// --- Begin WebAssembly instantiation support ---

function isFileURI(filename) {
  return filename.startsWith("file://");
}
function getBinary(filename) {
  try {
    if (filename === wasmBinaryFile && wasmBinary) {
      return new Uint8Array(wasmBinary);
    }
    if (readBinary) return readBinary(filename);
    throw "both async and sync fetching of the wasm failed";
  } catch (e) {
    abort(e);
  }
}
function getBinaryPromise(filename) {
  if (!wasmBinary && (ENVIRONMENT_IS_WEB || ENVIRONMENT_IS_WORKER)) {
    if (typeof fetch === "function" && !isFileURI(filename)) {
      return fetch(filename, { credentials: "same-origin" }).then(function(response) {
        if (!response.ok)
          throw "failed to load wasm binary file at '" + filename + "'";
        return response.arrayBuffer();
      }).catch(function() {
        return getBinary(filename);
      });
    }
    if (readAsync) {
      return new Promise(function(resolve, reject) {
        readAsync(filename, function(data) {
          resolve(new Uint8Array(data));
        }, reject);
      });
    }
  }
  return Promise.resolve().then(function() {
    return getBinary(filename);
  });
}
function instantiateArrayBuffer(filename, imports, callback) {
  return getBinaryPromise(filename).then(function(binary) {
    return WebAssembly.instantiate(binary, imports);
  }).then(callback, function(e) {
    err("failed to asynchronously prepare wasm: " + e);
    abort(e);
  });
}
function instantiateAsync(binary, filename, imports, callback) {
  if (
    binary ||
    typeof WebAssembly.instantiateStreaming !== "function" ||
    isDataURI(filename) ||
    isFileURI(filename) ||
    ENVIRONMENT_IS_NODE ||
    typeof fetch !== "function"
  ) {
    return instantiateArrayBuffer(filename, imports, callback);
  } else {
    return fetch(filename, { credentials: "same-origin" }).then(function(response) {
      var result = WebAssembly.instantiateStreaming(response, imports).then(callback, function(e) {
        err("wasm streaming compile failed: " + e);
        err("falling back to ArrayBuffer instantiation");
        return instantiateArrayBuffer(filename, imports, callback);
      });
      return result;
    });
  }
}

function createWasm() {
  var info = {
    'env': wasmImports,
    'wasi_snapshot_preview1': wasmImports
  };

  function receiveInstance(instance, module) {
    var exports = instance.exports;
    Module['asm'] = exports;
    wasmMemory = Module['asm']['memory'];
    updateMemoryViews();
    wasmTable = Module['asm']['__indirect_function_table'];
    addOnInit(Module['asm']['__wasm_call_ctors']);
    removeRunDependency('wasm-instantiate');
    return exports;
  }

  addRunDependency('wasm-instantiate');

  if (Module['instantiateWasm']) {
    try {
      return Module['instantiateWasm'](info, receiveInstance);
    } catch (e) {
      err('Module.instantiateWasm callback failed with error: ' + e);
      return false;
    }
  }

  function receiveInstantiationResult(result) {
    receiveInstance(result['instance']);
  }

  function instantiateArrayBuffer(receiver) {
    return getBinaryPromise(wasmBinaryFile).then(function (binary) {
      return WebAssembly.instantiate(binary, info);
    }).then(receiver, function (reason) {
      err('failed to asynchronously prepare wasm: ' + reason);
      abort(reason);
    });
  }

  function instantiateAsync() {
    if (!wasmBinary && typeof WebAssembly.instantiateStreaming === 'function' && !isDataURI(wasmBinaryFile) && !isFileURI(wasmBinaryFile) && typeof fetch === 'function') {
      return fetch(wasmBinaryFile, { credentials: 'same-origin' }).then(function (response) {
        var result = WebAssembly.instantiateStreaming(response, info);
        return result.then(receiveInstantiationResult, function (reason) {
          err('wasm streaming compile failed: ' + reason);
          err('falling back to ArrayBuffer instantiation');
          return instantiateArrayBuffer(receiveInstantiationResult);
        });
      });
    } else {
      return instantiateArrayBuffer(receiveInstantiationResult);
    }
  }

  return instantiateAsync();
}

// --- End WebAssembly instantiation support ---

// Additional Module function assignments from the finished version
var calledRun;
var wasmImports = {
  b: _abort,
  e: _emscripten_asm_const_int,
  d: _emscripten_date_now,
  c: _emscripten_memcpy_big,
  a: _emscripten_resize_heap
};
var asm = createWasm();
var ___wasm_call_ctors = function() {
  return (___wasm_call_ctors = Module.asm.g).apply(null, arguments);
};
var _SetBatchFractionSize = Module._SetBatchFractionSize = function() {
  return (_SetBatchFractionSize = Module._SetBatchFractionSize = Module.asm.h).apply(null, arguments);
};
var _SetAttractionForce = Module._SetAttractionForce = function() {
  return (_SetAttractionForce = Module._SetAttractionForce = Module.asm.i).apply(null, arguments);
};
var _SetLinkLength = Module._SetLinkLength = function() {
  return (_SetLinkLength = Module._SetLinkLength = Module.asm.j).apply(null, arguments);
};
var _SetRepulsionForce = Module._SetRepulsionForce = function() {
  return (_SetRepulsionForce = Module._SetRepulsionForce = Module.asm.k).apply(null, arguments);
};
var _SetCentralForce = Module._SetCentralForce = function() {
  return (_SetCentralForce = Module._SetCentralForce = Module.asm.l).apply(null, arguments);
};
var _SetDt = Module._SetDt = function() {
  return (_SetDt = Module._SetDt = Module.asm.m).apply(null, arguments);
};
var _Init = Module._Init = function() {
  return (_Init = Module._Init = Module.asm.n).apply(null, arguments);
};
var _Update = Module._Update = function() {
  return (_Update = Module._Update = Module.asm.o).apply(null, arguments);
};
var _SetPosition = Module._SetPosition = function() {
  return (_SetPosition = Module._SetPosition = Module.asm.p).apply(null, arguments);
};
var _FreeMemory = Module._FreeMemory = function() {
  return (_FreeMemory = Module._FreeMemory = Module.asm.q).apply(null, arguments);
};
var ___errno_location = function() {
  return (___errno_location = Module.asm.__errno_location).apply(null, arguments);
};
var _malloc = Module._malloc = function() {
  return (_malloc = Module._malloc = Module.asm.s).apply(null, arguments);
};
var _free = Module._free = function() {
  return (_free = Module._free = Module.asm.t).apply(null, arguments);
};
var stackSave = function() {
  return (stackSave = Module.asm.u).apply(null, arguments);
};
var stackRestore = function() {
  return (stackRestore = Module.asm.v).apply(null, arguments);
};
var stackAlloc = function() {
  return (stackAlloc = Module.asm.w).apply(null, arguments);
};
var ___cxa_is_pointer_type = function() {
  return (___cxa_is_pointer_type = Module.asm.__cxa_is_pointer_type).apply(null, arguments);
};

// Run the module
function run() {
  function doRun() {
    if (!calledRun) {
      calledRun = true;
      Module.calledRun = true;
      if (!ABORT) {
        initRuntime();
        if (Module.onRuntimeInitialized) Module.onRuntimeInitialized();
        postRun();
      }
    }
  }
  if (runDependencies > 0) return;
  preRun();
  if (runDependencies > 0) {
    dependenciesFulfilled = doRun;
    return;
  }
  if (Module.setStatus) {
    Module.setStatus("Running...");
    setTimeout(function() {
      setTimeout(function() {
        Module.setStatus("");
      }, 1);
      doRun();
    }, 1);
  } else {
    doRun();
  }
}
Module.cwrap = cwrap;
Module.setValue = setValue;
Module.getValue = getValue;
dependenciesFulfilled = function() {
  if (!calledRun) run();
};
if (Module.preInit) {
  if (typeof Module.preInit === 'function') Module.preInit = [Module.preInit];
  while (Module.preInit.length) {
    Module.preInit.pop()();
  }
}
try {
  run();
} catch (e) {
  console.error(e);
}
