/**
 * PIXEL2EDIT - Core Editor Engine
 * Single Source of Truth: designState
 */

class DesignEditor {
  constructor() {
    this.designState = {
      canvas: { width: 1080, height: 1350, background: '#ffffff' },
      elements: []
    };
    this.originalImageUrl = '';
    this.selectedElementId = null;

    // Viewport & Zoom
    this.zoomScale = 1.0;
    this.isFitZoom = true;
    this.viewMode = 'side-by-side'; // 'side-by-side' or 'overlay'
    this.overlayOpacity = 0.5;

    // History Stack for Undo / Redo
    this.historyStack = [];
    this.historyIndex = -1;
    this.maxHistory = 50;

    // Drag & Resize State
    this.dragState = null;
    this.resizeState = null;

    // DOM Elements
    this.canvasContainer = document.getElementById('designCanvas');
    this.elementsLayer = document.getElementById('canvasElementsLayer');
    this.selectionOverlay = document.getElementById('selectionOverlay');
    this.selectionTag = document.getElementById('selectionTag');
    this.editableViewport = document.getElementById('editableViewport');
    this.originalViewport = document.getElementById('originalViewport');
    this.originalImage = document.getElementById('originalReferenceImage');
    this.canvasOverlayImage = document.getElementById('canvasOverlayImage');
    this.overlayImageElement = document.getElementById('overlayImageElement');
    this.overlaySliderBar = document.getElementById('overlaySliderBar');
    this.overlayOpacitySlider = document.getElementById('overlayOpacitySlider');
    this.overlayOpacityValue = document.getElementById('overlayOpacityValue');

    this.initEvents();
  }

  loadDesign(design, imageUrl) {
    this.designState = JSON.parse(JSON.stringify(design));
    this.originalImageUrl = imageUrl;
    this.selectedElementId = null;

    // Reset history
    this.historyStack = [JSON.parse(JSON.stringify(this.designState))];
    this.historyIndex = 0;
    this.updateUndoRedoButtons();

    // Set images
    if (this.originalImage) this.originalImage.src = imageUrl;
    if (this.overlayImageElement) this.overlayImageElement.src = imageUrl;

    // Update labels
    const dimText = `${this.designState.canvas.width} × ${this.designState.canvas.height} px`;
    const origDim = document.getElementById('originalDimensionsLabel');
    const editDim = document.getElementById('editableDimensionsLabel');
    if (origDim) origDim.textContent = dimText;
    if (editDim) editDim.textContent = dimText;

    // Set fixed canvas size
    this.canvasContainer.style.width = `${this.designState.canvas.width}px`;
    this.canvasContainer.style.height = `${this.designState.canvas.height}px`;
    this.canvasContainer.style.backgroundColor = this.designState.canvas.background || '#ffffff';

    if (this.originalImage) {
      this.originalImage.style.width = `${this.designState.canvas.width}px`;
      this.originalImage.style.height = `${this.designState.canvas.height}px`;
    }

    this.renderElements();
    this.applyZoom();

    // Auto-select first element if available
    if (this.designState.elements.length > 0) {
      this.selectElement(this.designState.elements[0].id);
    }
  }

  pushHistoryState() {
    // If we branched off from a previous point, discard forward history
    if (this.historyIndex < this.historyStack.length - 1) {
      this.historyStack = this.historyStack.slice(0, this.historyIndex + 1);
    }

    this.historyStack.push(JSON.parse(JSON.stringify(this.designState)));
    if (this.historyStack.length > this.maxHistory) {
      this.historyStack.shift();
    } else {
      this.historyIndex++;
    }

    this.updateUndoRedoButtons();
  }

  undo() {
    if (this.historyIndex > 0) {
      this.historyIndex--;
      this.designState = JSON.parse(JSON.stringify(this.historyStack[this.historyIndex]));
      this.renderElements();
      if (this.selectedElementId) {
        this.updateSelectionBox();
        window.appToolbar?.syncFromElement(this.getSelectedElement());
        window.appInspector?.syncFromElement(this.getSelectedElement());
      }
      this.updateUndoRedoButtons();
      showToast('Undo', 'info');
    }
  }

  redo() {
    if (this.historyIndex < this.historyStack.length - 1) {
      this.historyIndex++;
      this.designState = JSON.parse(JSON.stringify(this.historyStack[this.historyIndex]));
      this.renderElements();
      if (this.selectedElementId) {
        this.updateSelectionBox();
        window.appToolbar?.syncFromElement(this.getSelectedElement());
        window.appInspector?.syncFromElement(this.getSelectedElement());
      }
      this.updateUndoRedoButtons();
      showToast('Redo', 'info');
    }
  }

  updateUndoRedoButtons() {
    const btnUndo = document.getElementById('tbUndo');
    const btnRedo = document.getElementById('tbRedo');
    if (btnUndo) btnUndo.disabled = (this.historyIndex <= 0);
    if (btnRedo) btnRedo.disabled = (this.historyIndex >= this.historyStack.length - 1);
  }

  renderElements() {
    this.elementsLayer.innerHTML = '';

    this.designState.elements.forEach((el) => {
      const elNode = document.createElement('div');
      elNode.id = `canvas_el_${el.id}`;
      elNode.className = `canvas-element element-type-${el.type}`;
      elNode.dataset.id = el.id;

      this.applyElementStyles(elNode, el);

      // Inner text wrapper
      const textSpan = document.createElement('div');
      textSpan.className = 'canvas-element-text';
      textSpan.textContent = el.content || '';
      elNode.appendChild(textSpan);

      // Click to select
      elNode.addEventListener('mousedown', (e) => {
        // Prevent selection clear from canvas click
        e.stopPropagation();
        this.selectElement(el.id);
        this.startDrag(e, el.id);
      });

      // Double-click to edit text inline
      elNode.addEventListener('dblclick', (e) => {
        e.stopPropagation();
        this.startInlineEditing(el.id, textSpan);
      });

      this.elementsLayer.appendChild(elNode);
    });

    if (this.selectedElementId) {
      this.updateSelectionBox();
    } else {
      this.hideSelectionBox();
    }
  }

  applyElementStyles(node, el) {
    const { position, size, style, transform, layout, zIndex } = el;
    node.style.left = `${position.x}px`;
    node.style.top = `${position.y}px`;
    node.style.width = `${size.width}px`;
    node.style.height = `${size.height}px`;
    node.style.fontFamily = `'${style.fontFamily || 'Inter'}', sans-serif`;
    node.style.fontSize = `${style.fontSize || 32}px`;
    node.style.fontWeight = style.fontWeight || 400;
    node.style.fontStyle = style.fontStyle || 'normal';
    node.style.textDecoration = style.textDecoration || 'none';
    node.style.color = style.color || '#1e293b';
    node.style.backgroundColor = style.backgroundColor || 'transparent';
    node.style.borderRadius = `${style.borderRadius || 0}px`;
    node.style.border = `${style.borderWidth || 0}px solid ${style.borderColor || 'transparent'}`;
    node.style.textAlign = style.textAlign || 'left';
    node.style.lineHeight = style.lineHeight || 1.2;
    node.style.letterSpacing = `${style.letterSpacing || 0}px`;
    node.style.textTransform = style.textTransform || 'none';
    node.style.opacity = style.opacity !== undefined ? style.opacity : 1.0;
    node.style.zIndex = zIndex || 1;

    // Button specific whitespace
    if (el.type === 'button') {
      node.style.whiteSpace = 'nowrap';
    } else {
      node.style.whiteSpace = 'pre-wrap';
    }

    // Padding
    if (layout?.padding) {
      const p = layout.padding;
      node.style.padding = `${p.top || 0}px ${p.right || 0}px ${p.bottom || 0}px ${p.left || 0}px`;
    }

    // Alignment within flexbox
    if (style.textAlign === 'center') {
      node.style.justifyContent = 'center';
    } else if (style.textAlign === 'right') {
      node.style.justifyContent = 'flex-end';
    } else {
      node.style.justifyContent = 'flex-start';
    }

    if (el.type === 'button') {
      node.style.alignItems = 'center';
    } else {
      node.style.alignItems = 'flex-start';
    }

    // Rotation
    if (transform?.rotation) {
      node.style.transform = `rotate(${transform.rotation}deg)`;
    } else {
      node.style.transform = 'none';
    }
  }

  selectElement(elementId) {
    this.selectedElementId = elementId;

    // Deselect all
    document.querySelectorAll('.canvas-element').forEach((n) => n.classList.remove('selected'));

    const el = this.getSelectedElement();
    if (!el) {
      this.hideSelectionBox();
      window.appToolbar?.onElementDeselected();
      window.appInspector?.onElementDeselected();
      return;
    }

    const node = document.getElementById(`canvas_el_${elementId}`);
    if (node) node.classList.add('selected');

    this.updateSelectionBox();

    // Sync Toolbar and Inspector
    window.appToolbar?.syncFromElement(el);
    window.appInspector?.syncFromElement(el);
  }

  deselectAll() {
    this.selectedElementId = null;
    document.querySelectorAll('.canvas-element').forEach((n) => n.classList.remove('selected'));
    this.hideSelectionBox();
    window.appToolbar?.onElementDeselected();
    window.appInspector?.onElementDeselected();
  }

  getSelectedElement() {
    if (!this.selectedElementId) return null;
    return this.designState.elements.find((e) => e.id === this.selectedElementId) || null;
  }

  updateSelectionBox() {
    const el = this.getSelectedElement();
    if (!el) {
      this.hideSelectionBox();
      return;
    }

    this.selectionOverlay.style.display = 'block';
    this.selectionOverlay.style.left = `${el.position.x}px`;
    this.selectionOverlay.style.top = `${el.position.y}px`;
    this.selectionOverlay.style.width = `${el.size.width}px`;
    this.selectionOverlay.style.height = `${el.size.height}px`;

    if (el.transform?.rotation) {
      this.selectionOverlay.style.transform = `rotate(${el.transform.rotation}deg)`;
    } else {
      this.selectionOverlay.style.transform = 'none';
    }

    if (this.selectionTag) {
      this.selectionTag.textContent = `${el.type.toUpperCase()}`;
    }
  }

  hideSelectionBox() {
    if (this.selectionOverlay) {
      this.selectionOverlay.style.display = 'none';
    }
  }

  // ==========================================================
  // Dragging & Moving Elements
  // ==========================================================
  startDrag(e, elementId) {
    if (e.button !== 0) return; // Primary mouse button only
    const el = this.designState.elements.find((item) => item.id === elementId);
    if (!el) return;

    this.dragState = {
      elementId,
      startX: e.clientX,
      startY: e.clientY,
      initialPosX: el.position.x,
      initialPosY: el.position.y,
      hasMoved: false
    };

    const onMouseMove = (moveEvent) => {
      if (!this.dragState) return;
      const dx = (moveEvent.clientX - this.dragState.startX) / this.zoomScale;
      const dy = (moveEvent.clientY - this.dragState.startY) / this.zoomScale;

      if (Math.abs(dx) > 2 || Math.abs(dy) > 2) {
        this.dragState.hasMoved = true;
      }

      el.position.x = Math.round(this.dragState.initialPosX + dx);
      el.position.y = Math.round(this.dragState.initialPosY + dy);

      const node = document.getElementById(`canvas_el_${el.id}`);
      if (node) {
        node.style.left = `${el.position.x}px`;
        node.style.top = `${el.position.y}px`;
      }

      this.updateSelectionBox();
      window.appInspector?.updatePositionInputs(el.position.x, el.position.y);
    };

    const onMouseUp = () => {
      if (this.dragState && this.dragState.hasMoved) {
        this.pushHistoryState();
      }
      this.dragState = null;
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }

  // ==========================================================
  // Resizing Elements
  // ==========================================================
  startResize(e, handleType) {
    e.stopPropagation();
    e.preventDefault();
    const el = this.getSelectedElement();
    if (!el) return;

    this.resizeState = {
      handle: handleType,
      startX: e.clientX,
      startY: e.clientY,
      initialX: el.position.x,
      initialY: el.position.y,
      initialWidth: el.size.width,
      initialHeight: el.size.height,
      hasResized: false
    };

    const onMouseMove = (moveEvent) => {
      if (!this.resizeState) return;
      const dx = (moveEvent.clientX - this.resizeState.startX) / this.zoomScale;
      const dy = (moveEvent.clientY - this.resizeState.startY) / this.zoomScale;

      let newX = this.resizeState.initialX;
      let newY = this.resizeState.initialY;
      let newW = this.resizeState.initialWidth;
      let newH = this.resizeState.initialHeight;

      if (handleType.includes('e')) newW = Math.max(20, this.resizeState.initialWidth + dx);
      if (handleType.includes('s')) newH = Math.max(15, this.resizeState.initialHeight + dy);
      if (handleType.includes('w')) {
        const potentialW = this.resizeState.initialWidth - dx;
        if (potentialW >= 20) {
          newW = potentialW;
          newX = this.resizeState.initialX + dx;
        }
      }
      if (handleType.includes('n')) {
        const potentialH = this.resizeState.initialHeight - dy;
        if (potentialH >= 15) {
          newH = potentialH;
          newY = this.resizeState.initialY + dy;
        }
      }

      el.position.x = Math.round(newX);
      el.position.y = Math.round(newY);
      el.size.width = Math.round(newW);
      el.size.height = Math.round(newH);
      this.resizeState.hasResized = true;

      const node = document.getElementById(`canvas_el_${el.id}`);
      if (node) {
        node.style.left = `${el.position.x}px`;
        node.style.top = `${el.position.y}px`;
        node.style.width = `${el.size.width}px`;
        node.style.height = `${el.size.height}px`;
      }

      this.updateSelectionBox();
      window.appInspector?.updateGeometryInputs(el.position.x, el.position.y, el.size.width, el.size.height);
    };

    const onMouseUp = () => {
      if (this.resizeState && this.resizeState.hasResized) {
        this.pushHistoryState();
      }
      this.resizeState = null;
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }

  // ==========================================================
  // Double-Click Inline Text Editing
  // ==========================================================
  startInlineEditing(elementId, textSpanNode) {
    const el = this.designState.elements.find((item) => item.id === elementId);
    if (!el) return;

    textSpanNode.contentEditable = 'true';
    textSpanNode.focus();

    // Select all text inside
    const range = document.createRange();
    range.selectNodeContents(textSpanNode);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);

    const onBlurOrDone = () => {
      textSpanNode.contentEditable = 'false';
      const updatedText = textSpanNode.textContent;
      if (updatedText !== el.content) {
        el.content = updatedText;
        this.pushHistoryState();
        window.appInspector?.updateContentInput(updatedText);
      }
      textSpanNode.removeEventListener('blur', onBlurOrDone);
      textSpanNode.removeEventListener('keydown', onKeyDown);
    };

    const onKeyDown = (kEvent) => {
      if (kEvent.key === 'Enter' && !kEvent.shiftKey) {
        kEvent.preventDefault();
        textSpanNode.blur();
      } else if (kEvent.key === 'Escape') {
        textSpanNode.textContent = el.content;
        textSpanNode.blur();
      }
    };

    textSpanNode.addEventListener('blur', onBlurOrDone);
    textSpanNode.addEventListener('keydown', onKeyDown);
  }

  // ==========================================================
  // Updating Element Property and State Mutation
  // ==========================================================
  updateElementProperty(path, value) {
    const el = this.getSelectedElement();
    if (!el) return;

    // e.g. path = 'style.fontSize'
    const parts = path.split('.');
    let target = el;
    for (let i = 0; i < parts.length - 1; i++) {
      if (!target[parts[i]]) target[parts[i]] = {};
      target = target[parts[i]];
    }
    target[parts[parts.length - 1]] = value;

    const node = document.getElementById(`canvas_el_${el.id}`);
    if (node) {
      this.applyElementStyles(node, el);
      if (path === 'content') {
        const span = node.querySelector('.canvas-element-text');
        if (span) span.textContent = value;
      }
    }

    this.updateSelectionBox();
    this.pushHistoryState();
  }

  applyPatch(patch) {
    const { elementId, changes } = patch;
    const el = this.designState.elements.find((e) => e.id === elementId);
    if (!el) return;

    if (changes.content !== undefined) el.content = changes.content;
    if (changes.position) {
      if (changes.position.x !== undefined) el.position.x = changes.position.x;
      if (changes.position.y !== undefined) el.position.y = changes.position.y;
    }
    if (changes.size) {
      if (changes.size.width !== undefined) el.size.width = changes.size.width;
      if (changes.size.height !== undefined) el.size.height = changes.size.height;
    }
    if (changes.style) {
      Object.assign(el.style, changes.style);
    }
    if (changes.transform) {
      Object.assign(el.transform, changes.transform);
    }

    const node = document.getElementById(`canvas_el_${el.id}`);
    if (node) {
      this.applyElementStyles(node, el);
      if (changes.content !== undefined) {
        const span = node.querySelector('.canvas-element-text');
        if (span) span.textContent = changes.content;
      }
    }

    this.selectElement(el.id);
    this.pushHistoryState();
  }

  deleteSelectedElement() {
    if (!this.selectedElementId) return;
    const idx = this.designState.elements.findIndex((e) => e.id === this.selectedElementId);
    if (idx !== -1) {
      this.designState.elements.splice(idx, 1);
      this.selectedElementId = null;
      this.renderElements();
      window.appToolbar?.onElementDeselected();
      window.appInspector?.onElementDeselected();
      this.pushHistoryState();
      showToast('Element deleted', 'info');
    }
  }

  // ==========================================================
  // Zoom & Viewport Scaling
  // ==========================================================
  applyZoom() {
    const displayLabel = document.getElementById('zoomLevelDisplay');

    if (this.isFitZoom) {
      const scrollArea = document.getElementById('editableScrollArea');
      if (scrollArea && this.designState.canvas.width) {
        const availW = scrollArea.clientWidth - 64;
        const availH = scrollArea.clientHeight - 64;
        const fitScaleX = availW / this.designState.canvas.width;
        const fitScaleY = availH / this.designState.canvas.height;
        this.zoomScale = Math.min(fitScaleX, fitScaleY, 1.0);
        this.zoomScale = Math.max(0.15, this.zoomScale);
      }
      if (displayLabel) displayLabel.textContent = `${Math.round(this.zoomScale * 100)}%`;
    } else {
      if (displayLabel) displayLabel.textContent = `${Math.round(this.zoomScale * 100)}%`;
    }

    const transformStr = `scale(${this.zoomScale})`;
    if (this.editableViewport) this.editableViewport.style.transform = transformStr;
    if (this.originalViewport) this.originalViewport.style.transform = transformStr;
  }

  zoomIn() {
    this.isFitZoom = false;
    this.zoomScale = Math.min(3.0, this.zoomScale + 0.15);
    this.applyZoom();
  }

  zoomOut() {
    this.isFitZoom = false;
    this.zoomScale = Math.max(0.2, this.zoomScale - 0.15);
    this.applyZoom();
  }

  zoomFit() {
    this.isFitZoom = true;
    this.applyZoom();
  }

  // ==========================================================
  // Event Bindings
  // ==========================================================
  initEvents() {
    // Deselect clicking canvas background
    this.canvasContainer?.addEventListener('mousedown', (e) => {
      if (e.target === this.canvasContainer || e.target === this.elementsLayer) {
        this.deselectAll();
      }
    });

    // Resize Handles
    document.querySelectorAll('.handle').forEach((h) => {
      h.addEventListener('mousedown', (e) => {
        this.startResize(e, h.dataset.handle);
      });
    });

    // Zoom Buttons
    document.getElementById('zoomInBtn')?.addEventListener('click', () => this.zoomIn());
    document.getElementById('zoomOutBtn')?.addEventListener('click', () => this.zoomOut());
    document.getElementById('zoomFitBtn')?.addEventListener('click', () => this.zoomFit());

    // Window Resize recalculates fit
    window.addEventListener('resize', () => {
      if (this.isFitZoom) this.applyZoom();
    });

    // Undo / Redo buttons
    document.getElementById('tbUndo')?.addEventListener('click', () => this.undo());
    document.getElementById('tbRedo')?.addEventListener('click', () => this.redo());

    // Delete Button
    document.getElementById('tbDeleteElement')?.addEventListener('click', () => this.deleteSelectedElement());
    document.getElementById('inspDeleteBtn')?.addEventListener('click', () => this.deleteSelectedElement());

    // Keyboard Shortcuts (Delete, Undo, Redo, Esc)
    window.addEventListener('keydown', (e) => {
      // Ignore if typing in text inputs or textareas
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName) || e.target.isContentEditable) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        if (e.shiftKey) {
          this.redo();
        } else {
          this.undo();
        }
      } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') {
        e.preventDefault();
        this.redo();
      } else if (e.key === 'Delete' || e.key === 'Backspace') {
        if (this.selectedElementId) {
          e.preventDefault();
          this.deleteSelectedElement();
        }
      } else if (e.key === 'Escape') {
        this.deselectAll();
      } else if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key) && this.selectedElementId) {
        // Pixel nudging
        e.preventDefault();
        const step = e.shiftKey ? 10 : 1;
        const el = this.getSelectedElement();
        if (el) {
          if (e.key === 'ArrowUp') el.position.y -= step;
          if (e.key === 'ArrowDown') el.position.y += step;
          if (e.key === 'ArrowLeft') el.position.x -= step;
          if (e.key === 'ArrowRight') el.position.x += step;

          const node = document.getElementById(`canvas_el_${el.id}`);
          if (node) {
            node.style.left = `${el.position.x}px`;
            node.style.top = `${el.position.y}px`;
          }
          this.updateSelectionBox();
          window.appInspector?.updatePositionInputs(el.position.x, el.position.y);
          this.pushHistoryState();
        }
      }
    });

    // View Modes: Side-by-Side vs Overlay
    document.getElementById('btnSideBySide')?.addEventListener('click', () => this.setViewMode('side-by-side'));
    document.getElementById('btnOverlay')?.addEventListener('click', () => this.setViewMode('overlay'));

    // Overlay Opacity Slider
    this.overlayOpacitySlider?.addEventListener('input', (e) => {
      const val = parseInt(e.target.value, 10);
      this.overlayOpacity = val / 100.0;
      if (this.overlayOpacityValue) this.overlayOpacityValue.textContent = `${val}%`;
      if (this.canvasOverlayImage) this.canvasOverlayImage.style.opacity = this.overlayOpacity;
    });

    // Mobile View Toggle
    document.getElementById('btnShowOriginal')?.addEventListener('click', () => this.setMobilePane('original'));
    document.getElementById('btnShowEditable')?.addEventListener('click', () => this.setMobilePane('editable'));
  }

  setViewMode(mode) {
    this.viewMode = mode;
    const btnSide = document.getElementById('btnSideBySide');
    const btnOverlay = document.getElementById('btnOverlay');
    const paneOriginal = document.getElementById('paneOriginal');

    if (mode === 'overlay') {
      btnOverlay?.classList.add('active');
      btnSide?.classList.remove('active');
      if (this.overlaySliderBar) this.overlaySliderBar.style.display = 'flex';
      if (this.canvasOverlayImage) {
        this.canvasOverlayImage.style.display = 'block';
        this.canvasOverlayImage.style.opacity = this.overlayOpacity;
      }
      if (paneOriginal) paneOriginal.style.display = 'none';
    } else {
      btnSide?.classList.add('active');
      btnOverlay?.classList.remove('active');
      if (this.overlaySliderBar) this.overlaySliderBar.style.display = 'none';
      if (this.canvasOverlayImage) this.canvasOverlayImage.style.display = 'none';
      if (paneOriginal) paneOriginal.style.display = 'flex';
    }

    this.applyZoom();
  }

  setMobilePane(pane) {
    const paneOriginal = document.getElementById('paneOriginal');
    const paneEditable = document.getElementById('paneEditable');
    const btnOrig = document.getElementById('btnShowOriginal');
    const btnEdit = document.getElementById('btnShowEditable');

    if (pane === 'original') {
      btnOrig?.classList.add('active');
      btnEdit?.classList.remove('active');
      paneOriginal?.classList.remove('mobile-hidden');
      paneEditable?.classList.add('mobile-hidden');
    } else {
      btnEdit?.classList.add('active');
      btnOrig?.classList.remove('active');
      paneEditable?.classList.remove('mobile-hidden');
      paneOriginal?.classList.add('mobile-hidden');
    }
  }
}

// Global Toast utility
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2800);
}

window.DesignEditor = DesignEditor;
