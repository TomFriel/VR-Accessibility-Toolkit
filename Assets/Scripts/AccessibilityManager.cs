using UnityEngine;

/*
PSEUDOCODE (clear overview)
--------------------------
- This manager now handles TWO separate systems:
    1) Global CVD simulation mode for the whole scene.
    2) Global Fix / Fix+ state used by posters that are still using the old global workflow.
- It finds the active CvdModeDriver and all AccessibilityPoster objects.
- It can still use keyboard input for editor testing:
    - F = toggle Fix
    - G = toggle Fix+
- It also exposes public button methods for VR UI:
    - SetNormal()
    - SetProtanopia()
    - SetDeuteranopia()
    - SetTritanopia()
- Whenever mode or Fix state changes, all posters are refreshed.
*/

public class AccessibilityManager : MonoBehaviour
{
    [Header("Keyboard testing")]
    public KeyCode toggleFixKey = KeyCode.F;
    public KeyCode toggleFixPlusKey = KeyCode.G;

    [Header("Global Fix State")]
    public bool applyFix = false;
    public bool applyFixPlus = false;

    [Header("Optional references")]
    [SerializeField] private CvdModeDriver modeDriver;
    [SerializeField] private AccessibilityPoster[] posters;

    private CvdModeDriver.CvdMode lastMode;

    private void Start()
    {
        ResolveReferences();
        lastMode = GetModeSafe();
        UpdatePosters();
    }

    private void Update()
    {
        // Keyboard support stays for editor testing.
        if (Input.GetKeyDown(toggleFixKey))
        {
            ToggleFix();
        }

        if (Input.GetKeyDown(toggleFixPlusKey))
        {
            ToggleFixPlus();
        }

        // Always refresh posters if global mode changes.
        var current = GetModeSafe();
        if (current != lastMode)
        {
            lastMode = current;
            UpdatePosters();
        }
    }

    private void ResolveReferences()
    {
        if (modeDriver == null)
        {
            modeDriver = CvdModeDriver.Instance != null
                ? CvdModeDriver.Instance
                : Object.FindFirstObjectByType<CvdModeDriver>();
        }

        if (posters == null || posters.Length == 0)
        {
            posters = Object.FindObjectsByType<AccessibilityPoster>(FindObjectsSortMode.None);
        }
    }

    public void RefreshPosters()
    {
        ResolveReferences();
        UpdatePosters();
    }

    public CvdModeDriver.CvdMode GetCurrentMode()
    {
        return GetModeSafe();
    }

    public void SetNormal()
    {
        SetMode(CvdModeDriver.CvdMode.Normal);
    }

    public void SetDeuteranopia()
    {
        SetMode(CvdModeDriver.CvdMode.Deuteranopia);
    }

    public void SetProtanopia()
    {
        SetMode(CvdModeDriver.CvdMode.Protanopia);
    }

    public void SetTritanopia()
    {
        SetMode(CvdModeDriver.CvdMode.Tritanopia);
    }

    public void SetMode(CvdModeDriver.CvdMode newMode)
    {
        ResolveReferences();

        if (modeDriver != null)
        {
            modeDriver.SetMode(newMode);
        }

        lastMode = newMode;
        UpdatePosters();
        Debug.Log($"CVD Mode set to: {newMode}");
    }

    public void ToggleFix()
    {
        applyFix = !applyFix;

        if (!applyFix)
        {
            applyFixPlus = false;
        }

        UpdatePosters();
        Debug.Log($"Apply Fix: {(applyFix ? "ON" : "OFF")} | Fix+: {(applyFixPlus ? "ON" : "OFF")}");
    }

    public void ToggleFixPlus()
    {
        if (!applyFix)
        {
            Debug.Log("Fix+ ignored because Apply Fix is OFF.");
            return;
        }

        applyFixPlus = !applyFixPlus;
        UpdatePosters();
        Debug.Log($"Apply Fix+: {(applyFixPlus ? "ON" : "OFF")}");
    }

    public void SetFixOff()
    {
        applyFix = false;
        applyFixPlus = false;
        UpdatePosters();
    }

    public void SetFixOn()
    {
        applyFix = true;
        UpdatePosters();
    }

    public void SetFixPlusOn()
    {
        applyFix = true;
        applyFixPlus = true;
        UpdatePosters();
    }

    private CvdModeDriver.CvdMode GetModeSafe()
    {
        if (modeDriver == null)
        {
            modeDriver = CvdModeDriver.Instance != null
                ? CvdModeDriver.Instance
                : Object.FindFirstObjectByType<CvdModeDriver>();
        }

        return modeDriver != null ? modeDriver.CurrentMode : CvdModeDriver.CvdMode.Normal;
    }

    private void UpdatePosters()
    {
        ResolveReferences();
        var mode = GetModeSafe();

        if (posters == null) return;

        foreach (var poster in posters)
        {
            if (poster != null)
            {
                poster.ApplyFixState(applyFix, applyFixPlus, mode);
            }
        }
    }
}
