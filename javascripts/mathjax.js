window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"], ["$", "$"]],
    displayMath: [["\\[", "\\]"], ["$$", "$$"]],
    processEscapes: true
  },
  options: {
    processHtmlClass: "arithmatex"
  }
};

let isRendering = false;

/**
 * Main render function to handle both LaTeX and Mermaid diagrams.
 * Designed for MkDocs Material's Single Page App (SPA) navigation.
 */
const renderAll = () => {
  if (isRendering) return;
  isRendering = true;

  // 1. Mermaid: Surgical Unwrap and Render
  if (typeof mermaid !== "undefined") {
    const blocks = document.querySelectorAll('.mermaid code');
    let needsMermaidRun = false;

    blocks.forEach(code => {
      const pre = code.parentElement;
      // Only process if we haven't unwrapped this specific block yet
      if (!pre.hasAttribute('data-processed')) {
        pre.textContent = code.textContent;
        pre.setAttribute('data-processed', 'true');
        needsMermaidRun = true;
      }
    });

    if (needsMermaidRun) {
      mermaid.initialize({ startOnLoad: false, theme: 'default' });
      mermaid.run({ 
        nodes: document.querySelectorAll('.mermaid') 
      });
    }
  }

  // 2. MathJax: Render LaTeX notations like O(log N)
  if (window.MathJax && window.MathJax.typesetPromise) {
    window.MathJax.typesetPromise();
  }

  // Release the mutex after a short delay to allow DOM to settle
  setTimeout(() => { 
    isRendering = false; 
  }, 100);
};

/**
 * MutationObserver catches content changes during instant navigation
 * without requiring the fragile document.subscribe hook.
 */
const observer = new MutationObserver((mutations) => {
  if (!isRendering) {
    renderAll();
  }
});

// Start observing the body for new module content
observer.observe(document.body, { 
  childList: true, 
  subtree: true 
});

// Initial load execution
window.addEventListener('load', renderAll);