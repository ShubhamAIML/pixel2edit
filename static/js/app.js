/**
 * PIXEL2EDIT - Main Application Orchestrator
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Core Services
  const editor = new DesignEditor();
  const toolbar = new AppToolbar(editor);
  const inspector = new AppInspector(editor);
  const aiEdit = new AiEditController(editor);
  const exporter = new ExportController(editor);

  // Expose globally for cross-module events
  window.appEditor = editor;
  window.appToolbar = toolbar;
  window.appInspector = inspector;
  window.appAiEdit = aiEdit;
  window.appExporter = exporter;

  // Views & Controls
  const landingView = document.getElementById('landingView');
  const editorView = document.getElementById('editorView');
  const headerEditorControls = document.getElementById('headerEditorControls');
  const newDesignBtn = document.getElementById('newDesignBtn');
  const exportDropdownWrapper = document.getElementById('exportDropdownWrapper');
  const brandLogoBtn = document.getElementById('brandLogoBtn');

  // Dropzone Elements
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const browseBtn = document.getElementById('browseFilesBtn');
  const dropzonePrompt = document.getElementById('dropzonePrompt');
  const dropzonePreview = document.getElementById('dropzonePreview');
  const previewImg = document.getElementById('previewImg');
  const previewFileName = document.getElementById('previewFileName');
  const previewFileSpecs = document.getElementById('previewFileSpecs');
  const reconstructBtn = document.getElementById('reconstructBtn');
  const removeFileBtn = document.getElementById('removeFileBtn');

  // Processing Modal Elements
  const processingModal = document.getElementById('processingModal');
  const stepItems = [
    document.getElementById('step1'),
    document.getElementById('step2'),
    document.getElementById('step3'),
    document.getElementById('step4'),
    document.getElementById('step5')
  ];

  let selectedFile = null;

  // ==========================================================
  // Dropzone & File Selection Handlers
  // ==========================================================
  browseBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    fileInput?.click();
  });

  dropzone?.addEventListener('click', (e) => {
    if (!selectedFile && e.target !== browseBtn) fileInput?.click();
  });

  fileInput?.addEventListener('change', (e) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelected(file);
    fileInput.value = '';
  });

  // Drag & Drop
  dropzone?.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('drag-over');
  });

  dropzone?.addEventListener('dragleave', () => {
    dropzone.classList.remove('drag-over');
  });

  dropzone?.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    const file = e.dataTransfer?.files?.[0];
    if (file) handleFileSelected(file);
  });

  removeFileBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    resetDropzone();
  });

  function handleFileSelected(file) {
    if (!file) return;

    // Validate type by MIME and file extension
    const ext = (file.name || '').split('.').pop().toLowerCase();
    const validExts = ['png', 'jpg', 'jpeg', 'webp', 'jfif'];
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/pjpeg', 'image/x-png', 'image/jfif'];
    const isImage = (file.type && file.type.startsWith('image/')) || validExts.includes(ext) || validTypes.includes((file.type || '').toLowerCase());

    if (!isImage) {
      showToast('Unsupported file type. Please upload PNG, JPG, or WEBP.', 'error');
      return;
    }

    // Validate size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      showToast('File is too large. Maximum size is 10MB.', 'error');
      return;
    }

    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      if (previewImg) previewImg.src = dataUrl;

      const kb = Math.round(file.size / 1024);
      if (previewFileName) previewFileName.textContent = file.name;
      if (previewFileSpecs) previewFileSpecs.textContent = `${kb} KB`;

      // Show preview state immediately
      if (dropzonePrompt) dropzonePrompt.style.display = 'none';
      if (dropzonePreview) dropzonePreview.style.display = 'flex';

      // Read natural image dimensions asynchronously
      const img = new Image();
      img.onload = () => {
        if (previewFileSpecs) {
          previewFileSpecs.textContent = `${img.naturalWidth} × ${img.naturalHeight} px • ${kb} KB`;
        }
      };
      img.src = dataUrl;
    };
    reader.readAsDataURL(file);
  }

  function resetDropzone() {
    selectedFile = null;
    if (fileInput) fileInput.value = '';
    if (previewImg) previewImg.src = '';
    if (dropzonePrompt) dropzonePrompt.style.display = 'flex';
    if (dropzonePreview) dropzonePreview.style.display = 'none';
  }

  // ==========================================================
  // Animated Processing Sequence
  // ==========================================================
  function startProcessingAnimation() {
    if (processingModal) processingModal.style.display = 'flex';

    stepItems.forEach((step, idx) => {
      if (!step) return;
      step.className = 'step-item';
      const icon = step.querySelector('.step-icon');
      if (icon) icon.textContent = '○';
    });

    // Animate steps sequentially
    const advanceStep = (stepIdx) => {
      if (stepIdx > 0 && stepItems[stepIdx - 1]) {
        stepItems[stepIdx - 1].className = 'step-item step-completed';
        const icon = stepItems[stepIdx - 1].querySelector('.step-icon');
        if (icon) icon.textContent = '✓';
      }
      if (stepIdx < stepItems.length && stepItems[stepIdx]) {
        stepItems[stepIdx].className = 'step-item step-active';
        const icon = stepItems[stepIdx].querySelector('.step-icon');
        if (icon) icon.textContent = '●';
      }
    };

    advanceStep(0);
    const timers = [
      setTimeout(() => advanceStep(1), 800),
      setTimeout(() => advanceStep(2), 1600),
      setTimeout(() => advanceStep(3), 2400),
      setTimeout(() => advanceStep(4), 3200)
    ];

    return () => {
      timers.forEach(clearTimeout);
      // Mark all completed
      stepItems.forEach((step) => {
        if (!step) return;
        step.className = 'step-item step-completed';
        const icon = step.querySelector('.step-icon');
        if (icon) icon.textContent = '✓';
      });
    };
  }

  function stopProcessingAnimation() {
    if (processingModal) processingModal.style.display = 'none';
  }

  // ==========================================================
  // Reconstruct Action (Triggered from Dropzone)
  // ==========================================================
  reconstructBtn?.addEventListener('click', async (e) => {
    e.stopPropagation();
    if (!selectedFile) {
      showToast('Please select an image first.', 'error');
      return;
    }

    const finishSteps = startProcessingAnimation();

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to analyze design image.');
      }

      finishSteps();

      // Brief delay so user sees all steps complete with green checks
      setTimeout(() => {
        stopProcessingAnimation();
        openEditor(data.design, data.image_url, data.mode);
      }, 600);

    } catch (err) {
      stopProcessingAnimation();
      console.error(err);
      showToast(err.message || 'Error reconstructing design.', 'error');
    }
  });

  // ==========================================================
  // Sample Cards Click Handler (1-Click Instant Demo)
  // ==========================================================
  document.querySelectorAll('.sample-card').forEach((card) => {
    card.addEventListener('click', async () => {
      const sampleId = card.dataset.sampleId;
      if (!sampleId) return;

      const finishSteps = startProcessingAnimation();

      try {
        const response = await fetch(`/api/sample/${sampleId}`);
        const data = await response.json();

        if (!response.ok || !data.success) {
          throw new Error(data.error || 'Failed to load sample template.');
        }

        finishSteps();

        setTimeout(() => {
          stopProcessingAnimation();
          openEditor(data.design, data.image_url, 'demo');
        }, 600);

      } catch (err) {
        stopProcessingAnimation();
        console.error(err);
        showToast(err.message || 'Error loading sample template.', 'error');
      }
    });
  });

  // ==========================================================
  // State Transition: Landing -> Editor
  // ==========================================================
  function openEditor(design, imageUrl, mode) {
    if (landingView) landingView.style.display = 'none';
    if (editorView) editorView.style.display = 'flex';
    if (headerEditorControls) headerEditorControls.style.display = 'flex';
    if (newDesignBtn) newDesignBtn.style.display = 'inline-flex';
    if (exportDropdownWrapper) exportDropdownWrapper.style.display = 'block';

    // Update status badge
    const badgeText = document.getElementById('aiStatusText');
    const badgeEl = document.getElementById('aiStatusBadge');
    if (badgeText && badgeEl) {
      if (mode === 'gemini') {
        badgeText.textContent = 'Gemini Flash Reconstructed';
        badgeEl.className = 'ai-badge badge-live';
      } else if (mode === 'ocr') {
        badgeText.textContent = 'OCR Vision Reconstructed';
        badgeEl.className = 'ai-badge badge-live';
      } else {
        badgeText.textContent = 'Design Reconstructed';
        badgeEl.className = 'ai-badge badge-live';
      }
    }

    editor.loadDesign(design, imageUrl);
    if (mode === 'gemini') {
      showToast('✨ Gemini Flash reconstructed your design! Click any text to edit or drag.', 'success');
    } else if (mode === 'ocr') {
      showToast('🔍 Layout & typography reconstructed! Click any element to edit or drag.', 'success');
    } else {
      showToast('✨ Design loaded! Click any element to edit, customize or drag.', 'success');
    }
  }

  // ==========================================================
  // State Transition: Editor -> Landing
  // ==========================================================
  function openLanding() {
    if (editorView) editorView.style.display = 'none';
    if (landingView) landingView.style.display = 'flex';
    if (headerEditorControls) headerEditorControls.style.display = 'none';
    if (newDesignBtn) newDesignBtn.style.display = 'none';
    if (exportDropdownWrapper) exportDropdownWrapper.style.display = 'none';
    resetDropzone();
  }

  newDesignBtn?.addEventListener('click', openLanding);
  brandLogoBtn?.addEventListener('click', openLanding);

});

