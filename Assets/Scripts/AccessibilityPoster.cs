using UnityEngine;

/*
PSEUDOCODE
--------------------------
- Each poster supports 2 workflows:
    1) Old global workflow using Apply Fix / Apply Fix+ from AccessibilityManager.
    2) New local button workflow using Original / Fix / Fix+ buttons above that poster.
- localView overrides the global Fix display when set through button clicks.
- Material chosen depends on:
    - current local view (Original / Fix / Fix+)
    - current global CVD mode (Normal / Protan / Deutan / Tritan)
- In Normal mode, Fix and Fix+ fall back to the original material unless you choose otherwise.
*/

// Manages material swapping for accessibility posters based on CVD mode and view preference.
public class AccessibilityPoster : MonoBehaviour
{
    // Defines the three possible viewing modes for a poster display.
    public enum PosterView
    {
        // Original poster material
        Original,
        // Algorithmically corrected material
        Fix,
        // Manually enhanced material
        FixPlus
    }

    // Mesh renderer that displays the poster
    [Header("Renderer")]
    public MeshRenderer targetRenderer;

    // Original material
    [Header("Normal (original)")]
    public Material normalMaterial;

    // Fix material for protanopia (red-blind)
    [Header("Fix (algorithmic) materials")]
    public Material protanFixMaterial;
    // Fix material for deuteranopia (green-blind)
    public Material deutanFixMaterial;
    // Fix material for tritanopia (blue-yellow)
    public Material tritanFixMaterial;

    // Fix+ material for protanopia (red-blind)
    [Header("Fix+ (manual enhanced) materials")]
    public Material protanFixPlusMaterial;
    // Fix+ material for deuteranopia (green-blind)
    public Material deutanFixPlusMaterial;
    // Fix+ material for tritanopia (blue-yellow)
    public Material tritanFixPlusMaterial;

    // Currently selected view mode
    [Header("Runtime state")]
    [SerializeField] private PosterView currentView = PosterView.Original;
    // Current CVD mode
    [SerializeField] private CvdModeDriver.CvdMode currentMode = CvdModeDriver.CvdMode.Normal;

    // Initializes renderer reference and fallback normal material.
    private void Awake()
    {
        // Auto-detect MeshRenderer if not manually assigned
        if (targetRenderer == null)
            targetRenderer = GetComponent<MeshRenderer>();

        // Log error if no renderer is found
        if (targetRenderer == null)
        {
            Debug.LogError($"AccessibilityPoster on {name}: no MeshRenderer found.");
            return;
        }

        // Use renderer's current material as fallback normal material if not specified
        if (normalMaterial == null)
            normalMaterial = targetRenderer.sharedMaterial;
    }

    // Applies initial material.
    private void Start()
    {
        // Apply initial material state
        RefreshMaterial();
    }

    // Switch to original material.
    public void ShowOriginal()
    {
        currentView = PosterView.Original;
        RefreshMaterial();
    }

    // Switch to Fix material.
    public void ShowFix()
    {
        currentView = PosterView.Fix;
        RefreshMaterial();
    }

    // Switch to Fix+ material.
    public void ShowFixPlus()
    {
        currentView = PosterView.FixPlus;
        RefreshMaterial();
    }

    // Update based on global fix state (fixOn, fixPlusOn, mode).
    public void ApplyFixState(bool fixOn, bool fixPlusOn, CvdModeDriver.CvdMode mode)
    {
        // Update current CVD mode
        currentMode = mode;

        // Determine which view to display based on fix state
        if (!fixOn)
        {
            // No fix enabled - show original
            currentView = PosterView.Original;
        }
        else if (fixPlusOn)
        {
            // Fix+ takes priority over regular fix
            currentView = PosterView.FixPlus;
        }
        else
        {
            // Regular fix enabled
            currentView = PosterView.Fix;
        }

        // Apply the new material
        RefreshMaterial();
    }

    // Update CVD mode and refresh display.
    public void SetCurrentMode(CvdModeDriver.CvdMode mode)
    {
        currentMode = mode;
        RefreshMaterial();
    }

    // Manually trigger material refresh.
    public void RefreshNow()
    {
        RefreshMaterial();
    }

    // Select appropriate material with fallback: FixPlus -> Fix -> Original.
    private void RefreshMaterial()
    {
        // Exit early if renderer is not available
        if (targetRenderer == null) return;

        Material chosen = normalMaterial;

        // Select material based on current view preference
        switch (currentView)
        {
            case PosterView.Original:
                // Always use the original material for this view
                chosen = normalMaterial;
                break;

            case PosterView.Fix:
                // Use Fix material for current CVD mode, fallback to original if not available
                chosen = GetFixMaterialForMode(currentMode) ?? normalMaterial;
                break;

            case PosterView.FixPlus:
                // Try FixPlus first, then Fix, then original as ultimate fallback
                chosen = GetFixPlusMaterialForMode(currentMode)
                         ?? GetFixMaterialForMode(currentMode)
                         ?? normalMaterial;
                break;
        }

        // Safety check - log error if we somehow ended up with no material
        if (chosen == null)
        {
            Debug.LogError($"AccessibilityPoster on {name}: chosen material is null.");
            return;
        }

        // Apply the selected material to the renderer
        targetRenderer.material = chosen;
    }

    // Get Fix material for given CVD mode.
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
                // Normal mode - no Fix material needed
                return null;
        }
    }

    // Get Fix+ material for given CVD mode.
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
                // Normal mode - no Fix+ material needed
                return null;
        }
    }
}