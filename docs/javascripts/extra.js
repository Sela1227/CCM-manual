/* ======================================================
   彰濱秀傳癌症中心 - 個管師訓練系統
   V5.0.0 起，版號、麵包屑、底部導覽、SELA 印記都由模板在 build 時產生
   （overrides/main.html），這支檔只剩搜尋觸發。
   ====================================================== */

// 首頁搜尋框與底部「搜尋」鈕共用：打開 Material 的搜尋 overlay 並聚焦輸入框
window.ccmOpenSearch = function () {
  var cb = document.getElementById("__search");
  if (cb) cb.checked = true;
  var inp = document.querySelector(".md-search__input");
  if (inp) setTimeout(function () { inp.focus(); }, 60);
};
