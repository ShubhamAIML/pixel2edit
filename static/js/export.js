/**
 * PIXEL2EDIT - Export Controller (HTML, JSON, PNG)
 */

class ExportController {
  constructor(editor) {
    this.editor = editor;

    this.mainBtn = document.getElementById('exportMainBtn');
    this.menu = document.getElementById('exportMenu');
    this.btnHtml = document.getElementById('exportHtmlBtn');
    this.btnJson = document.getElementById('exportJsonBtn');
    this.btnPng = document.getElementById('exportPngBtn');

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
    if (typeof html2canvas === 'undefined') {
      showToast('PNG export engine loading...', 'error');
      return;
    }

    try {
      showToast('Rendering canvas to PNG...', 'info');

      // Temporarily hide selection overlay and ensure full scale rendering
      const selectionOverlay = document.getElementById('selectionOverlay');
      const prevDisplay = selectionOverlay ? selectionOverlay.style.display : 'none';
      if (selectionOverlay) selectionOverlay.style.display = 'none';

      const canvasNode = document.getElementById('designCanvas');
      if (!canvasNode) throw new Error('Canvas not found');

      // Render at original 1:1 scale
      const canvas = await html2canvas(canvasNode, {
        scale: 1,
        backgroundColor: null,
        useCORS: true,
        logging: false
      });

      if (selectionOverlay) selectionOverlay.style.display = prevDisplay;

      canvas.toBlob((blob) => {
        if (blob) {
          this.downloadBlob(blob, 'pixel2edit_design.png');
          showToast('PNG image downloaded!', 'success');
        } else {
          showToast('Failed to generate PNG image.', 'error');
        }
      }, 'image/png');
    } catch (err) {
      console.error(err);
      showToast('PNG export failed.', 'error');
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
