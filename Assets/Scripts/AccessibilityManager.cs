using UnityEngine;

public class AccessibilityManager : MonoBehaviour
{
    public bool applyFix = false;
    public KeyCode toggleKey = KeyCode.G;

    [Header("Optional: drag your CvdModeDriver here. If empty, it auto-finds.")]
    [SerializeField] private CvdModeDriver modeDriver;

    private AccessibilityPoster[] posters;
    private CvdModeDriver.CvdMode lastMode;

    void Start()
    {
        // Find driver if not assigned
        if (modeDriver == null)
            modeDriver = CvdModeDriver.Instance != null
                ? CvdModeDriver.Instance
                : Object.FindFirstObjectByType<CvdModeDriver>();

        // Find posters
        posters = Object.FindObjectsByType<AccessibilityPoster>(FindObjectsSortMode.None);

        lastMode = GetModeSafe();
        UpdatePosters();
    }

    void Update()
    {
        if (Input.GetKeyDown(toggleKey))
        {
            applyFix = !applyFix;
            UpdatePosters();
            Debug.Log("ApplyFix set to: " + applyFix);
        }

        // If Apply Fix is ON and you change simulation mode, swap poster materials automatically
        if (applyFix)
        {
            var current = GetModeSafe();
            if (current != lastMode)
            {
                lastMode = current;
                UpdatePosters();
            }
        }
    }

    private CvdModeDriver.CvdMode GetModeSafe()
    {
        if (modeDriver == null)
            modeDriver = CvdModeDriver.Instance != null
                ? CvdModeDriver.Instance
                : Object.FindFirstObjectByType<CvdModeDriver>();

        return modeDriver != null ? modeDriver.CurrentMode : CvdModeDriver.CvdMode.Normal;
    }

    private void UpdatePosters()
    {
        if (posters == null) return;

        var mode = GetModeSafe();

        foreach (var poster in posters)
        {
            if (poster != null)
                poster.ApplyFix(applyFix, mode);
        }
    }
}
