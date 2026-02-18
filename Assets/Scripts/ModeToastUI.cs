using UnityEngine;
using TMPro;

public class ModeToastUI : MonoBehaviour
{
    [Header("References")]
    public CvdModeDriver modeDriver;
    public AccessibilityManager fixManager;
    public TextMeshProUGUI label;
    public CanvasGroup canvasGroup;

    [Header("Timing")]
    public float showSeconds = 1.5f;
    public float fadeSeconds = 0.25f;

    CvdModeDriver.CvdMode lastMode;
    bool lastFix;
    float timer;

    void Start()
    {
        if (modeDriver == null) modeDriver = FindFirstObjectByType<CvdModeDriver>();
        if (fixManager == null) fixManager = FindFirstObjectByType<AccessibilityManager>();
        if (canvasGroup == null) canvasGroup = GetComponent<CanvasGroup>();

        lastMode = modeDriver != null ? modeDriver.CurrentMode : CvdModeDriver.CvdMode.Normal;
        lastFix = fixManager != null && fixManager.applyFix;

        ShowText(BuildText(lastMode, lastFix));
    }

    void Update()
    {
        var mode = modeDriver != null ? modeDriver.CurrentMode : CvdModeDriver.CvdMode.Normal;
        var fix = fixManager != null && fixManager.applyFix;

        if (mode != lastMode || fix != lastFix)
        {
            lastMode = mode;
            lastFix = fix;
            ShowText(BuildText(mode, fix));
        }

        if (timer > 0f)
        {
            timer -= Time.deltaTime;

            if (canvasGroup != null)
            {
                float t = Mathf.Clamp01(timer / fadeSeconds);
                canvasGroup.alpha = timer > fadeSeconds ? 1f : t;
            }
        }
        else
        {
            if (canvasGroup != null) canvasGroup.alpha = 0f;
        }
    }

    void ShowText(string text)
    {
        if (label != null) label.text = text;
        timer = showSeconds;
        if (canvasGroup != null) canvasGroup.alpha = 1f;
    }

    string BuildText(CvdModeDriver.CvdMode mode, bool fixOn)
    {
        string modeName = mode switch
        {
            CvdModeDriver.CvdMode.Deuteranopia => "Deuteranopia Simulation",
            CvdModeDriver.CvdMode.Protanopia => "Protanopia Simulation",
            CvdModeDriver.CvdMode.Tritanopia => "Tritanopia Simulation",
            _ => "Normal Vision"
        };

        string fixText = fixOn ? "Apply Fix: ON" : "Apply Fix: OFF";
        return $"{modeName}\n{fixText}";
    }
}
