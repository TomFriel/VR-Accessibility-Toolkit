using UnityEngine;

public class AccessibilityPoster : MonoBehaviour
{
    [Header("Renderer")]
    public MeshRenderer targetRenderer;

    [Header("Materials")]
    public Material normalMaterial;          // original
    public Material protanFixMaterial;       // daltonized for Protan
    public Material deutanFixMaterial;       // daltonized for Deutan
    public Material tritanFixMaterial;       // daltonized for Tritan

    private void Awake()
    {
        if (targetRenderer == null)
            targetRenderer = GetComponent<MeshRenderer>();

        if (targetRenderer == null)
        {
            Debug.LogError($"AccessibilityPoster on {name}: no MeshRenderer found.");
            return;
        }

        // Start with original material
        if (normalMaterial == null)
            normalMaterial = targetRenderer.sharedMaterial;

        targetRenderer.material = normalMaterial;
    }

    // Called by AccessibilityManager when Apply Fix is toggled
    public void ApplyFix(bool enable)
    {
        if (targetRenderer == null) return;

        Material chosen = normalMaterial;

        if (enable)
        {
            var mode = ColourBlindModeController.CurrentMode;

            switch (mode)
            {
                case ColourBlindModeController.CvdMode.Protanopia:
                    if (protanFixMaterial != null) chosen = protanFixMaterial;
                    break;

                case ColourBlindModeController.CvdMode.Deuteranopia:
                    if (deutanFixMaterial != null) chosen = deutanFixMaterial;
                    break;

                case ColourBlindModeController.CvdMode.Tritanopia:
                    if (tritanFixMaterial != null) chosen = tritanFixMaterial;
                    break;

                case ColourBlindModeController.CvdMode.Normal:
                default:
                    chosen = normalMaterial;
                    break;
            }
        }

        if (chosen == null)
        {
            Debug.LogError($"AccessibilityPoster on {name}: chosen material is null.");
            return;
        }

        targetRenderer.material = chosen;
    }
}
