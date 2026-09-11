/**
 * PIXEL2EDIT - Right Inspector Panel Controller
 */

class AppInspector {
  constructor(editor) {
    this.editor = editor;

    // Elements
    this.emptyState = document.getElementById('inspectorEmpty');
    this.formState = document.getElementById('inspectorForm');
    this.typeBadge = document.getElementById('inspElementType');

    // Content
    this.contentSection = document.getElementById('inspContentSection');
    this.inputContent = document.getElementById('inspContentInput');

    // Geometry
    this.inputPosX = document.getElementById('inspPosX');
    this.inputPosY = document.getElementById('inspPosY');
    this.inputWidth = document.getElementById('inspWidth');
    this.inputHeight = document.getElementById('inspHeight');

    // Typography
    this.typographySection = document.getElementById('inspTypographySection');
    this.selectFontFamily = document.getElementById('inspFontFamily');
    this.inputFontSize = document.getElementById('inspFontSize');
    this.selectFontWeight = document.getElementById('inspFontWeight');

    // Appearance
    this.colorPicker = document.getElementById('inspColorPicker');
    this.colorHex = document.getElementById('inspColorHex');
    this.bgPicker = document.getElementById('inspBgPicker');
    this.bgHex = document.getElementById('inspBgHex');
    this.inputBorderRadius = document.getElementById('inspBorderRadius');
    this.inputBorderWidth = document.getElementById('inspBorderWidth');

    // Padding
    this.padTop = document.getElementById('inspPadTop');
    this.padRight = document.getElementById('inspPadRight');
    this.padBottom = document.getElementById('inspPadBottom');
    this.padLeft = document.getElementById('inspPadLeft');

    // Transform
    this.inputRotation = document.getElementById('inspRotation');
    this.inputOpacity = document.getElementById('inspOpacity');

    // Layers
    this.btnBringFront = document.getElementById('inspBringFront');
    this.btnSendBack = document.getElementById('inspSendBack');

    this.initEvents();
  }

  initEvents() {
    // Content live update
    this.inputContent?.addEventListener('input', (e) => {
      this.editor.updateElementProperty('content', e.target.value);
    });

    // Geometry
    this.inputPosX?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('position.x', parseFloat(e.target.value) || 0);
    });
    this.inputPosY?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('position.y', parseFloat(e.target.value) || 0);
    });
    this.inputWidth?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('size.width', Math.max(10, parseFloat(e.target.value) || 10));
    });
    this.inputHeight?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('size.height', Math.max(10, parseFloat(e.target.value) || 10));
    });

    // Typography
    this.selectFontFamily?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('style.fontFamily', e.target.value);
      window.appToolbar?.syncFromElement(this.editor.getSelectedElement());
    });
    this.inputFontSize?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('style.fontSize', parseFloat(e.target.value) || 32);
      window.appToolbar?.syncFromElement(this.editor.getSelectedElement());
    });
    this.selectFontWeight?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('style.fontWeight', parseInt(e.target.value, 10) || 400);
      window.appToolbar?.syncFromElement(this.editor.getSelectedElement());
    });

    // Colors
    this.colorPicker?.addEventListener('input', (e) => {
      const val = e.target.value;
      if (this.colorHex) this.colorHex.value = val;
      this.editor.updateElementProperty('style.color', val);
      window.appToolbar?.syncFromElement(this.editor.getSelectedElement());
    });
    this.colorHex?.addEventListener('change', (e) => {
      const val = e.target.value;
      if (this.colorPicker && val.startsWith('#')) this.colorPicker.value = val.substring(0, 7);
      this.editor.updateElementProperty('style.color', val);
      window.appToolbar?.syncFromElement(this.editor.getSelectedElement());
    });

    this.bgPicker?.addEventListener('input', (e) => {
      const val = e.target.value;
      if (this.bgHex) this.bgHex.value = val;
      this.editor.updateElementProperty('style.backgroundColor', val);
      window.appToolbar?.syncFromElement(this.editor.getSelectedElement());
    });
    this.bgHex?.addEventListener('change', (e) => {
      const val = e.target.value;
      if (this.bgPicker && val.startsWith('#')) this.bgPicker.value = val.substring(0, 7);
      this.editor.updateElementProperty('style.backgroundColor', val);
      window.appToolbar?.syncFromElement(this.editor.getSelectedElement());
    });

    // Radius & Border
    this.inputBorderRadius?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('style.borderRadius', Math.max(0, parseFloat(e.target.value) || 0));
    });
    this.inputBorderWidth?.addEventListener('change', (e) => {
      const bw = Math.max(0, parseFloat(e.target.value) || 0);
      this.editor.updateElementProperty('style.borderWidth', bw);
      if (bw > 0 && (!this.editor.getSelectedElement()?.style.borderColor || this.editor.getSelectedElement()?.style.borderColor === 'transparent')) {
        this.editor.updateElementProperty('style.borderColor', '#38bdf8');
      }
    });

    // Padding
    this.padTop?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('layout.padding.top', parseFloat(e.target.value) || 0);
    });
    this.padRight?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('layout.padding.right', parseFloat(e.target.value) || 0);
    });
    this.padBottom?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('layout.padding.bottom', parseFloat(e.target.value) || 0);
    });
    this.padLeft?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('layout.padding.left', parseFloat(e.target.value) || 0);
    });

    // Rotation & Opacity
    this.inputRotation?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('transform.rotation', parseFloat(e.target.value) || 0);
    });
    this.inputOpacity?.addEventListener('change', (e) => {
      const val = Math.max(0, Math.min(100, parseFloat(e.target.value) || 100));
      this.editor.updateElementProperty('style.opacity', val / 100.0);
    });

    // Bring to Front / Send to Back
    this.btnBringFront?.addEventListener('click', () => {
      const el = this.editor.getSelectedElement();
      if (!el) return;
      const maxZ = Math.max(...this.editor.designState.elements.map((e) => e.zIndex || 1), 1);
      el.zIndex = maxZ + 1;
      this.editor.updateElementProperty('zIndex', el.zIndex);
      showToast('Moved to top layer', 'info');
    });

    this.btnSendBack?.addEventListener('click', () => {
      const el = this.editor.getSelectedElement();
      if (!el) return;
      const minZ = Math.min(...this.editor.designState.elements.map((e) => e.zIndex || 1), 1);
      el.zIndex = Math.max(0, minZ - 1);
      this.editor.updateElementProperty('zIndex', el.zIndex);
      showToast('Moved to bottom layer', 'info');
    });
  }

  syncFromElement(el) {
    if (!el) {
      this.onElementDeselected();
      return;
    }

    if (this.emptyState) this.emptyState.style.display = 'none';
    if (this.formState) this.formState.style.display = 'block';

    if (this.typeBadge) {
      this.typeBadge.textContent = el.type;
    }

    // Content
    if (this.inputContent) {
      this.inputContent.value = el.content || '';
    }

    // Geometry
    if (this.inputPosX) this.inputPosX.value = Math.round(el.position.x);
    if (this.inputPosY) this.inputPosY.value = Math.round(el.position.y);
    if (this.inputWidth) this.inputWidth.value = Math.round(el.size.width);
    if (this.inputHeight) this.inputHeight.value = Math.round(el.size.height);

    // Typography
    const s = el.style || {};
    if (this.selectFontFamily) this.selectFontFamily.value = s.fontFamily || 'Inter';
    if (this.inputFontSize) this.inputFontSize.value = Math.round(s.fontSize || 32);
    if (this.selectFontWeight) this.selectFontWeight.value = String(s.fontWeight || 400);

    // Appearance
    if (this.colorHex) this.colorHex.value = s.color || '#1e293b';
    if (this.colorPicker && s.color && s.color.startsWith('#')) {
      this.colorPicker.value = s.color.substring(0, 7);
    }

    if (this.bgHex) this.bgHex.value = s.backgroundColor || 'transparent';
    if (this.bgPicker && s.backgroundColor && s.backgroundColor.startsWith('#')) {
      this.bgPicker.value = s.backgroundColor.substring(0, 7);
    }

    if (this.inputBorderRadius) this.inputBorderRadius.value = s.borderRadius || 0;
    if (this.inputBorderWidth) this.inputBorderWidth.value = s.borderWidth || 0;

    // Padding
    const p = el.layout?.padding || {};
    if (this.padTop) this.padTop.value = p.top || 0;
    if (this.padRight) this.padRight.value = p.right || 0;
    if (this.padBottom) this.padBottom.value = p.bottom || 0;
    if (this.padLeft) this.padLeft.value = p.left || 0;

    // Rotation & Opacity
    if (this.inputRotation) this.inputRotation.value = el.transform?.rotation || 0;
    if (this.inputOpacity) this.inputOpacity.value = Math.round((s.opacity !== undefined ? s.opacity : 1.0) * 100);
  }

  updatePositionInputs(x, y) {
    if (this.inputPosX) this.inputPosX.value = Math.round(x);
    if (this.inputPosY) this.inputPosY.value = Math.round(y);
  }

  updateGeometryInputs(x, y, w, h) {
    if (this.inputPosX) this.inputPosX.value = Math.round(x);
    if (this.inputPosY) this.inputPosY.value = Math.round(y);
    if (this.inputWidth) this.inputWidth.value = Math.round(w);
    if (this.inputHeight) this.inputHeight.value = Math.round(h);
  }

  updateContentInput(text) {
    if (this.inputContent) this.inputContent.value = text;
  }

  updateColorInputs(color, bgColor) {
    if (color && this.colorHex) {
      this.colorHex.value = color;
      if (this.colorPicker && color.startsWith('#')) this.colorPicker.value = color.substring(0, 7);
    }
    if (bgColor && this.bgHex) {
      this.bgHex.value = bgColor;
      if (this.bgPicker && bgColor.startsWith('#')) this.bgPicker.value = bgColor.substring(0, 7);
    }
  }

  onElementDeselected() {
    if (this.emptyState) this.emptyState.style.display = 'flex';
    if (this.formState) this.formState.style.display = 'none';
    if (this.typeBadge) this.typeBadge.textContent = 'None Selected';
  }
}

window.AppInspector = AppInspector;
