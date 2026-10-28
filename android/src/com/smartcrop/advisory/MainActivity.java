package com.smartcrop.advisory;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.GeolocationPermissions;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.Toast;

public class MainActivity extends Activity {

    private WebView webView;
    private ProgressBar progressBar;
    private ValueCallback<Uri[]> filePathCallback;
    private static final int FILE_CHOOSER_RESULT_CODE = 1001;
    // Default online URL or local fallback
    private static final String APP_URL = "http://10.0.2.2:5000";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = (WebView) findViewById(R.id.webview);
        progressBar = (ProgressBar) findViewById(R.id.progressBar);

        setupWebView();
        requestAppPermissions();
        loadApp();
    }

    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setGeolocationEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setBuiltInZoomControls(false);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        }

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                progressBar.setVisibility(View.VISIBLE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                // If local/online server is not running, load the bundled offline quick-advisory
                if (request.isForMainFrame()) {
                    loadOfflineAdvisory();
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
                if (newProgress == 100) {
                    progressBar.setVisibility(View.GONE);
                } else {
                    progressBar.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                callback.invoke(origin, true, false);
            }

            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    request.grant(request.getResources());
                }
            }

            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback,
                                            WebChromeClient.FileChooserParams fileChooserParams) {
                if (MainActivity.this.filePathCallback != null) {
                    MainActivity.this.filePathCallback.onReceiveValue(null);
                }
                MainActivity.this.filePathCallback = filePathCallback;

                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("image/*");
                startActivityForResult(Intent.createChooser(intent, "Select Plant Leaf Photo"), FILE_CHOOSER_RESULT_CODE);
                return true;
            }
        });
    }

    private void loadApp() {
        webView.loadUrl(APP_URL);
    }

    private void loadOfflineAdvisory() {
        String offlineHtml = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
                + "<style>body{background:#0B110E;color:#e8f5e9;font-family:sans-serif;padding:24px;line-height:1.6;}"
                + "h1{color:#00e676;font-size:22px;}h2{color:#ffd740;font-size:18px;margin-top:20px;}"
                + ".card{background:rgba(19,31,26,0.9);border:1px solid rgba(0,230,118,0.2);border-radius:12px;padding:16px;margin:12px 0;}"
                + ".btn{display:inline-block;background:#00e676;color:#0B110E;padding:12px 24px;border-radius:24px;text-decoration:none;font-weight:bold;margin-top:16px;}"
                + ".badge{background:rgba(255,82,82,0.2);color:#ff8a80;padding:4px 8px;border-radius:4px;font-size:12px;}"
                + "</style></head><body>"
                + "<h1>🌾 Smart Crop Advisory System</h1>"
                + "<p>குறு மற்றும் சிறு விவசாயிகளுக்கான நுண்ணறிவு பயிர் ஆலோசனைக் கட்டமைப்பு</p>"
                + "<div class='card'>"
                + "<h2>📞 Kisan Emergency Helpline</h2>"
                + "<p>Toll-Free Farmers Helpline: <b>1800-180-1551</b></p>"
                + "<p>Tamil Nadu Agriculture Dept: <b>044-28524823</b></p>"
                + "</div>"
                + "<div class='card'>"
                + "<h2>🌱 Quick Crop Advisory (Off-line)</h2>"
                + "<p>• <b>நெல் (Paddy):</b> சிறந்த பாசன முறை: 5-7cm நீர் நிறுத்துதல். குலை நோய் மருந்து: Tricyclazole 75WP (6g/10L).</p>"
                + "<p>• <b>தக்காளி (Tomato):</b> ஆரம்ப கருகல் நோய் தடுப்பு: Mancozeb 75WP (25g/10L). சொட்டு நீர் பாசனம் பரிந்துரைக்கப்படுகிறது.</p>"
                + "<p>• <b>மக்காச்சோளம் (Maize):</b> படைப்புழு கட்டுப்பாடு: Metarhizium anisopliae (5g/L) அல்லது வேப்பெண்ணெய் 3%.</p>"
                + "</div>"
                + "<div class='card'>"
                + "<h2>🔄 Connect Online Server</h2>"
                + "<p>Ensure your SmartCrop server is running at <b>" + APP_URL + "</b> or connect to internet.</p>"
                + "<a class='btn' href='javascript:location.reload()'>🔄 Retry Connection</a>"
                + "</div>"
                + "</body></html>";
        webView.loadDataWithBaseURL(null, offlineHtml, "text/html", "utf-8", null);
    }

    private void requestAppPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            String[] permissions = {
                "android.permission.CAMERA",
                "android.permission.RECORD_AUDIO",
                "android.permission.ACCESS_FINE_LOCATION"
            };
            requestPermissions(permissions, 200);
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_RESULT_CODE) {
            if (filePathCallback == null) return;
            Uri[] results = null;
            if (resultCode == Activity.RESULT_OK && data != null) {
                String dataString = data.getDataString();
                if (dataString != null) {
                    results = new Uri[]{Uri.parse(dataString)};
                }
            }
            filePathCallback.onReceiveValue(results);
            filePathCallback = null;
        } else {
            super.onActivityResult(requestCode, resultCode, data);
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
