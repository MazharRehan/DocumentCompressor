document.addEventListener("DOMContentLoaded", () => {
  const makeDZ = (elId) => new Dropzone(`#${elId}`, {
    url: "/",
    autoProcessQueue: false,
    addRemoveLinks: true,
    parallelUploads: 10
  });

  const dzCompress = makeDZ("compress-dropzone");
  const dzConvert = makeDZ("convert-dropzone");

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const postForm = async (path, formData) => {
    const res = await fetch(path, { method: "POST", body: formData });
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) {
      const j = await res.json();
      throw new Error(j.error || "Error");
    }
    const disp = res.headers.get("content-disposition") || "";
    console.log("Content-Disposition:", disp); // Debug
    // Try both quoted and unquoted filename patterns
    let match = /filename[*]?=["']?([^"';]+)["']?/i.exec(disp);
    const filename = match ? match[1].trim() : "download.bin";
    console.log("Extracted filename:", filename); // Debug
    const blob = await res.blob();
    downloadBlob(blob, filename);
  };

  document.getElementById("compress-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    dzCompress.getAcceptedFiles().forEach(f => fd.append("files", f, f.name));
    try {
      await postForm("/compress", fd);
    } catch (err) {
      alert(err.message);
    }
  });

  document.getElementById("convert-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    dzConvert.getAcceptedFiles().forEach(f => fd.append("files", f, f.name));
    try {
      await postForm("/convert", fd);
    } catch (err) {
      alert(err.message);
    }
  });
});