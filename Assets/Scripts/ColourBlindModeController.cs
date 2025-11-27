using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

[RequireComponent(typeof(Volume))]
public class ColourBlindModeController : MonoBehaviour
{
    private ColorAdjustments colorAdjustments;

    public enum CvdMode
    {
        Normal = 0,
        Protanopia = 1,
        Deuteranopia = 2,
        Tritanopia = 3
    }

    public CvdMode mode = CvdMode.Normal;

    void Start()
    {
        var volume = GetComponent<Volume>();

        if (volume == null)
        {
            Debug.LogError("CBC: No Volume component found on this GameObject.");
            return;
        }

        if (!volume.profile.TryGet(out colorAdjustments))
        {
            Debug.LogError("CBC: No ColorAdjustments override found on the Volume profile.");
            return;
        }

        Debug.Log("CBC: ColorAdjustments found, script is ready.");
        ApplyMode();
    }

    void Update()
    {
        if (colorAdjustments == null) return;

        // TEMP: keyboard controls for testing
        if (Input.GetKeyDown(KeyCode.Alpha1))
        {
            mode = CvdMode.Normal;
            ApplyMode();
        }
        else if (Input.GetKeyDown(KeyCode.Alpha2))
        {
            mode = CvdMode.Protanopia;
            ApplyMode();
        }
        else if (Input.GetKeyDown(KeyCode.Alpha3))
        {
            mode = CvdMode.Deuteranopia;
            ApplyMode();
        }
        else if (Input.GetKeyDown(KeyCode.Alpha4))
        {
            mode = CvdMode.Tritanopia;
            ApplyMode();
        }
    }

    private void ApplyMode()
    {
        if (colorAdjustments == null) return;

        switch (mode)
        {
            case CvdMode.Normal:
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = 0f;
                colorAdjustments.colorFilter.value = Color.white;
                Debug.Log("CBC: Normal mode applied.");
                break;

            case CvdMode.Protanopia:
                // Rough protanopia-ish: reduce reds, a bit desaturated + cyan tint
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = -40f;
                colorAdjustments.colorFilter.value = new Color(0.7f, 1.0f, 1.0f);
                Debug.Log("CBC: Protanopia mode applied.");
                break;

            case CvdMode.Deuteranopia:
                // Rough deuteranopia-ish: reduce greens, slightly magenta-ish tint
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = -40f;
                colorAdjustments.colorFilter.value = new Color(1.0f, 0.8f, 1.0f);
                Debug.Log("CBC: Deuteranopia mode applied.");
                break;

            case CvdMode.Tritanopia:
                // Rough tritanopia-ish: reduce blues, more yellow tint
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = -50f;
                colorAdjustments.colorFilter.value = new Color(1.0f, 1.0f, 0.7f);
                Debug.Log("CBC: Tritanopia mode applied.");
                break;
        }
    }
}
