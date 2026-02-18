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

    // Called by AccessibilityManager when Apply Fix is toggled OR mode changes
    public void ApplyFix(bool enable, CvdModeDriver.CvdMode mode)
    {
        if (targetRenderer == null) return;

        Material chosen = normalMaterial;

        if (enable)
        {
            switch (mode)
            {
                case CvdModeDriver.CvdMode.Protanopia:
                    if (protanFixMaterial != null) chosen = protanFixMaterial;
                    break;

                case CvdModeDriver.CvdMode.Deuteranopia:
                    if (deutanFixMaterial != null) chosen = deutanFixMaterial;
                    break;

                case CvdModeDriver.CvdMode.Tritanopia:
                    if (tritanFixMaterial != null) chosen = tritanFixMaterial;
                    break;

                case CvdModeDriver.CvdMode.Normal:
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
