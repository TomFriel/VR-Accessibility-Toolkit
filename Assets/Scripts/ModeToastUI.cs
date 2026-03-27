using UnityEngine;
using TMPro;

/*
PSEUDOCODE (clear overview)
--------------------------
- Wait until the welcome popup is dismissed before showing any toasts.
- Show toast with:
    - current CVD simulation mode
    - current poster display state (OFF / FIX / FIX+)
- Fade toast out after a short duration.
*/

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

    private CvdModeDriver.CvdMode lastMode;
    private bool lastFix;
    private bool lastFixPlus;
    private float timer;

    void Start()
    {
        if (modeDriver == null) modeDriver = FindFirstObjectByType<CvdModeDriver>();
        if (fixManager == null) fixManager = FindFirstObjectByType<AccessibilityManager>();
        if (canvasGroup == null) canvasGroup = GetComponent<CanvasGroup>();

        lastMode = modeDriver != null ? modeDriver.CurrentMode : CvdModeDriver.CvdMode.Normal;
        lastFix = fixManager != null && fixManager.applyFix;
        lastFixPlus = fixManager != null && fixManager.applyFixPlus;

        if (canvasGroup != null) canvasGroup.alpha = 0f;
    }

    void Update()
    {
        if (!WelcomeToastOnce.WelcomeDismissed) return;

        var mode = modeDriver != null ? modeDriver.CurrentMode : CvdModeDriver.CvdMode.Normal;
        var fix = fixManager != null && fixManager.applyFix;
        var fixPlus = fixManager != null && fixManager.applyFixPlus;

        if (mode != lastMode || fix != lastFix || fixPlus != lastFixPlus)
        {
            lastMode = mode;
            lastFix = fix;
            lastFixPlus = fixPlus;
            ShowText(BuildText(mode, fix, fixPlus));
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

    string BuildText(CvdModeDriver.CvdMode mode, bool fix, bool fixPlus)
    {
        string modeName = mode switch
        {
            CvdModeDriver.CvdMode.Deuteranopia => "Deuteranopia Simulation",
            CvdModeDriver.CvdMode.Protanopia => "Protanopia Simulation",
            CvdModeDriver.CvdMode.Tritanopia => "Tritanopia Simulation",
            _ => "Normal Vision"
        };

        string fixText =
            !fix ? "Poster View: ORIGINAL" :
            fixPlus ? "Poster View: FIX+" :
            "Poster View: FIX";

        return $"{modeName}\n{fixText}";
    }
}
