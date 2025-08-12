(function () { 
  const widgetWrapper = document.createElement("div");
  widgetWrapper.id = "rag-widget-wrapper";
  widgetWrapper.style.position = "fixed";
  widgetWrapper.style.bottom = "20px";
  widgetWrapper.style.right = "20px";
  widgetWrapper.style.zIndex = "9999";

  const shadowRoot = widgetWrapper.attachShadow({ mode: "open" });

  const style = document.createElement("style");
  style.textContent = `
    .rag-widget-container {
      all: initial;
      width: auto;
      height: auto;
      background: transparent !important;
    }

    iframe {
      width: 380px;
      height: 500px;
      border: none;
      border-radius: 16px;
      box-shadow: none !important;
      background: transparent !important;
    }
  `;

  const container = document.createElement("div");
  container.className = "rag-widget-container";

  const iframe = document.createElement("iframe");
  iframe.src = "http://localhost:4200/widget-embed"; 
  iframe.allow = "clipboard-write";
  iframe.allowTransparency = true;
  iframe.style.background = "transparent";

  container.appendChild(iframe);
  shadowRoot.appendChild(style);
  shadowRoot.appendChild(container);
  document.body.appendChild(widgetWrapper);
})();
