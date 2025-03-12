document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.drag-handle').forEach(handle => {
      handle.addEventListener('mousedown', initDrag, false);
    });
  });
  
  let currentHandle = null;
  
  function initDrag(e) {
    currentHandle = e.target;
    document.body.classList.add("no-select");
    document.documentElement.classList.add("no-select");
    document.addEventListener('mousemove', doDrag, false);
    document.addEventListener('mouseup', stopDrag, false);
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
    if (!currentHandle) return;
    document.removeEventListener('mousemove', doDrag, false);
    document.removeEventListener('mouseup', stopDrag, false);
    document.body.classList.remove("no-select");
    document.documentElement.classList.remove("no-select");
    currentHandle = null;
  }
  