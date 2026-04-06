using UnityEngine;

/*
PSEUDOCODE (clear overview)
--------------------------
- Hold references to:
    - MeshRenderer to update
    - Normal material (original)
    - Fix materials per CVD mode (Protan/Deutan/Tritan)
    - Fix+ materials per CVD mode (Protan/Deutan/Tritan)
- On Awake:
    - auto-find MeshRenderer if missing
    - cache current shared material as normalMaterial if missing
- ApplyFixState(fixOn, fixPlusOn, mode):
    - If Fix is OFF: use normalMaterial
    - If Fix is ON and Fix+ is OFF: use Fix material for that mode (fallback to normal)
    - If Fix is ON and Fix+ is ON: use Fix+ material for that mode (fallback to Fix, then normal)
*/

public class AccessibilityPoster : MonoBehaviour
{
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
        if (targetRenderer != null && normalMaterial != null)
            targetRenderer.material = normalMaterial;
    }

    public void ApplyFixState(bool fixOn, bool fixPlusOn, CvdModeDriver.CvdMode mode)
    {
        if (targetRenderer == null) return;

        Material chosen = normalMaterial;

        if (!fixOn)
        {
            chosen = normalMaterial;
        }
        else if (!fixPlusOn)
        {
            chosen = GetFixMaterialForMode(mode) ?? normalMaterial;
        }
        else
        {
            chosen = GetFixPlusMaterialForMode(mode)
                     ?? GetFixMaterialForMode(mode)
                     ?? normalMaterial;
        }

        if (chosen == null)
        {
            Debug.LogError($"AccessibilityPoster on {name}: chosen material is null.");
            return;
        }

        targetRenderer.material = chosen;
    }

    public void RefreshNow()
    {
        // Re-apply whatever material is currently on the renderer.
        // This is useful after textures are updated at runtime.
        if (targetRenderer != null && targetRenderer.material != null)
        {
            targetRenderer.material = targetRenderer.material;
        }
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