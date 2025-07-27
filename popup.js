document.getElementById("scrapeBtn").addEventListener("click", () => {
  const mode = document.getElementById("mode").value;
  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    chrome.tabs.sendMessage(tabs[0].id, { action: "scrape", type: mode });
  });
});
