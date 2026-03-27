using UnityEngine;

/*
PSEUDOCODE (clear overview)
--------------------------
- Each poster supports TWO workflows:
    1) Old global workflow using Apply Fix / Apply Fix+ from AccessibilityManager.
    2) New local button workflow using Original / Fix / Fix+ buttons above that poster.
- localView overrides the global Fix display when set through button clicks.
- Material chosen depends on:
    - current local view (Original / Fix / Fix+)
    - current global CVD mode (Normal / Protan / Deutan / Tritan)
- In Normal mode, Fix and Fix+ fall back to the original material unless you choose otherwise.
*/

public class AccessibilityPoster : MonoBehaviour
{
    public enum PosterView
    {
        Original,
        Fix,
        FixPlus
    }

    [Header("Renderer")]
    public MeshRenderer targetRenderer;

    [Header("Normal (original)")]
    public Material normalMaterial;

    [Header("Fix (algorithmic) materials")]
    public Material protanFixMaterial;
    public Material deutanFixMaterial;
    public Material tritanFixMaterial;

    [Header("Fix+ (manual enhanced) materials")]
    public Material protanFixPlusMaterial;
    public Material deutanFixPlusMaterial;
    public Material tritanFixPlusMaterial;

    [Header("Runtime state")]
    [SerializeField] private PosterView currentView = PosterView.Original;
    [SerializeField] private CvdModeDriver.CvdMode currentMode = CvdModeDriver.CvdMode.Normal;

    private void Awake()
    {
        if (targetRenderer == null)
            targetRenderer = GetComponent<MeshRenderer>();

        if (targetRenderer == null)
        {
            Debug.LogError($"AccessibilityPoster on {name}: no MeshRenderer found.");
            return;
        }

        if (normalMaterial == null)
            normalMaterial = targetRenderer.sharedMaterial;
    }

    private void Start()
    {
        RefreshMaterial();
    }

    public void ShowOriginal()
    {
        currentView = PosterView.Original;
        RefreshMaterial();
    }

    public void ShowFix()
    {
        currentView = PosterView.Fix;
        RefreshMaterial();
    }

    public void ShowFixPlus()
    {
        currentView = PosterView.FixPlus;
        RefreshMaterial();
    }

    // Keeps compatibility with your current manager.
    public void ApplyFixState(bool fixOn, bool fixPlusOn, CvdModeDriver.CvdMode mode)
    {
        currentMode = mode;

        if (!fixOn)
        {
            currentView = PosterView.Original;
        }
        else if (fixPlusOn)
        {
            currentView = PosterView.FixPlus;
        }
        else
        {
            currentView = PosterView.Fix;
        }

        RefreshMaterial();
    }

    public void SetCurrentMode(CvdModeDriver.CvdMode mode)
    {
        currentMode = mode;
        RefreshMaterial();
    }

    private void RefreshMaterial()
    {
        if (targetRenderer == null) return;

        Material chosen = normalMaterial;

        switch (currentView)
        {
            case PosterView.Original:
                chosen = normalMaterial;
                break;

            case PosterView.Fix:
                chosen = GetFixMaterialForMode(currentMode) ?? normalMaterial;
                break;

            case PosterView.FixPlus:
                chosen = GetFixPlusMaterialForMode(currentMode)
                         ?? GetFixMaterialForMode(currentMode)
                         ?? normalMaterial;
                break;
        }

        if (chosen == null)
        {
            Debug.LogError($"AccessibilityPoster on {name}: chosen material is null.");
            return;
        }

        targetRenderer.material = chosen;
    }

    private Material GetFixMaterialForMode(CvdModeDriver.CvdMode mode)
    {
        switch (mode)
        {
            case CvdModeDriver.CvdMode.Protanopia:
                return protanFixMaterial;
            case CvdModeDriver.CvdMode.Deuteranopia:
                return deutanFixMaterial;
            case CvdModeDriver.CvdMode.Tritanopia:
                return tritanFixMaterial;
            default:
                return null;
        }
    }

    private Material GetFixPlusMaterialForMode(CvdModeDriver.CvdMode mode)
    {
        switch (mode)
        {
            case CvdModeDriver.CvdMode.Protanopia:
                return protanFixPlusMaterial;
            case CvdModeDriver.CvdMode.Deuteranopia:
                return deutanFixPlusMaterial;
            case CvdModeDriver.CvdMode.Tritanopia:
                return tritanFixPlusMaterial;
            default:
                return null;
        }
    }
}
