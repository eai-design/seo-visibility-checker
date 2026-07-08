# SEO Visibility Checker

一個可放在 GitHub 使用的批量 SEO 可見性初篩工具：

- `batch_seo_visibility_checker.py`：批量抓取 URL，輸出 CSV 報告
- `docs/`：GitHub Pages 前端頁面，用來整理 URL、查看報告
- `.github/workflows/seo-visibility-check.yml`：手動觸發 GitHub Actions，抓取並更新 `docs/reports/latest.csv`

## 快速使用

### 方法一：GitHub Pages + GitHub Actions

1. 建立 GitHub repository，將這些文件上傳。
2. 到 Settings → Pages。
3. Source 選 `Deploy from a branch`。
4. Branch 選 `main`，Folder 選 `/docs`。
5. 到 Actions → SEO Visibility Check → Run workflow。
6. 在 `urls` 輸入框貼上一批 URL，一行一個。
7. Workflow 完成後，打開 GitHub Pages 頁面，點「讀取 latest.csv」。

### 方法二：本地執行

```bash
python3 batch_seo_visibility_checker.py sites.txt docs/reports/latest.csv
```

然後用前端頁面上傳 CSV，或直接打開 GitHub Pages 查看 `latest.csv`。

## 結果欄位

- `status`：HTTP 狀態碼
- `title`：頁面標題
- `meta_robots`：robots meta
- `canonical`：canonical URL
- `text_length`：抽取正文長度
- `restriction_terms_found`：登入/限制相關字眼
- `flags`：初篩判斷

## flags 說明

- `ok`：初步正常
- `thin_text`：正文過短，可能是空頁、JS 渲染或限制
- `noindex`：頁面含 noindex
- `login_or_restriction_words`：疑似含登入/限制提示
- `http_error`：HTTP 錯誤
- `fetch_failed`：抓取失敗
- `non_html`：不是 HTML 內容

## 官方驗證依據

- Google URL Inspection Tool: https://support.google.com/webmasters/answer/9012289
- Google crawlers overview: https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers
- Verify Googlebot: https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot

## 重要說明

這是初篩工具，不等同於 Googlebot 真實索引結果。最終仍應以 Google Search Console 的 URL Inspection / Live Test 為準。
