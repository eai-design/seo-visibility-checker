# 批量 SEO 可見性初篩工具

## 用途

用於批量檢查網站在「未登入、普通瀏覽器請求」下是否可訪問、是否有正文、是否存在 `noindex`、登入/限制提示等可疑問題。

它不能取代 Google Search Console Live Test，但可先把大量網站分成：

- `ok`：初步看起來可公開抓取
- `thin_text`：正文過短，可能是 JS 渲染、空頁或被限制
- `noindex`：頁面主動禁止索引
- `login_or_restriction_words`：頁面文字含登入/限制提示
- `http_error`：HTTP 4xx/5xx
- `fetch_failed`：抓取失敗

## 使用方法

1. 建立 URL 清單，例如 `sites.txt`：

```text
https://www.example.com/
https://www.example.com/article-a/
```

2. 執行：

```bash
python3 batch_seo_visibility_checker.py sites.txt seo_report.csv
```

如果使用本套 GitHub Pages 前端，建議輸出到：

```bash
python3 batch_seo_visibility_checker.py sites.txt docs/reports/latest.csv
```

3. 打開 `seo_report.csv`，優先抽查 flags 不是 `ok` 的 URL。

## 建議驗證流程

```text
批量腳本初篩 → 找出可疑 URL → Google Search Console URL Inspection → Test Live URL → 檢查 Google 抓取 HTML / Screenshot
```

## Google 官方驗證依據

- URL Inspection Tool: https://support.google.com/webmasters/answer/9012289
- Google crawlers overview: https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers
- Verify Googlebot: https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot

## 注意

不要只靠偽裝 Googlebot User-Agent 判斷結果。Google 官方要求用反向 DNS / 正向 DNS 驗證真正的 Googlebot。

## GitHub 使用方式

1. 把整個資料夾上傳到 GitHub repository。
2. 到 Settings → Pages，Source 選 `Deploy from a branch`，Branch 選 `main`，Folder 選 `/docs`。
3. 到 Actions → SEO Visibility Check → Run workflow。
4. 在輸入框貼上一批 URL，一行一個。
5. Workflow 完成後會更新 `docs/reports/latest.csv`。
6. 打開 GitHub Pages 網頁，點「讀取 latest.csv」查看報告。

前端頁面不直接抓網站，因為瀏覽器會受 CORS 限制；真正抓取由 GitHub Actions 或本地 Python 執行。
