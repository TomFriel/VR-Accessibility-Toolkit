using UnityEngine;

/*
PSEUDOCODE (clear overview)
--------------------------
- Maintain two toggles:
    - Apply Fix (F): swaps posters to corrected versions for the current CVD mode
    - Apply Fix+ (G): swaps posters to manual enhanced versions (only valid if Fix is ON)
- Find the active CvdModeDriver (assigned in inspector or auto-found).
- Find all AccessibilityPoster components in the scene.
- On Start: cache current mode and apply poster state once.
- On Update:
    - If F pressed: toggle Fix; if Fix becomes OFF, force Fix+ OFF; update posters.
    - If G pressed: toggle Fix+ only when Fix is ON; update posters.
    - If Fix is ON and CVD mode changes: update posters automatically.
*/

public class AccessibilityManager : MonoBehaviour
{
    [Header("Keys")]
    public KeyCode toggleFixKey = KeyCode.F;       // Apply Fix toggle key.
    public KeyCode toggleFixPlusKey = KeyCode.G;   // Apply Fix+ toggle key.

    [Header("State")]
    public bool applyFix = false;       // True when Fix is enabled.
    public bool applyFixPlus = false;   // True when Fix+ is enabled (only meaningful when Fix is ON).

    [Header("Optional: drag your CvdModeDriver here. If empty, it auto-finds.")]
    [SerializeField] private CvdModeDriver modeDriver; // Source of the current CVD mode.

    private AccessibilityPoster[] posters;          // Posters to update.
    private CvdModeDriver.CvdMode lastMode;         // Cached mode to detect changes.

    void Start() // Locates driver + posters and applies initial poster state.
    {
        if (modeDriver == null)
            modeDriver = CvdModeDriver.Instance != null
                ? CvdModeDriver.Instance
                : Object.FindFirstObjectByType<CvdModeDriver>();

        posters = Object.FindObjectsByType<AccessibilityPoster>(FindObjectsSortMode.None);

        lastMode = GetModeSafe();
        UpdatePosters();
    }

    void Update() // Handles Fix/Fix+ keys and refreshes posters on mode changes when Fix is active.
    {
        // Toggle Fix (F).
        if (Input.GetKeyDown(toggleFixKey))
        {
            applyFix = !applyFix;

            // Fix+ cannot remain enabled if Fix is OFF.
            if (!applyFix)
                applyFixPlus = false;

            UpdatePosters();
            Debug.Log($"Apply Fix: {(applyFix ? "ON" : "OFF")} | Fix+: {(applyFixPlus ? "ON" : "OFF")}");
        }

        // Toggle Fix+ (G), only if Fix is ON.
        if (Input.GetKeyDown(toggleFixPlusKey))
        {
            if (applyFix)
            {
                applyFixPlus = !applyFixPlus;
                UpdatePosters();
                Debug.Log($"Apply Fix+: {(applyFixPlus ? "ON" : "OFF")}");
            }
            else
            {
                // Optional: feedback if user presses G while Fix is OFF.
                Debug.Log("Fix+ ignored because Apply Fix is OFF. Press F first.");
            }
        }

        // If Fix is ON, update posters automatically when the simulation mode changes.
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

    private CvdModeDriver.CvdMode GetModeSafe() // Returns current CVD mode safely (auto-finds driver if needed).
    {
        if (modeDriver == null)
            modeDriver = CvdModeDriver.Instance != null
                ? CvdModeDriver.Instance
                : Object.FindFirstObjectByType<CvdModeDriver>();

        return modeDriver != null ? modeDriver.CurrentMode : CvdModeDriver.CvdMode.Normal;
    }

    private void UpdatePosters() // Applies current Fix/Fix+ state + mode to all posters.
    {
        if (posters == null) return;

        var mode = GetModeSafe();

        foreach (var poster in posters)
        {
            if (poster != null)
                poster.ApplyFixState(applyFix, applyFixPlus, mode);
        }
    }
}