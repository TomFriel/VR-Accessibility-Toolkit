using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

/// <summary>
/// Controls the scene-wide colour adjustments to roughly simulate
/// different types of colour vision deficiency (CVD).
/// This script expects a Volume with a ColorAdjustments override.
/// </summary>
[RequireComponent(typeof(Volume))]
public class ColourBlindModeController : MonoBehaviour
{
    // Reference to the ColorAdjustments override inside the Volume profile.
    private ColorAdjustments colorAdjustments;

    /// <summary>
    /// Static property so other scripts (like AccessibilityPoster)
    /// can read what mode is currently active without needing a direct reference.
    /// </summary>
    public static CvdMode CurrentMode { get; private set; }

    /// <summary>
    /// Enum of the supported CVD modes.
    /// It's defined INSIDE this class, so other scripts must refer to it as:
    /// ColourBlindModeController.CvdMode
    /// </summary>
    public enum CvdMode
    {
        Normal = 0,
        Protanopia = 1,
        Deuteranopia = 2,
        Tritanopia = 3
    }

    /// <summary>
    /// The mode currently selected in the Inspector.
    /// This is also updated at runtime via keyboard input.
    /// </summary>
    public CvdMode mode = CvdMode.Normal;

    private void Start()
    {
        // Get the Volume component on the same GameObject.
        var volume = GetComponent<Volume>();

        if (volume == null)
        {
            Debug.LogError("CBC: No Volume component found on this GameObject.");
            return;
        }

        // Try to get a ColorAdjustments override from the Volume profile.
        if (!volume.profile.TryGet(out colorAdjustments))
        {
            Debug.LogError("CBC: No ColorAdjustments override found on the Volume profile.");
            return;
        }

        Debug.Log("CBC: ColorAdjustments found, script is ready.");

        // Apply the initial mode set in the Inspector.
        ApplyMode();
    }

    private void Update()
    {
        // If we don't have ColorAdjustments, do nothing.
        if (colorAdjustments == null) return;

        // TEMP: keyboard input for testing in the Editor.
        // Later you can hook these to VR UI buttons or controller input.
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

    /// <summary>
    /// Applies the selected mode by adjusting the ColorAdjustments settings.
    /// This is a rough approximation, not medically accurate simulation.
    /// </summary>
    private void ApplyMode()
    {
        if (colorAdjustments == null) return;

        // Update the static mode so other scripts can read it.
        CurrentMode = mode;

        switch (mode)
        {
            case CvdMode.Normal:
                // No special filter: reset to neutral settings.
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = 0f;
                colorAdjustments.colorFilter.value = Color.white;
                Debug.Log("CBC: Normal mode applied.");
                break;

            case CvdMode.Protanopia:
                // Rough Protanopia-ish look:
                // slightly desaturated with a cyan-ish tint.
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = -40f;
                colorAdjustments.colorFilter.value = new Color(0.7f, 1.0f, 1.0f);
                Debug.Log("CBC: Protanopia mode applied.");
                break;

            case CvdMode.Deuteranopia:
                // Rough Deuteranopia-ish look:
                // slightly desaturated with a magenta-ish tint.
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = -40f;
                colorAdjustments.colorFilter.value = new Color(1.0f, 0.8f, 1.0f);
                Debug.Log("CBC: Deuteranopia mode applied.");
                break;

            case CvdMode.Tritanopia:
                // Rough Tritanopia-ish look:
                // stronger desaturation with a yellowish tint.
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = -50f;
                colorAdjustments.colorFilter.value = new Color(1.0f, 1.0f, 0.7f);
                Debug.Log("CBC: Tritanopia mode applied.");
                break;
        }
    }
}
