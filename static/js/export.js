/**
 * PIXEL2EDIT - Export Controller (HTML, JSON, PNG, PDF)
 * Guarantees 100% deformation-free exports matching exact canvas geometry.
 */

class ExportController {
  constructor(editor) {
    this.editor = editor;

    this.mainBtn = document.getElementById('exportMainBtn');
    this.menu = document.getElementById('exportMenu');
    this.btnHtml = document.getElementById('exportHtmlBtn');
    this.btnJson = document.getElementById('exportJsonBtn');
    this.btnPng = document.getElementById('exportPngBtn');
    this.btnPdf = document.getElementById('exportPdfBtn');

    this.initEvents();
  }

  initEvents() {
    this.mainBtn?.addEventListener('click', (e) => {
      e.stopPropagation();
      this.menu?.classList.toggle('show');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.mainBtn?.contains(e.target) && !this.menu?.contains(e.target)) {
        this.menu?.classList.remove('show');
      }
    });

    this.btnHtml?.addEventListener('click', () => {
      this.menu?.classList.remove('show');
      this.exportHtml();
    });

    this.btnJson?.addEventListener('click', () => {
      this.menu?.classList.remove('show');
      this.exportJson();
    });

    this.btnPng?.addEventListener('click', () => {
      this.menu?.classList.remove('show');
      this.exportPng();
    });

    this.btnPdf?.addEventListener('click', () => {
      this.menu?.classList.remove('show');
      this.exportPdf();
    });
  }

  /**
   * Captures the design canvas completely unscaled without viewport transform distortions.
   * Ensures all fonts are fully loaded and layout reflow is complete before capture.
   */
  async captureCanvasUnscaled(scaleFactor = 2) {
    if (typeof html2canvas === 'undefined') {
      throw new Error('Canvas render engine (html2canvas) is not loaded.');
    }

    const canvasNode = document.getElementById('designCanvas');
    const viewport = document.getElementById('editableViewport');
    if (!canvasNode) throw new Error('Canvas element not found.');

    // 1. Temporarily hide interactive selection overlay
    const selectionOverlay = document.getElementById('selectionOverlay');
    const prevOverlayDisplay = selectionOverlay ? selectionOverlay.style.display : 'none';
    if (selectionOverlay) selectionOverlay.style.display = 'none';

    // 2. Temporarily unscale viewport transform to guarantee 1:1 distortion-free coordinates
    const origTransform = viewport ? viewport.style.transform : '';
    const origTransition = viewport ? viewport.style.transition : '';
    if (viewport) {
      viewport.style.transition = 'none';
      viewport.style.transform = 'none';
    }

    // 3. Ensure all web fonts are completely loaded
    if (document.fonts && document.fonts.ready) {
      try {
        await document.fonts.ready;
      } catch (e) {
        console.warn('Font loading check non-blocking error:', e);
      }
    }

    // 4. Force layout reflow
    canvasNode.getBoundingClientRect();

    const canvasW = this.editor.designState.canvas.width || 1080;
    const canvasH = this.editor.designState.canvas.height || 1350;
    const canvasBg = this.editor.designState.canvas.background || '#ffffff';

    try {
      const renderedCanvas = await html2canvas(canvasNode, {
        width: canvasW,
        height: canvasH,
        scale: scaleFactor, // 2x for sharp retina / print output without blur
        backgroundColor: canvasBg,
        useCORS: true,
        logging: false,
        scrollX: 0,
        scrollY: 0,
        windowWidth: canvasW + 100,
        windowHeight: canvasH + 100
      });
      return renderedCanvas;
    } finally {
      // 5. Always restore editor zoom scale and selection state
      if (viewport) {
        viewport.style.transform = origTransform;
        viewport.style.transition = origTransition;
      }
      if (selectionOverlay) {
        selectionOverlay.style.display = prevOverlayDisplay;
      }
    }
  }

  async exportHtml() {
    try {
      showToast('Generating standalone HTML...', 'info');
      const response = await fetch('/api/export/html', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: 'PIXEL2EDIT Exported Design',
          design: this.editor.designState
        })
      });

      if (!response.ok) throw new Error('HTML export failed.');

      const blob = await response.blob();
      this.downloadBlob(blob, 'pixel2edit_design.html');
      showToast('Standalone HTML downloaded!', 'success');
    } catch (err) {
      console.error(err);
      showToast('Failed to export HTML.', 'error');
    }
  }

  exportJson() {
    try {
      const jsonStr = JSON.stringify(this.editor.designState, null, 2);
      const blob = new Blob([jsonStr], { type: 'application/json' });
      this.downloadBlob(blob, 'pixel2edit_design.json');
      showToast('Design JSON exported!', 'success');
    } catch (err) {
      console.error(err);
      showToast('Failed to export JSON.', 'error');
    }
  }

  async exportPng() {
    try {
      showToast('Rendering high-res PNG (2x)...', 'info');
      const renderedCanvas = await this.captureCanvasUnscaled(2);

      renderedCanvas.toBlob((blob) => {
        if (blob) {
          this.downloadBlob(blob, 'pixel2edit_design.png');
          showToast('High-Res PNG image downloaded!', 'success');
        } else {
          showToast('Failed to generate PNG image.', 'error');
        }
      }, 'image/png');
    } catch (err) {
      console.error(err);
      showToast('PNG export failed: ' + (err.message || err), 'error');
    }
  }

  async exportPdf() {
    try {
      showToast('Generating PDF document...', 'info');

      // Check jsPDF availability
      const jsPDFConstructor = (window.jspdf && window.jspdf.jsPDF) || window.jsPDF;
      if (!jsPDFConstructor) {
        showToast('PDF generator library is still loading. Please try again.', 'error');
        return;
      }

      const canvasW = this.editor.designState.canvas.width || 1080;
      const canvasH = this.editor.designState.canvas.height || 1350;
      const orientation = canvasW > canvasH ? 'landscape' : 'portrait';

      // Render unscaled high-res canvas (2x)
      const renderedCanvas = await this.captureCanvasUnscaled(2);

      const pdf = new jsPDFConstructor({
        orientation: orientation,
        unit: 'px',
        format: [canvasW, canvasH],
        hotfixes: ['px_scaling']
      });

      const imgData = renderedCanvas.toDataURL('image/png', 1.0);
      pdf.addImage(imgData, 'PNG', 0, 0, canvasW, canvasH, undefined, 'FAST');
      pdf.save('pixel2edit_design.pdf');

      showToast('PDF document downloaded!', 'success');
    } catch (err) {
      console.error(err);
      showToast('PDF export failed: ' + (err.message || err), 'error');
    }
  }

  downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

window.ExportController = ExportController;
