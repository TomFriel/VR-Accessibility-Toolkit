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
    - apply normalMaterial as the starting state
- ApplyFixState(fixOn, fixPlusOn, mode):
    - If Fix is OFF: use normalMaterial
    - If Fix is ON and Fix+ is OFF: use Fix material for that mode (fallback to normal)
    - If Fix is ON and Fix+ is ON: use Fix+ material for that mode (fallback to Fix, then normal)
*/

public class AccessibilityPoster : MonoBehaviour
{
    [Header("Renderer")]
    public MeshRenderer targetRenderer; // Renderer that receives material swaps.

    [Header("Normal (original)")]
    public Material normalMaterial; // Original poster material.

    [Header("Fix (algorithmic) materials")]
    public Material protanFixMaterial;
    public Material deutanFixMaterial;
    public Material tritanFixMaterial;

    [Header("Fix+ (manual enhanced) materials")]
    public Material protanFixPlusMaterial;
    public Material deutanFixPlusMaterial;
    public Material tritanFixPlusMaterial;

    private void Awake() // Ensures renderer/material references exist and applies the normal material.
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

        targetRenderer.material = normalMaterial;
    }

    public void ApplyFixState(bool fixOn, bool fixPlusOn, CvdModeDriver.CvdMode mode) // Applies correct material for OFF/FIX/FIX+.
    {
        if (targetRenderer == null) return;

        Material chosen = normalMaterial;

        if (!fixOn)
        {
            // OFF
            chosen = normalMaterial;
        }
        else if (fixOn && !fixPlusOn)
        {
            // FIX
            chosen = GetFixMaterialForMode(mode) ?? normalMaterial;
        }
        else
        {
            // FIX+
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

    private Material GetFixMaterialForMode(CvdModeDriver.CvdMode mode) // Returns FIX material for current mode (or null).
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

    private Material GetFixPlusMaterialForMode(CvdModeDriver.CvdMode mode) // Returns FIX+ material for current mode (or null).
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