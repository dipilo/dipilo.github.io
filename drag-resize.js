// Attach event listeners to all drag handles
document.querySelectorAll('.drag-handle').forEach(handle => {
  handle.addEventListener('mousedown', initDrag, false);
});

let currentHandle = null;

function initDrag(e) {
  currentHandle = e.target;
  window.addEventListener('mousemove', doDrag, false);
  window.addEventListener('mouseup', stopDrag, false);
}

function doDrag(e) {
  if (!currentHandle) return;
  const container = currentHandle.parentElement;
  const containerRect = container.getBoundingClientRect();
  // Calculate new height from mouse position relative to container top
  const newHeight = e.clientY - containerRect.top;
  if (newHeight > 300) {  // enforce minimum height
    container.style.height = newHeight + 'px';
  }
}

function stopDrag() {
  window.removeEventListener('mousemove', doDrag, false);
  window.removeEventListener('mouseup', stopDrag, false);
  currentHandle = null;
}
