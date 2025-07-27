chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action !== "scrape") return;

  const currentURL = location.href;

  fetch("http://localhost:5000/scrape", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      url: currentURL,
      type: msg.type  
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      alert("❌ " + data.error);
    } else {
      const blob = new Blob([data.result], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = msg.type === "table" ? "tables.csv" : "text.txt";
      a.click();
      URL.revokeObjectURL(url);
    }
  })
  .catch(err => {
    console.error(err);
    alert("❌ Failed to fetch data from Flask server.");
  });
});
