/**
 * PIXEL2EDIT - Formatting Toolbar Controller
 */

class AppToolbar {
  constructor(editor) {
    this.editor = editor;

    // Controls
    this.btnBold = document.getElementById('tbBold');
    this.btnItalic = document.getElementById('tbItalic');
    this.btnUnderline = document.getElementById('tbUnderline');
    this.selectFontFamily = document.getElementById('tbFontFamily');
    this.inputFontSize = document.getElementById('tbFontSize');
    this.btnFontSizeDec = document.getElementById('tbFontSizeDec');
    this.btnFontSizeInc = document.getElementById('tbFontSizeInc');
    this.inputTextColor = document.getElementById('tbTextColor');
    this.textColorBar = document.getElementById('tbTextColorBar');
    this.inputBgColor = document.getElementById('tbBgColor');
    this.bgColorBar = document.getElementById('tbBgColorBar');
    this.btnAlignLeft = document.getElementById('tbAlignLeft');
    this.btnAlignCenter = document.getElementById('tbAlignCenter');
    this.btnAlignRight = document.getElementById('tbAlignRight');
    this.selectTextTransform = document.getElementById('tbTextTransform');
    this.inputLetterSpacing = document.getElementById('tbLetterSpacing');

    this.initEvents();
  }

  initEvents() {
    // Bold
    this.btnBold?.addEventListener('click', () => {
      const el = this.editor.getSelectedElement();
      if (!el) return;
      const isBold = (el.style.fontWeight || 400) >= 700;
      const newWeight = isBold ? 400 : 700;
      this.editor.updateElementProperty('style.fontWeight', newWeight);
      this.btnBold.classList.toggle('active', !isBold);
      window.appInspector?.syncFromElement(el);
    });

    // Italic
    this.btnItalic?.addEventListener('click', () => {
      const el = this.editor.getSelectedElement();
      if (!el) return;
      const isItalic = (el.style.fontStyle || 'normal') === 'italic';
      const newStyle = isItalic ? 'normal' : 'italic';
      this.editor.updateElementProperty('style.fontStyle', newStyle);
      this.btnItalic.classList.toggle('active', !isItalic);
      window.appInspector?.syncFromElement(el);
    });

    // Underline
    this.btnUnderline?.addEventListener('click', () => {
      const el = this.editor.getSelectedElement();
      if (!el) return;
      const isUnder = (el.style.textDecoration || 'none') === 'underline';
      const newDecor = isUnder ? 'none' : 'underline';
      this.editor.updateElementProperty('style.textDecoration', newDecor);
      this.btnUnderline.classList.toggle('active', !isUnder);
      window.appInspector?.syncFromElement(el);
    });

    // Font Family
    this.selectFontFamily?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('style.fontFamily', e.target.value);
      window.appInspector?.syncFromElement(this.editor.getSelectedElement());
    });

    // Font Size Steppers & Input
    this.inputFontSize?.addEventListener('change', (e) => {
      const val = Math.max(8, Math.min(250, parseInt(e.target.value, 10) || 32));
      this.editor.updateElementProperty('style.fontSize', val);
      window.appInspector?.syncFromElement(this.editor.getSelectedElement());
    });

    this.btnFontSizeDec?.addEventListener('click', () => {
      const el = this.editor.getSelectedElement();
      if (!el) return;
      const curr = parseInt(el.style.fontSize || 32, 10);
      const next = Math.max(8, curr - 2);
      this.inputFontSize.value = next;
      this.editor.updateElementProperty('style.fontSize', next);
      window.appInspector?.syncFromElement(el);
    });

    this.btnFontSizeInc?.addEventListener('click', () => {
      const el = this.editor.getSelectedElement();
      if (!el) return;
      const curr = parseInt(el.style.fontSize || 32, 10);
      const next = Math.min(250, curr + 2);
      this.inputFontSize.value = next;
      this.editor.updateElementProperty('style.fontSize', next);
      window.appInspector?.syncFromElement(el);
    });

    // Text Color
    this.inputTextColor?.addEventListener('input', (e) => {
      const val = e.target.value;
      if (this.textColorBar) this.textColorBar.style.backgroundColor = val;
      this.editor.updateElementProperty('style.color', val);
      window.appInspector?.updateColorInputs(val, null);
    });

    // Background Color
    this.inputBgColor?.addEventListener('input', (e) => {
      const val = e.target.value;
      if (this.bgColorBar) this.bgColorBar.style.backgroundColor = val;
      this.editor.updateElementProperty('style.backgroundColor', val);
      window.appInspector?.updateColorInputs(null, val);
    });

    // Alignment
    this.btnAlignLeft?.addEventListener('click', () => this.setAlignment('left'));
    this.btnAlignCenter?.addEventListener('click', () => this.setAlignment('center'));
    this.btnAlignRight?.addEventListener('click', () => this.setAlignment('right'));

    // Text Transform
    this.selectTextTransform?.addEventListener('change', (e) => {
      this.editor.updateElementProperty('style.textTransform', e.target.value);
      window.appInspector?.syncFromElement(this.editor.getSelectedElement());
    });

    // Letter Spacing
    this.inputLetterSpacing?.addEventListener('change', (e) => {
      const val = parseFloat(e.target.value) || 0;
      this.editor.updateElementProperty('style.letterSpacing', val);
      window.appInspector?.syncFromElement(this.editor.getSelectedElement());
    });
  }

  setAlignment(align) {
    this.btnAlignLeft?.classList.toggle('active', align === 'left');
    this.btnAlignCenter?.classList.toggle('active', align === 'center');
    this.btnAlignRight?.classList.toggle('active', align === 'right');
    this.editor.updateElementProperty('style.textAlign', align);
    window.appInspector?.syncFromElement(this.editor.getSelectedElement());
  }

  syncFromElement(el) {
    if (!el) return;

    const s = el.style || {};

    // Bold, Italic, Underline
    this.btnBold?.classList.toggle('active', (s.fontWeight || 400) >= 700);
    this.btnItalic?.classList.toggle('active', (s.fontStyle || 'normal') === 'italic');
    this.btnUnderline?.classList.toggle('active', (s.textDecoration || 'none') === 'underline');

    // Font Family
    if (this.selectFontFamily) this.selectFontFamily.value = s.fontFamily || 'Inter';

    // Font Size
    if (this.inputFontSize) this.inputFontSize.value = Math.round(s.fontSize || 32);

    // Text Color
    if (this.inputTextColor && s.color && s.color.startsWith('#')) {
      this.inputTextColor.value = s.color.substring(0, 7);
      if (this.textColorBar) this.textColorBar.style.backgroundColor = s.color;
    }

    // Background Color
    if (this.inputBgColor && s.backgroundColor && s.backgroundColor.startsWith('#')) {
      this.inputBgColor.value = s.backgroundColor.substring(0, 7);
      if (this.bgColorBar) this.bgColorBar.style.backgroundColor = s.backgroundColor;
    }

    // Alignments
    const align = s.textAlign || 'left';
    this.btnAlignLeft?.classList.toggle('active', align === 'left');
    this.btnAlignCenter?.classList.toggle('active', align === 'center');
    this.btnAlignRight?.classList.toggle('active', align === 'right');

    // Text Transform
    if (this.selectTextTransform) this.selectTextTransform.value = s.textTransform || 'none';

    // Letter Spacing
    if (this.inputLetterSpacing) this.inputLetterSpacing.value = s.letterSpacing || 0;
  }

  onElementDeselected() {
    this.btnBold?.classList.remove('active');
    this.btnItalic?.classList.remove('active');
    this.btnUnderline?.classList.remove('active');
    this.btnAlignLeft?.classList.remove('active');
    this.btnAlignCenter?.classList.remove('active');
    this.btnAlignRight?.classList.remove('active');
  }
}

window.AppToolbar = AppToolbar;
