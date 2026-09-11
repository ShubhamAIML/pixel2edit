/**
 * PIXEL2EDIT - "Edit with AI" Natural Language Controller
 */

class AiEditController {
  constructor(editor) {
    this.editor = editor;

    this.modal = document.getElementById('aiEditModal');
    this.openBtn = document.getElementById('openAiEditBtn');
    this.closeBtn = document.getElementById('closeAiEditModalBtn');
    this.cancelBtn = document.getElementById('cancelAiEditBtn');
    this.submitBtn = document.getElementById('submitAiEditBtn');
    this.promptInput = document.getElementById('aiEditInput');
    this.targetLabel = document.getElementById('aiTargetElementLabel');
    this.spinner = document.getElementById('aiEditBtnSpinner');
    this.btnText = document.getElementById('aiEditBtnText');

    this.initEvents();
  }

  initEvents() {
    this.openBtn?.addEventListener('click', () => this.openModal());
    this.closeBtn?.addEventListener('click', () => this.closeModal());
    this.cancelBtn?.addEventListener('click', () => this.closeModal());

    // Suggestion pills
    document.querySelectorAll('.suggestion-pills .pill').forEach((pill) => {
      pill.addEventListener('click', () => {
        const pText = pill.dataset.prompt;
        if (this.promptInput) {
          this.promptInput.value = pText;
          this.promptInput.focus();
        }
      });
    });

    // Enter to submit
    this.promptInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.submitEdit();
      }
    });

    this.submitBtn?.addEventListener('click', () => this.submitEdit());
  }

  openModal() {
    const el = this.editor.getSelectedElement();
    if (this.targetLabel) {
      if (el) {
        const previewText = el.content ? `"${el.content.substring(0, 30)}..."` : el.type;
        this.targetLabel.textContent = `${el.type.toUpperCase()} (${previewText})`;
      } else {
        this.targetLabel.textContent = 'Primary Headline / First Element';
      }
    }

    if (this.promptInput) {
      this.promptInput.value = '';
    }

    if (this.modal) {
      this.modal.style.display = 'flex';
      setTimeout(() => this.promptInput?.focus(), 50);
    }
  }

  closeModal() {
    if (this.modal) {
      this.modal.style.display = 'none';
    }
  }

  async submitEdit() {
    const instruction = (this.promptInput?.value || '').trim();
    if (!instruction) {
      showToast('Please type an instruction for the AI.', 'error');
      return;
    }

    const selectedId = this.editor.selectedElementId;

    this.setLoading(true);

    try {
      const response = await fetch('/api/ai-edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instruction,
          design: this.editor.designState,
          selected_element_id: selectedId
        })
      });

      const resData = await response.json();

      if (!response.ok || !resData.success) {
        throw new Error(resData.error || 'AI edit request failed.');
      }

      // Apply returned patch to editor
      if (resData.patch) {
        this.editor.applyPatch(resData.patch);
        const explanation = resData.patch.explanation || 'Design updated with AI.';
        showToast(`✨ ${explanation}`, 'success');
        this.closeModal();
      }
    } catch (err) {
      console.error('AI Edit Error:', err);
      showToast(err.message || 'Failed to apply AI changes.', 'error');
    } finally {
      this.setLoading(false);
    }
  }

  setLoading(isLoading) {
    if (this.submitBtn) this.submitBtn.disabled = isLoading;
    if (this.spinner) this.spinner.style.display = isLoading ? 'inline-block' : 'none';
    if (this.btnText) this.btnText.textContent = isLoading ? 'Processing...' : 'Apply with AI';
  }
}

window.AiEditController = AiEditController;
